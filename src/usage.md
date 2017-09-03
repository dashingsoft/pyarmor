# Basic Usages

Here are some exampes to show basic usage of [Pyarmor].

All of first,

- Open a command box, enter the path of [Pyarmor] installed
- Run pyarmor.py with your favor python

Then following the steps below to learn how to use [Pyarmor]

## Import encrypted module

The common usage for Pyarmor is to encrypted some python modules,
import them in normal python environments.

[pybench](examples/pybench) is a collection of tests that provides a
standardized way to measure the performance of Python
implementations. It's an exactly one package to verify this
feature. We'll encrypted 2 scripts [Strings.py](examples/Strings.py)
and [Lists.py](examples/Lists.py), then import them by pybench.

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
    python pyarmor.py encrypt --with-capsule=pybench.zip --in-place --output=dist --src=examples/pybench Lists.py Strings.py
```

* --with-capsule specifies project capsule generated above. It's required.
* --in-place tell pyarmor save encrypted files in the same path of original file
* --src specifies relative path of scripts

This command will encrypt two scripts saved to

```
    examples/pybench/Lists.pye
    examples/pybench/Strings.pye
```

and generate some extra files in the output path "dist":

```
    pyshield.key
    pyshield.lic
    product.key
    * license.lic

    pyimcore.py
    pytransform.py
    _pytransofrm.dll or _pytransofrm.so
```

### Imported encrypted module

* Copy all the files in the path "dist/" to "examples/pybench"
* Add one line "import pyimcore" in the file "examples/pybench/pybench.py"
* Remove "examples/pybench/Lists.py" and "examples/pybench/Strings.py"
* Run pybench.py

Both Lists.py and Strings.py are removed, they are replaced with
"Lists.pye" and "Strings.pye". pybench.py still works, that's what
pyarmor does.

## Bind encrypted script to fix machine or expired it

Maybe you want to import encrypted scripts only in some special
machine, or expired it at some point. Pyarmor command "license" is
just for this case.

Command "encrypt" generates some extra files include "license.lic". In
above example, it's in the output path "dist". It's necessary to run
or import encrypted scripts. This file is a part of project capsule,
can be used in any machine and never expired.

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
    python pyarmor.py encrypt --with-capsule=pybench.zip --bind-disk "100304PBN2081SF3NJ5T"
```

This command will generate a "license.lic.txt" in the current path.

Continue above example, replace "examples/pybench/license.lic" with this "license.lic.txt"
```
    cp license.lic.txt examples/pybench/license.lic
```

Run pybench.py again

``` bash
    cd examples/pybench
    python pybench.py
```

It should work in this machine. If you copy "examples/pybench" to
other machine, it will failed to run pybench.py because encrypted
modules "Strings.pye" and "Lists.pye" could not be imported

### Generate a expired license
```
    python pyarmor.py encrypt --with-capsule=pybench.zip --expired-date=2018-05-30
```
The "license.lic.txt" generate by this command will expired on May 30, 2018

### Combined license
```
    python pyarmor.py encrypt --with-capsule=pybench.zip --expired-date=2018-05-30 --bind-disk "100304PBN2081SF3NJ5T"
```

The "license.lic.txt" generate by this command will expired on May 30,
2018 and only could be used in this machine.

## Run encrypted script

[examples/queens.py](examples/queens.py) is a script to solve eight
queens problem. This example show you how to run encrypted queens.py

### Generate a project capsule
```
    python pyarmor.py capsule project
```

This command will generate "project.zip" in current path.

### Encrypt script
```
    python pyarmor.py encrypt --with-capsule=project2.zip --main=queens --output=examples/runtime examples/queens.py
```
* --main tells pyarmor generate a wrapper script named "queens.py" in output path.

After this command, the script "queens.py" will be encrypted and saved
to "examples/runtime/queens.pye" , and all the extra files to run
encrypted "queens.pye" in the output path "examples/runtime".

The file list of "examples/runtime"

```
    pyshield.key
    pyshield.lic
    product.key
    license.lic

    pyimcore.py
    pytransform.py
    _pytransofrm.dll or _pytransofrm.so

    queens.py
    queens.pye

```

### Run encrypted script

``` bash
    cd examples/runtime
    python queens.py -n 8
```

Note that this queens.py is wrapper to run encrypted queens.pye, the
content of it would be

``` python
import pyimcore
from pytransform import exec_file
exec_file("queens.pye")
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
