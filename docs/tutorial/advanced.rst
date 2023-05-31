.. highlight:: console

====================
 Advanced Tutorial
====================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. program:: pyarmor gen

.. _using rftmode:

Using rftmode :sup:`pro`
========================

RFT mode could rename most of builtins, functions, classes, local variables. It equals rewriting scripts in source level.

Using :option:`--enable-rft` to enable RTF mode [#]_::

    $ pyarmor gen --enable-rft foo.py

For example, this script

.. code-block:: python
    :linenos:

    import sys

    def sum2(a, b):
        return a + b

    def main(msg):
        a = 2
        b = 6
        c = sum2(a, b)
        print('%s + %s = %d' % (a, b, c))

    if __name__ == '__main__':
        main('pass: %s' % data)

transform to

.. code-block:: python
    :linenos:

    pyarmor__17 = __assert_armored__(b'\x83\xda\x03sys')

    def pyarmor__22(a, b):
        return a + b

    def pyarmor__16(msg):
        pyarmor__23 = 2
        pyarmor__24 = 6
        pyarmor__25 = pyarmor__22(pyarmor__23, pyarmor__24)
        pyarmor__14('%s + %s = %d' % (pyarmor__23, pyarmor__24, pyarmor__25))

    if __name__ == '__main__':
        pyarmor__16('pass: %s' % pyarmor__20)

By default if RFT mode doesn't make sure this name could be changed, it will leave this name as it is.

RFT mode doesn't change names in the module attribute ``__all__``, it also doesn't change function arguments.

For example, this script

.. code-block:: python
    :emphasize-lines: 3,5,9

    import re

    __all__ = ['make_scanner']

    def py_make_scanner(context):
        parse_obj = context.parse_object
        parse_arr = context.parse_array

    make_scanner = py_make_scanner

transform to

.. code-block:: python
    :emphasize-lines: 3,5,9

    pyarmor__3 = __assert_armored__(b'\x83e\x9d')

    __all__ = ['make_scanner']

    def pyarmor__1(context):
        pyarmor__4 = context.parse_object
        pyarmor__5 = context.parse_array

    make_scanner = pyarmor__1

If want to know what're refactored exactly, enable trace rft to generate transformed script [#]_::

    $ pyarmor cfg trace_rft=1
    $ pyarmor gen --enable-rft foo.py

The transformed script will be stored in the path ``.pyarmor/rft``::

    $ cat .pyarmor/rft/foo.py

Now run the obfuscated script::

    $ python dist/foo.py

If something is wrong, try to obfuscate it again, it may make senses::

    $ pyarmor gen --enable-rft foo.py
    $ python dist/foo.py

If it still doesn't work, or you need transform more names, refer to :doc:`../topic/rftmode` to learn more usage.

.. [#] This feature is only available for :term:`Pyarmor Pro`.
.. [#] This feature only works for Python 3.9+

.. _using bccmode:

Using bccmode :sup:`pro`
========================

BCC mode could convert most of functions and methods in the scripts to equivalent C functions, those c functions will be compiled to machine instructions directly, then called by obfuscated scripts.

It requires ``c`` compiler. In Linux and Darwin, ``gcc`` and ``clang`` is OK. In Windows, only ``clang.exe`` works. It could be configured by one of these ways:

* If there is any ``clang.exe``, it's OK if it could be run in other path.
* Download and install Windows version of `LLVM <https://releases.llvm.org>`_
* Download `https://pyarmor.dashingsoft.com/downloads/tools/clang-9.0.zip`, it's about 26M bytes, there is only one file in it. Unzip it and save ``clang.exe`` to ``$HOME/.pyarmor/``. ``$HOME`` is home path of current logon user, check the environment variable ``HOME`` to get the real path.

After compiler works, using :option:`--enable-bcc` to enable BCC mode [#]_::

    $ pyarmor gen --enable-bcc foo.py

All the source in module level is not converted to C function.

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

When something is wrong, enable debug mode by common option ``-d``::

    $ pyarmor -d gen --enable-bcc foo.py

Check console log and trace log, most of cases there is modname and line no in console or trace log. Assume the problem function is ``sum2``, then tell BCC mode does not deal with it by this way::

    $ pyarmor cfg -p foo bcc:excludes "sum2"

Use ``-p`` to specify mod-name, and option ``bcc:excludes`` for function name.

Append more functions to exclude by this way::

    $ pyarmor cfg -p foo bcc:excludes + "hello"

When obfuscating package, it also could exclude one script separately. For example, the following commands tell BCC mode doesn't handle ``joker/card.py``, but all the other scripts in package ``joker`` are still handled by BCC mode::

    $ pyarmor cfg -p joker.card bcc:disabled=1
    $ pyarmor gen --enable-bcc /path/to/pkg/joker

It's possible that BCC mode could not support some Python features, in this case, use ``bcc:excludes`` and ``bcc:disabled`` to ignore them, and make all the others work.

If it still doesn't work, or you want to know more about BCC mode, goto :doc:`../topic/bccmode`.

.. [#] This feature is only available for :term:`Pyarmor Pro`.

Customization error handler
===========================

By default when something is wrong with obfuscated scripts, RuntimeError with traceback is printed::

    $ pyarmor gen -e 2020-05-05 foo.py
    $ python dist/foo.py

    Traceback (most recent call last):
      File "dist/foo.py", line 2, in <module>
        from pyarmor_runtime_000000 import __pyarmor__
      File "dist/pyarmor_runtime_000000/__init__.py", line 2, in <module>
        from .pyarmor_runtime import __pyarmor__
    RuntimeError: this license key is expired (1:10937)

If prefer to show error message only::

    $ pyarmor cfg on_error=1

    $ pyarmor gen -e 2020-05-05 foo.py
    $ python dist/foo.py

    this license key is expired (1:10937)

If prefer to quit directly without any message::

    $ pyarmor cfg on_error=2

    $ pyarmor gen -e 2020-05-05 foo.py
    $ python dist/foo.py

    $

Restore the default handler::

    $ pyarmor cfg on_error=0

Or reset this option::

    $ pyarmor cfg --reset on_error

.. note::

   This only works for execute the obfuscated scripts by Python interpreter directly. If :option:`--pack` is used, the script is loaded by `PyInstaller`_ loader, it may not work as expected.

Filter mix string
=================

By default :option:`--mix-str` encrypts all the string length > 8.

But it can be configured to filter any string to meet various needs.

Exclude short strings by length < 10::

    $ pyarmor cfg mix.str:threshold 10

Exclude any string by regular expression with format ``/pattern/``, the pattern syntax is same as module :mod:`re`. For example, exclude all strings length > 1000::

    $ pyarmor cfg mix.str:excludes "/.{1000,}/"

Append new ruler to exclude 2 words ``__main__`` and ``xyz``::

    $ pyarmor cfg mix.str:excludes ^ "__main__ xyz"

Reset exclude ruler::

    $ pyarmor cfg mix.str:excludes = ""

Encrypt only string length between 8 and 32 by regular expression::

    $ pyarmor cfg mix.str:includes = "/.{8,32}/"

Check trace log to find which strings are protected.

Filter assert function and import
=================================

:option:`--assert-call` and :option:`--assert-import` could protect function and module, but sometimes it may make mistakes.

One case is that pyarmor asserts a third-party function is obfuscated, thus the obfuscated scripts always raise protection error.

Adding an assert rule to fix this problem. For example, tell :option:`--assert-import` ignore module ``json`` and ``inspect`` by word list::

    $ pyarmor cfg assert.import:excludes = "json inspect"

Tell :option:`--assert-call` ignore all the function starts with ``wintype_`` by regular expression::

    $ pyarmor cfg assert.call:excludes "/wintype_.*/"

The other case is that some functions or modules are obfuscated, but pyarmor doesn't protect them. refer to next section `Patching source by inline marker`_ to fix this issue.

Patching source by inline marker
================================

Before obfuscating a script, Pyarmor scans each line, remove inline marker plus the following one white space, leave the rest as it is.

The default inline marker is ``# pyarmor:``, any comment line with this prefix will be as a inline marker.

For example, these lines

.. code-block:: python
    :emphasize-lines: 3,4

    print('start ...')

    # pyarmor: print('this script is obfuscated')
    # pyarmor: check_something()

will be changed to

.. code-block:: python
    :emphasize-lines: 3,4

    print('start ...')

    print('this script is obfuscated')
    check_something()

One real case: protecting hidden imported modules

By default :option:`--assert-import` could only protect modules imported by statement ``import``, it doesn't handle modules imported by other methods.

For example,

.. code-block:: python

    m = __import__('abc')

In obfuscated script, there is a builtin function :func:`__assert_armored__` could be used to check ``m`` is obfuscated. In order to make sure ``m`` could not be replaced by others, check it manually:

.. code-block:: python

    m = __import__('abc')
    __assert_armored__(m)


But this results in a problem, The plain script could not be run because ``__assert_armored__`` is only available in the obfuscated script.

The inline marker is right solution for this case. Let's make a little change

.. code-block:: python
    :emphasize-lines: 2

    m = __import__('abc')
    # pyarmor: __assert_armored__(m)

By inline marker, both the plain script and the obfuscated script work as expected.

Sometimes :option:`--assert-call` may miss some functions, in this case, using inline marker to protect them. Here is an example to protect extra function ``self.foo.meth``:

.. code-block:: python
    :emphasize-lines: 2

    # pyarmor: __assert_armored__(self.foo.meth)
    self.foo.meth(x, y, z)

Internationalization runtime error message
==========================================

Create :file:`messages.cfg` in the path :file:`.pyarmor`::

    $ mkdir .pyarmor
    $ vi .pyarmor/message.cfg

It's a ``.ini`` format file, add a section ``runtime.message`` with option ``languages``. The language code is same as environment variable ``LANG``, assume we plan to support 2 languages, and only customize 2 errors:

* error_1: license is expired
* error_2: license is not for this machine

.. code:: ini

  [runtime.message]

  languages = zh_CN zh_TW

  error_1 = invalid license
  error_2 = invalid license

``invalid license`` is default message for any non-matched language.

Now add 2 extra sections ``runtime.message.zh_CN`` and ``runtime.message.zh_TW``

.. code:: ini

  [runtime.message]

  languages = zh_CN zh_TW

  error_1 = invalid license
  error_2 = invalid license

  [runtime.message.zh_CN]

  error_1 = 脚本超期
  error_2 = 未授权设备

  [runtime.message.zh_TW]

  error_1 = 腳本許可證已經過期
  error_2 = 腳本許可證不可用於當前設備

Then obfuscate script again to make it works.

When obfuscated scripts start, it checks :envvar:`LANG` to get current language code. If this language code is not ``zh_CN`` or ``zh_TW``, default message is used.

:envvar:`PYARMOR_LANG` could force the obfuscated scripts to use specified language. If it's set, the obfuscated scripts ignore :envvar:`LANG`. For example, force the obfuscated script ``dist/foo.py`` to use lang ``zh_TW`` by this way::

    export PYARMOR_LANG=zh_TW
    python dist/foo.py

Generating cross platform scripts
=================================

.. versionadded:: 8.1

Here list all the standard :term:`platform` names.

In order to generate scripts for other platform, use :option:`--platform` specify target platform. For example, building scripts for windows.x86_64 in Darwin::

    $ pyarmor gen --platform windows.x86_64 foo.py

:mod:`pyarmor.cli.runtime` provides prebuilt binaries for these platforms. If it's not installed, pyarmor may complain of ``cross platform need pyarmor.cli.runtime, please run "pip install pyarmor.cli.runtime~=2.1.0" first``. Following the hint to install pyarmor.cli.runtime with the right version.


Using :option:`--platform` multiple times to support multiple platforms. For example, generate the scripts to run in most of x86_64 platforms::

    $ pyarmor gen --platform windows.x86_64
                  --platform linux.x86_64 \
                  --platform darwin.x86_64 \
                  foo.py

Obfuscating scripts for multiple Python versions
================================================

.. versionadded:: 8.3

This guide how to obfuscate the script `foo.py` which works with both Python 3.8 and 3.9.

First install Pyarmor for each Python version::

    $ python3.8 -m pip install pyarmor
    $ python3.9 -m pip install pyarmor

If you have Pyarmor license, register Pyarmor by any Python version::

    $ python3.8 -m pyarmor.cli reg pyarmor-regfile-xxxx.zip

Enable builtin plugin ``MultiPythonPlugin``::

    $ python3.8 -m pyarmor.cli cfg plugins + "MultiPythonPlugin"

Obfuscate the script to different output path by each Python version::

    $ python3.8 -m pyarmor.cli gen -O dist1 foo.py
    $ python3.9 -m pyarmor.cli gen -O dist2 foo.py

Then merge 2 output paths by any Python version::

    $ python3.8 -m pyarmor.cli.merge -O dist dist1 dist2

The final output path is ``dist``::

    $ python3.8 dist/foo.py
    $ python3.9 dist/foo.py

.. include:: ../_common_definitions.txt
