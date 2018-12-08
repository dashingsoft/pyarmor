.. _understand obfuscated scripts:

Understanding Obfuscated Scripts
================================

.. _global capsule:

Global Capsule
--------------

The :file:`.pyarmor_capsule.zip` in the ``HOME`` path called ``Global
Capsule``. It's created implicitly when executing command ``pyarmor
obfuscate``. |PyArmor| will read data from ``Global Capsule`` when
obfuscating scripts or generating licenses for obfuscated scripts.

Obfuscated Scripts
------------------

After the scripts are obfuscated by |PyArmor|, in the :file:`dist`
folder you find all the files you distribute to your users::

    myscript.py
    mymodule.py

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pyshield.key
    pyshield.lic
    product.key
    license.lic

The obfuscated scripts are normal Python scripts.

The module :file:`dist/mymodule.py` would be like this::

    __pyarmor__(__name__, __file__, b'\x06\x0f...')

The entry script :file:`dist/myscript.py` would be like this::

    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x0a\x02...')

.. _bootstrap code:

Bootstrap Code
--------------

The first 2 lines in the entry script called ``Bootstrap Code``. It's
only in the entry script::

    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

.. _runtime files:

Runtime Files
-------------

Except obfuscated scripts, all the other files are called ``Runtime Files``:

* :file:`pytransform.py`, a normal python module
* ``_pytransform``, a dynamic library implements core functions
* 4 data files

All of them are required to run obfuscated scripts.

The :file:`license.lic`
-----------------------

There is a special runtime file :file:`license.lic`. The default one,
which generated as executing ``pyarmor obfuscate``, allows obfuscated
scripts run in any machine and never expired.

To change this behaviour, use command ``pyarmor licenses`` to generate
new :file:`license.lic` and overwrite the default one.

Running Obfuscated Scripts
--------------------------

The obfuscated scripts is a normal python script, it can be run by
normal python interpreter::

    cd dist
    python myscript.py

Firt :ref:`Bootstrap Code` is executed:

* Import ``pyarmor_runtime`` from :file:`pytransform.py`
* Execute ``pyarmor_runtime``
    * Load dynamic library ``_pytransform`` by ``ctypes``
    * Check ``license.lic`` in the same path
    * Add there builtin functions ``__pyarmor__``, ``__enter_armor__``, ``__exit_armor__``

After that:

* Call ``__pyarmor__`` to import the obfuscated module.
* Call ``__enter_armor__`` to restore code object of function before executing each function
* Call ``__exit_armor__`` to obfuscate code object of function after each function return

See :ref:`How to Obfuscate Scripts`

Key Points to Use Obfuscated Scripts
------------------------------------

* The obfuscated script is a normal python script, so it can be
  seamless to replace original script.

* There is only one thing changed, the following code must be run
  before using any obfuscated script::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

* It can be put in any script anywhere, only if it run in the same
  Python interpreter. It will create some builtin function to deal
  with obfuscated code.

* The extra runtime file :file:`pytransform.py` must be in any Python
  path in target machine. :file:`pytransform.py` need load dynamic
  library ``_pytransform`` by ``ctypes``. It may be

    - :file:`_pytransform.so` in Linux
    - :file:`_pytransform.dll` in Windows
    - :file:`_pytransform.dylib` in MacOS

  This file is dependent-platform, download the right one to the same
  path of :file:`pytransform.py` according to target platform. All the
  prebuilt dynamic libraries list here

  http://pyarmor.dashingsoft.com/downloads/platforms/

* By default :file:`pytransform.py` search dynamic library
  ``_pytransform`` in the same path. Check
  ``pytransform._load_library`` to find the details.

* All the other :ref:`Runtime Files` should in the same path as
  dynamic library ``_pytransform``

* If :ref:`Runtime Files` locate in some other path, change
  :ref:`Bootstrap Code`::

    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/runtime-files')


.. include:: _common_definitions.txt
