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
    hdinfo       Show hardware information
    pack         Pack obfuscated scripts to one bundle


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
--exclude PATH          Exclude the path in recusrive mode
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

Next obfuscate all these scripts in the default output path `dist`.

And generate default :file:`license.lic` for obfuscated scripts and
make all the other :ref:`Runtime Files` in the `dist` path.

Finally insert :ref:`Bootstrap Code` into entry script.

The entry script is only the first script if there are more than one
script in command line.

**EXAMPLES**

* Obfuscate all the `.py` only in the same path of :file:`foo.py`::

     pyarmor obfuscate foo.py

* Obfuscate all the `.py` in the path of :file:`foo.py` recursively::

     pyarmor obfuscate --recursive foo.py

* Obfuscate all the `.py` in the path of :file:`foo.py` recursively,
  exclude all the `.py` in the path `build` and `dist`::

     pyarmor obfuscate --recursive --exclude build,dist foo.py

* Obfuscate only two scripts `foo.py`, `moda.py` exactly::

     pyarmor obfuscate --exact foo.py moda.py

* Obfuscate one package::

     pyarmor obfuscate --output dist/mypkg mypkg/__init__.py

* Obfuscate one module `moda.py` which could be used by any other
  plain script::

     pyarmor obfuscate --exact --no-bootstrap --no-restrict moda.py

* Obfuscate all the `.py` files in the same path of :file:`foo.py`,
  but do not insert cross protection code into obfuscated script
  :file:`dist/foo.py`::

     pyarmor obfuscate --no-cross-protection foo.py

* Obfuscate all the `.py` files in the same path of :file:`foo.py`,
  but do not insert bootstrap code at the beginning of obfuscated
  script :file:`dist/foo.py`::

     pyarmor obfuscate --no-bootstrap foo.py

.. _licenses:

licenses
--------

Generate new licenses for obfuscated scripts.

SYNOPSIS::

    pyarmor licenses <options> CODE

.. _pyarmor licenses command options:

OPTIONS:

-C CAPSULE, --capsule CAPSULE
                      Use this capsule to generate new licenses
-O OUTPUT, --output OUTPUT
                      Output path
-e YYYY-MM-DD, --expired YYYY-MM-DD
                      Expired date for this license
-d SN, --bind-disk SN
                      Bind license to serial number of harddisk
-4 IPV4, --bind-ipv4 IPV4
                      Bind license to ipv4 addr
-m MACADDR, --bind-mac MACADDR
                      Bind license to mac addr

pack
----

Obfuscate the scripts and pack them into one bundle.

SYNOPSIS::

    pyarmor pack <options> SCRIPT

.. _pyarmor pack command options:

OPTIONS:

-t TYPE, --type TYPE        cx_Freeze, py2exe, py2app, PyInstaller(default).
-O OUTPUT, --output OUTPUT  Directory to put final built distributions in.

hdinfo
------

Show hardware information of this machine, such as serial number of
hard disk, mac address of network card etc. The information got here
could be as input data to generate license file for obfuscated
scripts.

SYNOPSIS::

    pyarmor hdinfo

.. config:
    Option --manifest is comma-separated list of manifest template
    command, same as MANIFEST.in of Python Distutils. The default value is
    "global-include *.py"

    Option --entry is comma-separated list of entry scripts, relative to
    src path of project.

.. include:: _common_definitions.txt
