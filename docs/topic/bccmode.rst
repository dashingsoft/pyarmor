========================
Insight Into BCC Mode
========================

.. highlight:: console

.. program:: pyarmor gen

BCC mode could convert most of functions and methods in the scripts to equivalent C functions, those c functions will be compiled to machine instructions directly, then called by obfuscated scripts.

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

    $ ls pyarmor.trace.log
    $ grep trace.bcc pyarmor.trace.log

    trace.bcc            foo:5:hello
    trace.bcc            foo:9:sum2
    trace.bcc            foo:12:main

The first log means ``foo.py`` line 5 function ``hello`` is protected by bcc.
The second log means ``foo.py`` line 9 function ``sum2`` is protected by bcc.

If there is ``!`` after ``trace.bcc``, it means this function is ignored by BCC mode. For example::

    trace.bcc ! foo:29:Test.new (unsupported function "super")

Ignore module or function
=========================

When BCC scripts reports errors, a quick workaround is to ignore these problem modules or functions. Because BCC mode converts some functions to C code, these functions are not compatible with Python function object. They may not be called by outer Python scripts, and can't be fixed in Pyarmor side. In this case use configuration option ``bcc:excludes`` and ``bcc:disabled`` to ignore function or module, and make all the others work.

To ignore one module ``pkgname.modname`` by this command::

    $ pyarmor cfg -p pkgname.modname bcc:disabled=1

To ignore functions or class methods in one module::

    $ pyarmor cfg -p pkgname.modname bcc:excludes="name"
    $ pyarmor cfg -p pkgname.modname bcc:excludes="name1 name2 name3"

    $ pyarmor cfg -p pkgname.modname bcc:excludes="Class.method_1"
    $ pyarmor cfg -p pkgname.modname bcc:excludes="Class.*"

If no option ``-p``, same name function in the other scripts will be ignored too.

Here it's an example script :file:`foo.py`

.. code-block:: python

    def hello_a():
        pass

    def hello_b():
        pass

    class Test(object):

        def __init__(self):
            pass

        def hello_a():
            pass

Exclude functions by one of forms::

    $ pyarmor cfg -p foo bcc:excludes = "hello_a"
    $ pyarmor cfg -p foo bcc:excludes = "hello_a hello_b"
    $ pyarmor cfg -p foo bcc:excludes = "hello_*"

    $ pyarmor cfg -p foo bcc:excludes = "Test.hello_a"
    $ pyarmor cfg -p foo bcc:excludes = "Test.*"
    $ pyarmor cfg -p foo bcc:excludes = "Test.__*__"

    $ pyarmor cfg -p foo bcc:excludes = "hello_a Test.hello_a"

If want to BCC mode handle specified functions, use option `bcc:includes`::

    # clear excludes
    $ pyarmor cfg bcc:excludes = ""

    # BCC mode only handles module function "hello_a"
    $ pyarmor cfg -p foo bcc:includes = "hello_a"

    # Need extra settings let BCC mode handle class method "Test.hello_a"
    $ pyarmor cfg -p foo bcc:includes + "Test.hello_a"

    # BCC mode handles all methods of class "Test" except method "__init__"
    $ pyarmor cfg -p foo bcc:includes="Test.*" bcc:excludes="Test.__init__"

Let's enable trace mode to check these functions are ignored::

    $ pyarmor cfg enable_trace 1
    $ pyarmor gen --enable-bcc foo.py
    $ grep trace.bcc pyarmor.trace.log

Another example, in the following commands BCC mode ignores ``joker/card.py``, but handle all the other scripts in package ``joker``::

    $ pyarmor cfg -p joker.card bcc:disabled=1
    $ pyarmor gen --enable-bcc /path/to/pkg/joker

Both `bcc:includes` and `bcc:excludes` only work on top function and class method, they can't be used to filter nest function and methods of nest class.

For example,

.. code-block:: python

    def hello():

        def wrap():
            pass

        class Test:

            def __init__(self):
                pass

The nest function ``wrap`` and nest class ``Test`` can't be ignored by the following commands::

    pyarmor cfg bcc:excludes = "wrap hello.wrap Test.__init__ hello.Test.__init__"

The only solution is to ignore top function ``hello``::

    pyarmor cfg bcc:excludes = hello

.. versionadded:: 8.3.4

   The option `bcc:includes`.

.. versionchanged:: 8.3.4

   The option `bcc:excludes`, in previous version::

       # Exclude module function "hello_a" and any method "hello_a"
       pyarmor cfg bcc:excludes="hello_a"

       # It doesn't work if there is class name in filter
       pyarmor cfg bcc:excludes="Myclass.hello_a"

   Now::

       # Exclude module function "hello_a" and method "hello_a" in any class
       pyarmor cfg bcc:excludes="hello_a *.hello_a"

       # It works to ignore one method "Myclass.hello_a"
       pyarmor cfg bcc:excludes="Myclass.hello_a"

Changed features
================

Here are some changed features in the BCC mode:

* Calling `raise` without argument not in the exception handler will raise different exception.

.. code-block:: python

    >>> raise
    RuntimeError: No active exception to re-raise

    # In BCC mode
    >>> raise
    UnboundlocalError: local variable referenced before assignment

* Some exception messages may different from the plain script.

* Most of function attributes which starts with ``__`` doesn't exists, or the value is different from the original. For example, there is no `__qualname__` for BCC function.

* In the exception handler, `sys.exception()` will return `None`, so the functions depended on `sys.exception` may not work. For example

.. code-block:: python

    import traceback

    def main():
        try:
            1 / 0
        except Exception as e:

            # In BCC mode, sys.exception() will return None, the output is:
            #    None
            print(sys.exception())

            # It doesn't work in BCC mode, the output is "NoneType: None"
            traceback.print_exc()

            # The traceback will be printed by this form in BCC mode
            # But the traceback doesn't include line no. and source
            traceback.print_exception(e)

    main()

Unsupported features
====================

If a function uses any unsupported features, it could not be converted into C code.

Here list unsupported features for BCC mode:

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

And unsupported functions:

* exec
* eval
* super
* locals
* sys._getframe

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

Known issues
============

* When format string has syntax error, BCC mode may raise `SystemError: NULL object passed to Py_BuildValue`, instead of `SyntaxError` or `ValueError`.

  Found in test cases `lib/python3.12/test/test_fstring.py`:

  - test_invalid_syntax_error_message
  - test_missing_variable
  - test_syntax_error_for_starred_expressions
  - test_with_a_commas_and_an_underscore_in_format_specifier
  - test_with_an_underscore_and_a_comma_in_format_specifier
  - test_with_two_commas_in_format_specifier
  - test_with_two_underscore_in_format_specifier

* When generating BCC code, pyarmor may raise `RuntimeError: link bcc code failed`

  Try to add extra cflags `-DENABLE_BCC_MEMSET` for this platform. For example, use the following command for Windows X86::

      pyarmor cfg windows.x86.bcc:cflags += " -DENABLE_BCC_MEMSET"

  Or patch :file:`pyarmor/cli/default.cfg` directly, the final value should be like this::

      Section: windows.x86.bcc

      cflags = --target=i686-elf-linux -O3 -Wno-unsequenced -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-stack-protector -fPIC -mno-sse -std=c99 -c -DENABLE_BCC_MEMSET

.. include:: ../_common_definitions.txt
