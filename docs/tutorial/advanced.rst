.. highlight:: console

====================
 Advanced Tutorial
====================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. program:: pyarmor gen

Filter mix string
=================

Exclude short strings by length < 10::

    $ pyarmor cfg mix.str:threshold 10

Exclude any string startswith and endswith ``__`` by regular expression::

    $ pyarmor cfg mix.str:excludes "/__.*__/"

Append new ruler to exclude exact words::

    $ pyarmor cfg mix.str:excludes ^ "main xyz"

Reset exclude ruler::

    $ pyarmor cfg mix.str:excludes = ""

Encrypt only string length between 8 and 32 by regular expression::

    $ pyarmor cfg mix.str:includes = "/.{8,32}/"

Check trace log to find which strings are protected.

Filter assert function and import
=================================

Do not protect function::

    $ pyarmor cfg assert.call:excludes "fa fb"

Do not protect module::

    $ pyarmor cfg assert.import:excludes "ma mb"

Protect extra module or function by inline marker, refer to section `Patching source by inline marker`_

.. _using rftmode:

Using rftmode :sup:`pro`
========================

RFT mode could rename most of builints, functions, classes, local variables. It equals rewritting scripts in source level.

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

For a simple script, Pyarmor may transform the script automatically. In most of cases, it need add some rulers manually to make refactor works.

When something is wrong, first enable trace mode::

    $ pyarmor cfg enable_trace=1 trace_rft=1

Then run::

    $ pyarmor gen --enable-rft foo.py

Trace mdoe could generate the result script in the path ``.pyarmor/rft``::

    $ cat .pyarmor/rft/foo.py

And also generate trace log ``.pyarmor/pyarmor.trace.log``::

    $ cat .pyarmor/pyarmor.trace.log

There are 2 kinds of rft log::

    $ grep trace.rft .pyarmor/pyarmor.trace.log

    trace.rft            alec.t1090:32 (! self.dwFlags)
    trace.rft            alec.t1090:80 (self.width->self.pyarmor__21)

The first log says in the ``alec/t1090.py``, at line 32 ``self.dwFlags`` isn't changed.

The second log says at line 80 ``self.width`` transforms to ``self.pyarmor__21``

Now run the obfuscated script again::

    $ python dist/foo.py

If RFT script complains of name not found error, just exclude this name. For example, if no found name ``mouse_keybd``, exclude this name by this command::

    $ pyarmor cfg rft_excludes "mouse_keybd"

If no found name like ``pyarmor__22``, find the original name in the trace log::

    $ grep pyarmor__22 .pyarmor/pyarmor.trace.log

    trace.rft            alec.t1090:65 (self.height->self.pyarmor__22)
    trace.rft            alec.t1090:81 (self.height->self.pyarmor__22)

From search result, we know ``height`` is the source of ``pyarmor__22``, let's append it to exclude table::

    $ pyarmor cfg rft_excludes +"height"

Test it again::

    $ pyarmor gen --enable-rft foo.py
    $ python dist/foo.py

Repeat these steps to exclude all the problem names, until it works.

If it still doesn't work, or you need transform more names, refer to :doc:`../topic/rftmode` to learn more usage.

.. [#] This feature is only available for :term:`Pyarmor Pro`.

.. _using bccmode:

Using bccmode :sup:`pro`
========================

BCC mode could convert most of functions and methods in the scripts to equivalent C functions, those c functions will be comipled to machine instructions directly, then called by obfuscated scripts.

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

Check console log and trace log, most of cases there is modname and lineno in console or trace log. Assume the problem funtion is ``sum2``, then tell BCC mode does not deal with it by this way::

    $ pyarmor cfg -p foo bcc:excludes="sum2"

Use ``-p`` to specify modname, and option ``bcc:excludes`` for function name.

In order to exclude more functions, list all of them in the excludes::

    $ pyarmor cfg -p foo bcc:excludes="sum2 hello"

When obfuscating package, it also could exclude one script seperataly. For example, the following commands tell BCC mode doesn't handle ``joker/card.py``, but all the other scripts in package ``joker`` are still handled by BCC mode::

    $ pyarmor cfg -p joker.card bcc:disabled=1
    $ pyarmor gen --enable-bcc /path/to/pkg/joker

It's possible that BCC mode could not support some Python features, in this case, use ``bcc:excludes`` and ``bcc:disabled`` to ignore them, and make all the others work.

If it still doesn't work, or you want to know more about BCC mode, goto :doc:`../topic/bccmode`.

.. [#] This feature is only available for :term:`Pyarmor Pro`.

Customization error handler
===========================

By default when something is wrong with obfuscated scripts, a RuntimeError with error message is raised.

If prefer to show error message only::

    $ pyarmor cfg on_error=1

If prefer to quit directly without any message::

    $ pyarmor cfg on_error=2

Restore the default handler::

    $ pyarmor cfg on_error=0

Or reset this option::

    $ pyarmor cfg --reset on_error

After the option is changed, obfuscating the script again to make it effects.

Patching source by inline marker
================================

Before obfuscating a script, Pyarmor scans each line, remove inline marker plus the following one whitespace, leave the rest as it is.

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

In obfuscated script, there is a builtin function ``__assert_armored__`` could be used to check ``m`` is obfuscated. In order to make sure ``m`` could not be replaced by others, check it manually:

.. code-block:: python

    m = __import__('abc')
    __assert_armored__(m)


But this results in a problem, The plain script could not be run because ``__assert_armored__`` is only available in the obfuscated script.

The inline marker is right solution for this case. Let's make a little change

.. code-block:: python
    :emphasize-lines: 2

    m = __import__('abc')
    # pyarmor: __assert_armored__(m)

By inline marker, both the plain script and the obfsucated script work as expected.

Sometimes :option:`--assert-call` may miss some functions, in this case, using inline marker to protect them. Here is an example to protect extra function ``self.foo.meth``:

.. code-block:: python
    :emphasize-lines: 2

    # pyarmor: __assert_armored__(self.foo.meth)
    self.foo.meth(x, y, z)


Using plugins
=============

.. versionadded:: 8.x
                  This feature is still not implemented

Plugin is used in generating obfuscated scripts.

It may do some pre-build or post-build work.

TODO

Using hooks
===========

.. versionadded:: 8.x
                  This feature is still not implemented

Hook is used when running obfuscated scripts, it mainly does some special protection work.

A hook is a Python script called at

* boot: when importing the runtime package :mod:`pyarmor_runtime`
* period: only called when runtime key is in period mode
* import: when imporing an obfuscated module

TODO

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

:mod:`pyarmor.cli.runtime` provides prebuilt binaries for these platforms. If it's not installed, pyarmor may complain of ``cross platform need pyarmor.cli.runtime, please run "pip install pyarmor.cli.runtime==2.1" first``. Following the hint to install pyarmor.cli.runtime with the right version.


Using :option:`--platform` multiple times to support multiple platforms. For example, the command could generate the scripts to run in most of x86_64 platforms::

    $ pyarmor gen --platform windows.x86_64
                  --platform linux.x86_64 \
                  --platform darwin.x86_64 \
                  foo.py

Obfuscating scripts for multiple Pythons
========================================

.. versionadded:: 8.x
                  This feature is still not implemented

Use helper script `merge.py`

TODO

.. include:: ../_common_definitions.txt
