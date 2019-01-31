.. _understand obfuscated scripts:

Understanding Obfuscated Scripts
================================

.. _global capsule:

Global Capsule
--------------

The :file:`.pyarmor_capsule.zip` in the ``HOME`` path called `Global
Capsule`. It's created implicitly when executing command ``pyarmor
obfuscate``. |PyArmor| will read data from `Global Capsule` when
obfuscating scripts or generating licenses for obfuscated scripts.

Obfuscated Scripts
------------------

After the scripts are obfuscated by |PyArmor|, in the `dist` folder
you find all the files you distribute to your users::

    myscript.py
    mymodule.py

    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pytransform.py
    pytransform.key
    license.lic

The obfuscated scripts are normal Python scripts.

The module `dist/mymodule.py` would be like this::

    __pyarmor__(__name__, __file__, b'\x06\x0f...')

The entry script `dist/myscript.py` would be like this::

    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x0a\x02...')

.. _bootstrap code:

Bootstrap Code
--------------

The first 2 lines in the entry script called `Bootstrap Code`. It's
only in the entry script::

    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

.. _runtime files:

Runtime Files
-------------

Except obfuscated scripts, all the other files are called `Runtime Files`:

* `pytransform.py`, a normal python module
* `_pytransform.so`, or `_pytransform.dll`, or `_pytransform.dylib` a dynamic library implements core functions
* `pytransform.key`, data file
* `license.lic`, the license file for obfuscated scripts

All of them are required to run obfuscated scripts.

The `license.lic`
-----------------

There is a special runtime file `license.lic`. The default one,
which generated as executing ``pyarmor obfuscate``, allows obfuscated
scripts run in any machine and never expired.

To change this behaviour, use command ``pyarmor licenses`` to generate
new `license.lic` and overwrite the default one.

Running Obfuscated Scripts
--------------------------

The obfuscated scripts is a normal python script, it can be run by
normal python interpreter::

    cd dist
    python myscript.py

Firt :ref:`Bootstrap Code` is executed:

* Import `pyarmor_runtime` from `pytransform.py`
* Execute `pyarmor_runtime`
    * Load dynamic library `_pytransform` by `ctypes`
    * Check `license.lic` in the same path
    * Add there builtin functions `__pyarmor__`, `__enter_armor__`, `__exit_armor__`

After that:

* Call `__pyarmor__` to import the obfuscated module.
* Call `__enter_armor__` to restore code object of function before executing each function
* Call `__exit_armor__` to obfuscate code object of function after each function return

More information, refer to :ref:`How to Obfuscate Scripts` and :ref:`How to Run Obfuscated Scripts`

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

* The extra runtime file `pytransform.py` must be in any Python
  path in target machine. `pytransform.py` need load dynamic
  library `_pytransform` by `ctypes`. It may be

    - `_pytransform.so` in Linux
    - `_pytransform.dll` in Windows
    - `_pytransform.dylib` in MacOS

  This file is dependent-platform, download the right one to the same
  path of `pytransform.py` according to target platform. All the
  prebuilt dynamic libraries list here

  http://pyarmor.dashingsoft.com/downloads/platforms/

* By default `pytransform.py` search dynamic library `_pytransform` in
  the same path. Check `pytransform._load_library` to find the
  details.

* All the other :ref:`Runtime Files` should in the same path as
  dynamic library `_pytransform`

* If :ref:`Runtime Files` locate in some other path, change
  :ref:`Bootstrap Code`::

    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/runtime-files')

Two types of `license.lic`
--------------------------

In PyArmor, there are 2 types of `license.lic`

* `license.lic` of |PyArmor|, which locates in the source path of
  |PyArmor|. It's required to run `pyarmor`

* `license.lic` of Obfuscated Scripts, which is generated as
  obfuscating scripts or generating new licenses. It's required to run
  obfuscated scripts.

Each project has its own capsule `.pyarmor_capsule.zip` in project
path. This capsule is generated when run command `pyarmor init` to
create a project. And `license.lic` of |PyArmor| will be as an input
file to make this capsule.

When runing command `pyarmor build` or `pyarmor licenses`, it will
generate a `license.lic` in project output path for obfuscated
scripts. Here the project capsule `.pyarmor_capsule.zip` will be as
input file to generate this `license.lic` of Obfuscated Scripts.

So the relation between 2 `license.lic` is::

    license.lic of PyArmor --> .pyarmor_capsule.zip --> license.lic of Obfuscated Scripts

If the scripts are obfuscated by command `pyarmor obfuscate` other
than by project, :ref:`Global Capsule` is used implicitly.


.. include:: _common_definitions.txt
