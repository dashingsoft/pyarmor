# DEPRECATED from v3.3, see user-guide.md for new version.

# Basic Usages

Here are some exampes to show basic usage of [Pyarmor].

All of first,

- Open a command box, enter the path of [Pyarmor] installed
- Run pyarmor.py with your favor python

Then following the steps below to learn how to use [Pyarmor]

## Run and Import encrypted module

[pybench](examples/pybench) is a collection of tests that provides a
standardized way to measure the performance of Python
implementations. It's an exactly one package to verify this feature.

First,

### Generate a project capsule

Use command "capsule"

``` bash
    python pyarmor.py capsule pybench
```

Project capsule is a compressed zip file, which include all the files
used to encrypt scripts. This command will generate "pybench.zip" in
the current path.

Generally, one capsule is only used for one project.

### Encrypt modules

Use command "encrypt"

``` bash
    python pyarmor.py encrypt --with-capsule=pybench.zip --output=dist/pybench --src=examples/pybench "*.py"
    python pyarmor.py encrypt --with-capsule=pybench.zip --output=dist/pybench/package --src=examples/pybench/package "*.py"
```

* --with-capsule specifies project capsule generated above. It's required.
* --src specifies relative path of scripts
* Quotation mark is required for argument "*.py", otherwise selected files is in the current path other than **src** path.

This command will encrypte all scripts of pybench and saved to "dist/pybench"

```
    ls dist/pybench
    
    _pytransform.dll  Dict.py        Lookups.py       pyimcore.py     systimes.py
    Arithmetic.py     Exceptions.py  NewInstances.py  pyshield.key    Tuples.py
    Calls.py          Imports.py     Numbers.py       pyshield.lic    Unicode.py
    clockres.py       Instances.py   package          pytransform.py  With.py
    CommandLine.py    license.lic    product.key      Setup.py
    Constructs.py     Lists.py       pybench.py       Strings.py
        
```

All of the .py files here are obfuscated like this:

```
    __pyarmor__(__name__, b'xxxxxxxxxxx')
```

### Run and Imported encrypted module

* Edit **dist/pybench/pybench.py**, insert a line "import pyimcore" like this:

```
    import pyimcore
    __pyarmor__(__name__, b'xxx...')
    
```

* Run obfuscated script

```
    cd dist/pybench
    python pybench.py

```

## Bind encrypted script to fix machine or expired it

Maybe you want to import encrypted scripts only in some special
machine, or expired it at some point. Pyarmor command "license" is
just for this case.

Command "encrypt" generates some extra files include "license.lic". In
above example, it's in the output path "dist/pybench". It's necessary
to run or import encrypted scripts. This file is a part of project
capsule, can be used in any machine and never expired.

Command "license" will generate special "license.lic", which could be
bind to fixed machine or expired.

Now let's generate a license file bind to this machine, first got

``` bash
    python pyarmor.py hdinfo

    It prints harddisk infomation as the floowing

    Harddisk's serial number is '100304PBN2081SF3NJ5T'
```

Run command "license"
```
    python pyarmor.py license --with-capsule=pybench.zip --bind-disk "100304PBN2081SF3NJ5T"
```

This command will generate a "license.lic.txt" in the current path.

Continue above example, replace "examples/pybench/license.lic" with this "license.lic.txt"
```
    cp license.lic.txt dist/pybench/license.lic
```

Run pybench.py again

``` bash
    cd dist/pybench
    python pybench.py
```

It should work in this machine. If you copy "dist/pybench" to
other machine, it will failed to run pybench.py.

### Generate a expired license
```
    python pyarmor.py license --with-capsule=pybench.zip --expired-date=2018-05-30
```
The "license.lic.txt" generate by this command will expired on May 30, 2018

### Combined license
```
    python pyarmor.py license --with-capsule=pybench.zip --expired-date=2018-05-30 --bind-disk "100304PBN2081SF3NJ5T"
```

The "license.lic.txt" generate by this command will expired on May 30,
2018 and only could be used in this machine.

## Examples

### Use odoo with obfuscated module scripts

There is a odoo module "odoo_web_login":

```
    odoo_web_login/
        __init__.py
        mod_a.py
        mod_b.py
        
        controller/
            __init__.py
            mod_c.py
      
```

Now run the following command in the src path of Pyarmor:

```
    # Generate capsule at first
    python pyarmor.py capsule myodoo
    
    # Obfuscate scripts, assume ${src} is the parent path of "odoo_web_login"
    python pyarmor.py encrypt --with-capsule=myodoo.zip --output=dist/odoo_web_login --src=${src}/odoo_web_login "*.py"
    python pyarmor.py encrypt --with-capsule=myodoo.zip --output=dist/odoo_web_login/controller --src=${src}/odoo_web_login/controller "*.py"
    
    # Edit "dist/odoo_web_login/__init__.py", insert a line "import pyimcore" before the first line
    
    # Copy obfuscated scripts and all extra files to ${src}. Note: it will overwrite original scripts
    cp dist/odoo_web_login/* ${src}/odoo_web_login
    cp dist/odoo_web_login/controller/* ${src}/odoo_web_login/controller
    
    # Restart odoo again.
```

### Use py2exe with obfuscated scripts

First install py2exe, run py2exe-0.6.9.win32-py2.7.exe

There is an example of py2exe: **C:/Python27/Lib/site-packages/py2exe/samples/simple**

Edit **setup.py**, comment line 33 if you don't have wxPython installed

```
    # windows = ["test_wx.py"],
    console = ["hello.py"],
```

Run py2exe, 

```
    cd C:/Python27/Lib/site-packages/py2exe/samples/simple
    C:/Python27/python setup.py py2exe
```

Then encrypt python scripts

```
    cd ${pyarmor_installed_path}
    C:/Python27/python pyarmor.py capsule myproject
    C:/Python27/python pyarmor.py encrypt --with-capsule=myproject.zip --output=dist \
                       --src=C:/Python27/Lib/site-packages/py2exe/samples/simple \
                       hello.py
```

Edit **dist/hello.py**, insert "import pyimcore" at the begin of this
script. Only main script need this patch, all the other modules need nothing to do.


Copy all the py file to source path **simple**

```
    cd dist
    cp  pyimcore.py pytransform.py hello.py C:/Python27/Lib/site-packages/py2exe/samples/simple

```

Copy all the others file to py2exe's dist

```
    cp _pytransform.dll pyshield.lic pyshield.key product.key license.lic \
       C:/Python27/Lib/site-packages/py2exe/samples/simple/dist
```

Edit **setup.py** again, add an extra line:

```
    py_modules = ["pyimcore", "pytransform"], 
```

Patch **pytransform.py**,

```
    1. Comment line 188~189
    
    # if not os.path.abspath('.') == os.path.abspath(path):
    #    m.set_option('pyshield_path'.encode(), path.encode())

    2. Replace line 181 with
    
    m = cdll.LoadLibrary('_pytransform.dll')

```

Run py2exe again:

```
    cd C:/Python27/Lib/site-packages/py2exe/samples/simple
    C:/Python27/python setup.py py2exe
```

Now run "hello.exe"

```
    cd dist
    ./hello.exe
```

# Command Line Options

```
Usage: pyarmor [command name] [options]

Command name can be one of the following list

  help                Show this usage
  version             Show version information
  capsule             Generate project capsule used to encrypted files
  encrypt             Encrypt the scripts
  license             Generate registration code

If you want to know the usage of each command, type the
following command:

  pyarmor help [command name]

and you can type the left match command, such as

   pyarmor c
or pyarmor cap
or pyarmor capsule

```

[Pyarmor]: https://github.com/dashingsoft/pyarmor
