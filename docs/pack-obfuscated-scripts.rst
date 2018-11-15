Pack Obfuscated Scripts
=======================

The obfuscated scripts can replace Python scripts seamlessly, but
there is an issue when packing them into one bundle by [PyInstaller]_,
[py2exe]_, [py2app]_, [cx_Freeze]_

* All the dependencies of obfuscated scripts can NOT be found at all

To solve this problem, the command solution is

1. Find all the dependenices by original scripts.
2. Add runtimes files required by obfuscated scripts to the bundle
3. Update the bundle with obfuscated scripts
4. Replace entry scrirpt with obfuscated one

Depend on what tool used, there are different ways.

Work with PyInstaller
---------------------

Obfuscate scripts to ``dist/obf``::

    pyarmor obfuscate --output dist/obf hello.py

Generate specfile, add the obfuscated entry script and data files
required by obfuscated scripts::

    pyinstaller --add-data dist/obf/*.lic
                --add-data dist/obf/*.key
                --add-data dist/obf/_pytransform.*
                hello.py dist/obf/hello.py

Update specfile ``hello.spec``, insert the following lines after the
``Analysis`` object. The purpose is to replace all the original
scripts with obfuscated ones::

    a.scripts[0] = 'hello', 'dist/obf/hello.py', 'PYSOURCE'
    for i in range(len(a.pure)):
        if a.pure[i][1].startswith(a.pathex[0]):
            a.pure[i] = a.pure[i][0], a.pure[i][1].replace(a.pathex[0], os.path.abspath('dist/obf'), a.pure[i][2]

Run patched specfile to build final distribution::

    pyinstaller hello.spec

Check obfuscated scripts work::

   # It works
   dist/hello/hello.exe

   rm dist/hello/license.lic

   # It should not work
   dist/hello/hello.exe

Work with py2exe for Python 3
-----------------------------

For Python3.3 and later

Build bundle executable to ``dist`` with separated library::

    python -m py2exe.build_exe --library library-org.zip hello.py

Obfuscate scripts to ``dist/obf``::

    pyarmor obfuscate --output dist/obf hello.py

Build executable with obfuscated entry script to ``dist/obf/dist``,
all the other obfuscated scripts should be include by ``-i name`` or
``-p pkgname``::

    ( cd dist/obf;
      python -m py2exe.build_exe --library library.zip -i queens hello.py )

Update ``dist/obf/library.zip``, merge those files only in
``dist/library.zip``. Because the obfuscated scripts in the former,
all the other dependencies in the latter.

Copy all the files to final output::

  cp -a dist/obf/dist/* dist/

Copy runtime files required by obfuscated scripts to finial output::

  ( cd dist/obf;
    cp pyshield.key pyshield.lic product.key license.lic _pytransform.dll ../dist/ )

Check obfuscated scripts work::

   # It works
   dist/hello.exe

   rm dist/license.lic

   # It should not work
   dist/hello.exe

Work with cx_Freeze 5
---------------------

Run ``cxfreeze-quickstart`` to create setup script first.

Build bundle executable to ``dist`` with separated library::

    python setup.py build_exe --build-exe=dist

Obfuscate scripts to ``dist/obf``::

    pyarmor obfuscate --output dist/obf hello.py

Build executable with obfuscated entry script to ``dist/obf/dist``,
all the other obfuscated scripts should be include by ``-i name`` or
``-p pkgname``::

    cd dist/obf
    python setup.py build_exe --build-exe=dist -i queens

Update ``dist/obf/python34.zip``, merge those files only in
``dist/python34.zip``. Because the obfuscated scripts in the former,
all the other dependencies in the latter.

Copy all the files to final output::

  cp -a dist/obf/dist/* dist/

Copy runtime files required by obfuscated scripts to finial output::

  ( cd dist/obf;
    cp pyshield.key pyshield.lic product.key license.lic _pytransform.dll ../dist/ )

Check obfuscated scripts work::

   # It works
   dist/hello.exe

   rm dist/license.lic

   # It should not work
   dist/hello.exe
