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

  obfuscate

### Run Obfuscated Scripts

### Import Obfuscated Module

### Use Project to Manage Obfuscated Scripts

  init
  info
  build
  config
  check

### Distribute Obfuscated Scripts

#### License of Obfuscated Scripts

  licneses
  hdinfo

#### Cross Platform

The core of [Pyarmor] is written by C, the only dependency is libc. So
it's not difficult to build for any other platform, even for embeded
system. Contact <jondy.zhao@gmail.com> if you'd like to run encrypted
scripts in other platform.

The latest platform-depentent library could be
found [here](http://pyarmor.dashingsoft.com/downloads/platforms)

### Examples

#### odoo

#### py2exe

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
