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

  TODO:

============================
 Protecting system packages
============================

.. versionadded:: 8.2

When packing the scripts, Pyarmor could also protect system packages in the bundle. These are necessary options to prevent system packages from be replaced by plain scripts::

    $ pyarmor cfg assert.call:auto_mode="or" assert.call:includes = "*"
    $ pyarmor cfg assert.import:auto_mode="or" assert.import:includes = "*"

    $ pyinstaller foo.py
    $ pyarmor gen --assert-call --assert-import --restrict --pack dist/foo/foo foo.py

.. seealso:: :doc:`protection`

.. include:: ../_common_definitions.txt
