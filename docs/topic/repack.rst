=========================
Insight Into Pack Command
=========================

.. highlight:: console

.. program:: pyarmor gen

Pyarmor has no pack feature, it need call PyInstaller_ to pack the obfuscated script to final bundle, so first install PyInstaller_::

    $ pip install pyinstaller

PyInstaller_ will analysis script to find imported modules and packages, once the script is obfuscated, nothing could be found, the final bundle complains of missing module.

Pyarmor provides option :option:`--pack` to fix this problem, it supports the following values

- `onefile`: pack the obfuscated script to onefile
- `onedir`: pack the obfuscated script to onedir
- specfile: one ``.spec`` file used by PyInstaller to generate bundle

Once it's set, pyarmor will not only obfuscate the scripts, but also pack them to one bundle

Packing Scripts Automatically
=============================

Suppose our project tree like this::

    project/
        ├── foo.py
        ├── foo.spec
        ├── util.py
        └── joker/
            ├── __init__.py
            ├── card.py
            ├── queens.py
            └── config.json

Let's check what happens when the following commands are executed::

    $ cd project
    $ pyarmor gen --pack onefile foo.py

1. Pyarmor first call PyInstaller_ to analysis plain script `foo.py` to find all the imported moduels and packages
2. The imported module `util` and package `joker` are in the same path of `foo.py`, so Pyarmor will obfuscate `foo.py`, `util.py` and package `joker` by obfuscation options, and save them to path `.pyarmor/pack/dist`
3. For the other imported modules and packages, save them to hidden imports table
4. Finally pyarmor call PyInstaller again, pack all obfuscated scripts in `.pyarmor/pack/dist` and all the modules and packages in hidden imports table to one bundle.

Now let's run the final bundle, it's `dist/foo` or `dist/foo.exe`::

    $ ls dist/foo
    $ dist/foo

If need one folder bundle, just pass `onedir` to pack::

    $ pyarmor gen --pack onedir foo.py
    $ ls dist/foo
    $ dist/foo/foo

Using specfile
--------------

In this project, there already has one ``foo.spec`` which could be used to pack plain script to onefile. For example::

    $ pyinstaller foo.spec
    $ dist/foo

In this case, pass it to :option:`--pack` directly. For example::

    $ pyarmor gen --pack foo.spec -r foo.py util.py joker/

What will Pyarmor do?

1. Pyarmor first obfuscates the scripts list in the command line, save them to `.pyarmor/pack/dist`
2. Next generates ``foo.patched.spec`` by ``foo.spec``
3. Finally call PyInstaller_ to pack the bundle by ``foo.patched.spec``

This patched specfile could replace plain scripts with obfuscated ones in `.pyarmor/pack/dist` when generating the bundle

.. note::

   By this way, only listed scripts are obfuscated. If need obfuscate other used modules and packages, list all of them in command line.

Checking Obfuscated Scripts Have Been Packed
--------------------------------------------

Add one line in the script ``foo.py`` or ``joker/__init__.py``

.. code-block:: python

    print('this is __pyarmor__', __pyarmor__)

If it's not obfuscated, the final bundle will raise error. Because builtin name ``__pyarmor__`` is only available in the obfuscated scripts.

Using More PyInstaller Options
------------------------------

If need extra PyInstaller options, using configuration item ``pack:pyi_options``. For example, reset it with one PyInstaller option ``-w``::

    $ pyarmor cfg pack:pyi_options = " -w"

Note that there need one leading whitespace in the ``" -w"``, otherwise shell may complain of syntax error.

Let's append another option ``-i``, it must be one whitespace between option ``-i`` and its value, do not use ``=``. For example::

    $ pyarmor cfg pack:pyi_options + " -i favion.ico"

Append another option::

    $ pyarmor cfg pack:pyi_options + " --add-data joker/config.json:joker"

All of them could be done by one command::

    $ pyarmor cfg pack:pyi_options = " -w  -i favion.ico --add-data joker/config.json:joker"

.. seealso:: :ref:`pyarmor cfg`

Using More Obfuscation Options
------------------------------

You can use any other obfuscation options to improve security. For example::

    $ pyarmor gen --pack onefile --private foo.py

Anoter example, in Darwin, let obfuscated scripts work in both intel and Apple Silicon by extra option ``--platform darwin.x86_64,darwin.arm64``::

    $ pyarmor cfg pack:pyi_options = "--target-architecture universal2"
    $ pyarmor gen --pack onefile --platform darwin.x86_64,darwin.arm64 foo.py

Note that some of them may not work. For example, :option:`--restrict` can't be used with :option:`--pack`.

Packing obfuscated scripts manually
===================================

If something is wrong with :option:`--pack`, or the final bundle doesn't work, try to pack the obfuscated scripts manually.

You need to know how to `using PyInstaller`__ and `using spec file`__, if not, learn it by yourself.

__ https://pyinstaller.org/en/stable/usage.html
__ https://pyinstaller.org/en/stable/spec-files.html

* First obfuscate the script by Pyarmor. List all the scripts and folders need to be obfuscated after main script, other obfuscation options could be used, but no :option:`-i` or :option:`--prefix` [#]_::

    $ cd project/
    $ pyarmor gen -O obfdist -r foo.py util.py joker/

* Then generate ``foo.spec`` by PyInstaller_ [#]_::

    $ pyi-makespec --onefile foo.py

* Next patch ``foo.spec`` before line ``pyz = PYZ``, this is major work

.. code-block:: python

    # Pyarmor patch start:

    srcpath = ''
    obfpath = 'obfdist'

    def apply_pyarmor_patch(srcpath, obfpath):

        from PyInstaller.compat import is_win, is_cygwin
        extname = 'pyarmor_runtime' + ('.pyd' if is_win or is_cygwin else '.so')

        from glob import glob
        rtpkg = glob(os.path.join(obfpath, '*', extname))
        if len(rtpkg) != 1:
            raise RuntimeError('No runtime package found')
        rtpkg = os.path.basename(os.path.dirname(rtpkg[0]))

        extpath = os.path.join(rtpkg, extname)

        if hasattr(a.pure, '_code_cache'):
            code_cache = a.pure._code_cache
        else:
            from PyInstaller.config import CONF
            code_cache = CONF['code_cache'].get(id(a.pure))

        # Make sure both of them are absolute paths
        src = os.path.abspath(srcpath)
        obf = os.path.abspath(obfpath)

        count = 0
        for i in range(len(a.scripts)):
            if a.scripts[i][1].startswith(src):
                x = a.scripts[i][1].replace(src, obf)
                if os.path.exists(x):
                    a.scripts[i] = a.scripts[i][0], x, a.scripts[i][2]
                    count += 1
        if count == 0:
            raise RuntimeError('No obfuscated script found')

        for i in range(len(a.pure)):
            if a.pure[i][1].startswith(src):
                x = a.pure[i][1].replace(src, obf)
                if os.path.exists(x):
                    code_cache.pop(a.pure[i][0], None)
                    a.pure[i] = a.pure[i][0], x, a.pure[i][2]

        a.pure.append((rtpkg, os.path.join(obf, rtpkg, '__init__.py'), 'PYMODULE'))
        a.binaries.append((extpath, os.path.join(obf, extpath), 'EXTENSION'))

    apply_pyarmor_patch(srcpath, obfpath)

    # Pyarmor patch end.

    # Before this line
    # pyz = PYZ(...)

* Finally generate bundle by this patched ``foo.spec``, use option ``--clean`` to to remove all cached files::

    $ pyinstaller --clean foo.spec

If following this example, please

* Set ``srcpath`` to your path, in this example, it's current path
* Set ``obfpath`` to your real path, in this example, it's ``obfdist``

**how to verify obfuscated scripts have been packed**

Inserting some print statements in the ``foo.spec`` to print which script is replaced, or add some code only works in the obfuscated script.

For example, add one line in the main script ``foo.py``

.. code-block:: python

    print('this is __pyarmor__', __pyarmor__)

If it's not obfuscated, the final bundle will raise error.

.. rubric:: notes

.. [#] :option:`-i` or :option:`--prefix` results in runtime package could not be found
.. [#] Most of the other PyInstaller options could be used here

Packing with PyInstaller Bundle
===============================

.. deprecated:: 8.5.4

    Use :option:`--pack` ``onefile`` or ``onedir`` instead.

The option :option:`--pack` also could accept an executable file generated by PyInstaller_::

    $ pyinstaller foo.py
    $ pyarmor gen --pack dist/foo/foo foo.py

But only PyInstaller < 6.0 works by this method. If this option is set, pyarmor first obfuscates the scripts, then:

* Unpacking this executable to a temporary folder
* Replacing the scripts in bundle with obfuscated ones
* Appending runtime files to the bundle in this temporary folder
* Repacking this temporary folder to an executable file and overwrite the old

.. important::

   Only listed scripts are obfuscated, if need obfuscate more scripts and sub packages, list all of them in command line. For example::

    $ pyarmor gen --pack dist/foo/foo -r *.py dir1 dir2 ...

Segment fault in Apple M1
=========================

In Apple M1 if the final executable segment fault, please check codesign of runtime package::

    $ codesign -v dist/foo/pyarmor_runtime_000000/pyarmor_runtime.so

And re-sign it if the code sign is invalid::

    $ codesign -f -s dist/foo/pyarmor_runtime_000000/pyarmor_runtime.so

If you use :option:`--enable-bcc` or :option:`--enable-jit` to obfuscate the scripts, you need enable `Allow Execution of JIT-compiled Code Entitlement`__

If your app doesn’t have the new signature format, or is missing the DER entitlements in the signature, you’ll need to re-sign the app on a Mac running macOS 11 or later, which includes the DER encoding by default.

If you’re unable to use macOS 11 or later to re-sign your app, you can re-sign it from the command-line in macOS 10.14 and later. To do so, use the following command to re-sign the MyApp.app app bundle with DER entitlements by using a signing identity named "Your Codesign Identity" stored in the keychain::

    $ codesign -s "Your Codesign Identity" -f --preserve-metadata --generate-entitlement-der /path/to/MyApp.app

.. seealso:: `Using the latest code signature format`__

__ https://developer.apple.com/documentation/bundleresources/entitlements/com_apple_security_cs_allow-jit
__ https://developer.apple.com/documentation/xcode/using-the-latest-code-signature-format/

.. include:: ../_common_definitions.txt
