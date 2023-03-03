.. highlight:: console

====================
 Advanced Tutorials
====================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

Using rftmode :sup:`pro`
========================

RFT mode could rename most of builints, functions, classes, local
variables. It equals rewritting scripts in source level.

For example, the following Python script

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

will be reformed to

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

Using :option:`--enable-rft` to enable RTF mode::

    $ pyarmor gen --enable-rft foo.py

This feature is only available for :term:`Pyarmor Pro`.

Using bccmode :sup:`pro`
========================

BCC mode could convert most of functions and methods in the scripts to
equivalent C functions, those c functions will be comipled to machine
instructions directly, then called by obfuscated scripts.

Note that the code in model level is not converted to C function.

Using :option:`--enable-bcc` to enable BCC mode::

    $ pyarmor gen --enable-bcc foo.py

This feature is only available for :term:`Pyarmor Pro`.

Customization error handler
===========================

By default when something is wrong with obfuscated scripts, a RuntimeError with
error message is raised.

If prefer to show error message only::

    $ pyarmor cfg on_error=1

If prefer to quit directly without any message::

    $ pyarmor cfg on_error=2

Restore the default handler::

    $ pyarmor cfg on_error=0

Or reset this option::

    $ pyarmor cfg --reset on_error

After the option is changed, obfuscating the script again to make it effects.

Patching source by plugin marker
================================

Before obfuscating a script, Pyarmor scans each line, remove plugin marker plus
the following one whitespace, leave the rest as it is.

The default plugin marker is ``# pyarmor:``, any comment line with this prefix
will be as a plugin marker.

For example, these lines

.. code-block:: python
    :emphasize lines: 3,4

    print('start ...')

    # pyarmor: print('this is plugin code')
    # pyarmor: check_something()

will be changed to

.. code-block:: python
    :emphasize lines: 3,4

    print('start ...')

    print('this is plugin code')
    check_something()

One real case: protecting hidden imported modules

By default :option:`--assert-import` could only protect modules imported by
statement ``import``, it doesn't handle modules imported by other methods.

For example,

.. code-block:: python

    m = __import__('abc')

In obfuscated script, there is a builtin function ``__assert_armored__`` could
be used to check ``m`` is obfuscated. In order to make sure ``m`` could not be
replaced by others, check it manually:

.. code-block:: python

    m = __import__('abc')
    __assert_armored__(m)


But this results in a problem, The plain script could not be run because
``__assert_armored__`` is only available in the obfuscated script.

The plugin marker is right solution for this case. Let's make a little change

.. code-block:: python
                :emphasize lines: 2

    m = __import__('abc')
    # pyarmor: __assert_armored__(m)

By plugin marker, both the plain script and the obfsucated script work as
expected.

Using hooks
===========

.. versionadded:: 8.1
                  This feature is not implemented in 8.0

Hooks is used to do some extra checks when running obfuscated scripts.

A hook is a Python script called in any of

* boot: when importing the runtime package :mod:`pyarmor_runtime`
* period: only called when runtime key is in period mode
* import: when imporing an obfuscated module

An example of hook script :file:`hook.py`

.. code:: python

    {
       'boot': '''def boot_hook(*args):
       print('hello, boot hook')''',

       'import': '''def import_hook(*args):
       print('hello, import hook')''',

       'period': '''def period_hook(*args):
       print('hello, period hook')''',
    }

Save it to global or local configuration path

Internationalization runtime error message
==========================================

Create :file:`messages.cfg` in the path :file:`.pyarmor`::

    $ mkdir .pyarmor
    $ vi .pyarmor/message.cfg

It's a ``.ini`` format file, add a section ``runtime.message`` with option
``languages``. The language code is same as environment variable ``LANG``,
assume we plan to support 2 languages, and only customize 2 errors:

* error_1: license is expired
* error_2: license is not for this machine

.. code:: ini

  [runtime.message]

  languages = zh_CN zh_TW

  error_1 = invalid license
  error_2 = invalid license

error_1 and error_2 is default message for any non-matched language.

Now add 2 extra sections ``runtime.message.zh_CN`` and ``runtime.message.zh_TW``

.. code:: ini

  [runtime.message.zh_CN]

  error_1 = 脚本超期
  error_2 = 未授权设备

  [runtime.message.zh_TW]

  error_1 = 腳本許可證已經過期
  error_2 = 腳本許可證不可用於當前設備

Then obfuscate script again to make it works.

:envvar:`PYARMOR_LANG` could be used to set runtime language. If it's set, the
obfuscated scripts ignore :envvar:`LANG`.

Generating cross platform scripts
=================================

.. versionadded:: 8.1
                  This feature is not implemented in 8.0

Use :option:`--platform`

Obfuscating scripts for multiple Pythons
========================================

.. versionadded:: 8.1
                  This feature is not implemented in 8.0

Use helper script `merge.py`

.. include:: ../_common_definitions.txt
