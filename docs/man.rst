.. _man:


Man Page
========

Pyarmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

The syntax of the ``pyarmor`` command is:

    ``pyarmor`` [*command*] [*options*]

The most commonly used pyarmor commands are::

    obfuscate    Obfuscate python scripts
    licenses     Generate new licenses for obfuscated scripts
    pack         Pack obfuscated scripts to one bundle

See ``pyarmor <command> -h`` for more information on a specific command.

obfuscate
---------

``pyarmor obfuscate <options> SCRIPT...``

.. _pyarmor obfuscate command options:

-O PATH, --output PATH  Output path
-r, --recursive         Match files recursively
--restrict              Enable restrict mode
--capsule CAPSULE       Use this capsule to obfuscate code

licenses
--------

``pyarmor licenses <options> CODE``

.. _pyarmor licenses command options:

-C CAPSULE, --capsule CAPSULE
                      Use this capsule other than default capsule
-O OUTPUT, --output OUTPUT
                      Output path
--restrict            Generate a license for restrict mode
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

``pyarmor pack <options> SCRIPT``

.. _pyarmor pack command options:


-t TYPE, --type TYPE  cx_Freeze, py2exe, py2app, PyInstaller
-s SETUP, --setup SETUP
                      Setup script, default is setup.py, or ENTRY.spec for
                      PyInstaller
-O OUTPUT, --output OUTPUT
                      Directory to put final built distributions in (default
                      is output path of setup script)

.. include:: _common_definitions.txt
