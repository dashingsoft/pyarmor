========================
Insight Into RFT Mode
========================

.. highlight:: console

For a simple script, pyarmor may reform the scripts automatically. In most of cases, it need extra work to make it works.

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
* all the strings defined in the module attribute ``__all__``

It's simple to decide whether or not transform a single name, but it's difficult for each name in attribute chains. For example,

.. code-block:: python

    foo().stack[2].count = 3
    (a+b).tostr().get()

So how to handle attribute ``stack``, ``count``, ``tostr`` and ``get``? The problem is that it's impossible to confirm function return type or expression result type.In some cases, it may be valid to return different types with different arguments.

There are 2 methods for RFT mode to handle name in the attribute chains which don't know parent type.

- **rft-auto-exclude**

  This is default method.

  The idea is search all attribute chains in the scripts and analysis each name in the chain. If not sure it's safe to rename, add it to exclude table, and do not touch all the names in exclude table.

  It's simple to use, but may leave more names not changed.

- **rft-auto-include**

  This method first search all the functions, classes and methods in the scripts, add them to include table, and transform all of them. If same name is used in attribute chains, but can't make sure its type, leave attribute name as it is, but log it with format ``modname:lineno:chains``.

  Then users manually analysis these logs, convert it to a ruler if it need to be renamed.

  This method could transform more names, but need more efforts to make the scripts work.

Enable RFT Mode
===============

Enable RFT mode in command line::

    $ pyarmor gen --enable-rft foo.py

Enabled by :command:`pyarmor cfg`::

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

Trace rft log
=============

When both of trace log and trace rft are enabled, RFT mode will log how to deal with attributes::

    $ pyarmor cfg enable_trace=1 trace_rft=1
    $ pyarmor gen --enable-rft foo.py
    $ grep trace.rft .pyarmor/pyarmor.trace.log

    trace.rft            alec.t1090:32 (! self.dwFlags)
    trace.rft            alec.t1090:33 (self.wScan->self.pyarmor__4)

The first log starts with ``!`` means no transform ``self.dwFlags``

The second log means ``self.wScan`` is transfrormed to ``self.pyarmor__4``

Enable debug mode could generate more trace log::

    $ pyarmor -d gen --enable-rft foo.py
    $ grep trace.rft .pyarmor/pyarmor.trace.log

    ...
    trace.rft            alec.t1090:15 (exclude "wintypes LONG")
    ...

This log starts with ``exclude`` means 2 words ``wintypes`` and ``LONG`` are excluded by refactor, do not touch them in all the attribute chains.

Exclude name rule
=================

When RFT scripts complain of name not found error, just exclude this name. For example, if no found name ``mouse_keybd``, exclude this name by this command::

    $ pyarmor cfg rft_excludes "mouse_keybd"
    $ pyarmor gen --enable-rft foo.py

If no found name like ``pyarmor__22``, find the original name in the trace log::

    $ grep pyarmor__22 .pyarmor/pyarmor.trace.log

    trace.rft            alec.t1090:65 (self.height->self.pyarmor__22)
    trace.rft            alec.t1090:81 (self.height->self.pyarmor__22)

From search result, we know ``height`` is the source of ``pyarmor__22``, let's append it to exclude table::

    $ pyarmor cfg rft_excludes +"height"
    $ pyarmor gen --enable-rft foo.py
    $ python dist/foo.py

Repleat these step until all the problem names are excluded.

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

Special for wild card form of import
====================================

The wild card form of import — `from module import *` — is a special case.

If this module is in the obfuscated pakcage, RFT mode will parse the source and check the module’s namespace for a variable named ``__all__``

If this module is outer package, RFT mode could not get the source. So RFT mode will import it and query module attribute ``__all__``. If this module could not be imported, it may raise ``ModuleNotFoundError``, please set :envvar:`PYTHONPATH` or any otherway let Python could import this module.

If ``__all__`` is not defined, the set of public names includes all names found in the module’s namespace which do not begin with an underscore character ('_').

.. include:: ../_common_definitions.txt
