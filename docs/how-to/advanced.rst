.. highlight:: console

====================
 Fix encoding error
====================

The default encoding is ``utf-8``, if encoding error occurs when obfuscating the scripts, set encoding to right one. For example, change default encoding to ``gbk``::

    $ pyarmor cfg encoding=gbk

When customizing runtime error message, it also could specify encoding for ``messages.cfg``. For example, set encoding to ``gbk`` by this command::

    $ pyarmor cfg messages=messages.cfg:gbk

====================
 Removing docstring
====================

It's easy to remove docstring from obfuscated scripts::

    $ pyarmor cfg optimize 2

The argument optimize specifies the optimization level of the compiler; the default value of -1 selects the optimization level of the interpreter as given by -O options. Explicit levels are 0 (no optimization; __debug__ is true), 1 (asserts are removed, __debug__ is false) or 2 (docstrings are removed too).

.. customize-obfuscated-script
.. hidden-outer-runtime-key
.. check-debugger-by-yourself
.. protect-script-by-yourself

.. include:: ../_common_definitions.txt
