# Protect Python Scripts By PyArmor

PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts. It
protects Python scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate co_code of each function (code object) in runtime.
* Clear f_locals of frame as soon as code object completed execution.
* Verify the license file of obfuscated scripts while running it.

Look at what happened after `foo.py` is obfuscated by PyArmor. Here
are the files list in the output path `dist`

```
    foo.py

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pytransform.key
    license.lic
```

`dist/foo.py` is obfuscated script, the content is

``` python
    from pytransform import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...')
```

All the other extra files called `Runtime Files`, which are required to run or
import obfuscated scripts. So long as runtime files are in any Python path,
obfuscated script `dist/foo.py` can be used as normal Python script. That is to say:

**The original python scripts can be replaced with obfuscated scripts seamlessly.**

## Obfuscated Python Scripts

How to obfuscate python scripts by PyArmor?

First compile Python script to code object

``` c
    char *filename = "foo.py";
    char *source = read_file( filename );
    PyCodeObject *co = Py_CompileString( source, "<frozen foo>", Py_file_input );
```

Next change this code object as the following ways

* Wrap byte code `co_code` within a `try...finally` block

```
    wrap header:

            LOAD_GLOBALS    N (__armor_enter__)     N = length of co_consts
            CALL_FUNCTION   0
            POP_TOP
            SETUP_FINALLY   X (jump to wrap footer) X = size of original byte code

    changed original byte code:

            Increase oparg of each absolute jump instruction by the size of wrap header

            Obfuscate original byte code

            ...

    wrap footer:

            LOAD_GLOBALS    N + 1 (__armor_exit__)
            CALL_FUNCTION   0
            POP_TOP
            END_FINALLY
```

* Append function names `__armor_enter`, `__armor_exit__` to `co_consts`

* Increase `co_stacksize` by 2

* Set CO_OBFUSCAED (0x80000000) flag in `co_flags`

* Change all code objects in the `co_consts` recursively

Then serialize this reformed code object, obfuscate it to protect constants and literal strings

``` c
    char *string_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( string_code  );
```

Finally generate obfuscated script

``` c
    sprintf( buf, "__pyarmor__(__name__, __file__, b'%s')", obfuscated_code );
    save_file( "dist/foo.py", buf );
```

The obfuscated script is a normal Python script, it looks like this

```
    __pyarmor__(__name__, __file__, b'\x01\x0a...')
```

## Run Obfuscated Script

How to run obfuscated script `dist/foo.py` by Python Interpreter?

The first 2 lines, which called `Bootstrap Code`

``` python
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
```

It will fulfil the following tasks

* Load dynamic library `_pytransform` by `ctypes`
* Check `dist/license.lic` is valid or not
* Add 3 cfunctions to module `builtins`
  * `__pyarmor__`
  * `__armor_enter__`
  * `__armor_exit__`

The next code line in `dist/foo.py` is

```
    __pyarmor__(__name__, __file__, b'\x01\x0a...')

```
`__pyarmor__` is called, it will import original module from obfuscated code

```c
    static PyObject *
    __pyarmor__(char *name, char *pathname, unsigned char *obfuscated_code)
    {
        char *string_code = restore_obfuscated_code( obfuscated_code );
        PyCodeObject *co = marshal.loads( string_code );
        return PyImport_ExecCodeModuleEx( name, co, pathname );
    }
```

After that, in the runtime of this python interpreter

* `__armor_enter__` is called as soon as code object is executed, it
  will restore byte-code of this code object

``` c
    static PyObject *
    __armor_enter__(PyObject *self, PyObject *args)
    {
        // Got code object
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // Increase refcalls of this code object
        // Borrow co_names->ob_refcnt as call counter
        // Generally it will not increased  by Python Interpreter
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt ++;

        // Restore byte code if it's obfuscated
        if (IS_OBFUSCATED(f_code->co_flags)) {
            restore_byte_code(f_code->co_code);
            clear_obfuscated_flag(f_code);
        }

        Py_RETURN_NONE;
    }
```

* `__armor_exit__` is called so long as code object completed
  execution, it will obfuscate byte-code again

``` c
    static PyObject *
    __armor_exit__(PyObject *self, PyObject *args)
    {
        // Got code object
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // Decrease refcalls of this code object
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt --;

        // Obfuscate byte code only if this code object isn't used by any function
        // In multi-threads or recursive call, one code object may be referenced
        // by many functions at the same time
        if (refcalls->ob_refcnt == 1) {
            obfuscate_byte_code(f_code->co_code);
            set_obfuscated_flag(f_code);
        }

        // Clear f_locals in this frame
        clear_frame_locals(frame);

        Py_RETURN_NONE;
    }
```

## License of Obfuscated Scripts

When call `pyarmor_runtime()` in `dist/foo.py`, it will check the file
`dist/license.lic`. If it's invalid, the python interpreter reports
error and quits. The default license is generated while obfuscating
Python scripts. It allows to run obfuscated scripts in any machine and
never expired.

If we generate a new license which includes an expired date, or some
hardware infromation, for examples, serial number of harddisk, mac
address of network address etc. The obfuscated scripts will be
aborted, if any of these conditions isn't satisfied in the target
machine.

PyArmor has command `hdinfo` to print hardware information in target machine

```bash
    pyarmor hdinfo
```

PyArmor has command `licenses` used to generate new liceses

``` bash
    pyarmor licenses
            --expired 2018-12-31
            --bind-disk "100304PBN2081SF3NJ5T"
            --bind-mac "70:f1:a1:23:f0:94"
            --bind-ipv4 "202.10.2.52"
            Customer-Jondy
```

More information visit [PyArmor Homepage](http://pyarmor.dashingsoft.com/)
