.. _man page:

Man Page
========

PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

The syntax of the ``pyarmor`` command is::

    pyarmor <command> [options]

The most commonly used pyarmor commands are::

    obfuscate    Obfuscate python scripts
    licenses     Generate new licenses for obfuscated scripts
    pack         Pack obfuscated scripts to one bundle
    hdinfo       Show hardware information

The commands for project::

    init         Create a project to manage obfuscated scripts
    config       Update project settings
    build        Obfuscate all the scripts in the project

    info         Show project information
    check        Check consistency of project

See `pyarmor <command> -h` for more information on a specific command.

.. _obfuscate:

obfuscate
---------

Obfuscate python scripts.

**SYNOPSIS**::

    pyarmor obfuscate <options> SCRIPT...

**OPTIONS**

-O, --output PATH       Output path, default is `dist`
-r, --recursive         Search scripts in recursive mode
--exclude PATH          Exclude the path in recusrive mode. Multiple paths are allowed, separated by ","
--exact                 Only obfuscate list scripts
--no-bootstrap          Do not insert bootstrap code to entry script
--no-cross-protection   Do not insert protection code to entry script
--no-restrict           Disable restrict mode

**DESCRIPTION**

PyArmor first checks whether :ref:`Global Capsule` exists in the
``HOME`` path. If not, make it.

Then find all the scripts to be obfuscated. There are 3 modes to
search the scripts:

* Normal: find all the `.py` files in the same path of entry script
* Recursive: find all the `.py` files in the path of entry script recursively
* Exact: only these scripts list in the command line

If there is an entry script, PyArmor will modify it, insert cross
protection code into the entry script.

Next obfuscate all these scripts in the default output path `dist`.

After that generate default :file:`license.lic` for obfuscated scripts
and make all the other :ref:`Runtime Files` in the `dist` path.

Finally insert :ref:`Bootstrap Code` into entry script.

The entry script is only the first script if there are more than one
script in command line.

Option `--no-restrict` is required if the obfuscated scripts will be
imported by the plain scripts. By default the obfuscated scripts only
can be imported from other obfuscated scripts.

**EXAMPLES**

* Obfuscate all the `.py` only in the current path::

     pyarmor obfuscate foo.py

* Obfuscate all the `.py` in the current path recursively::

     pyarmor obfuscate --recursive foo.py

* Obfuscate all the `.py` in the current path recursively, exclude all
  the `.py` in the path `build` and `dist`::

     pyarmor obfuscate --recursive --exclude build,dist foo.py

* Obfuscate only two scripts `foo.py`, `moda.py` exactly::

     pyarmor obfuscate --exact foo.py moda.py

* Obfuscate all the `.py` file in the path `mypkg/`::

     pyarmor obfuscate --output dist/mypkg mypkg/__init__.py

* Obfuscate one module `moda.py` which could be used by any other
  plain script::

     pyarmor obfuscate --exact --no-restrict moda.py

* Obfuscate all the `.py` files in the current path, but do not insert
  cross protection code into obfuscated script :file:`dist/foo.py`::

     pyarmor obfuscate --no-cross-protection foo.py

* Obfuscate all the `.py` files in the current path, but do not insert
  bootstrap code at the beginning of obfuscated script
  :file:`dist/foo.py`::

     pyarmor obfuscate --no-bootstrap foo.py

.. _licenses:

licenses
--------

Generate new licenses for obfuscated scripts.

**SYNOPSIS**::

    pyarmor licenses <options> CODE

**OPTIONS**

-O, --output OUTPUT         Output path
-e, --expired YYYY-MM-DD    Expired date for this license
-d, --bind-disk SN          Bind license to serial number of harddisk
-4, --bind-ipv4 IPV4        Bind license to ipv4 addr
-m, --bind-mac MACADDR      Bind license to mac addr
--no-restrict               Generate license for non-restrict mode

**DESCRIPTION**

In order to run obfuscated scripts, it's necessarey to hava a
:flile:`license.lic`. As obfuscating the scripts, there is a default
:file:`license.lic` created at the same time. In this license the
obfuscated scripts can run on any machine and never expired.

This command is used to generate new licenses for obfuscated
scripts. For example::

    pyarmor licenses --expired 2019-10-10 mycode

An expired license will be generated in the default output path plus
code name `licenses/mycode`, then overwrite the old one in the same
path of obfuscated script::

    cp licenses/mycode/license.lic dist/

Another example, bind obfuscated scripts in mac address and expired on
2019-10-10::

    pyarmor licenses --expired 2019-10-10 --bind-mac 2a:33:50:46:8f tom
    cp licenses/tom/license.lic dist/

Before this, run command :ref:`hdinfo` to get hardware information::

    pyarmor hdinfo

There maybe have whitespace in the serial number of harddisk for some
machines, just quote it in the command line::

    pyarmor licenses --bind-disk "100304PBN2081SF3NJ5T " jondy

If the obfuscated scripts will be imported by other plain scripts, do
not miss option `--no-restrict`::

    pyarmor licenses --no-restrict mycode2

.. _pack:

pack
----

Obfuscate the scripts and pack them into one bundle.

**SYNOPSIS**::

    pyarmor pack <options> SCRIPT

**OPTIONS**

-t, --type TYPE      cx_Freeze, py2exe, py2app, PyInstaller(default).
-O, --output OUTPUT  Directory to put final built distributions in.

**DESCRIPTION**

PyArmor first packes the script by calling the third-party tool such
as PyInstaller, gets the dependencies and other required files.

Then obfuscates all the `.py` files in the same path of entry script.

Next replace the original scripts with the obfuscated ones.

Finally pack all of them into one bundle

This command only works for simple script. For complicated cases,
refer to :ref:`How to pack obfuscated scripts`.

.. _hdinfo:

hdinfo
------

Show hardware information of this machine, such as serial number of
hard disk, mac address of network card etc. The information got here
could be as input data to generate license file for obfuscated
scripts.

**SYNOPSIS**::

    pyarmor hdinfo

.. _init:

init
----

Create a project to manage obfuscated scripts.

**SYNOPSIS**::

    pyarmor init <options> PATH

**OPTIONS**

-t, --type <auto,app,pkg>  Project type, default value is `auto`
-s, --src SRC              Base path of python scripts, default is current path
-e, --entry ENTRY          Entry script of this project

**DESCRIPTION**

This command will create a project in the specify `PATH`, and a
:file:`.pyarmor_config` will be created at the same time, which is
project configuration of JSON format.

If the option `--type` is set to `auto`, which is the default value,
the project type will set to `pkg` if the entry script is
`__init__.py`, otherwise to `app`.

The `init` command will set the properties `disable_restrict_mode` and
`is_package` of this project to `1` if the new project is configured
as `pkg`, otherwise they're set to `0`.

After project is created, use command config_ to change the project
settings.

**EXAMPLES**

* Create a project in the current path::

    pyarmor init --entry foo.py

* Create a project in the build path `obf`::

    pyarmor init --entry foo.py obf

* Create a project for package::

    pyarmor init --entry __init__.py

* Create a project in the path `obf`, manage the scripts in the path
  `/path/to/src`::

    pyarmor init --src /path/to/src --entry foo.py obf

.. _config:

config
------

Update project settings.

**SYNOPSIS**::

    pyarmor config <options> [PATH]

**OPTIONS**

--name NAME                     Project name
--title TITLE                   Project title
--src SRC                       Project src
--output OUTPUT                 Output path for obfuscated scripts
--manifest TEMPLATE             Manifest template string
--entry SCRIPT                  Entry script of this project
--is-package <0,1>              Set project as package or not
--disable-restrict-mode <0,1>   Disable or enable restrict mode
--obf-mod <0,1>                 Disable or enable to obfuscate module
--obf-code <0,1>                Disable or enable to obfuscate function
--wrap-mode <0,1>               Disable or enable to wrap mode
--cross-protection <0,1>        Disable or enable to insert cross protection code into entry script
--runtime-path RPATH            Set the path of runtime files in target machine

**DESCRIPTION**

Run this command in project path to change project settings::

    pyarmor config --option new-value

Or specify the project path at the end::

    pyarmor config --option new-value /path/to/project

Option --manifest is comma-separated list of manifest template
command, same as MANIFEST.in of Python Distutils.

Option --entry is comma-separated list of entry scripts, relative to
src path of project.

**EXAMPLES**

* Change project name and title::

    pyarmor config --name "project-1"  --title "My PyArmor Project"

* Change project entries::

    pyarmor config --entry foo.py,hello.py

* Exclude path `build` and `dist`, do not search `.py` file from these
  paths::

    pyarmor config --manifest "global-include *.py, prune build, prune dist"

* Obfuscate script with wrap mode off::

    pyarmor config --wrap-mode 0

.. _build:

build
-----

Build project, obfuscate all scripts in the project.

**OPTIONS**

-B, --force           Force to obfuscate all scripts
-r, --only-runtime    Generate extra runtime files only
-n, --no-runtime      DO NOT generate runtime files
-O, --output OUTPUT   Output path, override project configuration

**DESCRIPTION**

Run this command in project path::

    pyarmor build

Or specify the project path at the end::

    pyarmor build /path/to/project

**EXAMPLES**

* Only obfuscate the scripts which have been changed since last
  build::

    pyarmor build

* Force build all the scripts::

    pyarmor build -B

* Generate runtime files only, do not try to obfuscate any script::

    pyarmor build -r

* Obfuscate the scripts only, do not generate runtime files::

    pyarmor build -n

* Save the obfuscated scripts to other path, it'll not change the
  output path of project settings::

    pyarmor build -B -O /path/to/other

.. _info:

info
----

Show project information.

**SYNOPSIS**::

    pyarmor info [PATH]

**DESCRIPTION**

Run this command in project path::

    pyarmor info

Or specify the project path at the end::

    pyarmor info /path/to/project

.. _check:

check
-----

Check consistency of project.

**SYNOPSIS**::

    pyarmor check [PATH]

**DESCRIPTION**

Run this command in project path::

    pyarmor check

Or specify the project path at the end::

    pyarmor check /path/to/project

.. include:: _common_definitions.txt
