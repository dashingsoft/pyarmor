.. _how pyarmor does it:

How PyArmor Does It
===================

Look at what happened after ``foo.py`` is obfuscated by PyArmor. Here are the
files list in the output path :file:`dist`::

    foo.py

    pytransform/
        __init__.py
        _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
        pytransform.key
        license.lic

:file:`dist/foo.py` is obfuscated script, the content is::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'\x06\x0f...')

There is an extra folder `pytransform` called :ref:`Runtime Package`, which are
the only required to run or import obfuscated scripts. So long as this package
is in any Python Path, the obfuscated script `dist/foo.py` can be used as normal
Python script. That is to say:

**The original python scripts can be replaced with obfuscated scripts seamlessly.**


.. _how to obfuscate scripts:

How to Obfuscate Python Scripts
-------------------------------

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

Next serializing reformed code object and obfuscate it to protect constants and
literal strings::

    char *string_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( string_code  );

Finally generate obfuscated script::

    sprintf( buf, "__pyarmor__(__name__, __file__, b'%s')", obfuscated_code );
    save_file( "dist/foo.py", buf );

The obfuscated script is a normal Python script, it looks like this::

    __pyarmor__(__name__, __file__, b'\x01\x0a...')


.. _how to deal with plugins:

How to Deal With Plugins
------------------------

In PyArmor, the plugin is used to inject python code into the obfuscted script
before the script is obfuscated, thus the plugin code could be executed when the
obfuscated script is running. For example, use a plugin to check internet time::

    pyarmor obfuscate --plugin check_ntp_time foo.py

Why not insert the plugin code into the script directly? Because most of them
must be called in the obufscated scripts. For example, get the license
information of the obfuscated scripts.

Each plugin is a normal Python script, PyArmor searches it by this way:

* If the plugin has absolute path, then find the corresponding `.py` file exactly.
* If it has relative path, search the `.py` file in:
    - The current path
    - ``$HOME/.pyarmor/plugins``
    - ``{pyarmor_folder}/plugins``
* Raise exception if not found

When there is plugin specified as obfuscating the script, each comment line will
be scanned to find any plugin marker. There are 3 types of plugin marker:

* Plugin Definition Marker
* Plugin Inline Marker
* Plugin Call Marker

The `Plugin Definition Marker` looks like this::

    # {PyArmor Plugins}

Generally there is only one in a script, all the plugins will be injected
here. It must be one leading comment line, no indentation. If there is no plugin
definition marker, none of plugins will be injected.

The others are mainly used to call the function defined in the plugin
scripts. There are 3 forms, any comment line with this prefix will be as a
plugin marker::

    # PyArmor Plugin:
    # pyarmor_
    # @pyarmor_

They could appear many times, in any indentation, generally should be behind
plugin definition marker.

The first form called `Plugin Inline Marker`, PyArmor just removes this pattern
and one following whitespace exactly, and leave the rest part as it is. For
example, these are inline markers in the script ``foo.py``::

    # PyArmor Plugin: check_ntp_time()
    # PyArmor Plugin: print('This is plugin code')
    # PyArmor Plugin: if sys.flags.debug:
    # PyArmor Plugin:     check_something():

In the ``dist/foo.py``, they'll be replaced as::

    check_ntp_time()
    print('This is plugin code')
    if sys.flags.debug:
        check_something()

So long as there is any plugin specified in the command line, these replacements
will be taken place. If there is no external plugin script, use special plugin
name ``on`` in the command line. For example::

    pyarmor obfuscate --plugin on foo.py

The second form called `Plugin Call Marker`, it's only used to call function
deinfed in the plugin script. Besides, if this function name is not specified as
plugin name, PyArmor doesn't touch this marker. For example, obufscate the
script by this command::

    pyarmor obfuscate --plugin check_ntp_time foo.py

In the ``foo.py``, only the first marker will be handled, the second marker will
be kept as it is, because there is no plugin name specified in the command line
as the function name ``check_multi_mac``::

    # pyarmor_check_ntp_time()
    # pyarmor_check_multi_mac()

    ==>

    check_ntp_time()
    # pyarmor_check_multi_mac()

The last form ``# @pyarmor_`` is almost same as the second, but the comment
prefix will be replaced with ``@``, it's mainly used to inject a decorator. For
example::

    # @pyarmor_assert_obfuscated(foo.connect)
    def login(user, name):
        foo.connect(user, name)

    ==>

    @assert_obfuscated(foo.connect)
    def login(user, name):
        foo.connect(user, name)

If the plugin name have a leading ``@``, it will be injected into the script
only when it's used in the script, otherwise it's ignored. For example::

    pyarmor obfuscate --plugin @check_ntp_time foo.py

The script ``foo.py`` must call plugin function ``check_ntp_time`` by one of
`Plugin Call Marker`. For example::

    # pyarmor_check_ntp_time()

The `Plugin Inline Marker` doesn't work. For example::

    # PyArmor Plugin: check_ntp_time()

Even this marker will be replaced with ``check_ntp_time()``, but the plugin
script will not be injected into the obfuscated script. When it runs, it will
complain of no function `check_ntp_name` found.

.. _special handling of entry script:

Special Handling of Entry Script
--------------------------------

There are 2 extra changes for entry script:

* Before obfuscating, insert protection code to entry script.
* After obfuscated, insert bootstrap code to obfuscated script.

Before obfuscating entry scipt, PyArmor will search the content line by line. If
there is line like this::

    # {PyArmor Protection Code}

PyArmor will replace this line with protection code.

If there is line like this::

    # {No PyArmor Protection Code}

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
            def _check_co_key(co, v):
                return (len(co.co_names), len(co.co_consts), len(co.co_code)) == v
            for k, (v1, v2, v3) in {keylist}:
                co = getattr(pytransform, k).{code}
                if not _check_co_key(co, v1):
                    raise RuntimeError('unexpected pytransform.py')
                if v2:
                    if not _check_co_key(co.co_consts[1], v2):
                        raise RuntimeError('unexpected pytransform.py')
                if v3:
                    if not _check_co_key(co.{closure}[0].cell_contents.{code}, v3):
                        raise RuntimeError('unexpected pytransform.py')

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

All the string template ``{xxx}`` will be replaced with real value by PyArmor.

To prevent PyArmor from inserting this protection code, pass
``--no-cross-protection`` as obfuscating the scripts::

    pyarmor obfuscate --no-cross-protection foo.py

After the entry script is obfuscated, the :ref:`Bootstrap Code` will be inserted
at the beginning of the obfuscated script.


.. _how to run obfuscated scripts:

How to Run Obfuscated Script
----------------------------

How to run obfuscated script ``dist/foo.py`` by Python Interpreter?

The first 2 lines, which called ``Bootstrap Code``::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

It will fulfil the following tasks

* Load dynamic library ``_pytransform`` by ``ctypes``
* Check ``license.lic`` is valid or not
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

* ``__armor_enter__`` is called as soon as code object is executed, it will
  restore byte-code of this code object::

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

* ``__armor_exit__`` is called so long as code object completed execution, it
  will obfuscate byte-code again::

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

.. _how to pack obfuscated scripts:

How To Pack Obfuscated Scripts
------------------------------

The obfuscated scripts generated by PyArmor can replace Python scripts
seamlessly, but there is an issue when packing them into one bundle by
PyInstaller:

**All the dependencies of obfuscated scripts CAN NOT be found at all**

To solve this problem, the common solution is

1. Find all the dependencies by original scripts.
2. Add runtimes files required by obfuscated scripts to the bundle
3. Replace original scripts with obfuscated in the bundle
4. Replace entry script with obfuscated one

PyArmor provides command :ref:`pack` to achieve this. But in some cases maybe it
doesn't work. This document describes what the command `pack` does, and also
could be as a guide to bundle the obfuscated scripts by yourself.

First install ``pyinstaller``::

    pip install pyinstaller

Then obfuscate scripts to ``dist/obf``::

    pyarmor obfuscate --output dist/obf --package-runtime 0 hello.py

Next generate specfile, add runtime files required by obfuscated scripts::

    pyi-makespec --add-data dist/obf/license.lic:. \
                 --add-data dist/obf/pytransform.key:. \
                 --add-data dist/obf/_pytransform.*:. \
                 -p dist/obf --hidden-import pytransform \
                 hello.py

If the scripts are obfuscated by super mode::

    pyarmor obfuscate --output dist/obf --advanced 2 --package-runtime 0 hello.py

Generate `.spec` file by this command::

    pyi-makespec -p dist/obf --hidden-import pytransform hello.py

.. _note:

    In windows, the ``:`` should be replace with ``;`` in the command line.

And patch specfile ``hello.spec``, insert the following lines after the
``Analysis`` object. The purpose is to replace all the original scripts with
obfuscated ones::

    src = os.path.abspath('.')
    obf_src = os.path.abspath('dist/obf')

    for i in range(len(a.scripts)):
        if a.scripts[i][1].startswith(src):
            x = a.scripts[i][1].replace(src, obf_src)
            if os.path.exists(x):
                a.scripts[i] = a.scripts[i][0], x, a.scripts[i][2]

    for i in range(len(a.pure)):
        if a.pure[i][1].startswith(src):
            x = a.pure[i][1].replace(src, obf_src)
            if os.path.exists(x):
                if hasattr(a.pure, '_code_cache'):
                    with open(x) as f:
                        a.pure._code_cache[a.pure[i][0]] = compile(f.read(), a.pure[i][1], 'exec')
                a.pure[i] = a.pure[i][0], x, a.pure[i][2]

Run patched specfile to build final distribution::

    pyinstaller --clean -y hello.spec

.. note::

   Option ``--clean`` is required, otherwise the obfuscated scripts will not be
   replaced because the cached `.pyz` will be used.

Check obfuscated scripts work::

   dist/hello/hello.exe

.. include:: _common_definitions.txt
