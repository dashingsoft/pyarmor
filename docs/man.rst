.. _man:


Man Page
========

The syntax of the ``pyarmor`` command is:

    ``pyarmor`` [*command*] [*options*]


Command ``obfuscate``
---------------------

.. _pyarmor obfuscate command options:


``pyarmor obfuscate`` <options> SCRIPT...

-O PATH, --output PATH  Output path
-r, --recursive         Match files recursively
--restrict              Enable restrict mode
--capsule CAPSULE       Use this capsule to obfuscate code

Command ``licenses``
--------------------

.. _pyarmor licenses command options:


``pyarmor licenses`` <options> CODE


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


Command ``pack``
----------------

.. _pyarmor pack command options:


``pyarmor pack`` <options> SCRIPT


-t TYPE, --type TYPE  cx_Freeze, py2exe, py2app, PyInstaller
-s SETUP, --setup SETUP
                      Setup script, default is setup.py, or ENTRY.spec for
                      PyInstaller
-O OUTPUT, --output OUTPUT
                      Directory to put final built distributions in (default
                      is output path of setup script)

.. include:: _common_definitions.txt
