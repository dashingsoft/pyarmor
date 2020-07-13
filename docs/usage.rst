.. _using pyarmor:


Using PyArmor
=============

The syntax of the ``pyarmor`` command is:

    ``pyarmor`` [*command*] [*options*]

Obfuscating Python Scripts
--------------------------

Use command :ref:`obfuscate` to obfuscate python scripts. In the most simple
case, set the current directory to the location of your program ``myscript.py``
and execute::

    pyarmor obfuscate myscript.py

|PyArmor| obfuscates :file:`myscript.py` and all the :file:`*.py` in the same folder:

* Create :file:`.pyarmor_capsule.zip` in the ``HOME`` folder if it doesn't exists.
* Creates a folder :file:`dist` in the same folder as the script if it does not exist.
* Writes the obfuscated :file:`myscript.py` in the :file:`dist` folder.
* Writes all the obfuscated :file:`*.py` in the same folder as the script in the :file:`dist` folder.
* Copy runtime files used to run obfuscated scripts to the :file:`dist` folder.

In the :file:`dist` folder the obfuscated scripts and all the required files are
generated::

    dist/
        myscript.py

        pytransform/
            __init__.py
            _pytransform.so/.dll/.dylib

The extra folder ``pytransform`` called :ref:`Runtime Package`, it's required to
run the obfuscated script.

Normally you name one script on the command line. It's entry script. The content
of :file:`myscript.py` would be like this::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'\x06\x0f...')

The first 2 lines called :ref:`Bootstrap Code`, are only in the entry
script. They must be run before using any obfuscated file. For all the other
obfuscated :file:`*.py`, there is only last line::

    __pyarmor__(__name__, __file__, b'\x0a\x02...')

Run the obfuscated script::

    cd dist
    python myscript.py

By default, only the :file:`*.py` in the same path as the entry script are
obfuscated. To obfuscate all the :file:`*.py` in the sub-folder recursively,
execute this command::

    pyarmor obfuscate --recursive myscript.py

Distributing Obfuscated Scripts
-------------------------------

Just copy all the files in the output path `dist` to end users. Note that except
the obfuscated scripts, the :ref:`Runtime Package` need to be distributed to end
users too.

The :ref:`Runtime Package` may not with the obfuscated scripts, it could be
moved to any Python path, only if `import pytransform` works.

About the security of obfuscated scripts, refer to :ref:`The Security of PyArmor`

.. note::

   PyArmor need NOT be installed in the runtime machine

Generating License For Obfuscated Scripts
-----------------------------------------

Use command :ref:`licenses` to generate new :file:`license.lic` for obfuscated
scripts.

Generate an expired license for obfuscated script::

    pyarmor licenses --expired 2019-01-01 r001

|PyArmor| generates new license file:

* Read data from :file:`.pyarmor_capsule.zip` in the ``HOME`` folder
* Create :file:`license.lic` in the ``licenses/r001`` folder
* Create :file:`license.lic.txt` in the ``licenses/r001`` folder

Obfuscate the scripts with this new one::

    pyarmor obfuscate --with-license licenses/r001/license.lic myscript.py

Now run obfuscated script, It will report error after Jan. 1, 2019::

    cd dist
    python myscript.py

Generate license to bind obfuscated scripts to fixed machine, first get hardware
information::

    pyarmor hdinfo

Then generate new license bind to harddisk serial number and mac address::

    pyarmor licenses --bind-disk "100304PBN2081SF3NJ5T" --bind-mac "20:c1:d2:2f:a0:96" code-002

Run obfuscated script with new license::

    pyarmor obfuscate --with-license licenses/code-002/license.lic myscript.py

    cd dist/
    python myscript.py

It also could be use an outer license file `license.lic` with the obfuscated
scripts. By outer license, just obfuscate scripts once, then generate new
license to overwrite the old license on demand. This is the tradional way, refer
to :ref:`How to use outer license file`

Extending License Type
----------------------

It's easy to extend any other licese type for obfuscated scripts: **just add
authentication code in the entry script**. The script can't be changed any more
after it is obfuscated, so do whatever you want in your script. In this case the
:ref:`module pytransform` would be useful.

The prefer way is :ref:`using plugin to extend license type`. The advantage is
that your scripts needn't be changed at all. Just write authentication code in a
separated script, and inject it in the obfuscated scripts as obfuscating. For
more information, refer to :ref:`How to Deal with Plugins`

Here are some plugin examples

https://github.com/dashingsoft/pyarmor/tree/master/plugins

Obfuscating Single Module
-------------------------

To obfuscate one module exactly, use option ``--exact``::

    pyarmor obfuscate --exact foo.py

Only :file:`foo.py` is obfuscated, now import this obfuscated module::

    cd dist
    python -c "import foo"

Obfuscating Whole Package
-------------------------

Run the following command to obfuscate a package::

    pyarmor obfuscate --recursive --output dist/mypkg mykpg/__init__.py

To import the obfuscated package::

    cd dist
    python -c "import mypkg"

Packing Obfuscated Scripts
--------------------------

Use command ``pack`` to pack obfuscated scripts into the bundle.

First install `PyInstaller`::

    pip install pyinstaller

Set the current directory to the location of your program
``myscript.py`` and execute::

    pyarmor pack myscript.py

|PyArmor| packs :file:`myscript.py`:

* Execute ``pyarmor obfuscate`` to obfuscate :file:`myscript.py`
* Execute ``pyinstaller myscipt.py`` to create :file:`myscript.spec`
* Update :file:`myscript.spec`, replace original scripts with obfuscated ones
* Execute ``pyinstaller myscript.spec`` to  bundle the obfuscated scripts

In the ``dist/myscript`` folder you find the bundled app you distribute to your
users.

Run the final executeable file::

    dist/myscript/myscript

Generate an expired license for the bundle::

    pyarmor licenses --expired 2019-01-01 code-003
    pyarmor pack --with-license licenses/code-003/license.lic myscript.py

    dist/myscript/myscript

For complicated cases, refer to command :ref:`pack` and :ref:`How to pack obfuscated scripts`.

Improving Security Further
--------------------------

These `PyArmor`_ features could import security further:

1. :ref:`Using super mode` to obufscate scripts if possible, otherwise enable
   :ref:`Advanced Mode` if the platform is supported. In Windows and the
   performance meets the requirement, enable :ref:`VM Mode`
2. Try to :ref:`binding obfuscated scripts to Python interpreter`. Generally
   it's not required for :ref:`Super Mode`.
3. Make sure the entry script is patched by `cross protection code
   <https://pyarmor.readthedocs.io/en/latest/how-to-do.html#special-handling-of-entry-script>`_,
   and try to :ref:`Customizing cross protection code`
4. Use the corresponding :ref:`Restrict Mode`
5. Use the high security code obfuscation `--obf-code=2`
6. :ref:`Using plugin to improve security` by injecting your private checkpoints
   in the obfuscated scripts
7. If data files need to be protected, refer to :ref:`How to protect data files`

About the security of obfuscated scripts, refer to :ref:`The Security of PyArmor`

.. include:: _common_definitions.txt
