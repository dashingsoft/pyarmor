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

### Obfuscate Python Scripts

Obfuscate a simple script **examples/queens.py** in the source path of
Pyarmor

```
    python pyarmor.py obfuscate --src examples --entry queens.py "*.py"
    
    # Note that quotation mark is required for file patterns, otherwise
    # it will be expanded base on current path by shell.

    # Obfuscated scripts are saved in default output path "dist"
    cd dist
    cat queens.py
    
    # Run obfuscated script
    python queens.py
```

### Import Obfuscated Module

Import obfuscated moduels in a normal python scripts

```
    python pyarmor.py obfuscate --src XXX --entry main.py a.py b.py
    
    # a.py and b.py are obfuscated.
    # main.py is not. Only two extra lines are inserted at the begin.
    cd dist
    cat main.py
      ...
      from pytransform import pyarmor_runtime
      pyarmor_runtime()
      ...
    
    # Run main.py
    python main.py
```

### Use Project to Manage Obfuscated Scripts

It's better to obfuscate a complicate python project, there are the
several advantages:

* Increment build, only updated scripts are obfuscated since last
  build
  
* Obfuscate scripts by more modes

The following examples show how to obfuscate a python package
**pybench**, which locates in the **examples/pybench** in the source
of pyarmor.

```
    mkdir projects
    python pyarmor.py init --src examples/pybench --entry pybench.py \
                           projects/pybench

    # This command will create 2 files: .pyarmor_config, .pyarmor_capsule.zip
    # in the project path "projects/pybench"
    cd projects/pybench

    # And there is a shell script "pyarmor" is created at the same time.
    # (In windows, the name is "pyarmor.bat")
    
    # Show project information
    ./pyarmor info
    
    # Now run "pyarmor" to obfuscated all the scripts by subcommand "build"
    #
    ./pyarmor build

    # Check obfuscated script
    cd dist
    cat pybench.py

    # Run obfuscated script
    python pybench.py

```

After some source scripts changed, just run **build** again

```
    cd projects/pybench
    ./pyarmor build
```

Obfuscate scripts by other mode, for obfuscation mode, refer to [How to obfuscate python scripts](mechanism.md)

```
    cd projects/pybench
    
    # Only obfuscate whole module, not each code object
    ./pyarmor config --obf-module-mode=des --obf-code-mode=none
    
    # Force rebuild all
    ./pyarmor build --force
```

### Distribute Obfuscated Scripts

First obfuscate all scripts in build machine.

Then copy all the files in output path "dist" to target machine

That's all.

**Note** Python version in build machine must be same as in target
machine. To be exact, the magic string value used to recognize
byte-compiled code files (.pyc files) must be same.

#### License of Obfuscated Scripts

There is a file **license.lic** in the output path "dist", the default
one permits the obfuscated scripts run in any machine and never
expired. Replace it with others can change this behaviour.

For examples, expire obfuscated scripts on some day

```
    cd project/pybench
    
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

```
    cd project/pybench
    ./pyarmor licenses RCode-1 RCode-2 RCode-3 RCode-4 RCode-5
    ls licenses/
    
```

Bind obfuscated scripts in fixed machine

```
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

#### Cross Platform

The only difference for cross platform is need to replace
platform-dependent library **_pytransform** with the right one for
target machine

All the latest prebuilt platform-dependent library **_pytransform** could be
found [here](http://pyarmor.dashingsoft.com/downloads/platforms)

The core of [Pyarmor] is written by C, the only dependency is libc. So
it's not difficult to build for any other platform, even for embeded
system. Contact <jondy.zhao@gmail.com> if you'd like to run encrypted
scripts in other platform.

### Examples

#### obfuscate odoo module

There is odoo module "web-login":

```
    /path/to/web-login
        __init__.py
        *.py
        controller/
            __init__.py
            *.py
```

It's imported by odoo server,

```
    python pyarmor.py init --src=/path/to/web-login --entry=__init__.py \
                           projects/odoo
    cd projects/odoo
    ./pyarmor config --output=dist/web-login
    ./pyarmor build
    
    # Obfuscated scripts saved in "dist/web-login"
    # Tell odoo server load "web-login" module from here
```

#### py2exe with obfuscated scripts

The problem is that all the scripts is in a zip file "library.zip"
after py2exe packages obfuscated scripts.

Another challange is that py2exe cound not find dependent modules after
scripts are obfuscated.

```
    python pyarmor.py init --src=examples/py2exe \
                           --entry="hello.py,setup.py" \
                           projects/py2exe
    cd projects/py2exe
    
    # This is the key, change default runtime-path
    ./pyarmor config --runtime-path=''
    
    # Obfuscate scirpts
    ./pyarmor/build
    

    # First run py2exe in original package, so that all the required
    # python system library files are generated in the ${OUTPUT}
    #
    ( cd ../../examples/py2exe; python setup.py py2exe )
    
    # Move to final output
    mv ../../examples/py2exe/dist output/
    
    # Run py2exe in obfuscated package with "-i" and "-p", because
    # py2exe can not find dependent modules after they're obfuscated
    #
    cd dist
    python setup.py py2exe --includei queens --dist-dir ../output
    
    # Copy runtime files to "output"
    cp pyshield.* product.key license.lic _pytransform.dll ../output
    
    # Now run hello.exe
    cd ../output
    ./hello.exe
```

## Benchmark Test

How about the performance after scripts are obfuscated, run
**benchmark** in target machine

```
    python pyarmor.py benchmark
```

## Configure File

Each project has a configure file. It's a json file, used to specify
scripts to be obfuscated, and how to obfuscate etc.

### name

Project name.

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
    global-include *.py, exclude test*.py
```

### entry

A string includes one or many entry scripts.

When build project, insert the following bootstrap code for each
entry:

```
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
```

The entry name is relative to **src**.

Multi entries are separated by comma, for example, 

```
    main.py, another/main.py
```

Note that entry may be NOT obfuscated, if **manifest** does not
specify this entry. In this case, bootstrap code will be inserted into
the header of entry script either. So that it can import other
obfuscated modules.

### output

A path used to save output of build. It's relative to current path of
process.

### capsule

Filename of project capsule.

### obf_module_mode

How to obfuscate whole code object of module:

* none

    No obfuscate

* des

    Obfuscate whole code object by DES algorithm

### obf_code_mode

How to obfuscate byte code of each code object:

* none

    No obfuscate

* des

    Obfuscate byte-code by DES algorithm

* fast
    
    Obfuscate byte-code by a simple algorithm, it's faster than DES

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
