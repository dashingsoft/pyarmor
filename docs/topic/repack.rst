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

Once it's set, pyarmor will first obfuscate the scripts, then automatically pack them to one bundle

Packing Scripts Automatically
=============================

Suppose our project tree like this::

    project/
        ├── foo.py
        ├── queens.py
        └── joker/
            ├── __init__.py
            ├── queens.py
            └── config.json

Let's check what happens when the following commands are executed::

    $ cd project
    $ pyarmor gen --pack onefile foo.py

1. Pyarmor first open `foo.py`, then find it need `queens.py` and package `joker`
2. Then obfuscate all of them to one temporary path `.pyarmor/pack/dist`
3. Next pyarmor call PyInstaller with plain script `foo.py`, to get all the system packages [#]_ used by `foo.py`, and save all of them to hiddenimports table.
4. Finally pyarmor call PyInstaller again but with obfuscated scripts and all of hidden imports to generate final bundle.

Now let's run the final bundle, it's `dist/foo` or `dist/foo.exe`::

    $ ls dist/foo
    $ dist/foo

If need one folder bundle, just pass `onedir` to pack::

    $ pyarmor gen --pack onedir foo.py
    $ ls dist/foo
    $ dist/foo/foo

.. [#] Python system modules and packages aren't obfuscated

Using specfile
--------------

In this project, there already has one ``foo.spec`` which could be used to pack plain script to onefile. For example::

    $ pyinstaller foo.spec
    $ dist/foo

In this case, pass it ``foo.spec``  to :option:`--pack` directly. For example::

    $ pyarmor gen --pack foo.spec -r foo.py joker/

1. Pyarmor obfuscates the scripts list in the command line, save them to `.pyarmor/pack/dist`
2. Then generates ``foo.patched.spec`` by ``foo.spec``, this patch could replace plain scripts with obfuscated ones in the bundle
3. Finally call PyInstaller_ to pack bundle by ``foo.patched.spec``

.. note::

   By specfile, only listed scripts are obfuscated. If need obfuscate other used modules and packages, list all of them in command line.

Checking Obfuscated Scripts Have Been Packed
--------------------------------------------

Add one line in the script ``foo.py`` or ``joker/__init__.py``

.. code-block:: python

    print('this is __pyarmor__', __pyarmor__)

If it's not obfuscated, the final bundle will raise error. Because builtin name ``__pyarmor__`` is only available in the obfuscated scripts.

Using More PyInstaller Options
------------------------------

If need extra PyInstaller options, using configuration item ``pack:pyi_options``. For example, reset it with one PyInstaller option ``-w``::

    $ pyarmor cfg pack:pyi_options = "-w"

Let's append another option ``-i``, note that it must be one whitespace between option ``-i`` and its value, do not use ``=``. For example::

    $ pyarmor cfg pack:pyi_options ^ "-i favion.ico"

Append another option::

    $ pyarmor cfg pack:pyi_options ^ "--add-data joker/config.json:joker"

.. note::

    In Windows, it may need quote ``^``. For example::

        C:\Projects\build> pyarmor cfg pack:pyi_options "^" "-i favion.ico"

.. seealso:: :ref:`pyarmor cfg`

Using More Obfuscation Options
------------------------------

In Darwin, let obfuscated scripts work in both intel and Apple Silicon by extra option ``--platform darwin.x86_64,darwin.arm64``::

    $ pyarmor gen --pack onefile --platform darwin.x86_64,darwin.arm64 foo.py

You can use any other obfuscation options to improve security. For example::

    $ pyarmor gen --pack onefile --private foo.py

Note that some of them may not work. For example, :option:`--restrict` can't be used with :option:`--pack`.

Packing obfuscated scripts manually
===================================

If something is wrong with :option:`--pack`, or the final bundle doesn't work, try to pack the obfuscated scripts manually.

You need to know how to `using PyInstaller`__ and `using spec file`__, if not, learn it by yourself.

__ https://pyinstaller.org/en/stable/usage.html
__ https://pyinstaller.org/en/stable/spec-files.html

Here is an example to pack script ``foo.py`` in the path ``/path/to/src``

* First obfuscate the script by Pyarmor [#]_::

    $ cd /path/to/src
    $ pyarmor gen -O obfdist -r foo.py joker/

* Then generate ``foo.spec`` by PyInstaller [#]_::

    $ pyi-makespec --onefile foo.py

* Next patch ``foo.spec`` before line ``pyz = PYZ``, this is major work

.. code-block:: python

    a = Analysis(
        ...
    )

    # Pyarmor patch start:

    obfpath = r'/path/to/obfdist'
    srcpath = r'/path/to/src'
    rtpkg = 'pyarmor_runtime_000000'
    rtext = 'pyarmor_runtime.so'

    def pyarmor_patcher(src, obfdist):

        # Make sure both of them are absolute paths
        src = os.path.abspath(src)
        obfdist = os.path.abspath(obfdist)

        count = 0
        for i in range(len(a.scripts)):
            if a.scripts[i][1].startswith(src):
                x = a.scripts[i][1].replace(src, obfdist)
                if os.path.exists(x):
                    a.scripts[i] = a.scripts[i][0], x, a.scripts[i][2]
                    count += 1
        if count == 0:
            raise RuntimeError('No obfuscated script found')

        for i in range(len(a.pure)):
            if a.pure[i][1].startswith(src):
                x = a.pure[i][1].replace(src, obfdist)
                if os.path.exists(x):
                    if hasattr(a.pure, '_code_cache'):
                        with open(x) as f:
                            a.pure._code_cache[a.pure[i][0]] = compile(
                                f.read(), a.pure[i][1], 'exec')
                    a.pure[i] = a.pure[i][0], x, a.pure[i][2]

    a.pure.append((
        rtpkg,
        os.path.join(obfpath, rtpkg, '__init__.py'),
        'PYMODULE'
    ))
    a.binaries.append((
        os.path.join(rtpkg, rtext),
        os.path.join(obfpath, rtpkg, rtext),
        'EXTENSION'
    ))
    pyarmor_patcher(srcpath, obfpath)

    # Pyarmor patch end.

    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

* Finally generate bundle by this patched ``foo.spec``, use option `--clean` to to remove all cached files::

    $ pyinstaller --clean foo.spec

If following this example, please

* Replace all the ``/path/to/src`` and ``/path/to/obfdist`` with actual path
* Replace all the ``pyarmor_runtime_000000`` with actual name
* In Windows, replace ``pyarmor_runtime.so`` with ``pyarmor_runtime.pyd``

**how to verify obfuscated scripts have been packed**

Inserting some print statements in the ``foo.spec`` to print which script is replaced, or add some code only works in the obfuscated script.

For example, add one line in the main script ``foo.py``

.. code-block:: python

    print('this is __pyarmor__', __pyarmor__)

If it's not obfuscated, the final bundle will raise error.

.. rubric:: notes

.. [#] Do not use :option:`-i` and :option:`--prefix` to obfuscate the scripts
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
