# Protect Python Scripts By Pyarmor

Pyarmor is a command line tool used to import or run obfuscated Python
scripts. It protects Python scripts by the following ways:

* Obfuscate source file to protect constants and literal strings.
* Obfuscate byte code of each code object.
* Clear f_locals of frame as soon as code object completed execution.
* Expired obfuscated scripts, or bind to fixed machine.

Look at what happened after `foo.py` is obfuscated by Pyarmor. Here it's file
list in the output path `dist`

```
    foo.py

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS

    pyshield.key
    pyshield.lic
    product.key
    license.lic

```

`dist/foo.py` is obfuscated script, the content is

``` python
    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...')

```

All the other extra files called `Runtime Files`, which are required to run or
import obfuscated scripts. So long as runtime files are in any Python path,
obfuscated script `foo.py` can be used as normal Python script.

There are 2 phases for Pyarmor to protect Python scrpts:

* Build obfuscated script
* Run or import obfuscated script

## Build Obfuscated Script

First compile Python script to code object

``` c
    char *filename = "foo.py";
    char *source = read_file( filename );
    PyCodeObject *co = Py_CompileString( source, "<frozen foo>", Py_file_input );

```

Next change the code object as the following way:

* Wrap byte code `co_code`, insert a `try...finally` block

```
    wrap header:

            LOAD_GLOBALS    N (__armor_enter__)
            CALL_FUNCTION   0
            POP_TOP
            SETUP_FINALLY   F (jump to wrap footer, the code of finally block)

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

* Set CO_OBFUSCAED flag in `co_flags`

* Change all code object in the `co_consts` recursively

Then serialize this reformed code object, obfuscate it to protect constants and literal strings:

``` c
    char *string_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( string_code  );

```

Finally generate obfuscated script:

``` c
    sprintf( buf, "__pyarmor__(__name__, __file__, b'%s')", obfuscated_code );
    save_file( "dist/foo.py", buf );

```

The obfuscated script is a normal Python script, It looks like this

```
    __pyarmor__(__name__, __file__, b'\x01\x0a...')

```

## Run Obfuscated Script

In order to run the obfuscated script, there are 3 functions need to be added to `builtins` module:

* `__pyarmor__`
* `__armor_enter__`
* `__armor_exit__`

It can be done by the following lines, which called `Bootstrap Code`

``` python
    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

```

When obufscated module is imported by Python interpreter:

* `__pyarmor__` is called at first, it will import obufscated module

```c
    static PyObject *
    __pyarmor__(char *name, char *pathname, unsigned char *obfuscated_code)
    {
        char *string_code = resotre_obfuscated_code( obfuscated_code );
        PyObject *co = marshal.loads( string_code );
        return PyImport_ExecCodeModuleEx( name, co, pathname );
    }
```

* `__armor_enter__` is called as soon as code object is executed

``` c
    static PyObject *
    __armor_enter__(PyObject *self, PyObject *args)
    {
        // Got code object
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // Increase refcalls of this code object
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

* `__armor_exit__` is called so long as code object completed execution

``` c
    static PyObject *
    exit_armor(PyObject *self, PyObject *args)
    {
        // Got code object
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // Decrease refcalls of this code object
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt --;

        // Obfuscate byte code only if this code object isn't used by any function
        if (refcalls->ob_refcnt == 1) {
          obfuscate_byte_code(f_code->co_code);
          set_obfuscated_flag(f_code);
        }

        // Clear f_locals in this frame
        clear_frame_locals(frame);

        Py_RETURN_NONE;
    }

```

## Expired Obfuscated Script

By default the obfuscated scripts can run in any machine and never expired. This
behaviour can be changed by replacing runtime file `dist/license.lic`

First generate an expired license:

``` bash
    python pyarmor.py licenses --expired 2018-12-31 Customer-Jondy

```

It will make a new `license.lic`, replace `dist/license.lic` with this one. The
obfuscated script will not work after 2018.

Now generate a license bind to fixed machine:

``` bash
    python pyarmor.py licenses --bind-hard "100304PBN2081SF3NJ5T"
                               --bind-mac "70:f1:a1:23:f0:94"
                               --bind-ipv4 "202.10.2.52"
                               Customer-Jondy
```

Interesting? More information visit https://github.com/dashingsoft/pyarmor
