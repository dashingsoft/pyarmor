.. highlight:: console

==========
 Man Page
==========

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

Pyarmor is a powerful tool to obfuscate Python scripts with rich option set that
provides both high-level operations and full access to internals.

pyarmor
=======

.. program:: pyarmor

.. describe:: Syntax

    pyarmor [options] <command> ...

.. describe:: Options

-h, --help            show available command set then quit
-v, --version         show version information then quit
-q, --silent          suppress all normal output :option:`... <-q>`
-d, --debug           show more information in the console :option:`... <-d>`
--home PATH           set Pyarmor HOME path :option:`... <--home>`

These options can be used after :program:`pyarmor` but before command, here are
available commands:

================================  ====================================
:ref:`gen <pyarmor gen>`          Obfuscate scripts
:ref:`gen key <pyarmor gen key>`  Generate outer runtime key
:ref:`cfg <pyarmor cfg>`          Show and configure environments
:ref:`reg <pyarmor reg>`          Register Pyarmor
================================  ====================================

See :command:`pyarmor <command> -h` for more information on a specific command.

.. describe:: Description

.. option:: -q, --silent

            Suppress all normal output.

For example::

    pyarmor -q gen foo.py

.. option:: -d, --debug

            Show more information in the console

When something is wrong, print more debug informations in the console. For
example::

    pyarmor -d gen foo.py

.. option:: --home PATH[,GLOBAL[,LOCAL[,REG]]]

            Set Pyarmor :term:`Home Path`, :term:`Global Configuration Path`,
            :term:`Local Configuration Path` and :term:`Registration File Path`

The default paths

* :term:`Home Path` is :file:`~/.pyarmor`

* :term:`Global Configuration Path` is :file:`~/.pyarmor/config`, it's always
  relative to :term:`Home Path`

* :term:`Local Configuration Path` is :file:`.pyarmor`

* :term:`Registration File Path` is same as :term:`Home Path`

All of them could be changed by this option. For example, change home path to
:file:`~/.pyarmor2`::

    $ pyarmor --home ~/.pyarmor2 ...

Then

* :term:`Global Configuration Path` is :file:`~/.pyarmor2/config`
* :term:`Registration File Path` is :file:`~/.pyarmor2`
* :term:`Local Configuration Path` still is :file:`.pyarmor`

Another example, keep all others but change global path only::

    $ pyarmor --home ,config2 ...

This command sets :term:`Global Configuration Path` to :file:`~/.pyarmor/config2`

Another example, keep all others but change local path only::

    $ pyarmor --home ,,/var/myproject/ ...

This command sets :term:`Local Configuration Path` to :file:`/var/myproject`

Another example, set :term:`Registration File Path` to :file:`/opt/pyarmor/`::

    $ pyarmor --home ,,,/opt/pyarmor ...

It's useful when may use :command:`sudo` to run :command:`pyarmor`
occassionally. This makes sure the registration file could be found even switch
to another user.

When there are many Pyarmor Licenses registerred in one machine, set each
license to different :term:`Registration File Path`

There are 2 solutions

The first solution, one license one home::

    $ pyarmor --home ~/.pyarmor1 reg pyarmor-regfile-2051.zip
    $ pyarmor --home ~/.pyarmor1 gen project1/foo.py

    $ pyarmor --home ~/.pyarmor2 reg pyarmor-regfile-2052.zip
    $ pyarmor --home ~/.pyarmor2 gen project2/foo.py

The second solution, same home, one license one path::

    $ pyarmor --home ,,,pyarmor1 reg pyarmor-regfile-2051.zip
    $ pyarmor --home ,,,pyarmor1 gen project1/foo.py

    $ pyarmor --home ,,,pyarmor2 reg pyarmor-regfile-2052.zip
    $ pyarmor --home ,,,pyarmor2 gen project2/foo.py

Start pyarmor with clean configuration by setting :term:`Global Configuration
Path` and :term:`Local Configuration Path` to any non-exists path ``x``::

    $ pyarmor --home ,x,x, gen foo.py

.. seealso:: :envvar:`PYARMOR_HOME`

.. _pyarmor gen:

pyarmor gen
===========

Generate obfuscated scripts and all the required runtime files.

.. program:: pyarmor gen

.. describe:: Syntax

    pyarmor gen <options> <SCRIPT or PATH>

.. describe:: Options

-h, --help                      show option list and help information then quit
-O PATH, --output PATH          output path :option:`... <-O>`
-r, --recursive                 search scripts in recursive mode :option:`... <-r>`

-e DATE, --expired DATE         set expired date :option:`... <-e>`
-b DEV, --bind-device DEV       bind obfuscated scripts to device :option:`... <-b>`
--period N                      check runtime key periodically :option:`... <--period>`
--outer                         enable outer runtime key :option:`... <--outer>`

--platform NAME                 cross platform obfuscation :option:`... <--platform>`
-i                              store runtime files inside package :option:`... <-i>`
--prefix PREFIX                 import runtime package with PREFIX :option:`... <--prefix>`

--obf-module <0,1>              obfuscate whole module (default is 1) :option:`... <--obf-module>`
--obf-code <0,1>                obfuscate each function (default is 1) :option:`... <--obf-code>`
--no-wrap                       disable wrap mode :option:`... <--no-wrap>`
--enable <jit,rft,bcc,themida>  enable different obfuscation features :option:`... <--enable>`
--mix-str                       protect string constant :option:`... <--mix-str>`
--private                       enable private mode for script :option:`... <--private>`
--restrict                      enable restrict mode for package :option:`... <--restrict>`
--assert-import                 assert module is obfuscated :option:`... <--assert-import>`
--assert-call                   assert function is obfuscated  :option:`... <--assert-call>`

--pack BUNDLE                   repack bundle with obfuscated scripts  :option:`... <--pack>`

.. describe:: Description

This command is used to obfuscate all the scripts and packages listed in the command line. For example::

    pyarmor gen foo.py
    pyarmor gen src/mypkg
    pyarmor gen -r src/mypkg
    pyarmor gen -r src/pkg1 src/pkg2 libs/dbpkg
    pyarmor gen -r main.py src/*.py libs/utils.py libs/dbpkg

All the files list in the command line will be taken as scripts. For example::

    pyarmor gen foo.pyw README.txt

pyarmor will try to compile ``README.txt``, then may complain of ``syntax error``

If obfuscate all the scripts in one path, use one of these commands::

    pyarmor gen src/*.py
    pyarmor gen src/
    pyarmor gen -r src/

Here is wrong command, it will obfuscate all the files in ``src``::

    pyarmor gen src/*


.. option:: -O PATH, --output PATH

Set the output path for all the generated files, default is ``dist``

.. option:: -r, --recursive

When obfuscating package, search all scripts recursively. No this option, only the scripts in package path are obfuscated.

.. option:: -i

When obfuscating package, store the runtime files inside package. For example::

    $ pyarmor gen -r -i mypkg

The :term:`runtime package` will be stored inside package ``dist/mypkg``::

    $ ls dist/
    ...      mypkg/

    $ ls dist/mypkg/
    ...            pyarmor_runtime_000000/

Without this option, the output path is like this::

    $ ls dist/
    ...      mypkg/
    ...      pyarmor_runtime_000000/

This option can't be used to obfuscate script.

.. option:: --prefix PREFIX

Only used when obfuscating many packages at the same time and still store the runtime package inside package.

In this case, use this option to specify which package is used to store runtime package. For example::

    $ pyarmor gen --prefix mypkg src/mypkg mypkg1 mypkg2

This command tells pyarmor to store runtime package inside ``dist/mypkg``, and make ``dist/mypkg1`` and ``dist/mypkg2`` to import runtime package from ``mypkg``.

Checking  the content of ``.py`` files in output path to make it clear.

As a comparison, obfuscating 3 packages without this option::

    $ pyarmor gen -O dist2 src/mypkg mypkg1 mypkg2

And check ``.py`` files in the path ``dist2``.

.. option:: -e DATE, --expired DATE

            Expired date of obfuscated scripts.

It supports 4 forms:

* A number stands for valid days
* A date with iso format ``YYYY-MM-DD``
* A leading ``.`` with above 2 forms

Without leading dot, the obfuscated scripts checks NTP server time. For example::

    $ pyarmor gen -e 30 foo.py
    $ pyarmor gen -e 2022-12-31 foo.py

With leading dot, it checks local time. For example::

    $ pyarmor gen -e .30 foo.py
    $ pyarmor gen -e .2022-12-31 foo.py

.. option:: -b DEV, --bind-device DEV

            Use this option multiple times to bind multiple machines

Bind obfuscated script to specified device. Now only harddisk serial number, ethernet address and IPv4 address are available.

For example::

    $ pyarmor gen -b 128.16.4.10 foo.py
    $ pyarmor gen -b 52:38:6a:f2:c2:ff foo.py
    $ pyarmor gen -b HXS2000CN2A foo.py

Also set 30 valid days for this device::

    $ pyarmor gen -e 30 -b 128.16.4.10 foo.py

Check all of hardware informations in this device::

    $ pyarmor gen -b "128.16.4.10 52:38:6a:f2:c2:ff HXS2000CN2A" foo.py

Using this options multiple times means binding many machines. For example, the following command makes the obfuscated scripts could run 2 machiens::

    $ pyarmor gen -b "52:38:6a:f2:c2:ff" -b "f8:ff:c2:27:00:7f" foo.py

In case there are more network cards, binding anyone by this form::

    $ pyarmor gen -b "<2a:33:50:46:8f>" foo.py

Bind all network cards by this form::

    $ pyarmor gen -b "<2a:33:50:46:8f,f0:28:69:c0:24:3a>" foo.py

In Linux, it's possible to bind named ethernet card::

    $ pyarmor gen -b "eth1/fa:33:50:46:8f:3d" foo.py

If there are many harddisks. In Windows, binding anyone by sequence no::

      $ pyarmor gen -b "/0:FV994730S6LLF07AY" foo.py
      $ pyarmor gen -b "/1:KDX3298FS6P5AX380" foo.py

In Linux, binding to specify name::

      $ pyarmor gen -b "/dev/vda2:KDX3298FS6P5AX380" foo.py

.. option:: --period N

Check :term:`Runtime Key` periodically.

Support units:

* s
* m
* h

The default unit is hour, for example, the following examples are equivalent::

    $ pyarmor gen --period 1 foo.py
    $ pyarmor gen --period 3600s foo.py
    $ pyarmor gen --period 60m foo.py
    $ pyarmor gen --period 1h foo.py

.. note::

   If the obfuscated script enters an infinite loop without call any obfuscated function, it doesn't trigger periodic check.

.. option:: --outer

            Enable :term:`outer key`

It tells the obfuscated scripts find :term:`runtime key` in outer file.

Once this option is specified, :ref:`pyarmor gen key` must be used to generate an outer key file and copy to the corresponding path in :term:`target device`. Otherwise the obfuscated scripts will complain of ``missing license key to run the script``

The default name of outer key is ``pyarmor.rkey``, it can be changed by this command::

    $ pyarmor cfg outer_keyname=".pyarmor.key"

By this command the name of outer key is set to ``.pyarmor.key``.

.. option:: --platform NAME

            Specify target platform to run obfuscated scripts.

The name must be one of standard :term:`platform` defined by Pyarmor.

It requires :mod:`pyarmor.cli.runtime` to get prebuilt binary libraries of other platforms.

.. option:: --private

            Enable private mode for scripts.

When private mode is enabled, the function name is empty in traceback. And the obfuscated scripts could not be imported by plain script or Python interpreter.

It can't be used with :option:`--restrict`, the latter enables private mode implicitly.

.. option:: --restrict

            Enable restirct mode for package, do not use it to obfuscate scripts.

            It enables :option:`--private` implicitly, and has all the features of private mode.

When restrict mode is enabled, all the modules excpet ``__init__.py`` in the package could not be imported by plain scripts.

For example, obfuscate a restrict package to ``dist/joker``::

    $ pyarmor gen -i --restrict joker
    $ ls dist/
    ...    joker/

Then create a plaint script ``dist/foo.py``

.. code-block:: python

    import joker
    print('import joker should be OK')
    from joker import queens
    print('import joker.queens should fail')

Run it to verify::

    $ cd dist
    $ python foo.py
    ... import joker should be OK
    ... RuntimeError: unauthorized use of script

If there are extra modules need to be exported, list all the modules in this command::

    $ pyarmor cfg exclude_restrict_modules="__init__ queens"

Then obfuscate the package again.

.. option:: --obf-module <0,1>

            Enable the whole module (default is 1)

.. option:: --obf-code <0,1>

            Enable each function in module (default is 1)

.. option:: --no-wrap

            Disable wrap mode

If wrap mode is enabled, when enter a function, it's restored. but when exit,
this function will be obfuscated again.

If wrap mode is disabled, once the function is restored, it's never be
obfuscated again.

If :option:`--obf-code` is ``0``, this option is meaningless.

.. option:: --enable <jit,rft,bcc,themida>

            Enable different obfuscation features.

.. option:: --enable-jit

Use :term:`JIT` to process some sentensive data to improve security.

.. option:: --enable-rft

            Enable :term:`RFT Mode` to obfuscate the script :sup:`pro`

.. option:: --enable-bcc

            Enable :term:`BCC Mode` to obfuscate the script :sup:`pro`

.. option:: --enable-themida

            Use `Themida`_ to protect extension module in :term:`runtime package`

            Only works for Windows platform.

.. option:: --mix-str

            Mix the string constant in scripts :sup:`basic`

.. option:: --assert-call

            Assert function is obfuscated

If this option is enabled, Pyarmor scans each function call in the scripts. If
the called function is in the obfuscated scripts, protect it as below, and leave
others as it is. For example,

.. code-block:: python
    :emphasize-lines: 4

    def fib(n):
        a, b = 0, 1
        return a, b

    print('hello')
    fib(n)

will be changed to

.. code-block:: python
    :emphasize-lines: 4

    def fib(n):
        a, b = 0, 1

    print('hello')
    __assert_armored__(fib)(n)

The function ``__assert_armored__`` is a builtin function in obfuscated script.
It checks the argument, if it's an obfuscated function, then returns this
function, otherwise raises protection exception.

In this example, ``fib`` is protected, ``print`` is not.

.. option:: --assert-import

            Assert module is obfuscated

If this option is enabled, Pyarmor scans each ``import`` statement in the
scripts. If the imported module is obfuscated, protect it as below, and leave
others as it is. For example,

.. code-block:: python
    :emphasize-lines: 2

    import sys
    import foo

will be changed to

.. code-block:: python
    :emphasize-lines: 2,3

    import sys
    import foo
    __assert_armored__(foo)

The function ``__assert_armored__`` is a builtin function in obfuscated script.
It checks the argument, if it's an obfuscated module, then return this module,
otherwise raises protection exception.

This option neither touchs statement ``from import``, nor the module imported by
function ``__import__``.

.. option:: --pack BUNDLE

            Repack bundle with obfuscated scripts

Here ``BUNDLE`` is an executable file generated by PyInstaller_

Pyarmor just obfuscates the script first.

Then unpack the bundle.

Next replace all the ``.pyc`` in the bundle with obfuscated scripts, and append
all the :term:`runtime files` to the bundle.

Finally repack the bundle and overwrite the original ``BUNDLE``.

.. _pyarmor gen key:

pyarmor gen key
===============

Generate :term:`outer key` for obfuscated scripts.

.. program:: pyarmor gen key

.. describe:: Syntax

    pyarmor gen key <options>

.. describe:: Options

-O PATH, --output PATH      output path
-e DATE, --expired DATE     set expired date
--period N                  check runtime key periodically
-b DEV, --bind-device DEV   bind obfuscated scripts to device

.. describe:: Description

This command is used to generate :term:`outer key`, the options in this command
have same meaning as in the :ref:`pyarmor gen`.

There must be at least one of option ``-e`` or ``-b`` for :term:`outer key`.

It's invalid that outer key is neither expired nor binding to a device. For this
case, don't use outer key.

By default the outer key is saved to ``dist/pyarmor.rkey``. For example::

    $ pyarmor gen key -e 30
    $ ls dist/pyarmor.rkey

Save outer key to other path by this way::

    $ pyarmor gen key -O dist/mykey2 -e 10
    $ ls dist/mykey2/pyarmor.rkey

By default the outer key name is ``pyarmor.rkey``, use the following command to
change outer key name to any others. For example, ``sky.lic``::

    $ pyarmor cfg outer_keyname=sky.lic
    $ pyarmor gen key -e 30
    $ ls dist/sky.lic

.. _pyarmor cfg:

pyarmor cfg
===========

Configure or show Pyarmor environments

.. program:: pyarmor cfg

.. describe:: Syntax

    pyarmor cfg <options> [OPT[=VALUE]] ...

.. describe:: Options

-h, --help           show this help message and exit
-p NAME              private settings for special module or package
-g, --global         do everything in global settings, otherwise local
                     settings
-r, --reset          reset option to default value
--encoding ENCODING  specify encoding to read configuration file

.. describe:: Description

Run this command without arguments to show all available options::

    $ pyarmor cfg

Show one exact option ``obf_module``::

    $ pyarmor cfg obf_module

Show all options which start with ``obf``::

    $ pyarmor cfg obf*

Set option to new value::

    $ pyarmor cfg obf_module=0

Reset option to default::

    $ pyarmor cfg -r obf_module

Change option ``excludes`` in the section ``finder`` by this form::

    $ pyarmor cfg finder:excludes=ast

If no prefix ``finder``, for example::

    $ pyarmor cfg excludes=ast

Not only option ``excludes`` in section ``finder``, but also in other sections
``assert.call``, ``mix.str`` etc. are changed.

.. option:: -p NAME

            Private settings for special module or package

All the settings is only used for specified module `NAME`.

.. option:: -g, --global

            Do everything in global settings

Without this option, all the changed settings are soted in :term:`Local
Configuration Path`, generally it's ``.pyarmor`` in the current path. By this
option, everything is stored in :term:`Global Configuration Path`, generally
it's ``~/.pyarmor/config/global``

.. option:: -r, --reset

            Reset option to default value

.. _pyarmor reg:

pyarmor reg
===========

Register Pyarmor or upgrade Pyarmor license

.. program:: pyarmor reg

.. describe:: Syntax

    pyarmor reg [OPTIONS] [FILENAME]

.. describe:: Options

-h, --help            show this help message and exit
-p NAME, --product NAME
                      license to this product
-u, --upgrade         upgrade Pyarmor license
-y, --confirm         register Pyarmor without asking for confirmation

.. describe:: Arguments

The ``FILENAME`` must be one of these forms:

* ``pyarmor-regcode-xxxx.txt`` got by purchasing Pyarmor license
* ``pyarmor-regfile-xxxx.zip`` got by initial registration with above file

.. describe:: Description

Check the registration information::

    $ pyarmor -v

Show verbose information::

    $ pyarmor reg

.. option:: -p NAME, --product NAME

            Set product name bind to license

When initial registration, use this option to set proudct name bind to license.

If no this option, the product name is set to ``non-profits``.

It's meanless to use this option after initial registration.

``TBD`` is a special product name. If product name is ``TBD`` at initial
registration, the product name can be changed later.

For any other product name, it can't be changed any more.

.. option:: -y, --confirm

            In initial registration, without asking for confirmation

.. option:: -u, --upgrade

            Upgrade old license to Pyarmor 8.0 Licese

.. important::

   Once initial registration successfully, :file:`pyarmor-regcode-xxxx.txt` may
   not work again. Using registration file :file:`pyarmor-regfile-xxxx.zip` for
   next registration instead.

   PLEASE BACKUP registration file :file:`pyarmor-regfile-xxxx.zip` carefully,
   Pyarmor doesn't provide lost-found service

Using registration file :file:`pyarmor-regfile-xxxx.zip` to register Pyarmor in
other machine.

Copy it to target device, then run this command::

    $ pyarmor reg pyarmor-regfile-xxxx.zip

Environment Variables
=====================

The following environment variables only used in :term:`Build Machine` when
generating the obfuscated scripts, not in :term:`Target Device`.

.. envvar:: PYARMOR_HOME

            Same as :option:`pyarmor --home`

It mainly used in the shell scrits to change Pyarmor settings. If
:option:`pyarmor --home` is set, this environment var is ignored.

.. envvar:: PYARMOR_PLATFORM

            Set the right :term:`Platform` to run :command:`pyarmor`

It's mainly used in some platforms Pyarmor could not tell right but still works.

.. envvar:: PYARMOR_CC

            Specify C compiler for bccmode

.. envvar:: PYARMOR_CLI

            Only for compatible with old Pyarmor, ignore this if you don't use
            old command prior to 8.0

If you do not use new commands in Pyarmor 8.0, and prefer to only use old
commands, set it to ``7``, for example::

    # In Linux
    export PYARMOR_CLI=7
    pyarmor -h

    # Or
    PYARMOR_CLI=7 pyarmor -h

    # In Windows
    set PYARMOR_CLI=7
    pyarmor -h

It forces command :command:`pyarmor` to use old cli directly.

Without it, :command:`pyarmor` first try new cli, if the command line couldn't
be parsed by new cli, fallback to old cli.

This only works for command :command:`pyarmor`.

.. include:: ../_common_definitions.txt
