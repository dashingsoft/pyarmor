.. _man page:


Man Page
========

Pyarmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

The syntax of the ``pyarmor`` command is::

    pyarmor <command> [options]

The most commonly used pyarmor commands are::

    obfuscate    Obfuscate python scripts
    licenses     Generate new licenses for obfuscated scripts
    pack         Pack obfuscated scripts to one bundle
    hdinfo       Show hardware information

..
    The commands with project::

    init         Create a project to manage obfuscated scripts
    config       Update project information
    build        Obfuscate all the scripts in the project

    info         Show project information
    check        Check consistency of project

See `pyarmor <command> -h` for more information on a specific command.

obfuscate
---------

Obfuscate python scripts.

|PyArmor| first checks whether :file:`.pyarmor_capsule.zip` exists in
the ``HOME`` path. If not, make it.

Then search all the `.py` files in the path of entry script, and
obfuscate them in the default output path `dist`.

Next generate default :file:`license.lic` for obfuscated scripts and
make all the other :ref:`Runtime Files` in the `dist` path.

Finally insert :ref:`Bootstrap Code` into each entry script.

SYNOPSIS::

    pyarmor obfuscate <options> SCRIPT...

.. _pyarmor obfuscate command options:

OPTIONS

-O PATH, --output PATH  Output path
-r, --recursive         Match files recursively
--capsule CAPSULE       Use this capsule to obfuscate scripts

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

-t TYPE, --type TYPE  cx_Freeze, py2exe, py2app, PyInstaller(default).
-s SETUP, --setup SETUP
                      Setup script, default is setup.py.
-O OUTPUT, --output OUTPUT
                      Directory to put final built distributions in (default
                      is output path of setup script)

hdinfo
------

Show hardware information of this machine, such as serial number of
hard disk, mac address of network card etc. The information got here
could be as input data to generate license file for obfuscated
scripts.

SYNOPSIS::

    pyarmor hdinfo

.. include:: _common_definitions.txt
