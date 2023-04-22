.. highlight:: console

====================
 Fix encoding error
====================

Set script encoding to ``utf-8``::

    $ pyarmor cfg encoding=utf-8

When customize runtime error message, set encoding of ``messages.cfg`` to ``gbk``::

    $ pyarmor cfg messages=messages.cfg:gbk

====================
 Removing docstring
====================

It's easy to remove docstring from obfuscated scripts::

    $ pyarmor cfg optimize 2

.. customize-obfuscated-script
.. hidden-outer-runtime-key
.. check-debugger-by-yourself
.. protect-script-by-yourself

.. include:: ../_common_definitions.txt
