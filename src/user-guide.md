# DEPRECATED from v5.0, see https://pyarmor.readthedocs.io/en/latest/ instead

# User Guide For PyArmor v4

This is the documentation for PyArmor 3.4 and later.

## Tab of Content

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
    - [Obfuscate Python Scripts](#obfuscate-python-scripts)
    - [Import Obfuscated Module](#import-obfuscated-module)
    - [Use Project to Manage Obfuscated Scripts](#use-project-to-manage-obfuscated-scripts)
        - [Change Default Project Configuration](#change-default-project-configuration)
    - [Distribute Obfuscated Scripts](#distribute-obfuscated-scripts)
        - [Pack Obfuscated Scripts into bundle](#pack-obfuscated-scripts-into-bundle)
    - [License of Obfuscated Scripts](#license-of-obfuscated-scripts)
    - [Cross Platform](#cross-platform)
    - [Use runtime path](#use-runtime-path)
    - [Keypoints of Using Obfuscated Scripts](#keypoints-of-using-obfuscated-scripts)
- [Benchmark Test](#benchmark-test)
- [Examples](examples/README.md)
- [Project Configure File](#project-configure-file)
- [Command Options](#command-options)
    - [obfuscate](#obfuscate)
    - [licenses](#licenses)
    - [pack](#pack)
    - [init](#init)
    - [config](#config)
    - [build](#build)
    - [info](#info)
    - [check](#check)
    - [hdinfo](#hdinfo)
    - [benchmark](#benchmark)
- [Appendix](#appendix)
    - [Limitions](#limitions)
    - [About license.lic](#about-licenselic)
    - [Restrict Mode](#restrict-mode)
    - [Use Decorator to Protect Code Object](#use-decorator-to-protect-code-object)
    - [Take Registration Code Effect](#take-registration-code-effect)
    - [Get Hardware Information](#get-hardware-information)
    - [Many Obfuscated Package Within Same Python Interpreter](#many-obfuscated-package-within-same-python-interpreter)

## Introduction

PyArmor is a command line tool used to obfuscate python scripts, bind obfuscated
scripts to fixed machine or expire obfuscated scripts. It protects Python
scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate co_code of each function (code object) in runtime.
* Clear f_locals of frame as soon as code object completed execution.
* Verify the license file of obfuscated scripts while running it.

Refer to [Protect Python Scripts By PyArmor](docs/protect-python-scripts-by-pyarmor.md)

## Installation

The simple way is pip

    pip install pyarmor

After that, there is a command will be avaiable in Python script path

    pyarmor -h

And there is a web ui for PyArmor:

    pyarmor-webui

It will start a light weight web server in localhost, and open a page in web
browser. Note that the `webui` doesn't include all the features of PyArmor, it's
only for basic usage, full features still need shell command way.

Or get source package from [pypi/pyarmor](https://pypi.python.org/pypi/pyarmor)

After you get source package, unpack it to any path, then run paramor.py as
common python script

    python pyarmor.py -h


## Usage

Shell commands will shown for Unix-based systems. Windows has analogous commands
for each.

### Obfuscate Python Scripts

Obfuscate a simple script `examples/simple/queens.py` in the source path of
PyArmor

    pyarmor obfuscate examples/simple/queens.py

Obfuscated scripts are saved in default output path `dist`, the content of
obfuscated script like this

``` python
    from pytransform import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...')
```

The first 2 lines are called `Bootstrap Code`, it's only inserted into the entry
script. For the other obfuscated scripts, there is only last line. The bootstrap
code must be called before to use any obfuscated scripts.

And there are some extra files in the `dist`

    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pytransform.py
    pytransform.key
    license.lic

All of them are required to run obfuscated scripts, called `runtime files`.

Run obfuscated script, or import it

    cat dist/
    python queens.py
    python -c 'import queens'

### Use Project to Manage Obfuscated Scripts

It's better to create a project to manage these obfuscated scripts,
there are the several advantages:

* Increment build, only updated scripts are obfuscated since last build
* Filter obfuscated scripts in the project, exclude some scripts
* More convenient to manage obfuscated scripts

Use command `init` to create a project,

    pyarmor init --src=examples/pybench --entry=pybench.py projects/pybench

The project path `projects/pybench` will be created, and ther are 3 files in it:

    .pyarmor_config
    .pyarmor_capsule.zip
    pyarmor.bat or pyarmor

The first file is a json format to save project configuration.

The second file called `Projct Capsule`, it includes important data used to
obfuscate scripts and generate the license file for obfuscated scripts in the
project.

The last file is shell script to call `pyarmor` quickly.

The common usage for project is to do any thing in the project path.

    cd projects/pybench

Show project information

    ./pyarmor info

Obfuscate all the scripts in this project

    ./pyarmor build

By default, all the `.py` files in the `src` path will be obfuscated, they're
saved in the path `dist`. However if there is a `__init__.py` in the `src` path,
the output path will be `dist/pkgname`.

Run obfuscated script,

    cd dist
    python pybench.py

After some source scripts changed, just run `build` again

    cd projects/pybench
    ./pyarmor build

#### Change Default Project Configuration

Change project information by command `config`

    ./pyarmor config --title="My Package"
    ./pyarmor config --help

Use option `--manifest` to filter obfuscated scripts. For example, exclude
`__init__.py` and folder `test` from project

    ./pyarmor config --manifest="global-include *.py, exclude __init__.py, prune test"

Obfuscate scripts by other modes, for example, only obfuscate whole module, not
each code object

    ./pyarmor config --obf-module-mode=des --obf-code-mode=none

Force rebuild all

    ./pyarmor build --force

About project configuration information, refer to [Project Configure File](#project-configure-file)

### License of Obfuscated Scripts

There is a file `license.lic` in the output path `dist`, it's generated while
obfuscating scripts, it allows obfuscated scripts run in any machine and never
expired.

Command `licenses` used to generate new license, it will get a RSA private key
from `Project Capsule` to generate license file. In the installed path of
PyArmor, there is a global `Project Capsule`, which used by command
`obfuscate`. But for projects, they have their local capsule.

The license file generated by one project doesn't work in another project. In a
word, run `licenses` in one project path, the licenses generated only for this
project. In any path not a project, the generated licenses are used for command
`obfuscate`

Note that this is not applied to trial version PyArmor. The license generated by
trial PyArmor can be used in any project.

Generate expired license with global `Project Capsule`

    cd /path/to/anywhere-not-project-path
    pyarmor licenses --expired 2018-12-31 pro-01
    cp licenses/pro-01/license.lic dist/

Generate batch licenses for a project

    cd projects/pybench
    ./pyarmor licenses RCode-1 RCode-2 RCode-3 RCode-4 RCode-5
    ls licenses/

Bind obfuscated scripts to fixed machine, first get hardware information

    pyarmor hdinfo

Then generate license bind to harddisk serial number and mac address

    pyarmor licenses --bind-disk '100304PBN2081SF3NJ5T'
                     --bind-mac '20:c1:d2:2f:a0:96'
                     Customer-John


### Distribute Obfuscated Scripts

It's simple to distribute obfuscated scripts, just copy all the files
in output path `dist` to target machine

**Note** Python version in build machine must be same as in target
machine. To be exact, the magic string value used to recognize
byte-compiled code files (.pyc files) must be same.

#### Pack Obfuscated Scripts Into Bundle

From v4.4, introduces a command `pack` to pack obfuscated scripts with
`PyInstaller`, `py2exe`, `py2app`, `cx_Freeze` etc.

The prefer way is `PyInstaller`, first install `PyInstaller`

    pip install pyinstaller

Then run command `pack` to pack obfuscated scripts

    pyarmor pack examples/py2exe/hello.py

Run the final executeable file

    dist/hello/hello

Check they're obfuscated

    rm dist/hello/license.lic
    dist/hello/hello

For the other tools, before run command `pack`, the setup script must
be written. For py2exe, here is an example script
`examples/py2exe/setup.py`. It will pack the entry script `hello.py`
and `queens.py`. To be sure it works

    cd examples/py2exe
    python setup.py py2exe

Then run command `pack` to pack obfuscated scripts

     pyarmor pack --type py2exe py2exe/hello.py

Run the final executeable file

    cd py2exe/dist
    ./hello

Check they're obfuscated

    rm license.lic
    ./hello

For cx_Freeze, py2app, it's almost same as py2exe. Learn more options
about command [pack](#pack)

What does command `pack` do? Refer to [pack-obfuscated-scripts.rst](../docs/pack-obfuscated-scripts.rst)

Quick start from the following template scripts

* [pack-obfuscated-scripts.bat](examples/pack-obfuscated-scripts.bat) for Windows
* [pack-obfuscated-scripts.sh](examples/pack-obfuscated-scripts.sh) for most of others

### Cross Platform

The only difference for cross platform is need to replace
platform-dependent library `_pytransform` with the right one for
target machine

All the latest prebuilt platform-dependent library `_pytransform`
list [here](http://pyarmor.dashingsoft.com/downloads/platforms)

It's written by C, the only dependency is libc. So it's not difficult
to build for any other platform, even for embeded system. Contact
<jondy.zhao@gmail.com> if you'd like to run encrypted scripts in other
platform.

### Use runtime path

There are several extra files should be distributed with obfuscated
scripts. They're called **runtime files**

```
    pytransform.py, _pytransform.so or _pytransform.dll or _pytransform.dylib
    pytransform.key, license.lic
```

Generally all of the **runtime files** will be generated in the output
path when obfuscate python scripts.

By default all the **runtime files** locate in the top path of
obfuscated scripts. Use runtime path to specify where to find
**runtime files** if they're not in default path.

```bash
    cd projects/myproject

    # Note that runtime path is a directory in target machine, it maybe
    # doesn't exists in build machine
    ./pyarmor config --runtime-path=/path/to/runtime-files

    ./pyarmor build --only-runtime --output runtimes

    # All the runtime files will be generated in path "runtimes"
    ls ./runtimes

    # Copy all the runtimes to runtime path in target machine
    cp ./runtimes/* /path/to/runtime-files
```

### Keypoints of Using Obfuscated Scripts

* Obfuscated script is a normal python script, so it can be seamless
  to replace original script.

* There is only one thing changed, the following code must be run
  before using any obfuscated script.

```python
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
```

* In restrict mode, it must be in the entry scripts. If restrict mode
  is disabled, it can be put in any script anywhere, only if it run in
  the same Python interpreter. It will create some builtin function to
  deal with obfuscated code.

* The extra runtime file `pytransform.py` must be in any Python path
  in target machine.

* `pytransform.py` need load dynamic library `_pytransform`. It may be

    * `_pytransform.so` in Linux
    * `_pytransform.dll` in Windows
    * `_pytransform.dylib` in MacOS

  It's dependent-platform, download the right one to the same path of
  `pytransform.py` according to target platform. All the prebuilt
  dynamic libraries
  list [here](http://pyarmor.dashingsoft.com/downloads/platforms/)

* By default `pytransform.py` search dynamic library `_pytransform` in
  the same path. Check `pytransform.py!_load_library` to find the
  details.

* All the other **runtime files** should in the same path as dynamic
  library `_pytransform`.

* If runtime files locate in some other path, change bootstrap code:

```python
    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/runtime-files')
```

## Benchmark Test

How about the performance after scripts are obfuscated, run
`benchmark` in target machine

```bash
    python pyarmor.py benchmark
```

## Project Configure File

Each project has a configure file. It's a json file named
`.pyarmor_config` stored in the project path, used to specify
scripts to be obfuscated, and how to obfuscate etc.

* [name](#name)
* [title](#title)
* [src](#src)
* [manifest](#manifest)
* [is_package](#is_package)
* [disable_restrict_mode](#disable_restrict_mode)
* [entry](#entry)
* [output](#output)
* [capsule](#capsule)
* [obf_module_mode](#obf_module_mode)
* [obf_code_mode](#obf_code_mode)
* [runtime_path](#runtime_path)

### name

Project name.

### title

Project title.

### src

Base path to match files by manifest template string.

Generally it's absolute path.

### manifest

A string specifies files to be obfuscated, same as MANIFEST.in of
Python Distutils, default value is

```
    global-include *.py
```

It means all files anywhere in the `src` tree matching.

Multi manifest template commands are spearated by comma, for example

```
    global-include *.py, exclude __mainfest__.py, prune test
```

Refer to https://docs.python.org/2/distutils/sourcedist.html#commands

### is_package

Available values: 0, 1, None

When it's set to 1, the basename of `src` will be appended to `output`
as the final path to save obfuscated scripts, and runtime files are
still in the path `output`

When init a project and no `--type` specified, it will be set to 1 if
there is `__init__.py` in the path `src`, otherwise it's None.

### disable_restrict_mode

Available values: 0, 1, None

When it's None or 0, obfuscated scripts can not be imported from outer
scripts. Generally it's apply to a standalone application.

When protected python files are module or package, it means obfuscated
scripts is allowed to be imported by outer scripts, it must be set to
1.

By default it's set to 1.

### entry

A string includes one or many entry scripts.

When build project, insert the following bootstrap code for each
entry:

```python
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
```

The entry name is relative to `src`, or filename with absolute path.

Multi entries are separated by comma, for example,

```
    main.py, another/main.py, /usr/local/myapp/main.py
```

Note that entry may be NOT obfuscated, if `manifest` does not
specify this entry. In this case, bootstrap code will be inserted into
the header of entry script either. So that it can import other
obfuscated modules.

### output

A path used to save output of build. It's relative to project path.

### capsule

Filename of project capsule. It's relative to project path if it's not
absolute path.

### obf_module_mode

How to obfuscate whole code object of module:

* none

    No obfuscate

* des

    Obfuscate whole code object by DES algorithm

The default value is `des`

### obf_code_mode

How to obfuscate byte code of each code object:

* none

    No obfuscate

* des

    Obfuscate byte-code by DES algorithm

* fast

    Obfuscate byte-code by a simple algorithm, it's faster than DES

* wrap

    The wrap code is different from `des` and `fast`. In this mode,
    when code object start to execute, byte-code is restored. As soon
    as code object completed execution, byte-code will be obfuscated
    again.

    Refer to [Mechanism Without Restrict Mode](mechanism.md#mechanism-without-restrict-mode)

The default value is `wrap` when `disable_restrict_mode` is set to 1,
it's `des` in any other case

### runtime_path

None or any path.

When run obfuscated scripts, where to find dynamic library
"_pytransform". The default value is None, it means it's in the same
path of "pytransform.py".

It's useful when obfuscated scripts are packed into a zip file, for
example, use py2exe to package obfuscated scripts. Set runtime_path to
an empty string, and copy runtime files, `_pytransform.dll`,
`pytransform.key`, `license.lic` to same path of zip file, will solve
this problem.

## Command Options

Available commands

- [obfuscate](#obfuscate)
- [licenses](#licenses)
- [pack](#pack)
- Project Commands
    - [init](#init)
    - [config](#config)
    - [build](#build)
    - [info](#info)
    - [check](#check)
- [hdinfo](#hdinfo)
- [benchmark](#benchmark)

See online document

```
    pyarmor <command> --help
```

### benchmark

```
Usage: pyarmor benchmark [-h] [-m {none,des}] [-c {none,des,fast,wrap}]

optional arguments:
  -h, --help            show this help message and exit
  -m {none,des}, --obf-module-mode {none,des}
  -c {none,des,fast,wrap}, --obf-code-mode {none,des,fast,wrap}

```

Run benchmark test in current machine. This command used to test the performaces
of obfuscated scripts in different obfuscate mode. For examples


```
    # This is the default mode for package
    pyarmor benchmark --obf-module-mode=des --obf-code-mode=wrap

    # This is the default mode for standalone application
    pyarmor benchmark --obf-module-mode=des --obf-code-mode=des

```

### build

```
Usage: pyarmor build [-h] [-B] [-r] [-n] [-O OUTPUT] [PATH]

positional arguments:
  PATH                  Project path

optional arguments:
  -h, --help            show this help message and exit
  -B, --force           Obfuscate all scripts even if they're not updated
  -r, --only-runtime    Generate extra runtime files only
  -n, --no-runtime      DO NOT generate extra runtime files
  -O OUTPUT, --output OUTPUT
                        Output path, override project configuration

```

After the project has been created, use `build` to obfuscate all scripts in the
project.

```
    # Obfuscate all scripts specified by the project `projects/myproject`
    pyarmor build projects/myproject

    # Or build in the project path
    cd projects/myproject
    ./pyarmor build

    # Note that there is no scripts will be obfuscated by last build command,
    # because only updated scripts are obfuscated since last build
    #
    # To obfuscate all scripts even if they're not updated
    #
    ./pyarmor build --force

    # Do not generate runtime files, only obfuscate scripts
    ./pyarmor build -B --no-runtime

    # Generate runtime files only
    ./pyarmor build --only-runtime

    # Save obfuscated scripts in `/opt/pyarmor/dist` other than `dist`
    ./pyarmor build -B -n --output /opt/pyarmor/dist
```

### check

```
usage: pyarmor.py check [-h] [PATH]

positional arguments:
  PATH        Project path

optional arguments:
  -h, --help  show this help message and exit

```

Check consistency of project

```
    pyarmor check projects/myproject
    cd projects/myproject
    ./pyarmor check

```

### config

```
usage: pyarmor config [-h] [--name NAME] [--title TITLE] [--src SRC]
                      [--output OUTPUT] [--capsule CAPSULE]
                      [--manifest TEMPLATE] [--entry SCRIPT]
                      [--is-package {0,1}] [--disable-restrict-mode {0,1}]
                      [--obf-module-mode {none,des}]
                      [--obf-code-mode {none,des,fast,wrap}]
                      [--runtime-path RPATH]
                      [PATH]

positional arguments:
  PATH                  Project path

optional arguments:
  -h, --help            show this help message and exit
  --name NAME
  --title TITLE
  --src SRC
  --output OUTPUT
  --capsule CAPSULE     Project capsule
  --manifest TEMPLATE   Manifest template string
  --entry SCRIPT        Entry script of this project
  --is-package {0,1}
  --disable-restrict-mode {0,1}
  --obf-module-mode {none,des}
  --obf-code-mode {none,des,fast,wrap}
  --runtime-path RPATH

```

After the project has been created, use `config` to update project settings.

```
    pyarmor config --name=mypkg projects/myproject

    cd projects/myproject
    ./pyarmor config  --title="My Package"

```

option `--entry`, `--manifest` are relative to `--src` path

```
    ./pyarmor config --src=/opt/pyarmor/examples/simple --entry=queens.py
    ./pyarmor config --entry="main.py, /home/jondy/test/main.py"

    # All the *.py files in src path
    ./pyarmor config --manifest="global-include *.py"

    # All the *.py files in src path, no any test_*.py no any file in path `test`
    ./pyarmor config --manifest="global-include *.py, global-exclude test_*.py, prune test"

    # All the *.py files in src path except __init__.py
    # All the *.py files in the path `packages` except `__manifest__.py`
    ./pyarmor config --manifest="include *.py, exclude __init__.py, recursive-include packages/ *.py, recursive-exclude packages/ __manifest__.py"

```

option `--output`, `--capsule` are relative to project path

```
    ./pyarmor config --output=dist2
    ./pyarmor config --output=/opt/pyarmor/dist

    # Change project capsule
    ./pyarmor config --capsule=/opt/pyarmor/common/.pyarmor_capsule.zip
```

See [Project Configure File](project-configure-file) for details.

### hdinfo

```
Usage: pyarmor hdinfo [-h]

optional arguments:
  -h, --help  show this help message and exit
```

Run this command in target machine to get hardware information which could be
used to generate `license.lic` by command `licenses` to bind obfuscated scripts
to target machine.

```
    pyarmor hdinfo

```

### info

```
usage: pyarmor info [-h] [PATH]

positional arguments:
  PATH        Project path

optional arguments:
  -h, --help  show this help message and exit

```

Show project information

```
    pyarmor info projects/myproject

    cd projects/myproject
    ./pyarmor info

```

### init

```
usage: pyarmor init [-h] [-t {auto,app,pkg}] [-e ENTRY] -s SRC
                    [--capsule CAPSULE] [project]

positional arguments:
  project               Project path

optional arguments:
  -h, --help            show this help message and exit
  -t {auto,app,pkg}, --type {auto,app,pkg}
  -e ENTRY, --entry ENTRY
                        Entry script of this project
  -s SRC, --src SRC     Base path of python scripts
  --capsule CAPSULE     Use this capsule other than creating new one

```

This command creates an empty project in the specified path - basically a
configure file .pyarmor_config, a project capsule .pyarmor_capsule.zip, and a
shell script "pyarmor" will be created (in windows, it called "pyarmor.bat").

Option --type specifies project type: app or package. If it's pakcage type, the
obfuscated scripts will be saved in the sub-directory `package-name` of output
path. `auto` means project type will be set to package if there is `__init__.py`
in the project src path, otherwise `app`.

Option --src specifies where to find python source files. By default, all .py
files in this directory will be included in this project.

Option --entry specifies main script, which could be run directly after
obfuscated. Note that entry script maybe isn't obfuscated.

Option --capsule specifies project capsule file which has been created. If it is
set, no new project capsule is generated, just link to this capsule.

```
    # Create app project
    pyarmor init --src=example/simple --entry=queens.py projects/simple
    pyarmor init --type=app --src=example/testpkg --entry=queens.py projects/mypkg

    # Create package project
    pyarmor init --src=example/testpkg --entry=queens.py projects/mypkg
    pyarmor init --type=pkg --src=example/testpkg --entry=queens.py projects/mypkg


    # Use same capsule with other project, so that obfuscated scripts can be
    # run in the same process of Python Interpreter.
    pyarmor init --src=odoo/login --entry=__init__.py projects/login
    pyarmor init --src=odoo/weblogin --entry=__init__.py \
                 --capsule=projects/login/.pyarmor_capsule.zip \
                 projects/weblogin
```

### licenses

```
usage: pyarmor licenses [-h] [-e YYYY-MM-DD] [-d SN] [-4 a.b.c.d]
                        [-m x:x:x:x] [--bind-domain DOMAIN] [-P PROJECT]
                        [-C CAPSULE] [-O OUTPUT] [--restrict]
                        CODE [CODE ...]

positional arguments:
  CODE                  Registration code for this license

optional arguments:
  -h, --help            show this help message and exit
  -P PROJECT, --project PROJECT
                        Project path
  -C CAPSULE, --capsule CAPSULE
                        Project capsule
  -O OUTPUT, --output OUTPUT
                        Output path
  --restrict
                        Generate license for restrict mode

Bind license to hardware:
  -e YYYY-MM-DD, --expired YYYY-MM-DD
                        Expired date for this license
  -d SN, --bind-disk SN
                        Bind license to serial number of harddisk
  -4 a.b.c.d, --bind-ipv4 a.b.c.d
                        Bind license to ipv4 addr
  -m x:x:x:x, --bind-mac x:x:x:x
                        Bind license to mac addr
  --bind-domain DOMAIN  Bind license to domain name

```

Generate licenses for obfuscated scripts.

In order to generate license, project capsule must be specified. First get
capsule from option `--capsule`, if it's None. Then get the capsule from project
specified by option `--project`. If no project is specified, use the default
capsule `.pyarmor_capsule.zip` in the current path.

If option `--output` is specified, all the generated licenses will be saved to
`OUTPUT/licenses`. Otherwise `PROJECT/licenses` if `--project` is specifed. If
both of them are None, the default output path is `./licenses`

In order to bind licenses to fixed machine, use command hdinfo to get all
available hardware information:

    pyarmor hdinfo

Then generate licenses

```
    # Expired license
    pyarmor licenses --expired=2018-05-12 Customer-Jordan
    pyarmor licenses --capsule=project2.zip \
        --output=/home/jondy/project2 \
        --expired=2018-05-12 Customer-Jordan

    # Expired license for project
    pyarmor licenses --project=projects/myproject \
        --expired=2018-05-12 Customer-Jordan

    # Bind license to fixed harddisk and expired someday
    cd projects/myproject
    ./pyarmor licenses -e 2018-05-12 \
        --bind-disk '100304PBN2081SF3NJ5T' Customer-Tom

    # Batch expired licenses for many customers
    cd projects/myproject
    ./pyarmor licenses -e 2018-05-12 Customer-A Customer-B Customer-C

```

### obfuscate

```
usage: pyarmor obfuscate [-h] [-O PATH] [-e SCRIPT] [-s SRC]
                         [-r] [--capsule CAPSULE]
                         [patterns [patterns ...]]

positional arguments:
  patterns              File patterns, default is "*.py"

optional arguments:
  -h, --help            show this help message and exit
  -O PATH, --output PATH
  -e SCRIPT, --entry SCRIPT
                        Entry script
  -s SRC, --src SRC     Base path for matching python scripts
  -r, --recursive       Obfuscate files recursively
  --capsule CAPSULE     Use this capsule to obfuscate code

```

Obfuscate scripts without project.

```
    # Obfuscate the script, save obfuscated scripts to `dist`
    pyarmor examples/test/main.py

    # Use /opt/pyarmor/.pyarmor_capsule.zip, other than make new one in the src path
    pyarmor --capsule=/opt/pyarmor/.pyarmor_capsule.zip examples/test/main.py

    # Obfuscate all the "*.py" files in the path "examples/simple" recursively
    pyarmor --recursive -examples/simple/queens.py
```

### pack

```
usage: pyarmor.py pack [-h] [-v] [-t TYPE] [-s SETUP] [-O OUTPUT] SCRIPT

positional arguments:
  SCRIPT                Entry script

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -t TYPE, --type TYPE  py2app, cx_Freeze, py2exe
  -s SETUP, --setup SETUP
                        Setup script, default is setup.py

  -O OUTPUT, --output OUTPUT
                        Directory to put final built distributions in (default
                        is output path of setup script)

```

Pack obfuscated scripts with PyInstaller, py2exe/py2app or cx_Freeze, the prefer
way is PyInstaller,

    pip install pyinstaller
    pyarmor pack examples/simple/hello.py

This will make a bundle with obfuscated scripts in the path `dist/hello/`.

For other tools, a setup script must be exists before to run `pack`. For
examples

    pyarmor pack --type py2exe /path/to/src/hello.py
    pyarmor pack --type cx_Freeze /path/to/src/hello.py

PyArmor will run setup script `/path/to/src/setup.py`, the final output path is
same as of the setup script. PyArmor just updates some files, replace all the
original python scripts with obfuscated ones, and copy runtime files required by
obfuscated scripts there.

In case `setup.py` in the different path

    pyarmor pack -t cx_Freeze --setup /path/to/project/setup.py
                              /path/to/project/src/main.py

## Appendix

### Limitions

* Run pyarmor.py with non-debug Python interpreter. If Python
  interpreter is compiled with Py_TRACE_REFS or Py_DEBUG, pyarmor will
  crash.

* The callback function set by `sys.settrace`, `sys.setprofile`,
  `threading.settrace` and `threading.setprofile` will be ignored when
  running obfuscated scripts.

### Attribute `__file__`

The `__file__` of code object will be `<frozen name>` other than real
filename. But `__file__` of moudle is still filename. For example,
obfuscate the following script `foo.py`

```
def hello(msg):
    print(msg)
```

Then import this obfuscated script:

```
import foo

# The output will be 'foo.py'
print(foo.__file__)

# The output will be '<frozen foo>'
print(foo.hello.__file__)
```

### About license.lic

In pyarmor, there are 2 types of `license.lic`

* `license.lic` of PyArmor, which locates in the source path of
  pyarmor. It's required to run PyArmor.

* `license.lic` of Obfuscated Scripts, which is generated when
  obfuscating scripts or generating new licenses. It's required to run
  obfuscated scripts.

Each project has its own capsule `.pyarmor_capsule.zip` in project
path. This capsule is generated when run command `pyarmor init` to
create a project. And `license.lic` of PyArmor will be as an input
file to make this capsule.

When runing command `pyarmor build` or `pyarmor licenses`, it will
generate a `license.lic` in project output path for obfuscated
scripts. Here the project capsule `.pyarmor_capsule.zip` will be as
input file to generate this `license.lic` of Obfuscated Scripts.

So the relation between 2 `license.lic` is

```
    `license.lic` of PyArmor --> `.pyarmor_capsule.zip` --> `license.lic` of Obfuscated Scripts
```

After purchase a registration code of PyArmor, replace the content
`license.lic` of PyArmor with it. So the `.pyarmor_capsule.zip`
generated by this `license.lic` will be different from which generated
by the trial version of PyArmor.

### Restrict Mode

Restrict mode is instroduced from PyArmor v3.6.

In restrict mode, obfuscated scripts must be one of the following formats:

```python
    __pyarmor__(__name__, __file__, b'...')

Or

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')

Or

    from pytransform import pyarmor_runtime
    pyarmor_runtime('...')
    __pyarmor__(__name__, __file__, b'...')

```

And obfuscated script must be imported from obfuscated script. No any
other statement can be inserted into obfuscated scripts. For examples,

```bash
    $ cat a.py
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')

    $ python a.py

```
It works.

```bash
    $ cat b.py
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')
    print(__name__)

    $ python b.py

```
It doesn't work, because there is an extra code "print"

```bash
    $ cat c.py
    __pyarmor__(__name__, __file__, b'...')

    $ cat main.py
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    import c

    $ python main.py

```

It doesn't work, because obfuscated script "c.py" can NOT be imported
from no obfuscated scripts in restrict mode


```bash
    $ cat d.py
    import c
    c.hello()

    # Then obfuscate d.py
    $ cat d.py
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')


    $ python d.py

```
It works.

So restrict mode can avoid obfuscated scripts observed from no obfuscated code.

Sometimes restrict mode is not suitable, for example, a package used
by other scripts. Other clear scripts can not import obfuscated
package in restrict mode. So it need to disable restrict mode, and set
`obf-code-mode` to `wrap`

```bash
    # Create project at first
    pyarmor init --src=examples/py2exe --entry=hello.py projects/testmod

    # Disable restrict mode by command "config"
    # Use 'wrap' mode to obfuscate code objects
    # And only obfuscate queens.py

    cd projects/testmod
    ./pyarmor config --manifest="include queens.py" --disable-restrict-mode=1 \
                     --obf-code-mode=wrap projects/testmod

    # Obfuscate queens.py
    ./pyarmor build

    # Import obfuscated queens.py from no obfuscated script hello.py
    cd dist
    python hello.py

```

The mode `wrap` is introduced from v3.9.0, it will obfuscate code
object again as soon as this code object returns.

Refer to [Mechanism Without Restrict Mode](mechanism.md#mechanism-without-restrict-mode)

Enable restrict mode again

```
    pyarmor config --disable-restrict-mode=0 --obf-code-mode=des projects/testmod
```

### Use Decorator to Protect Code Object

When restrict mode is disabled, there is another way to proetect code
object not to be accessed from outer clear scripts.

First define decorator `wraparmor`

```python

# For Python 2
from __builtin__ import __wraparmor__

# For Python 3
from builtins import __wraparmor__

def wraparmor(func):
    def wrapper(*args, **kwargs):
         __wraparmor__(func)
         tb = None
         try:
             return func(*args, **kwargs)
         except Exception as err:
             tb = sys.exc_info()[2]
             raise err
         finally:
             __wraparmor__(func, tb, 1)
    wrapper.__module__ = func.__module__
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__.update(func.__dict__)
    return wrapper

```

PyCFunction `__wraparmor__` will be added into builtins module when
call **pyarmor_runtime**. It can be used in the decorator `wraparmor`
only. The due is to restore func_code before function call, and
obfuscate func_code after function return.

Then add this decorator to any function which intend to be protect,
for example,

``` python

@wraparmor
def main():
    pass

class Queens:

    @wraparmor
    def __init__(self):
        pass

    @staticmethod
    @wraparmor
    def check(cls):
        pass

```

Note that source code of decorator "wraparmor" should be in any of
obfuscated scripts.

#### Protect module with decorator "wraparmor"

Here is an example `examples/testmod`, entry script is `hello.py`,
and it's not obfuscated. It will import obfuscated module `queens`,
and try to disassemble some functions in this module. In order to
protect those code object, add extra decorator at the begin:


``` python
    try:
        from builtins import __wraparmor__
    except Exception:
        from __builtin__ import __wraparmor__
    def wraparmor(func):
        def wrapper(*args, **kwargs):
             __wraparmor__(func)
             tb = None
             try:
                 return func(*args, **kwargs)
             except Exception:
                 tb = sys.exc_info()[2]
                 raise
             finally:
                 __wraparmor__(func, tb, 1)
        wrapper.__module__ = func.__module__
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__.update(func.__dict__)
        # Only for test
        wrapper.orig_func = func
        return wrapper
```

And decorate all of functions and methods. Refer to
`examples/testmod/queens.py`

``` bash
    # Create project
    pyarmor init --src=examples/testmod --entry=hello.py projects/testmod

    # Change to this project
    cd projects/testmod

    # Configure this project
    ./pyarmor config --manifest="include queens.py" --disable-restrict-mode=1

    # Obfuscate queens.py
    ./pyarmor build

    # Import obfuscated queens.py from hello.py
    cd dist
    python hello.py

```

### Take Registration Code Effect

In the trial version of PyArmor, the key used to obfuscated scripts is
fixed. In the normal version of PyArmor, the key used to obfuscated
scripts is random. And different project has different key. After got
a registration code, generally it will be sent to you by email like
this:

```
Regcode:
XABCILAKSDKALSDKFAJFLAJFLAJFDJASDFJAJFASKDJFAJasdkfkASSDASFAFAkaisiidoa
siSILKaISO28SLFaWIwlifskalsfKKIS5
```

In order to apply registration code, open the file `license.lic` in
the pyarmor installed path by any text editor, replace the content
with the regcode only (one line, no any newline), then save it.

Because the project capsule has been generated by trial pyarmor, so it
need to be removed, and generate new one by non-trial pyarmor.

### Get Hardware Information

Run the following command in customer machine

```
    # Download a tool 'hdinfo'

    # For John
    wget http://pyarmor.dashingsoft.com/downloads/platforms/linux_x86_64/hdinfo

    # For Lily
    wget http://pyarmor.dashingsoft.com/downloads/platforms/win_amd64/hdinfo.exe

    # All the other support platforms
    #
    #     http://pyarmor.dashingsoft.com/downloads/platforms/macosx_intel/hdinfo
    #     http://pyarmor.dashingsoft.com/downloads/platforms/win32/hdinfo.exe
    #     http://pyarmor.dashingsoft.com/downloads/platforms/linux_i386/hdinfo

    # For Tom, the platform is not supported, use the other way described below

    # Run hdinfo, it will print hardware information.
    ./hdinfo

    Serial number of first harddisk: '100304PBN2081SF3NJ5T'

    Mac address: '70:f1:a1:23:f0:94'

    Ip address: '192.168.121.101'

    Domain name: ''

```

The other way is to install a fresh pyarmor from github or pypi, then run command:

```
    pyarmor hdinfo
```
The output is same as `hdinfo`. Note that a fresh pyarmor is enough to
get hardward information. DO NOT copy the pyarmor in build machine to
customer machine directly, especially `license.lic` has been replaced
with registration code of pyarmor.

### Many Obfuscated Package Within Same Python Interpreter

Suppose there are 3 odoo modules `web-login1`, `web-login2`,
`web-login3`, they'll be obfuscated separately, but run in the same
python interpreter.

Because these packages will run in same Python interpreter, so they must
use same project capsule.

```bash
    # Create project for "login1"
    pyarmor init --type=pkg --src=/path/to/web-login1 \
                           --entry=__init__.py \
                           projects/odoo/login1

    # Create project for others
    #
    # Other than create new capsule for project, just clone the capsule
    # specified by option `--capsule`
    #
    pyarmor init --type=pkg --src=/path/to/web-login2 \
                 --entry=__init__.py \
                 --capsule=projects/odoo/login1/.pyarmor_capsule.zip \
                 projects/odoo/login2
    pyarmor init --type=pkg --src=/path/to/web-login3 \
                 --entry=__init__.py \
                 --capsule=projects/odoo/login1/.pyarmor_capsule.zip \
                 projects/odoo/login3

    # Configure project, exclude `__mainfest__.py`
    ( cd projects/odoo/login1; ./pyarmor config --manifest "global-include *.py, exclude __manifest__.py" )
    ( cd projects/odoo/login2; ./pyarmor config --manifest "global-include *.py, exclude __manifest__.py" )
    ( cd projects/odoo/login3; ./pyarmor config --manifest "global-include *.py, exclude __manifest__.py" )

```

Then build all projects

```bash
    # Only obfuscate scripts, no runtime files
    (cd projects/odoo/login1; ./pyarmor build --no-runtime)
    (cd projects/odoo/login2; ./pyarmor build --no-runtime)
    (cd projects/odoo/login3; ./pyarmor build --no-runtime)
```

Distribute obfuscated modules

```
    cp -a projects/odoo/login1/dist/web-login1 /path/to/odoo/addons
    cp /path/to/web-login1/__manifest__.py /path/to/odoo/addons/web-login1

    cp -a projects/odoo/login2/dist/web-login2 /path/to/odoo/addons
    cp /path/to/web-login2/__manifest__.py /path/to/odoo/addons/web-login2

    cp -a projects/odoo/login3/dist/web-login3 /path/to/odoo/addons
    cp /path/to/web-login3/__manifest__.py /path/to/odoo/addons/web-login3

```

Add bootstrap code to launch script of odoo server, so that it knows
how to import obfuscated module. Suppose launch script is
`/path/to/odoo-server/python/launch.py`

```
    # Only generate runtime files to `projects/odoo/runtimes`
    (cd projects/odoo/login1; ./pyarmor build --only-runtime --output ../runtimes)

    # Because project capsules are same, it's same with proect login2 or login3 to
    # generate runtime files

    # Copy all runtime files to odoo server
    cp projects/odoo/runtimes/* /path/to/odoo-server/python

    # Edit `launch.py`, insert two lines
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
```

Now restart odoo server.
