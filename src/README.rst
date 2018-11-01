Protect Python Scripts By Pyarmor
=================================

Pyarmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts. It
protects Python scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate byte code of each code object.
* Clear f_locals of frame as soon as code object completed execution.
* Expired obfuscated scripts, or bind to fixed machine.

Look at what happened after ``foo.py`` is obfuscated by Pyarmor. Here
are the files list in the output path ``dist``::

    foo.py

    pytransform.py
    _pytransform.so
    or _pytransform.dll in Windows
    or _pytransform.dylib in MacOS

    pyshield.key
    pyshield.lic
    product.key
    license.lic

``dist/foo.py`` is obfuscated script, the content is::

    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...', 1)

All the other extra files called ``Runtime Files``, which are required to run or
import obfuscated scripts. So long as runtime files are in any Python path,
obfuscated script ``dist/foo.py`` can be used as normal Python script.

**The original python scripts can be replaced with obfuscated scripts seamlessly.**

For details to visit `https://github.com/dashingsoft/pyarmor/blob/master/docs/protect-python-scripts-by-pyarmor.md <https://github.com/dashingsoft/pyarmor/blob/master/docs/protect-python-scripts-by-pyarmor.md>`_

Support Platforms
-----------------

* Python 2.5, 2.6, 2.7 and Python3
* win32, win_amd64, linux_i386, linux_x86_64, macosx_intel
* Embedded Platform: Raspberry Pi, Banana Pi, TS-4600 / TS-7600

Quick Start
-----------

Install::

    pip install pyarmor

Obfuscate Scripts::

    python pyarmor.py obfuscate --src=examples/simple --entry=foo.py "*.py"

Run Obfuscated Scripts::

    cd dist
    python foo.py

More usage visit `https://github.com/dashingsoft/pyarmor/blob/master/src/user-guide.md <https://github.com/dashingsoft/pyarmor/blob/master/src/user-guide.md>`_

Expired Obfuscated Script
-------------------------

By default the obfuscated scripts can run in any machine and never expired. This
behaviour can be changed by replacing runtime file ``dist/license.lic``

First generate an expired license::

    python pyarmor.py licenses --expired 2018-12-31 Customer-Jondy

This command will make a new ``license.lic``, replace ``dist/license.lic``
with this one. The obfuscated script will not work after 2018.

Now generate another license bind to fixed machine::

    python pyarmor.py licenses --bind-hard "100304PBN2081SF3NJ5T"
                               --bind-mac "70:f1:a1:23:f0:94"
                               --bind-ipv4 "202.10.2.52"
                               Customer-Jondy

Interesting? More information visit `https://github.com/dashingsoft/pyarmor <https://github.com/dashingsoft/pyarmor>`_
