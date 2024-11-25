Protect Python Scripts By Pyarmor
=================================

Pyarmor is a command line tool used to obfuscate python scripts, bind obfuscated scripts to fixed machine or expire obfuscated scripts.

Key Features
------------

* The obfuscated scritpt is still a normal `.py` script, in most of cases the original python scripts can be replaced with obfuscated scripts seamlessly.
* Provide many ways to obfuscate the scripts to balance security and performance
* Rename functions/methods/classes/variables/arguments, irreversible obfuscation
* Convert part of Python functions to C function, compile to binary by high optimize option, irreversible obfuscation
* Bind obfuscated scripts to fixed machine or expire obfuscted scripts
* Protect obfuscated scripts by Themida (Only for Windows)

Support Platforms
-----------------

* Python 3.7~3.13
* Windows
* Many linuxs, include embedded systems
* Apple Intel and Apple Silicon

Quick Start
-----------

Install::

    pip install pyarmor

Obfuscate the script `foo.py`::

    pyarmor gen foo.py

This command generates an obfuscated script `dist/foo.py` like this:

.. code:: python

    from pyarmor_runtime import __pyarmor__
    __pyarmor__(__name__, __file__, b'\x28\x83\x20\x58....')

Run it::

    python dist/foo.py

More Resources
--------------

- `Home <https://github.com/dashingsoft/pyarmor>`_
- `Website <http://pyarmor.dashingsoft.com>`_
- `中文网站 <http://pyarmor.dashingsoft.com/index-zh.html>`_
- `Issues <https://github.com/dashingsoft/pyarmor/issues>`_
- `Documentation <https://pyarmor.readthedocs.io/>`_
