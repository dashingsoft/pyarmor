# Pyarmor WebApp Tutorial

Pyarmor is a tool used to run and import encrypt python scripts.

WebApp is a one-page web application. It's gui interface of
Pyarmor. This tutorial mainly show the usage of WebApp.

## Download

First download Pyarmor WebApp from <https://github.com/dashingsoft/pyarmor/releases/download/v3.1.2/pyarmor-webapp.zip>

Then extract it to any path, for example **/opt**. In this turorial,
**/opt** will be as the installed path of Pyarmor WebApp. Replace it
with real path when run these examples.

## Startup

Enter path **/opt/pyarmor/webapp**, double click **start-server.bat** for Windows or **start-server.sh** for Linux.

Or start WebApp from command line, suppose python installed at **D:/tools/Python27**

```
cd /opt/pyarmor/webapp
D:/tools/Python27/python server.py

```

It will lanch a console window, at the same time a web page will be
opened in the web browser. This is WebApp.

Click tab **Project**, enter the graphic world of Pyarmor.

### Demo Mode

If there is a button **Demo Version** in the top right corner, it is
to say, Oh, what I'm doing is not reality. The purpose of this mode is
only to help users to understand the functions of Pyarmor, there are 2
cases:

  * [Pyarmor official online demo](http://pyarmor.dashingsoft.com)
  * Open **/opt/pyarmor/webapp/index.html** in web browser directly.

## Usage

There are examples

### Import encrypted module

pybench

### Run encrypted script

queens

### Bind encrypted script to one machine

### Expired encrypted script on some day

## Appendix

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
