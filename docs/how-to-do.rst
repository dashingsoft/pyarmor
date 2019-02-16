=======================
 How |PyArmor| Does It
=======================

Look at what happened after ``foo.py`` is obfuscated by PyArmor. Here
are the files list in the output path :file:`dist`::

    foo.py

    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pytransform.py
    pytransform.key
    license.lic

:file:`dist/foo.py` is obfuscated script, the content is::


    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...')

All the other extra files called `Runtime Files`, which are required to run or
import obfuscated scripts. So long as runtime files are in any Python path,
obfuscated script `dist/foo.py` can be used as normal Python script. That is to say:

**The original python scripts can be replaced with obfuscated scripts seamlessly.**

.. _how to obfuscate scripts:

How to Obfuscate Python Scripts
===============================

How to obfuscate python scripts by PyArmor?


First compile python script to code object::

    char *filename = "foo.py";
    char *source = read_file( filename );
    PyCodeObject *co = Py_CompileString( source, "<frozen foo>", Py_file_input );


Then change code object as the following way

* Wrap byte code ``co_code`` within a ``try...finally`` block::

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

* Append function names ``__armor_enter``, ``__armor_exit__`` to ``co_consts``

* Increase ``co_stacksize`` by 2

* Set CO_OBFUSCAED (0x80000000) flag in ``co_flags``

* Change all code objects in the ``co_consts`` recursively


Next serializing reformed code object and obfuscate it to protect
constants and literal strings::

    char *string_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( string_code  );

Finally generate obfuscated script::

    sprintf( buf, "__pyarmor__(__name__, __file__, b'%s')", obfuscated_code );
    save_file( "dist/foo.py", buf );

The obfuscated script is a normal Python script, it looks like this::

    __pyarmor__(__name__, __file__, b'\x01\x0a...')


.. _how to run obfuscated scripts:

How to Run Obfuscated Script
============================

How to run obfuscated script ``dist/foo.py`` by Python Interpreter?

The first 2 lines, which called ``Bootstrap Code``::

    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

It will fulfil the following tasks

* Load dynamic library ``_pytransform`` by ``ctypes``
* Check ``dist/license.lic`` is valid or not
* Add 3 cfunctions to module ``builtins``: ``__pyarmor__``, ``__armor_enter__``, ``__armor_exit__``

The next code line in ``dist/foo.py`` is::

    __pyarmor__(__name__, __file__, b'\x01\x0a...')

``__pyarmor__`` is called, it will import original module from obfuscated code::

    static PyObject *
    __pyarmor__(char *name, char *pathname, unsigned char *obfuscated_code)
    {
        char *string_code = restore_obfuscated_code( obfuscated_code );
        PyCodeObject *co = marshal.loads( string_code );
        return PyImport_ExecCodeModuleEx( name, co, pathname );
    }

After that, in the runtime of this python interpreter

* ``__armor_enter__`` is called as soon as code object is executed, it
  will restore byte-code of this code object::

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

* ``__armor_exit__`` is called so long as code object completed
  execution, it will obfuscate byte-code again::

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

.. _special handling of entry script:

Special Handling of Entry Script
================================

There are 2 extra changes for entry script:

* Before obfuscating, insert protection code to entry script.
* After obfuscated, insert bootstrap code to obfuscated script.

Before obfuscating entry scipt, PyArmor will search the content line
by line. If there is line like this::

    # {PyArmor Protection Code}

PyArmor will replace this line with protection code.

If there is line like this::

    # No PyArmor Protection Code

PyArmor will not patch this script.

If both of lines aren't found, insert protection code before the line::

    if __name__ == '__main__'

Do nothing if no `__main__` line found.

Here it's the default template of protection code::

    def protect_pytransform():

        import pytransform

        def check_obfuscated_script():
            CO_SIZES = 49, 46, 38, 36
            CO_NAMES = set(['pytransform', 'pyarmor_runtime', '__pyarmor__',
                            '__name__', '__file__'])
            co = pytransform.sys._getframe(3).f_code
            if not ((set(co.co_names) <= CO_NAMES)
                    and (len(co.co_code) in CO_SIZES)):
                raise RuntimeError('Unexpected obfuscated script')

        def check_mod_pytransform():
            CO_NAMES = set(['Exception', 'LoadLibrary', 'None', 'PYFUNCTYPE',
                            'PytransformError', '__file__', '_debug_mode',
                            '_get_error_msg', '_handle', '_load_library',
                            '_pytransform', 'abspath', 'basename', 'byteorder',
                            'c_char_p', 'c_int', 'c_void_p', 'calcsize', 'cdll',
                            'dirname', 'encode', 'exists', 'exit',
                            'format_platname', 'get_error_msg', 'init_pytransform',
                            'init_runtime', 'int', 'isinstance', 'join', 'lower',
                            'normpath', 'os', 'path', 'platform', 'print',
                            'pyarmor_init', 'pythonapi', 'restype', 'set_option',
                            'str', 'struct', 'sys', 'system', 'version_info'])

            colist = []

            for name in ('dllmethod', 'init_pytransform', 'init_runtime',
                         '_load_library', 'pyarmor_init', 'pyarmor_runtime'):
                colist.append(getattr(pytransform, name).{code})

            for name in ('init_pytransform', 'init_runtime'):
                colist.append(getattr(pytransform, name).{closure}[0].cell_contents.{code})
            colist.append(pytransform.dllmethod.{code}.co_consts[1])

            for co in colist:
                if not (set(co.co_names) < CO_NAMES):
                    raise RuntimeError('Unexpected pytransform.py')

        def check_lib_pytransform():
            filename = pytransform.os.path.join({rpath}, {filename})
            size = {size}
            n = size >> 2
            with open(filename, 'rb') as f:
                buf = f.read(size)
            fmt = 'I' * n
            checksum = sum(pytransform.struct.unpack(fmt, buf)) & 0xFFFFFFFF
            if not checksum == {checksum}:
                raise RuntimeError("Unexpected %s" % filename)
        try:
            check_obfuscated_script()
            check_mod_pytransform()
            check_lib_pytransform()
        except Exception as e:
            print("Protection Fault: %s" % e)
            pytransform.sys.exit(1)

    protect_pytransform()

All the string template `{xxx}` will be replaced with real value by
PyArmor.

To prevent PyArmor from inserting this protection code, pass
`--cross-protection=0` as obfuscating the scripts::

    pyarmor obfuscate --cross-protection=0 foo.py

After the entry script is obfuscated, the :ref:`Bootstrap Code` will
be inserted at the beginning of the obfuscated script.

.. include:: _common_definitions.txt
