.. _understanding obfuscated scripts:

Understanding Obfuscated Scripts
================================

.. _global capsule:

Global Capsule
--------------

The :file:`.pyarmor_capsule.zip` in the ``HOME`` path called `Global
Capsule`. |PyArmor| will read data from `Global Capsule` when obfuscating
scripts or generating licenses for obfuscated scripts.

All the trial version of PyArmor shares one same :file:`.pyarmor_capsule.zip`,
which is created implicitly when executing command ``pyarmor obfuscate``. It
uses 1024 bits RSA keys, called `public capsule`.

For purchased version, each user will receive one exclusive `private capsule`,
which use 2048 bits RSA key.

The capsule can't help restoring the obfuscated scripts at all. If your `private
capsuel` got by someone else, the risk is that he/she may generate new license
for your obfuscated scripts.

Generally this capsule is only in the build machine, it's not used by the
obfuscated scripts, and should not be distributed to the end users.

Obfuscated Scripts
------------------

After the scripts are obfuscated by |PyArmor|, in the `dist` folder you find all
the required files to run obfuscated scripts::

    dist/
        myscript.py
        mymodule.py

        pytransform/
            __init__.py
            _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
            pytransform.key
            license.lic

The obfuscated scripts are normal Python scripts. The module `dist/mymodule.py`
would be like this::

    __pyarmor__(__name__, __file__, b'\x06\x0f...', 1)

The entry script `dist/myscript.py` would be like this::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'\x0a\x02...', 1)

.. note::

   In PyArmor, entry script is the first obfuscated script to be run or to be
   imported in a python interpreter process. For example, `__init__.py` is entry
   script if only one single python package is obfuscated.

.. _bootstrap code:

Bootstrap Code
--------------

The first 2 lines in the entry script called `Bootstrap Code`. It's only in the
entry script::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

For the obfuscated package which entry script is `__init__.py`. The bootstrap
code may make a relateive import by leading "."::

    from .pytransform import pyarmor_runtime
    pyarmor_runtime()

And there is another form if the runtime path is specified as obfuscating
scripts::

    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/runtime')

.. _runtime package:

Runtime Package
---------------

The package `pytransform` which is in the same folder with obfuscated scripts
called `Runtime Packge`. It's required to run the obfuscated script, and it's
the only dependency of obfuscated scripts.

Generally this package is in the same folder with obfuscated scripts, but it can
be moved anywhere. Only this package in any Python Path, the obfuscated scripts
can be run as normal scripts. And all the scripts obfuscated by the same
:ref:`Global Capsule` could share this package.

There are 4 files in this package::

    pytransform/
        __init__.py                  A normal python module
        _pytransform.so/.dll/.lib    A dynamic library implements core functions
        pytransform.key              Data file
        license.lic                  The license file for obfuscated scripts


Before v5.7.0, the runtime package has another form `Runtime Files`

.. _runtime files:

Runtime Files
~~~~~~~~~~~~~

They're not in one package, but as four separated files::

    pytransform.py               A normal python module
    _pytransform.so/.dll/.lib    A dynamic library implements core functions
    pytransform.key              Data file
    license.lic                  The license file for obfuscated scripts

Obviously `Runtime Package` is more clear than `Runtime Files`.

.. _the license file for obfuscated script:

The License File for Obfuscated Script
--------------------------------------

There is a special runtime file `license.lic`, it's required to run the
obfuscated scripts.

When executing ``pyarmor obfuscate``, a default one will be generated, which
allows obfuscated scripts run in any machine and never expired.

In order to bind obfuscated scripts to fix machine, or expire the obfuscated
scripts, use command ``pyarmor licenses`` to generate a new `license.lic` and
overwrite the default one.

.. note::

    In PyArmor, there is another `license.lic`, which locates in the source path
    of PyArmor. It's required to run `pyarmor`, and issued by me, :)

Key Points to Use Obfuscated Scripts
------------------------------------

* The obfuscated scripts are normal python scripts, so they can be seamless to
  replace original scripts.

* There is only one thing changed, the `bootstrap code`_ must be executed before
  running or importing any obfuscated scripts.

* The `runtime package`_ must be in any Python Path, so that the `bootstrap
  code`_ can run correctly.

* The `bootstrap code`_ will load dynamic library `_pytransform.so/.dll/.dylib`
  by `ctypes`. This file is dependent-platform, all the prebuilt dynamic
  libraries list here :ref:`Support Platforms`

* By default the `bootstrap code`_ searchs dynamic library `_pytransform` in the
  `runtime package`_. Check `pytransform._load_library` to find the details.

* If the dynamic library `_pytransform` isn't within the `runtime package`_,
  change the `bootstrap code`_::

    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/runtime')

  Both of runtime files `license.lic` and `pytransform.key` should be in this
  path either.

* When starts a fresh python interpreter process by `multiprocssing.Process`,
  `os.exec`, `subprocess.Popen` etc., make sure the `bootstrap code`_ are called
  in new process before running any obfuscated script.

More information, refer to :ref:`How to Obfuscate Scripts` and :ref:`How to Run Obfuscated Scripts`

.. include:: _common_definitions.txt
