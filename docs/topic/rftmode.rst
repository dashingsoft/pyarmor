========================
Insight Into RFT Mode
========================

.. highlight:: console

For a simple script, pyarmor may reform the scripts automatically. In most of cases, it need extra work to make it works.

This chapter describes how RFT mode work, it's helpful to solve RFT mode issues of complex package and scripts.

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
* all the strings defined in the module attribute ``__all__``
* all the name startswith ``__``

It's simple to decide whether or not transform a single name, but it's difficult for each name in attribute chains. For example,

.. code-block:: python

    foo().stack[2].count = 3
    (a+b).tostr().get()

So how to handle attribute ``stack``, ``count``, ``tostr`` and ``get``? The problem is that it's impossible to confirm function return type or expression result type.In some cases, it may be valid to return different types with different arguments.

There are 2 methods for RFT mode to handle name in the attribute chains which don't know parent type.

- **rft-auto-exclude**

  This is default method.

  The idea is search all attribute chains in the scripts and analysis each name in the chain. If not sure it's safe to rename, add it to exclude table, and do not touch all the names in exclude table.

  By default the file ``.pyarmor/rft_exclude_table`` is used to store exclude table.

  When pyarmor rft mode first run, exclude table is empty. It scans each script and append unknown names to exclude table. After all the scripts are obfuscated, it stores all the names in the exclude table to the file ``.pyarmor/rft_exclude_table``.

  RFT mode doesn't remove this file, only append new names to it repeatly, please delete it manually when needed.

  When second run rft mode, it loads exclude table from ``.pyarmor/rft_exclude_table``. Comparing with the first time exclude table is empty, obviously the second time more names are kept, it may fix some name errors.

  It's simple to use, but may leave more names not changed.

- **rft-auto-include**

  This method first search all the functions, classes and methods in the scripts, add them to include table, and transform all of them. If same name is used in attribute chains, but can't make sure its type, leave attribute name as it is.

  For a simple script, Pyarmor could transform the script automatically. But for a complex script, it may raise name binding error. For example::

    $ python dist/foo.py

    AttributeError: module 'foo' has no attribute 'register_namespace'

  In order to fix this proble, exclude the problem name, leave it as it is by this way::

    $ pyarmor cfg rft_excludes + "register_namespace"
    $ pyarmor gen --enable-rft foo.py
    $ python dist/foo.py

  Repeat these steps to exclude all problem names, until it works.

  This method could transform more names, but need more efforts to make the scripts work.

Enable RFT Mode
===============

Enable RFT mode in command line::

    $ pyarmor gen --enable-rft foo.py

Enable it by :command:`pyarmor cfg`::

    $ pyarmor cfg enable_rft=1
    $ pyarmor gen foo.py

Enable **rft-auto-include** method by disable ``rft_auto_exclude``::

    $ pyarmor cfg rft_auto_exclude=0

Enable **rft-auto-exclude** method again::

    $ pyarmor cfg rft_auto_exclude=1

Check transformed script
========================

When trace rft mode is enabled, RFT mode will generate transformed script in the path ``.pyarmor/rft`` with full package name::

    $ pyarmor cfg trace_rft 1
    $ pyarmor gen --enable-rft foo.py
    $ ls .pyarmor/rft

Check the transformed script::

    $ cat .pyarmor/rft/foo.py

.. note::

   This feature only works for Python 3.9+

Trace rft log
=============

When both of trace log and trace rft are enabled, RFT mode will log which names and attributes are transformed::

    $ pyarmor cfg enable_trace=1 trace_rft=1
    $ pyarmor gen --enable-rft foo.py
    $ grep trace.rft .pyarmor/pyarmor.trace.log

    trace.rft            foo:1 (import sys as pyarmor__1)
    trace.rft            foo:12 (self.wScan->self.pyarmor__4)

The first log means module ``sys`` is transformed to ``pyarmor__1``

The second log means ``wScan`` is transformed to ``pyarmor__4``

Exclude name rule
=================

When RFT scripts complain of name not found error, just exclude this name. For example, if no found name ``mouse_keybd``, exclude this name by this command::

    $ pyarmor cfg rft_excludes "mouse_keybd"
    $ pyarmor gen --enable-rft foo.py

If no found name like ``pyarmor__22``, find the original name in the trace log::

    $ grep pyarmor__22 .pyarmor/pyarmor.trace.log

    trace.rft            foo:65 (self.height->self.pyarmor__22)
    trace.rft            foo:81 (self.height->self.pyarmor__22)

From search result, we know ``height`` is the source of ``pyarmor__22``, let's append it to exclude table::

    $ pyarmor cfg rft_excludes + "height"
    $ pyarmor gen --enable-rft foo.py
    $ python dist/foo.py

Repleat these step until all the problem names are excluded.

Handle wild card form of import
===============================

The wild card form of import — `from module import *` — is a special case.

If this module is in the obfuscated pakcage, RFT mode will parse the source and check the module’s namespace for a variable named ``__all__``

If this module is outer package, RFT mode could not get the source. So RFT mode will import it and query module attribute ``__all__``. If this module could not be imported, it may raise ``ModuleNotFoundError``, please set :envvar:`PYTHONPATH` or any otherway let Python could import this module.

If ``__all__`` is not defined, the set of public names includes all names found in the module’s namespace which do not begin with an underscore character ('_').

Handle module attribute ``__all__``
===================================

By default RFT mode doesn't touch all the names in the module ``__all__``. If this name is defined as a Class, its methods and attributes are not changed.

It's possible to ignore this attribute by this command::

    $ pyarmor cfg rft_export__all__ 0

It will transform names in the ``__all__``, but it may not work if it's imported by other scripts.

.. include:: ../_common_definitions.txt

..
    Include name rule
    =================

    This is only for **rft-auto-include**

    The rule is used to transform name in chain attributes

    One line one rule, the rule format::

        patterns actions

        patterns = pattern1.pattern2.pattern3...
        actions = [%?].[%?].[%?]...

    Each pattern is same as pattern in :mod:`fnmatch`, each action is char ``?`` or ``%``. ``%`` means no transform, ``?`` means transform the corresponding attribute.

    For example, a ruler::

        self.task.x %.%.?

    apply to this script

    .. code-block:: python
        :linenos:
        :emphasize-lines: 8,9

        class Sdipmk:

            def __init__(self):
                self.width = 100
                self.height = 200

            def move(self, x, y, absolute=False):
                self.task.x = int(abs(x*65536/self.width)) if absolute else int(x)
                self.task.y = int(abs(y*65536/self.height)) if absolute else int(y)
                return Mouse(MS_MOVE, x, y)

    First configure this ruler by command::

        $ pyarmor cfg rft_rulers "self.task.x %.%.?"

    Then check the result::

        $ pyarmor gen --enable-rft foo.py
        $ grep trace.rft .pyarmor/pyarmor.trace.log

        trace.rft            foo:8 (self.task.x->self.task.pyarmor__2)

    line 8 ``self.task.x`` will be transformed to ``self.task.pyarmor__2``

    Let's change action to ``%.?.?``, and check the result::

        $ pyarmor cfg rft_rulers "self.task.x %.?.?"
        $ grep trace.rft .pyarmor/pyarmor.trace.log

        trace.rft            foo:8 (self.task.x->self.pyarmor__1.pyarmor__2)

    Do not change action to ``?.?.?``, it doesn't work, the first action can't be ``?``

    Let's add new ruler to change ``self.task.y``, here need to use ``^`` to append new line to rulers::

        $ pyarmor cfg rft_rulers ^"self.task.y %.?.?"
        $ grep trace.rft .pyarmor/pyarmor.trace.log

        trace.rft            foo:8 (self.task.x->self.pyarmor__1.pyarmor__2)
        trace.rft            foo:9 (self.task.y->self.pyarmor__1.pyarmor__3)

    Actually, both of rulers can combined to one::

        $ pyarmor cfg rft_rulers = "self.task.* %.?.?"
        $ grep trace.rft .pyarmor/pyarmor.trace.log

        trace.rft            foo:8 (self.task.x->self.pyarmor__1.pyarmor__2)
        trace.rft            foo:9 (self.task.y->self.pyarmor__1.pyarmor__3)
