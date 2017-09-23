# Pyarmor WebApp Tutorial

Pyarmor is a tool used to run and import encrypt python scripts.

WebApp is a one-page web application. It's gui interface of Pyarmor. This
tutorial mainly show the usage of WebApp.

## Download

First download Pyarmor WebApp from <https://github.com/dashingsoft/pyarmor/releases/download/v3.1.2/pyarmor-webapp.zip>

Then extract it to any path, for example **/opt**. In this turorial, **/opt**
will be as the installed path of Pyarmor WebApp. Replace it with real path when
run these examples.

## Startup

Enter path **/opt/pyarmor/webapp**, double click **start-server.bat** for Windows or **start-server.sh** for Linux.

Or start WebApp from command line, suppose python installed at **D:/tools/Python27**

```
cd /opt/pyarmor/webapp
D:/tools/Python27/python server.py

```

It will lanch a console window, at the same time a web page will be opened in
the web browser. This is WebApp.

Click tab **Project**, enter the graphic world of Pyarmor.

![](images/pyarmor-webapp.jpg)

## Usage

Here are 4 cases to show basic usage:

* First case it's to run a simple encrypted script
* Then a more complicated example, used encrypted module and package.
* Next one is to bind encrypted scripts to some machine
* Last is to expire encrypted scripts on some day

### Run encrypted script

This example show how to encrypt script [/opt/pyarmor/src/examples/queens.py](../src/examples/queens.py) and run it.

1. Encrypt script

    * Type **Title**, **Base Path**, **Start Wrapper Script**, **Build Path** as the following figure
    * Click button **Encrypt**

    ![](images/project-queen.jpg)

    About the format of **Startup Wrapper Script**, refer to appendix [Startup Wrapper Script](#startup-wrapper-script)

2. Run it

```
    # Encrypted files are saved here
    cd /opt/pyarmor/webapp/build

    # Run ecnrypted queens.pye with arguments "6"
    python main.py 6

```
   
3. Check the content of main.py

```
    import pyimcore
    from pytransform import exec_file
    exec_file('queens.pye')

```

3. Click button **Save** to save project information

### Import encrypted module

[/opt/pyarmor/src/examples/pybench](../src/examples/pybench) is a collection of
tests that provides a standardized way to measure the performance of Python
implementations. This example show how to use encrypted pybench except main
script [pybench.py](../src/examples/pybench/pybench.py) and package/\__init__.py

It's possible to encrypt package/\__init__.py, but not recommended for the sake of performance.

Why not encrypt [pybench.py](../src/examples/pybench/pybench.py), don't worry, you'll find answer at the end of this example. Now begin this example.

#### Encrypt modules

* Copy whole directory **/opt/pyarmor/src/examples/pybench** to **/opt/pyarmor/webapp/build**

```
    cp -a /opt/pyarmor/src/examples/pybench /opt/pyarmor/webapp/build

```

* Click button **New** to create a new project
* Type **Title**, **Base Path**, **MANIFEST.in** as the following figure

    ![](images/project-pybench.jpg)

    About the format of **MANIFEST.in**, refer to appendix [MANIFEST.in](#manifest.in)

* Click side tab **Advanced**

* Check **Remove source files after enrypt successfully.**

    ![](images/project-advanced.jpg)

* Click button **Save** to save project information

* Click button **Encrypt**

    Because **Build Path** is empty, all the encrypted files will saved in **Base Path**

#### Run pybench to import encrypted modules

* Enter path **/opt/pyarmor/webapp/build/pybench**

    List content of this directory, there is only one ".py" file **pybench.py**, all the others are ".pye"

* Edit pybench.py, after the first code line 13, insert line 14

```
    13: from __future__ import print_function
    14: import pyimcore
```

* Run pybench.py

```
    python pybench.py
```

It's no problem to encrypt **[pybench.py](../src/examples/pybench/pybench.py)**
either, but leave this work to you. A
tip [Startup Wrapper Script](#startup-wrapper-script)

### Bind encrypted script to one machine

This examble show how to bind encrypted script to this machine. Here we reuse
project **Queen** created in the first example.

* Get serial number of harddisk before this example

```
    cd /opt/pyarmor/src
    python pyarmor.py hdinfo
    Harddisk's serial number is '100304PBN2081SF3NJ5T'
```

* Click button **Open**, back first example
* Select **project-1:Queen** in the project list, then click **Open** in the dialog

    ![](images/project-open.jpg)

* Click side tab **Licenses**
* Check **Run encrypted scripts in special machine, type harddisk serial number of target machine**
* Type **100304PBN2081SF3NJ5T** in the below text box

    ![](images/project-license-1.jpg)

* Click bottom button **Generate**

    ![](images/project-license-2.jpg)

    Note that new license will be list in **Available Licenses**, here it is
    **Bind to 100304PBN2081SF3NJ5T (projects\\project-2\\license-0.lic)**

    The license filename is the part in the parentheses, fullpath would be
    **/opt/pyarmor/webapp/projects/project-2/license-0.lic**

* Replace the default license **/opt/pyarmor/webapp/build/license.lic** generated in first example

```
    cp /opt/pyarmor/webapp/projects/project-2/license-0.lic /opt/pyarmor/webapp/build/license.lic
```

* Run main.py again

```
    cd /opt/pyarmor/webapp/build
    python main.py
    
```

It would not work if you run main.py in other machine.

### Expire encrypted script on some day

This examble show how to expire encrypted script on some day. Here we still
reuse project **Queen**.

* Click side tab **Licenses**
* Check **Expired encrypted scripts at some point, type expired date (YYYY-MM-NN)**
* Type **2017-12-25** in the below text box

    ![](images/project-license-3.jpg)

* Click bottom button **Generate**

    New license will be list in **Available Licenses**, the filename will be shown in the parentheses.

* Replace **/opt/pyarmor/webapp/build/license.lic** with this file as above example

* Run main.py again

    It would not work after Christmas of 2017 even in this machine.

## Appendix

### Startup Wrapper Script

It used to generate a python script to call the encrypted script. The basic of
format

```
    NAME:ALIAS.py
```

NAME means main script name, ALIAS.py is target filename. For example,
if Startup Wrapper Script is **pybench:main.py**, after click button
Encrypt, **main.py** will be generated. Its content would be

```
import pyimcore
from pytransform import exec_file
exec_file('pybench.pye')
```

Note that **pybench.pye** in the last line.

If ALIAS equals NAME, it could simplify to be

```
    NAME

```

### MANIFEST.in

The manifest template has one command per line, where each command
specifies a set of files to include or exclude from the encrypted
project. For an example, let’s look at the Distutils’ own manifest
template:

```
include *.txt
recursive-include examples *.txt *.py
prune examples/sample?/build

```

The meanings should be fairly clear: include all files in the project
path matching *.txt, all files anywhere under the examples directory
matching *.txt or *.py, and exclude all directories matching
examples/sample?/build. All of this is done after the standard include
set, so you can exclude files from the standard set with explicit
instructions in the manifest template.


|              Command               |              Description                                                              |
|------------------------------------|---------------------------------------------------------------------------------------|
|include pat1 pat2 ...               | include all files matching any of the listed patterns                                 |
|exclude pat1 pat2 ...               | exclude all files matching any of the listed patterns                                 |
|recursive-include dir pat1 pat2 ... | include all files under dir matching any of the listed patterns                       |
|recursive-exclude dir pat1 pat2 ... | exclude all files under dir matching any of the listed patterns                       |
|global-include pat1 pat2 ...        | include all files anywhere in the source tree matching — & any of the listed patterns |
|global-exclude pat1 pat2 ...        | exclude all files anywhere in the source tree matching — & any of the listed patterns |
|prune dir                           | exclude all files under dir                                                           |
|graft dir                           | include all files under dir                                                           |


The patterns here are Unix-style “glob” patterns: * matches any
sequence of regular filename characters, ? matches any single regular
filename character, and [range] matches any of the characters in range
(e.g., a-z, a-zA-Z, a-f0-9_.). The definition of “regular filename
character” is platform-specific: on Unix it is anything except slash;
on Windows anything except backslash or colon.

### Demo Mode

If there is a button **Demo Version** in the top right corner of tab
**Project**, it is to say, Oh, what I'm doing is not reality. The
purpose of this mode is only to help users to understand the functions
of Pyarmor, there are 2 cases:

  * [Pyarmor official online demo](http://pyarmor.dashingsoft.com)
  * Open **/opt/pyarmor/webapp/index.html** in web browser directly.
