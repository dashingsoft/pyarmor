========================
Insight Into BCC Mode
========================

.. highlight:: console

.. program:: pyarmor gen

BCC mode could convert most of functions and methods in the scripts to equivalent C functions, those c functions will be comipled to machine instructions directly, then called by obfuscated scripts.

When BCC scripts reports errors, a quick workaround is to ignore these problem functions. In many cases, this kind of problem can't be fixed. Because BCC mode converts some functions to C code, these funtions are not compatiable with Python function object. So they may not work when called by outer Python scripts.

It requires ``c`` compiler. In Linux and Darwin, ``gcc`` and ``clang`` is OK. In Windows, only ``clang.exe`` works. It could be configured by one of these ways:

* If there is any ``clang.exe``, it's OK if it could be run in other path.
* Download and install Windows version of `LLVM <https://releases.llvm.org>`_
* Download `https://pyarmor.dashingsoft.com/downloads/tools/clang-9.0.zip`, it's about 26M bytes, there is only one file in it. Unzip it and save ``clang.exe`` to ``$HOME/.pyarmor/``. ``$HOME`` is home path of current logon user, check the environment variable ``HOME`` to get the real path.

Enable BCC mode
===============

After compiler works, using :option:`--enable-bcc` to enable BCC mode::

    $ pyarmor gen --enable-bcc foo.py

All the source in module level is not converted to C function.

Trace bcc log
=============

To check which functions are converted to C function, enable trace mode before obfuscate the script::

    $ pyarmor cfg enable_trace=1
    $ pyarmor gen --enable-bcc foo.py

Then check the trace log::

    $ ls .pyarmor/pyarmor.trace.log
    $ grep trace.bcc .pyarmor/pyarmor.trace.log

    trace.bcc            foo:5:hello
    trace.bcc            foo:9:sum2
    trace.bcc            foo:12:main

The first log means ``foo.py`` line 5 function ``hello`` is protected by bcc.
The second log means ``foo.py`` line 9 function ``sum2`` is protected by bcc.

Ignore module or function
=========================

When something is wrong, enable debug mode by common option ``-d``::

    $ pyarmor -d gen --enable-bcc foo.py

Check console log and trace log, most of cases there is modname and lineno in console or trace log. Assume the problem funtion is ``sum2``, then tell BCC mode does not deal with it by this way::

    $ pyarmor cfg -p foo bcc:excludes="sum2"

Use ``-p`` to specify modname, and option ``bcc:excludes`` for function name.

In order to exclude more functions, list all of them in the excludes::

    $ pyarmor cfg -p foo bcc:excludes="sum2 hello"

When obfuscating package, it also could exclude one script seperataly. For example, the following commands tell BCC mode doesn't handle ``joker/card.py``, but all the other scripts in package ``joker`` are still handled by BCC mode::

    $ pyarmor cfg -p joker.card bcc:disabled=1
    $ pyarmor gen --enable-bcc /path/to/pkg/joker

It's possible that BCC mode could not support some Python features, in this case, use ``bcc:excludes`` and ``bcc:disabled`` to ignore them, and make all the others work.

Changed features
================

Here are some changed features in the BCC mode:

* Calling `raise` without argument not in the exception handler will raise different exception.

.. code-block:: python

    >>> raise
    RuntimeError: No active exception to reraise

    # In BCC mode
    >>> raise
    UnboundlocalError: local variable referenced before assignment

* Some exception messages may different from the plain script.

* Most of function attributes which starts with ``__`` doesn't exists, or the value is different from the original.

Unsupport features
==================

If a function uses any unsupoported features, it could not be converted into C code.

Here list unsupport features for BCC mode:

.. code-block:: python

    unsupport_nodes = (
        ast.ExtSlice,

        ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith,
        ast.Await, ast.Yield, ast.YieldFrom, ast.GeneratorExp,

        ast.NamedExpr,

        ast.MatchValue, ast.MatchSingleton, ast.MatchSequence,
        ast.MatchMapping, ast.MatchClass, ast.MatchStar,
        ast.MatchAs, ast.MatchOr
    )

And unsupport functions:

* exec,
* eval
* super
* locals
* sys._getframe
* sys.exc_info

For example, the following functions are not obfuscated by BCC mode, because they use unsupported features or unsupported functions:

.. code-block:: python

   async def nested():
       return 42

   def foo1():
       for n range(10):
           yield n

   def foo2():
      frame = sys._getframe(2)
      print('parent frame is', frame)

.. include:: ../_common_definitions.txt
