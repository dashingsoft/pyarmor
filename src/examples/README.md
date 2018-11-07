# Exmaples

[中文版](README-ZH.md)

A good example maybe is the best teacher. There are several sample
shell scripts distributed with source package of Pyarmor. All of them
are rich comment used to obfuscate Python scripts in different cases,
`.bat` for Windows, `.sh` for Linux and MacOS. Find them in the path
`examples`, edit the variables in it according to actual enviroments,
then run it to obfuscate your python scripts quickly.

* [obfuscate-app.bat](obfuscate-app.bat) / [obfuscate-app.sh](obfuscate-app.sh)

    This is hello world of pyarmor.

* [obfuscate-pkg.bat](obfuscate-pkg.bat) / [obfuscate-pkg.sh](obfuscate-pkg.sh)

    If Python source files are distributd as a package, for example,
    an odoo module. The functions in the package are imported from
    source by end users, this is for you.

* [build-with-project.bat](build-with-project.bat) / [build-with-project.sh](build-with-project.sh)

    If the above two examples do not meet your needs, try
    Project. There are several advantages to manage obfuscated scripts
    by Project

        Increment build, only updated scripts are obfuscated since last build
        Filter scripts, for example, exclude all the test scripts
        More convenient command to manage obfuscated scripts

* [build-for-exe.bat](build-for-exe.bat) / [build-for-freeze.bat](build-for-freeze.bat)

    The basic usage show how to obfuscate scripts by Pyarmor, then
    distribute them by py2exe or cx_Freeze. It's almost applied to
    py2app and PyInstaller.

Not only those scripts, but also some really examples are distributed
with Pyarmor. Just open a command window, follow the instructions in
this document, learn how to use Pyarmor by these examples.

In the rest sections, assume that Python is installed, it can be
called `python`. And Pyarmor has been installed in the
`/path/to/pyarmor`.

Shell commands will shown for Unix-based systems. Windows has
analogous commands for each.

## Example 1: Obfuscate scripts

Learn from this example

* How to obufscate python scripts in the path `examples/simple`
* How to run obfuscated scripts
* How to distribute obfuscated scripts

```
    cd /path/to/pyarmor

    # Obfuscate python scripts in the path `examples/simple`
    python pyarmor.py obfuscate --recursive --src examples/simple --entry queens.py

    # Obfuscated scripts saved in the output path `dist`
    cd dist

    # Run obfuscated scripts
    python queens.py

    # Zip all the files in the path `dist`, distribute this archive
    zip queens-obf.zip .
```


## Example 2: Obfuscate package

Learn from this example

* How to obfuscate a python package `mypkg` in the path `examples/testpkg`
* How to expire this obfuscated package on some day
* How to import obfuscated package `mypkg` by outer script `main.py`
* How to distribute obfuscated package to end user


```
    cd /path/to/pyarmor

    # Obfuscate all the python scripts in the package, obfuscated package saved in the path `dist/mypkg`
    # python pyarmor.py obfuscate --src "examples/testpkg/mypkg" --entry "__init__.py" --output "dist/mypkg"

    # Generate an expired license on 2019-01-01
    python pyarmor.py licenses --expired 2019-01-01 mypkg2018

    # Overwrite the default license
    cp licenses/mypkg2018/license.lic dist/mypkg

    # Import functions from obfuscated package
    cd dist
    cp ../examples/testpkg/main.py ./
    python main.py

    # Zip the whole path `mypkg`, distribute this archive
    zip -r mypkg-obf.zip mypkg
```

## Example 3: Build with project

Learn from this example

* How to use project to manage obfuscated scripts
* How to bind obfuscated scripts to harddisk, network card
* How to distribute obfuscated scripts to different platform
* How to generate license for each user

In this example, obfuscated script `queens.py` in the path `examples/simple`
will be distributed to three customers with different licenses:

* John, run on any Ubuntu 64, but expired on May 5, 2019
* Lily, run one Windows 10 (64-bit), the serial number of harddisk is `100304PBN2081SF3NJ5T`
* Tom,  run on Raspberry Pi, mac address of network card is `70:f1:a1:23:f0:94`, and expired on May 5, 2019

```
    cd /path/to/pyarmor

    # Create a project in the path `projects/simple`
    python pyarmor.py init --src=examples/simple --entry=queens.py projects/simple

    # Change to project path
    cd projects/simple

    # A shell script "pyarmor" is created here (In windows it is "pyarmor.bat")
    # Use command `build` to obfuscate all the `.py` in the project
    ./pyarmor build

    # Generate licenses for each customer
    #
    # For John, generate an expired license, new license in "licenses/john/license.lic"
    ./pyarmor licenses --expired 2019-03-05 john

    # For Lily, generate a license bind to harddisk, new license in "licenses/lily/license.lic"
    ./pyarmor licenses --bind-disk '100304PBN2081SF3NJ5T' lily

    # For Tom, generate an expired license bind to mac address, new license in "licenses/tom/license.lic"
    ./pyarmor licenses --bind-mac '70:f1:a1:23:f0:94' --expired 2019-03-05 tom

    # Create distribution package for John
    #
    mkdir -p customers/john

    # Copy obfuscated scripts
    cp -a dist/ customers/john

    # Replace default license
    cp licenses/john/license.lic customers/john/dist

    # Replace platform-dependent dynamic library `_pytransform`
    rm -f customer/john/dist/_pytransform.*
    wget http://pyarmor.dashingsoft.com/downloads/platforms/linux_x86_64/_pytransform.so -O customer/john/dist/_pytransform.so

    # Zip all files in the path `customer/john/dist`, distribute the archive to John

    # Do the same thing for Lily and Tom, except for platform-dependent dynamic library `_pytransform`
    #
    # For Lily
    wget http://pyarmor.dashingsoft.com/downloads/platforms/win_amd64/_pytransform.dll

    # For Tom
    wget http://pyarmor.dashingsoft.com/downloads/platforms/raspberrypi/_pytransform.so

```

## Example 4: Build for py2exe

Learn from this example

* How to change project settings with command `config`
* How to filter scripts, for example, exclude all the test scripts
* How to generate runtime files only
* How to obfuscated scripts only, without runtime files
* How to work with py2exe (It's same as Py2Installer, py2app, cx_Freeze)

In this example, py2exe and zip need to be installed. In the path
`examples/py2exe`, py2exe will convert entry script `hello.py` to `hello.exe`,
package all the other python scripts into the file `library.zip`. Pyarmor need
to obfuscate all the python scripts, update them into `library.zip`, copy
runtime files to output path of py2exe.

The main challenge here it's how py2exe can find the modules imported
by obfuscated scripts.

```bash
    cd /path/to/pyarmor

    # Create a project
    python pyarmor.py init --src=examples/py2exe --entry="hello.py" projects/py2exe

    # Enter project path
    cd projects/py2exe

    # Change project settings
    #
    # Set `--runtime-path` to empty string, otherwise obfuscated scripts can
    # not find dynamic library `_pytransform`
    #
    # Set `--disable-restrict-mode` to 1, otherewise obfuscated scripts maybe
    # complain `error return without exception set`
    #
    # Use `--mantifest` to exclude some scripts, about the format
    # Refer to https://docs.python.org/2/distutils/sourcedist.html#commands
    #
    # Note that entry script `hello.py` is excluded, why? see below
    #
    ./pyarmor config --runtime-path='' --disable-restrict-mode=1 \
                     --manifest "global-include *.py, exclude hello.py setup.py pytransform.py, prune dist, prunde build"

    # Obfuscate all the scripts in project, no runtime files generated
    ./pyarmor build --no-runtime

    # Move modified entry script to source path
    cp ../../examples/py2exe/hello.py hello.py.bak
    mv dist/hello.py ../../examples/py2exe

    # Copy extra required module to source path
    cp ../../pytransform.py ../../examples/py2exe

    # Here only entry script `hello.py` are modified, there are 2 lines
    # inserted at the beginning
    #
    #     from pytransform import pyarmor_runtime
    #     pyarmor_runtime
    #
    # So py2exe will package pytransform.py and all the files imported by
    # pytransform.py, for example, `ctypes`
    #
    # Once script is obfuscated, py2exe can not find the dependent moudle.
    # That's why entry script `hello.py` can not be obfuscated.
    #
    # Run py2exe from source path, generate `hello.exe`, `library.zip` in the `dist`
    ( cd ../../examples/py2exe; python setup.py py2exe )

    # Restore original entry script
    mv hello.py.bak ../../examples/py2exe/hello.py

    # Compile all obfuscated scripts to .pyc（Remove option -b before Python 3.2)
    python -m compileall -b dist

    # Update `library.zip`, replace original scripts with obfuscated scripts
    ( cd dist; zip -r ../../../examples/py2exe/dist/library.zip *.pyc )

    # Generate runtime files only, save in other path `runtimes`
    ./pyarmor build --only-runtime --output runtimes

    # Copy them to output path of py2exe
    cp runtimes/* ../../examples/py2exe/dist

    # Now run `hello.exe`
    cd ../../examples/py2exe/dist
    ./hello.exe
```
