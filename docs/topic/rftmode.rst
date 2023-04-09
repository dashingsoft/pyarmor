========================
Insight Into RFT Mode
========================

.. highlight:: console

For a simple script, pyarmor may reform the scripts automatically. In most of cases, it need extra configuration to make it works.

This chapter describes how RFT mode work, and how to solve issues for complex package and scripts.

What're RFT mode changed?

* function
* class
* method
* global variable
* local variable
* builtin name
* import name

What're RFT mode not changed?

* argument in function definition
* keyword argument name in call
* all the string names defined in the module attribute ``__all__``

It's simple to decide whether or not transform a single name, but it's difficult for each name in attribute chains. For example,

.. code-block:: python

    foo().stack[2].count = 3
    (a+b).tostr().get()

So how to handle attribute ``stack``, ``count``, ``tostr`` and ``get``? There are 2 methods for RFT mode to handle name in the attribute chains

- **rft-auto-exclude**

  This is default method.

  The idea is search all attribute chains in the scripts and analysis each name in the chain. If not sure it's safe to rename, add it to exclude table, and do not touch all the names in exclude table.

  It's simple to use, but may leave more names not changed.

- **rft-auto-include**

  This method first renames all the functions, classes and methods, add them to include table. If same name is used in attribute chains, but can't make sure its type, leave it but log it with format ``modname:lineno:attribute chains``.

  Then users manually analysis these logs, convert it to a ruler if it need to be renamed.

  This method could transform more names, but need more efforts to make the scripts work.

Enable RFT Mode
===============

Enable RFT mode in command line::

    $ pyarmor gen --enable-rft foo.py

Enabled by :command:`pyarmor cfg`::

    $ pyarmor cfg enable_rft=1
    $ pyarmor gen foo.py

Enable **rft-auto-include** method::

    $ pyarmor cfg rft_auto_exclude=0

Enable **rft-auto-exclude** method::

    $ pyarmor cfg rft_auto_exclude=1

Check transformed script

Trace rft log

Exclude name rule

Include name rule

Issues for ``from xxx impor *``

.. include:: ../_common_definitions.txt
