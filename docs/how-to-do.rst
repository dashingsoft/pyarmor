=======================
 How |PyArmor| Does It
=======================

Look at what happened after ``foo.py`` is obfuscated by Pyarmor. Here
are the files list in the output path :file:`dist`::

    foo.py

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS

    pyshield.key
    pyshield.lic
    product.key
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

How to obfuscate python scripts by Pyarmor?


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

.. include:: _common_definitions.txt
