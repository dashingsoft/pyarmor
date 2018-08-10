# User Guide For Pyarmor v4

This is the documentation for Pyarmor 3.4 and later.

## Introduction

Pyarmor v3.4 introduces a group new commands. For a simple package,
use command **obfuscate** to obfuscate scripts directly. For
complicated package, use Project to manage obfuscated scripts.

Project includes 2 files, one configure file and one project
capsule. Use manifest template string, same as MANIFEST.in of Python
Distutils, to specify the files to be obfuscated.

To create a project, use command **init**, use command **info** to
show project information. **config** to update project settings, and
**build** to obfuscate the scripts in the project.

Other commands, **benchmark** to metric performance, **hdinfo** to
show hardware information, so that command **licenses** can generate
license bind to fixed machine.

All the old commands **capsule**, **encrypt**, **license** are
deprecated, and will be removed from v4.

## Usage

Shell commands will shown for Unix-based systems. Windows has
analogous commands for each.

### Obfuscate Python Scripts

Obfuscate a simple script **examples/simple/queens.py** in the source
path of Pyarmor

```bash
    python pyarmor.py obfuscate --src=examples/simple --entry=queens.py "*.py"

    # Note that quotation mark is required for file patterns, otherwise
    # it will be expanded base on current path by shell.

    # Obfuscated scripts are saved in default output path "dist"
    #
    # There are some extra files in the "dist":
    #
    #    pytransform.py
    #    _pytransform.*
    #    *.key
    #    *.lic
    #
    # All of them are required to run obfuscated scripts, called "runtime files"
    #
    cd dist
    ls
    cat queens.py

    # Run obfuscated script
    python queens.py
```

### Import Obfuscated Module

Import obfuscated moduels from a clear python script

```bash
    python pyarmor.py obfuscate --src=examples/py2exe --entry=hello.py \
                                --no-restrict queens.py

    # Option --no-restrict is required, otherwise clear script can not
    # import obfuscated module
    #
    # queens.py is obfuscated. Entry hello.py is clear script. Two extra
    # lines are inserted at the begin of "hello.py"
    #
    #    from pytransform import pyarmor_runtime
    #    pyarmor_runtime()
    #
    # They're called "bootstrap code"
    #
    cd dist
    cat hello.py
    cat queens.py

    # Run hello.py
    python hello.py
```

### Use Project to Manage Obfuscated Scripts

It's better to create a project to manage these obfuscated scripts,
there are the several advantages:

* Increment build, only updated scripts are obfuscated since last build
* Obfuscate scripts by more modes
* Filter obfuscated scripts in the src path of project
* Expired obfuscated scripts or bind to fixed machine
* More convenient to manage obfuscated scripts

There are 2 project types:

* Application, or called Standalone Package
* Package used by other clear scripts

For application, all the obfuscated python scripts only used by
package self. Pyarmor uses a simple and efficient way to protect
Python scripts.

For package used by other clear scripts, things get a little
complicated. Pyarmor uses a different way to protect Python scripts.

About the details, refer to [How to obfuscate python scripts](mechanism.md)

#### Standalone Package

This example show how to obfuscate a standalone python package
**pybench**, which locates in the **examples/pybench** in the source
of pyarmor.

```bash
    mkdir projects

    # Use command 'init' to create a project configured as application.
    #
    # It will create two files in the project path "projects/pybench":
    #
    #   .pyarmor_config
    #   .pyarmor_capsule.zip
    #
    # Option --type=app specify the project is standalone package
    #
    python pyarmor.py init --type=app --src=examples/pybench \
                           --entry=pybench.py projects/pybench


    cd projects/pybench

    # And there is a shell script "pyarmor" is created at the same time.
    # (In windows, the name is "pyarmor.bat")

    # Show project information
    ./pyarmor info

    # Now run command "build" to obfuscated all the scripts in the src
    #
    ./pyarmor build

    # Check obfuscated script
    cd dist
    cat pybench.py

    # Run obfuscated script
    python pybench.py

```

After some source scripts changed, just run **build** again

```bash
    cd projects/pybench
    ./pyarmor build
```
#### Package Used by Other Clear Scripts

This example show how to obfuscate a package `examples/testpkg/mypkg`,
it used by clear script `examples/testpkg/main.py`

```bash
    # First create project with command 'init'
    #
    # This command will create a project configured as package
    #
    # Note that option --entry, it uses absolute path. Because package
    # are used by some other scripts, they may be in different path.
    #
    python pyarmor.py init --type=package --src=examples/testpkg/mypkg \
                           --entry=$(pwd)/examples/testpkg/main.py \
                           projects/testpkg

    # Show project information
    #
    # Note that 'is_package' and 'disable_restrict_mode' set to 1
    #
    cd projects/testpkg
    ./pyarmor info

    # Obfuscate package 'mypkg'
    #
    # This command will obfuscate all the scripts in the package 'mypkg'
    #
    # Bootstrap code will be inserted into entry script 'main.py'
    # and save to 'dist'
    #
    # All the runtime files will be saved to 'dist', all of these files
    # are required to import obfuscated scripts
    #
    # All the obfuscated package scripts are stored in 'dist/mypkg'
    #
    ./pyarmor build

    # Check entry script
    cat dist/main.py

    # Check obfuscated script
    cat dist/mypkg/foo.py

    # Now run clear entry script 'main.py' to import obfuscated
    # package 'mypkg'
    #
    cd dist
    python main.py
```

#### Change Default Project Configuration

* Show project information by command `info`

```bash
    cd projects/testpkg
    ./pyarmor info
```

* Change project information by command `config`

```bash
    cd projects/testpkg
    ./pyarmor config --title="My Package"

    ./pyarmor config --help
```

* Use option `--manifest` to specify obfuscated scripts

```bash
    cd projects/testpkg

    # Exclude "__init__.py" from project, it will not be obfuscated
    # Exclude all the files in test
    ./pyarmor config --manifest="global-include *.py, exclude __init__.py, prune test"

    # Force rebuild all
    # Note that pyarmor will not copy "__init__.py" to output path, which has
    # been excluded from project
    #
    ./pyarmor build --force

```

* Obfuscate scripts by other modes

```bash
    cd projects/pybench

    # Only obfuscate whole module, not each code object
    ./pyarmor config --obf-module-mode=des --obf-code-mode=none

    # Force rebuild all
    ./pyarmor build --force
```

About project configuration information, refer to [Project Configure File](#project-configure-file)

### Distribute Obfuscated Scripts

First obfuscate all scripts in build machine.

For standalone package, copy all the files in output path "dist" to
target machine

For package which used by other scripts:

* Copy all the runtime files to any python search path in target
  machine.

* Copy whole obfuscated package path to target machine, generally it
  locates in `dist/pkgname`

* Add 2 extra lines in main script before imported obfuscated package
  in target machine. Generally, these lines has been inserted into
  entry scripts of the project.

```python
    from pytransform import pyarmor_runtime
    pyarmor_runtime()

```

**Note** Python version in build machine must be same as in target
machine. To be exact, the magic string value used to recognize
byte-compiled code files (.pyc files) must be same.

### License of Obfuscated Scripts

There is a file **license.lic** in the output path "dist", the default
one permits the obfuscated scripts run in any machine and never
expired. Replace it with others can change this behaviour.

For examples, expire obfuscated scripts on some day

```bash
    cd projects/pybench

    # Generate a new license.lic
    ./pyarmor licenses --expired 2018-12-31 Customer-A

    # New license saved in "licenses/Customer-A/license.lic"
    # Readable text saved in "licenses/Customer-A/license.lic.txt"
    cat licenses/Customer-A/license.lic.txt
    "Expired:2018-12-23*CODE:Customer-A"

    # Replace default license.lic
    cp licenses/Customer-A/license.lic dist/

    # Run obfuscated scripts, it will not work after 2018-12-31
    cd dist
    python pybench.py
```

Command **licenses** used to generate new license, note that it's
plural. It can generate batch licenses.

```bash
    cd projects/pybench
    ./pyarmor licenses RCode-1 RCode-2 RCode-3 RCode-4 RCode-5
    ls licenses/

```

Bind obfuscated scripts to fixed machine

```bash
    # Run command hdinfo to get hardware information
    ./pyarmor hdinfo

    # Generate license bind to harddisk serial number
    ./pyarmor licenses --bind-disk '100304PBN2081SF3NJ5T' Customer-Tom

    # Generate license bind to ipv4 and mac address
    ./pyarmor licenses --bind-ipv4 '192.168.121.101' \
                       --bind-mac '20:c1:d2:2f:a0:96' Customer-John

    # Generate license bind to domain name and expire on 2018-12-31
    ./pyarmor licenses -e 2018-12-31 --bind-domain 'dashingsoft.com' \
                       Customer-Jondy

```

Note that `license.lic` generated by different project is **NOT**
compatible. For example,

```
    # Create `license.lic` in another project
    cd projects/myproject
    ./pyarmor licenses customer-jondy
    ls licenses/customer-jondy/license.lic

    # Copy this `license.lic` to project pybench
    cp licenses/customer-jondy/license.lic ../../projects/pybench/dist

    # Run obfuscated scripts in project pybench, it will report error
    cd ../../projects/pybench/dist
    python pybench.py

```
But this is not applied to Pyarmor of trial version. The `license.lic`
generated by trial Pyarmor can be used to any project created by trial
Pyarmor.

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

### Run Pyarmor with debug mode

By default, pyarmor prints simple message when something is wrong,
turn on debug mode to print all the trace stack

```bash
    python -d pyarmor.py ...
```

### Use runtime path

There are several extra files should be distributed with obfuscated
scripts. They're called **runtime files**

```
    pytransform.py, _pytransform.so or _pytransform.dll or _pytransform.dylib
    pyshield.key, pyshield.lic, product.key, license.lic
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

    ./pyarmor build

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
**benchmark** in target machine

```bash
    python pyarmor.py benchmark
```

## Examples

### Obfuscate odoo module

There is odoo module "web-login":

```
    /path/to/web-login
        __init__.py
        __manifest__.py
        *.py
        controller/
            __init__.py
            *.py
```

Assume odoo server will load it from **/path/to/odoo/addons/web-login**

```bash
    # Create a project
    python pyarmor.py init --type=package --src=/path/to/web-login \
                           --entry=__init__.py \
                           projects/odoo
    cd projects/odoo

    # Because __manifest__.py will read by odoo server directly, so it
    # should keep literal. Exclude it from project files.
    #
    ./pyarmor config --output=dist \
                     --manifest "global-include *.py, exclude __manifest__.py"
    ./pyarmor build

    # Obfuscated scripts saved in "dist/web-login", copy all of them and
    # original __manifest__.py to addon path of odoo server
    cp -a dist/web-login /path/to/odoo/addons
    cp /path/to/web-login/__manifest__.py /path/to/odoo/addons/web-login

    # Copy runtime files
    cp dist/*pytransform* dist/*.key dist/*.lic /path/to/odoo/addons/web-login

```

### Obfuscate many odoo modules

Suppose there are 3 odoo modules `web-login1`, `web-login2`,
`web-login3`, they'll be obfuscated separately, but run in the same
python interpreter.

First create common project, then clone to project1, project2, project3

```bash
    # Create common project "login"
    # Here src is any path
    python pyarmor.py init --type=package --src=/opt/odoo/pyarmor \
                           --entry=__init__.py \
                           projects/odoo/login

    # Configure common project, set runtime-path to an absolute path
    ./pyarmor config --output=dist --runtime-path=/opt/odoo/pyarmor \
                     --manifest "global-include *.py, exclude __manifest__.py" \
                     projects/odoo/login

    # Clone to project1
    python pyarmor.py init --src=/path/to/web-login1 \
                           --clone=projects/odoo/login \
                           projects/odoo/login1

    # Clone to project2
    python pyarmor.py init --src=/path/to/web-login2 \
                           --clone=projects/odoo/login \
                           projects/odoo/login2

    # Clone to project3
    python pyarmor.py init --src=/path/to/web-login3 \
                           --clone=projects/odoo/login \
                           projects/odoo/login3
```

Then build all projects

```bash
    # Only generate runtime files in common project
    (cd projects/odoo/login; ./pyarmor build --only-runtime)

    # Only obfuscate scripts, no runtime files
    (cd projects/odoo/login1; ./pyarmor build --no-runtime)
    (cd projects/odoo/login2; ./pyarmor build --no-runtime)
    (cd projects/odoo/login3; ./pyarmor build --no-runtime)
```

Finally distribute obfuscated modules

```
    cp -a projects/odoo/login1/dist/web-login1 /path/to/odoo/addons
    cp /path/to/web-login1/__manifest__.py /path/to/odoo/addons/web-login1

    cp -a projects/odoo/login2/dist/web-login2 /path/to/odoo/addons
    cp /path/to/web-login2/__manifest__.py /path/to/odoo/addons/web-login2

    cp -a projects/odoo/login3/dist/web-login3 /path/to/odoo/addons
    cp /path/to/web-login3/__manifest__.py /path/to/odoo/addons/web-login3

    # Copy all runtime files to runtime path
    mkdir -p /opt/odoo/pyarmor
    cp projects/odoo/login/runtimes/* /opt/odoo/pyarmor

    # Add /opt/odoo/pyarmor to python path in odoo server startup script
    # so that each module can import pytransform

    # Or copy pytransform.py to any python path
    cp projects/odoo/login/runtimes/pytransform.py /Any/Python/Path

```

Now restart odoo server.

### py2exe with obfuscated scripts

The problem is that all the scripts is in a zip file "library.zip"
after py2exe packages obfuscated scripts.

Another challange is that py2exe cound not find dependent modules after
scripts are obfuscated.

```bash
    python pyarmor.py init --src=examples/py2exe \
                           --entry="hello.py,setup.py" \
                           projects/py2exe
    cd projects/py2exe

    # This is the key, change default runtime-path
    ./pyarmor config --runtime-path=''

    # Obfuscate scripts
    ./pyarmor build


    # First run py2exe in original package, so that all the required
    # python system library files are generated in the "dist"
    #
    ( cd ../../examples/py2exe; python setup.py py2exe )

    # Move to final output
    mv ../../examples/py2exe/dist output/

    # Run py2exe in obfuscated package with "-i" and "-p", because
    # py2exe can not find dependent modules after they're obfuscated
    #
    ( cd dist; python setup.py py2exe --include queens --dist-dir ../output )

    # Copy runtime files to "output"
    cp runtimes/* ../output

    # Now run hello.exe
    cd output
    ./hello.exe
```

## Project Configure File

Each project has a configure file. It's a json file named
`.pyarmor_config` stored in the project path, used to specify
scripts to be obfuscated, and how to obfuscate etc.

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

It means all files anywhere in the **src** tree matching.

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

When init a project and no `--type` specified, it will be set to 1 if
there is `__init__.py` in the path `src`, otherwise it's None.

### entry

A string includes one or many entry scripts.

When build project, insert the following bootstrap code for each
entry:

```python
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
```

The entry name is relative to **src**, or filename with absolute path.

Multi entries are separated by comma, for example,

```
    main.py, another/main.py, /usr/local/myapp/main.py
```

Note that entry may be NOT obfuscated, if **manifest** does not
specify this entry. In this case, bootstrap code will be inserted into
the header of entry script either. So that it can import other
obfuscated modules.

### output

A path used to save output of build. It's relative to project path.

### capsule

Filename of project capsule.

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
an empty string, and copy runtime files, _pytransform.dll,
pyshield.key, pyshield.lic, product.key, license.lic to same path of
zip file, will solve this problem.

## Command Options

Available command: init, config, build, info, check, licenses, hdinfo, benchmark

See online document

```
    python pyarmor.py <command> --help
```

## Appendix

### Limitions

* Run pyarmor.py with non-debug Python interpreter. If Python
  interpreter is compiled with Py_TRACE_REFS or Py_DEBUG, pyarmor will
  crash.

### About license.lic

In pyarmor, there are 2 types of `license.lic`

* `license.lic` of Pyarmor, which locates in the source path of
  pyarmor. It's required to run Pyarmor.

* `license.lic` of Obfuscated Scripts, which is generated when
  obfuscating scripts or generating new licenses. It's required to run
  obfuscated scripts.

Each project has its own capsule `.pyarmor_capsule.zip` in project
path. This capsule is generated when run command `pyarmor init` to
create a project. And `license.lic` of Pyarmor will be as an input
file to make this capsule.

When runing command `pyarmor build` or `pyarmor licenses`, it will
generate a `license.lic` in project output path for obfuscated
scripts. Here the project capsule `.pyarmor_capsule.zip` will be as
input file to generate this `license.lic` of Obfuscated Scripts.

So the relation between 2 `license.lic` is

```
    `license.lic` of Pyarmor --> `.pyarmor_capsule.zip` --> `license.lic` of Obfuscated Scripts
```

For the trial version of Pyarmor, `.pyarmor_capsule.zip` of all the
projects are same. So `license.lic` of Obfuscated Scripts are
compatible for all projects. But for normal version of Pyarmor,
different project has different capsule `.pyarmor_capsule.zip`, so
`license.lic` of Obfuscated Scripts only works for this project.

### Restrict Mode

Restrict mode is instroduced from Pyarmor v3.6.

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
    python pyarmor.py init --src=examples/py2exe --entry=hello.py projects/testmod

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
    python pyarmor.py config --disable-restrict-mode=0 --obf-code-mode=des projects/testmod
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

Here is an example **examples/testmod**, entry script is **hello.py**,
and it's not obfuscated. It will import obfuscated module **queens**,
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
**examples/testmod/queens.py**

``` bash
    # Create project
    python pyarmor.py init --src=examples/testmod --entry=hello.py projects/testmod

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
