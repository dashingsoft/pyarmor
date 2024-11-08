===================
 Basic Tutorial
===================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor

We'll assume you have Pyarmor 8.0+ installed already. You can tell Pyarmor is installed and which version by running the following command in a shell prompt (indicated by the $ prefix)::

    $ pyarmor --version

If Pyarmor is installed, you should see the version of your installation. If it isn't, you'll get an error.

This tutorial is written for Pyarmor 8.0+, which supports Python 3.7 and later. If the Pyarmor version doesn't match, you can refer to the tutorial for your version of Pyarmor by using the version switcher at the bottom right corner of this page, or update Pyarmor to the newest version.

Throughout this tutorial, assume run :command:`pyarmor` in project path which includes::

    project/
        ├── foo.py
        ├── queens.py
        └── joker/
            ├── __init__.py
            ├── queens.py
            └── config.json

Pyarmor uses :ref:`pyarmor gen` with rich options to obfuscate scripts to meet the needs of different applications.

Here only introduces common options in a short, using any combination of them as needed. About usage of each option in details please refer to :ref:`pyarmor gen`

Debug mode and trace log
========================

When something is wrong, check console log to find what Pyarmor does, and use :option:`-d` to generate :file:`pyarmor.debug.log` to get more information::

    $ pyarmor -d gen foo.py
    $ cat pyarmor.debug.log

Trace log is useful to check whatever protected by Pyarmor, enable it by this command::

    $ pyarmor cfg enable_trace=1

After that, :ref:`pyarmor gen` will generate a logfile :file:`pyarmor.trace.log`. For example::

    $ pyarmor gen foo.py
    $ cat pyarmor.trace.log

    trace.co             foo:1:<module>
    trace.co             foo:5:hello
    trace.co             foo:9:sum2
    trace.co             foo:12:main

Each line starts with ``trace.co`` is reported by code object protector. The first log says ``foo.py`` module level code is obfuscated, second says function ``hello`` at line 5 is obfuscated, and so on.

Enable both debug and trace mode could show much more information::

    $ pyarmor -d gen foo.py

Disable trace log by this command::

    $ pyarmor cfg enable_trace=0

.. program:: pyarmor gen

More options to protect script
==============================

For scripts, use these options to get more security::

    $ pyarmor gen --enable-jit --mix-str --assert-call --private foo.py

Using :option:`--enable-jit` tells Pyarmor processes some sensitive data by ``c`` function generated in runtime.

Using :option:`--mix-str` [#]_ could mix the string constant (length > 8) in the scripts.

Using :option:`--assert-call` makes sure function is obfuscated, to prevent called function from being replaced by special ways

Using :option:`--private` prevents plain scripts visiting module attributes

For example,

.. code-block:: python
    :emphasize-lines: 1,10

    data = "abcefgxyz"

    def fib(n):
        a, b = 0, 1
        while a < n:
            print(a, end=' ')
            a, b = b, a+b

    if __name__ == '__main__':
        fib(n)

String constant ``abcefgxyz`` and function ``fib`` will be protected like this

.. code-block:: python
    :emphasize-lines: 1,10

    data = __mix_str__(b"******")

    def fib(n):
        a, b = 0, 1
        while a < n:
            print(a, end=' ')
            a, b = b, a+b

    if __name__ == '__main__':
        __assert_call__(fib)(n)

If function ``fib`` is obfuscated, ``__assert_call__(fib)`` returns original function ``fib``. Otherwise it will raise protection exception.

To check which function or which string are protected, enable trace log and check trace logfile::

    $ pyarmor cfg enable_trace=1
    $ pyarmor gen --mix-str --assert-call fib.py
    $ cat pyarmor.trace.log

    trace.assert.call    fib:10:'fib'
    trace.mix.str        fib:1:'abcxyz'
    trace.mix.str        fib:9:'__main__'
    trace.co             fib:1:<module>
    trace.co             fib:3:fib

.. [#] :option:`--mix-str` is not available in trial version

More options to protect package
===============================

For package, remove :option:`--private` and append 2 extra options::

    $ pyarmor gen --enable-jit --mix-str --assert-call --assert-import --restrict joker/

Using :option:`--assert-import` prevents obfuscated modules from being replaced with plain script. It checks each import statement to make sure the modules are obfuscated.

Using :option:`--restrict` makes sure the obfuscated module is only available inside package. It couldn't be imported from any plain script, also not be run by Python interpreter.

By default ``__init__.py`` is not restricted, all the other modules are invisible from outside. Let's check this, first create a script :file:`dist/a.py`

.. code-block:: python

    import joker
    print('import joker OK')
    from joker import queens
    print('import joker.queens OK')

Then run it::

    $ cd dist
    $ python a.py
    ... import joker OK
    ... RuntimeError: unauthorized use of script

In order to export ``joker.queens``, either removing option :option:`--restrict`, or config only this module is not restrict like this::

    $ pyarmor cfg -p joker.queens restrict_module=0

Then obfuscate this package with restrict mode::

    $ pyarmor gen --restrict joker/

Now do above test again, it should work::

    $ cd dist/
    $ python a.py
    ... import joker OK
    ... import joker.queens

Copying package data files
==========================

Many packages have data files, but they're not copied to output path.

There are 2 ways to solve this problem:

1. Before generating the obfuscated scripts, copy the whole package to output path, then run :ref:`pyarmor gen` to overwrite all the ``.py`` files::

     $ mkdir dist/joker
     $ cp -a joker/* dist/joker
     $ pyarmor gen -O dist -r joker/

2. Changing default configuration let Pyarmor copy data files::

     $ pyarmor cfg data_files=*
     $ pyarmor gen -O dist -r joker/

Only copy ``*.yaml`` and ``*.json``::

     $ pyarmor cfg data_files="*.yaml *.json"

Checking runtime key periodically
=================================

Checking runtime key every hour::

    $ pyarmor gen --period 1 foo.py

Binding to many machines
========================

Using :option:`-b` many times to bind obfuscated scripts to many machines.

For example, machine A and B, the ethernet addresses are ``66:77:88:9a:cc:fa`` and ``f8:ff:c2:27:00:7f`` respectively. The obfuscated script could run in both of machine A and B by this command ::

    $ pyarmor gen -b "66:77:88:9a:cc:fa" -b "f8:ff:c2:27:00:7f" foo.py

Using outer file to store runtime key
=====================================

First obfuscating script with :option:`--outer`::

    $ pyarmor gen --outer foo.py

In this case, it could not be run at this time::

    $ python dist/foo.py

Let generate an outer runtime key valid for 3 days by this command::

    $ pyarmor gen key -e 3

It generates a file ``dist/pyarmor.rkey``, copy it to runtime package::

    $ cp dist/pyarmor.rkey dist/pyarmor_runtime_000000/

Now run :file:`dist/foo.py` again::

    $ python dist/foo.py

Let's generate another license valid for 10 days::

    $ pyarmor gen key -O dist/key2 -e 10

    $ ls dist/key2/pyarmor.rkey

Copy it to runtime package to replace the original one::

    $ cp dist/key2/pyarmor.rkey dist/pyarmor_runtime_000000/

The outer runtime key file also could be saved to other paths, refer to :term:`outer key`.

Localization runtime error
==========================

Some of runtime error messages could be customized. When something is wrong with the obfuscated scripts, it prints your own messages.

First create :file:`messages.cfg` in the path :file:`.pyarmor`::

    $ mkdir .pyarmor
    $ vi .pyarmor/messages.cfg

Then edit it. It's a ``.ini`` format file, change the error messages as needed

.. code-block:: ini

  [runtime.message]

    error_1 = this license key is expired
    error_2 = this license key is not for this machine
    error_3 = missing license key to run the script
    error_4 = unauthorized use of script

Now obfuscate the script in the current path to use customized messages::

    $ pyarmor gen foo.py

If we want to show same message for all of license errors, edit it like this

.. code-block:: ini

  [runtime.message]

    error_1 = invalid license key
    error_2 = invalid license key
    error_3 = invalid license key

Here no ``error_4``, it means this error uses the default message.

And then obfuscate the scripts again.

Packing obfuscated scripts
==========================

Pyarmor need PyInstaller to pack the obfuscated scripts, so first make sure PyInstaller has been installed. If not, simple install it by this command::

    $ pip install pyinstaller

Packing to one file
-------------------

.. versionadded:: 8.5.4

Packing script to one file only need one command::

    $ pyarmor gen --pack onefile foo.py

Run the final bundle::

    $ dist/foo

Pyarmor will automatically obfuscate `foo.py` and all the other used modules and packages in the same path, then pack the obfuscated to one bundle.

.. important::

   Please pass plain script in command line, for example, `foo.py` should not been obfuscated.

Packing to one folder
---------------------

.. versionadded:: 8.5.4

Packing script to one folder::

    $ pyarmor gen --pack onedir foo.py

Run the final bundle::

    $ dist/foo/foo

Using .spec file
----------------

.. versionadded:: 8.5.8

If the plain script has been packed by one spec file. For example::

    $ pyinstaller foo.spec
    $ dist/foo

Then pass this specfile to :option:`--pack` to let Pyarmor pack the obfuscated scripts. For example::

    $ pyarmor gen --pack foo.spec -r foo.py joker/
    $ dist/foo

Note that all the other scripts or packages must be list after main script, otherwise they won't be obfuscated by this way.

More information about pack feature, refer to :doc:`../topic/repack`

.. include:: ../_common_definitions.txt
