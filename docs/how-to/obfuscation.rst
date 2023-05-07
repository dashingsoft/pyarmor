.. highlight:: console

..
  ========================
   Obfuscating Django app
  ========================

  TODO:

  ===========================
   Building obfuscated wheel
  ===========================

  TODO:

========================
 Packing with outer key
========================

This example shows how to pack ``src/myapp.py`` with :term:`outer key`

First pack it by PyInstaller::

    $ pyinstaller myapp.py

Next obfuscate the script with outer key::

    $ pyarmor gen --outer --pack dist/myapp/myapp myapp.py

Then generate an outer key::

    $ pyarmor gen key -O keylist -e 30

For one-folder mode, generally save outer key in the runtime package. For example::

    $ cp keylist/pyarmor.rkey dist/myapp/pyarmor_runtime_000000/

Thus it could run ``dist/myapp/myapp`` in any path. For example::

    $ dist/myapp/myapp

For one-file mode, generally store outer key to the same path of executable, and rename it to ``EXECUTABLE.KEYNAME``. For example::

    $ pyinstaller --onefile myapp.py
    $ pyarmor gen --outer --pack dist/myapp myapp.py
    $ pyarmor gen key -O keylist -e 30
    $ cp keylist/pyarmor.rkey dist/myapp.pyarmor.rkey

Thus it could run ``dist/myapp`` in any path. For example::

    $ dist/myapp

The outer key also could be stored in a fixed path specified by :envvar:`PYARMOR_RKEY`. For example::

    $ export PYARMOR_RKEY=/opt/pyarmor/runtime_data
    $ mkdir -p /opt/pyarmor/runtime_data
    $ cp keylist/pyarmor.rkey /opt/pyarmor/runtime_data/
    $ dist/foo

============================
 Protecting system packages
============================

.. versionadded:: 8.2

When packing the scripts, Pyarmor could also protect system packages in the bundle. These are necessary options to prevent system packages from be replaced by plain scripts::

    $ pyinstaller foo.py
    $ pyarmor gen --assert-call --assert-import --restrict --pack dist/foo/foo foo.py

.. seealso:: :doc:`protection`

.. include:: ../_common_definitions.txt
