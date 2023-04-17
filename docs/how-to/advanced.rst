.. highlight:: console

================
 Advanced Usage
================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

Fix encoding error
==================

Set script encoding::

    $ pyarmor cfg encoding=utf-8

When customize runtime error message, set encoding of ``messages.cfg``::

    $ pyarmor cfg messages=messages.cfg:gbk

Querying runtime key information in outer script
================================================

.. versionadded:: 8.x
                  This feature is still not implemented

When generate outer runtime key, use plugin to store informaion as comment in the key file

Then read key file and parse comment lines.

Extending verification method for runtime key
=============================================

.. versionadded:: 8.x
                  This feature is still not implemented

In obfuscated scripts, call function ``__pyarmor__`` to get user data stored in the runtime key.

.. code-block:: python

   user_data = __pyarmor__(None, None, b'keyinfo', 1)
   if not verify_user_data(user_data):
       sys.exit(1)

.. customize-obfuscated-script
.. hidden-outer-runtime-key
.. check-debugger-by-yourself
.. protect-script-by-yourself

.. include:: ../_common_definitions.txt
