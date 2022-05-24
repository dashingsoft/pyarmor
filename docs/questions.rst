.. _questions:

When Things Go Wrong
====================

Some necessary knowledges and technicals are required to used pyarmor. Check
this list, make sure you know them, and your question is not related to them.

.. _Necessary Knowledges:

Necessary Knowledges
--------------------

Shell
~~~~~

pyarmor is a command line tool, it must be run in the shell or terminal. If you
know nothing about shell command, use `pyarmor-webui`_ instead.

When command `pyarmor` complains of argument error, unknown option etc. Please
use option ``-h`` to list all the available options, and fix command syntax
error by these hints. For example::

    pyarmor obfuscate -h

Python
~~~~~~

How to run Python
https://docs.python.org/3.8/tutorial/interpreter.html#using-the-python-interpreter

Source Code Encoding
~~~~~~~~~~~~~~~~~~~~

If the obfuscated scripts print unexpected output, you need learn this

https://docs.python.org/3.8/tutorial/interpreter.html#source-code-encoding

Then set the right source code encoding in the scripts, first run the plain
script to make sure everything is fine, then obfuscate the scripts again.


Python Import System
~~~~~~~~~~~~~~~~~~~~

The obfuscated scripts need an extra :ref:`Runtime Package` to run, it's a
common Python package, which could be imported as normal Python module or
package. If it can't be imported correctly, for example, not distributed with
the obfuscated scripts or stored in the wrong place, the obfuscated scripts may
raise exceptions like this::

   ModuleNotFoundError: No module named 'app.pytransform'

This is not PyArmor's error, just Python can not find it. In this case, you need
know Python how to import module, package, what's absolute import and relative
import, you must know what's ``sys.path``

https://docs.python.org/3.8/library/sys.html#sys.path

The obfuscated script is a very simple Python script, the first line is an
import statement, the second line is a function call. For any import or no
module found error, for example::

    ImportError: No module named model.NukepediaDB

Just think it as a common python script, check whether the module, package or
extension file locates in the right place according to Python Import System. If
not, move the module, package or extension file to right path.

Refer to the following official document or by search engineer to understand
Python Import System

https://docs.python.org/3.8/reference/simple_stmts.html#the-import-statement


PyInstaller
~~~~~~~~~~~

If you'd like to pack the obfuscated scripts to one executable, and your project
structure is complex, you must know `PyInstaller`_ and could pack your project
by `PyInstaller`_ directly.

https://pyinstaller.readthedocs.io/en/stable/usage.html


Common Solutions
----------------

I have receive a lot of issues, most of them aren't pyarmor's defect, but use
pyarmor in wrong way. So when you're in trouble with pyarmor, spending a few
hours to understand pyarmor may solve the problem quickly. Self-help is better
than help from others, it also could save time for both of us.

First make sure you have read the basic guide :ref:`Using PyArmor`.

Look through :ref:`Understanding Obfuscated Scripts`, especially the section
:ref:`The Differences of Obfuscated Scripts`

If you don't know how to use pyarmor in a special case, have a glance at the toc
of :ref:`Advanced Topics`.

Here are several common solutions

* Upgrade pyarmor to latest stable version, please check :ref:`change logs`
  before upgrading. If pyarmor works fine before, but now doesn't work, also
  make a :ref:`clean uninstallation`, re-install pyarmor, and start everything
  from refresh state.

* As obfuscating the script by ``pyarmor``, check not only the last error
  message, but also each log carefully to understand what pyarmor is doing, it's
  very helpful to find the problem. And try to get more information by common
  option ``-d``. For example::

      pyarmor -d obfuscate --recursive foo.py

* As running the obfuscated scripts, turn on Python debug option by ``-d`` to
  print more information. If there is line number and script name in the
  traceback, check the source script around this line. Make sure it doesn't use
  any feature changed by obfuscated scripts. For example::

      python -d obf_foo.py

* If you distribute the obfuscated scripts in different platform or docker, make
  sure the related cross platform options are set. Because the obfuscated
  scripts include binary library, it's platform dependent, and Python version in
  target must be same as the version to obfuscate the scripts.

* If you are using command :ref:`pack`, make sure PyInstaller could pack the
  plain scripts directly and the final bundle works.

* If you are using the scripts obfuscated by :ref:`Restrict mode` 3 or more, try
  to use the default restrict mode. If low restrict mode works, check the
  scripts make sure they don't violate the restrict mode.

* If you are using complex scripts or packages, try a simple script or package
  to check it works or not.

* Understanding pyarmor by doing a test in a few minutes if something you're not
  sure.

The default option of pyarmor works for common cases, but for complex cases, you
need understand the different options for each command. First list all available
options of ``obfuscate`` by option ``-h``::

    pyarmor obfuscate -h

You may find the desired option by its short description. If you're not sure, go
to :ref:`Man Page` to read the details of each option.

Maybe the simplest way to understand an option is, do a test in one minute. For
example, the option ``--bootstrap`` is used to control how to generate the
bootstrap code for obfuscated scripts, do tests in a fresh path like this::

  cd /path/to/test
  mkdir case-1
  cd case-1
  echo "print('Hello')" > foo.py
  pyarmor obfuscate --bootstrap 2 foo.py
  ls dist/
  cat dist/foo.py

  cd /path/to/test
  mkdir case-2
  cd case-2
  echo "print('Hello')" > foo.py
  pyarmor obfuscate --bootstrap 3 foo.py
  ls dist/
  cat dist/foo.py

You can combine different options to do similar tests, it could help you
understand pyarmor quickly.

.. note::

   There are a lot of reporeted `issues`_, search here first try to find same
   issue.

.. _reporting an issue:

Reporting an issue
------------------

When there is no solution in the document, about security issue, send email to
pyarmor@163.com, all the others please click `issues`_ to report, and
provide the necessary information

1. The full pyarmor command and full output log (required)
2. If distributing the obfuscated script to other machine, which files are copied (optional)
3. The command to run the obfuscated scripts and full traceback when something is wrong

The output log could be redirected to a file by this way::

    pyarmor obfuscate foo.py >log.txt 2>&1

Here it's an example, the title of issue::

  cannot import name 'pyarmor' from 'pytransform'

The content of issue (copy all of these to github and modify it)::

    1. On MacOS 10.14 run pyarmor to obfuscate the script
    ```
    $ pyarmor obfuscate --exact main.py
    INFO     Create pyarmor home path: /Users/jondy/.pyarmor
    INFO     Create trial license file: /Users/jondy/.pyarmor/license.lic
    INFO     Generating public capsule ...
    INFO     PyArmor Trial Version 7.0.1
    INFO     Python 3.7.10
    INFO     Target platforms: Native
    INFO     Source path is "/Users/jondy/workspace/pyarmor-webui/test/__runner__/__src__"
    INFO     Entry scripts are ['main.py']
    INFO     Use cached capsule /Users/jondy/.pyarmor/.pyarmor_capsule.zip
    INFO     Search scripts mode: Exact
    INFO     Save obfuscated scripts to "dist"
    INFO     Read product key from capsule
    INFO     Obfuscate module mode is 2
    INFO     Obfuscate code mode is 1
    INFO     Wrap mode is 1
    INFO     Restrict mode is 1
    INFO     Advanced value is 0
    INFO     Super mode is False
    INFO     Super plus mode is not enabled
    INFO     Generating runtime files to dist/pytransform
    INFO     Extract pytransform.key
    INFO     Generate default license file
    INFO     Update capsule to add default license file
    INFO     Copying /Users/jondy/workspace/pyarmor-webui/venv/lib/python3.7/site-packages/pyarmor/platforms/darwin/x86_64/_pytransform.dylib
    INFO     Patch library dist/pytransform/_pytransform.dylib
    INFO     Patch library file OK
    INFO     Copying /Users/jondy/workspace/pyarmor-webui/venv/lib/python3.7/site-packages/pyarmor/pytransform.py
    INFO     Rename it to pytransform/__init__.py
    INFO     Generate runtime files OK
    INFO     Start obfuscating the scripts...
    INFO     	/Users/jondy/workspace/pyarmor-webui/test/__runner__/__src__/main.py -> dist/main.py
    INFO     Insert bootstrap code to entry script dist/foo.py
    INFO     Obfuscate 1 scripts OK.
    ```
    2. Copy the whole folder `dist/` to target machine Ubuntu
    3. Failed to run the obfuscated script by Python 3.7 in Unbutu
    ```
    $ cd dist/
    $ python3 main.py
    Traceback (most recent call last):
    File "main.py", line 1, in <module>
      from pytransform import pyarmor
    ImportError: cannot import name 'pyarmor' from 'pytransform' (/home/jondy/dist/pytransform/__init__.py)
    ```

.. important::

   The issue may be marked as ``invalid`` and be closed directly in any of:

   * Not reported as template or missing necessary information
   * There is the exact solution in the documentation


Segment fault
-------------

In the following cases, obfuscated scripts may crash

* Running obfuscated script by debug version Python
* Obfuscating scripts by Python X.Y but running the obfuscated scripts by
  different Python version M.N
* Running the scripts in different platform but obfuscate them without option
  ``--platform``

  - Docker, it's Alpine Linux, in PyArmor, the platform name is `musl.x86_64`,
    not `linux.x86_64`
  - In Windows, 32-bit Windows is different from 64-bit Windows
  - In 64-bit Windows, 32-bit Python is different from 64-bit Python

* Read ``co_code`` or other attributes of the obfuscated code object by any way,
  some third packages may analysis the byte code to do something.
* Importing the scripts obfuscated by restrict mode 3 and more in non-obfuscated
  script may crash. It also may crash if it's obfuscated by ``obf-code=0``
* Mixing the scripts obfuscated by different option ``--advanced``
* In MacOS, the core library of pyarmor is linked to standard system Python, for
  others, use ``install_name_tool`` to change ``rpath`` to adapt this machine.

For PyArmor 5.5.0 ~ 6.6.0, some machines may be crashed because of advanced
mode. A quick workaround is to disable advanced mode by editing the file
:file:`pytransform.py` which locates in the installed path of ``pyarmor`` , in
the function ``_load_library``, uncomment about line 202. The final code looks
like this::

    # Disable advanced mode if required
    m.set_option(5, c_char_p(1))


Bootstrap Problem
-----------------

Could not find `_pytransform`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generally, the dynamic library `_pytransform` is in the :ref:`runtime package`,
before v5.7.0, it's in the same path of obfuscated scripts. It may be:

* `_pytransform.so` in Linux
* `_pytransform.dll` in Windows
* `_pytransform.dylib` in MacOS

First check whether the file exists. If it exists:

* Check the permissions of dynamic library

    If there is no execute permissions in Windows, it will complain:
    `[Error 5] Access is denied`

* Check whether `ctypes` could load `_pytransform`::

    from pytransform import _load_library
    m = _load_library(path='/path/to/dist')

* Try to set the runtime path in the :ref:`Bootstrap Code` of entry
  script::

    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/dist')

Still doesn't work, report an issues_


ERROR: Unsupport platform linux.xxx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Please refer to :ref:`Support Platforms`


/lib64/libc.so.6: version 'GLIBC_2.14' not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In some machines there is no `GLIBC_2.14`, it will raise this exception.

One solution is patching `_pytransform.so` by the following way.

First check version information::

    readelf -V /path/to/_pytransform.so
    ...

    Version needs section '.gnu.version_r' contains 2 entries:
     Addr: 0x00000000000056e8  Offset: 0x0056e8  Link: 4 (.dynstr)
      000000: Version: 1  File: libdl.so.2  Cnt: 1
      0x0010:   Name: GLIBC_2.2.5  Flags: none  Version: 7
      0x0020: Version: 1  File: libc.so.6  Cnt: 6
      0x0030:   Name: GLIBC_2.7  Flags: none  Version: 8
      0x0040:   Name: GLIBC_2.14  Flags: none Version: 6
      0x0050:   Name: GLIBC_2.4  Flags: none  Version: 5
      0x0060:   Name: GLIBC_2.3.4  Flags: none  Version: 4
      0x0070:   Name: GLIBC_2.2.5  Flags: none  Version: 3
      0x0080:   Name: GLIBC_2.3  Flags: none  Version: 2

Then replace the entry of `GLIBC_2.14` with `GLIBC_2.2.5`:

* Copy 4 bytes at 0x56e8+0x10=0x56f8 to 0x56e8+0x40=0x5728
* Copy 4 bytes at 0x56e8+0x18=0x5700 to 0x56e8+0x48=0x5730

Here are sample commands::

    xxd -s 0x56f8 -l 4 _pytransform.so | sed "s/56f8/5728/" | xxd -r - _pytransform.so
    xxd -s 0x5700 -l 4 _pytransform.so | sed "s/5700/5730/" | xxd -r - _pytransform.so

.. note::

   From v5.7.9, this patch is not required. In cross-platform all you need to do
   is specify the platform to `centos6.x86_64` to fix this issue. For example::

     pyarmor obfuscate --platform centos6.x86_64 foo.py

'pyarmor' is not recognized issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If `pyarmor` is installed by pip, please search "pyarmor" in the computer, then
run full path pyarmor, or add path of pyarmor to environment variable PATH.

If not by pip, the equivalent of the pyarmor command is running Python script
"pyarmor.py" found in the distribution folder.

__snprintf_chk: symbol not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When run pyarmor in some dockers, it may raise this exception. Because these
dockers are built with musl-libc, but the default ``_pytransform.so`` is built
with glibc, ``__snprintf_chk`` is missed in the musl-libc.

In this case, try to download the corresponding dynamic library

For x86/64
http://pyarmor.dashingsoft.com/downloads/latest/alpine/_pytransform.so

For ARM
http://pyarmor.dashingsoft.com/downloads/latest/alpine.arm/_pytransform.so

And overwrite the old one which filename could be found in the traceback.


Obfuscating Scripts Problem
---------------------------

Warning: code object xxxx isn't wrapped
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It means this function isn't been obfuscated, because it includes some
special instructions.

For example, there is 2-bytes instruction `JMP 255`, after the code
object is obfuscated, the operand is increased to `267`, and the
instructions will be changed to::

    EXTEND 1
    JMP 11

In this case, it's complex to obfuscate the code object with wrap
mode. So the code object is obfuscated with non wrap mode, but all the
other code objects still are obfuscated with wrap mode.

In current version add some unused code in this function so that the
operand isn't the critical value may avoid this warning.

.. note::

   Before v5.5.0, in this case the code object is left as it is.

Code object could not be obufscated with advanced mode 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because this function includes some jump instructions that couldn't be
handled. In this case, just refine this function, make sure the first statement
will not generate jump instruction. For example, assignment, function call or
any simple statement. However, the compound statements, for examples, `try`,
`for`, `if`, `with`, `while` etc. will generate the jump instructions. If there
is no anyway to refactor the function, insert the following statement at the
beginning of this function::

  [None, None]

It will generate some instructions but doesn't change anything.

Error: Try to run unauthorized function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If there is any file `license.lic` or `pytransform.key` in the current
path, pyarmor maybe reports this error. One solution is to remove all
of that files, the other solution to upgrade PyArmor to v5.4.5 later.


'XXX' codec can't decode byte 0xXX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add the exact source encode at the begin of the script. For example::

    # -*- coding: utf-8 -*-

Refer to https://docs.python.org/2.7/tutorial/interpreter.html#source-code-encoding

If the source encode has been added into main script, it still raises this
issue. Please check the output log to find the exact script name, it may not the
main script.


Why plugin doesn't work
~~~~~~~~~~~~~~~~~~~~~~~

If the plugin script doesn't work as expected, first check the plugin script
could be injected into the entry script by set Python debug flag::

  # In linux
  export PYTHONDEBUG=y
  # In Windows
  set PYTHONDEBUG=y

  pyarmor obfuscate --exact --plugin check_ntp_time foo.py

It will generate patched file ``foo.py.pyarmor-patched``, make sure the content
of plugin script has been inserted into the right place, and the verify function
will be executed.


Running Obfuscated Scripts Problem
----------------------------------

The `license.lic` generated doesn't work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The key is that the capsule used to obfuscate scripts must be same as
the capsule used to generate licenses.

The :ref:`Global Capsule` will be changed if the trial license file of
|PyArmor| is replaced with normal one, or it's deleted occasionally
(which will be generated implicitly as running command `pyarmor
obfuscate` next time).

In any cases, generating new license file with the different capsule
will not work for the obfuscated scripts before. If the old capsule is
gone, one solution is to obfuscate these scripts by the new capsule
again.


NameError: name '__pyarmor__' is not defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
No :ref:`Bootstrap Code` are executed before importing obfuscated scripts.

* When creating new process by `Popen` or `Process` in mod `subprocess` or
  `multiprocessing`, to be sure that :ref:`Bootstrap Code` will be called before
  importing any obfuscated code in sub-process. Otherwise it will raise this
  exception.
* If `pytransform.py` or `pytransform/__init__.py` raises this exception. Make
  sure it is not obfuscated, it must be plain script.
* Also check system module `os`, `ctypes`, make sure they're not obfuscated, try
  to use option ``--exclude`` to exclude the whole Python system library path.

How to check :ref:`Bootstrap Code` executed or not? One simple way is to insert
one print statement before them. For example

.. code:: python

    print('Start to run bootstrap code')
    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

If the message is printed, then it's OK. Removing the print statement and check
other causes.

The other solution for this issue is :ref:`using super mode` to obfuscate the
scripts.

Marshal loads failed when running xxx.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Check whether the version of Python to run obfuscated scripts is same as the
   version of Python to obfuscate script

2. Run obfuscated script by `python -d` to show more error message.

3. Be sure the capsule used to generated the license file is same as the capsule
   used to obfuscate the scripts. The filename of the capsule will be shown in
   the console when the command is running.

4. For cross platform obfuscation, make sure the dynamic library feature is set
   correctly, refer to :ref:`Obfuscating scripts with different features`

_pytransform can not be loaded twice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When the function `pyarmor_runtime` is called twice, it will complaint
`_pytransform can not be loaded twice`

For example, if an obfuscated module includes the following lines::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(....)

When importing this module from entry script, it will report this
error. The first 2 lines should be in the entry script only, not in
the other module.

This limitation is introduced from v5.1, to disable this check, just
edit `pytransform.py` and comment these lines in function
`pyarmor_runtime`::

    if _pytransform is not None:
        raise PytransformError('_pytransform can not be loaded twice')

.. note::

   This limitation has been removed from v5.3.5.


Check restrict mode failed
~~~~~~~~~~~~~~~~~~~~~~~~~~
Use obfuscated scripts in wrong way, by default all the obfuscated
scripts can't be changed any more.

Besides packing the obfuscated scripts will report this error
either. Do not pack the obfuscated scripts, but pack the plain scripts
directly.

For more information, refer to :ref:`Restrict Mode`


Protection Fault: unexpected xxx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use obfuscated scripts in wrong way, by default, all the runtime files
can't be changed any more. Do not touch the following files

* pytransform.py
* _pytransform.so/.dll/.dylib

If the entry script is obfuscated by new version, but the runtime files are
still old, it may raise this exception. Using option ``--no-cross-protection``
to disable this protection, or using option ``--runtime`` to specify the same
runtime files when obfuscating the scrpits, could fix this issue.

For more information, refer to :ref:`Special Handling of Entry Script`


Run obfuscated scripts reports: Invalid input packet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Mixing trial version and purchased version to obfuscate scripts and generate
`license.lic` also may raise this exception. Make sure all the files generated
by trial version, for example, obfusbcated script, license file and runtime
files, are removed.

Make sure the runtime module or package `pytransform` imported by the obfuscated
scripts is the one distributed with the obfuscated scripts. For example, running
the obfuscated scripts `python dist/foo.py` in the source path of pyarmor
package may rasie this exception, because `pytransform.py` of pyarmor will be
imported by the `dist/foo.py` unexpectedly.

If the scripts are obfuscated in different platform, check the notes in
:ref:`Distributing Obfuscated Scripts To Other Platform`

Before v5.7.0, check if there is any of `license.lic` or `pytransform.key` in
the current path. Make sure they're generated for the obfuscated scripts. If
not, rename them or move them to other path.

Because the obfuscated scripts will first search the current path, then search
the path of runtime module `pytransform.py` to find the file `license.lic` and
`pytransform.key`. If they're not generated for the obfuscated script, this
error will be reported.


OpenCV fails because of `NEON - NOT AVAILABLE`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In some Raspberry Pi platform, run the obfuscated scripts to import
OpenCV fails::

    ************************************************** ****************
    * FATAL ERROR: *
    * This OpenCV build doesn't support current CPU / HW configuration *
    * *
    * Use OPENCV_DUMP_CONFIG = 1 environment variable for details *
    ************************************************** ****************

    Required baseline features:
    NEON - NOT AVAILABLE
    terminate called after throwing an instance of 'cv :: Exception'
      what (): OpenCV (3.4.6) /home/pi/opencv-python/opencv/modules/core/src/system.cpp:538: error:
    (-215: Assertion failed) Missing support for required CPU baseline features. Check OpenCV build
    configuration and required CPU / HW setup. in function 'initialize'

One solution is to specify optioin ``--platform`` to `linux.armv7.0`::

    pyarmor obfuscate --platform linux.armv7.0 foo.py
    pyarmor build --platform linux.armv7.0
    pyarmor runtime --platform linux.armv7.0

The other solution is to set environment variable `PYARMOR_PLATFORM`
to `linux.armv7.0`. For examples::

    PYARMOR_PLATFORM=linux.armv7.0 pyarmor obfuscate foo.py
    PYARMOR_PLATFORM=linux.armv7.0 pyarmor build

    Or,

    export PYARMOR_PLATFORM=linux.armv7.0
    pyarmor obfuscate foo.py
    pyarmor build

How to customize error message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I have started to play around with pyarmor. When using a license file that
expires you get the message “License is expired”. Is there a way to change this
message?

At this time, you need patch the source script `pytransform.py` in the pyarmor
package. There is a function `pyarmor_runtime`

.. code:: python

    def pyarmor_runtime(path=None, suffix='', advanced=0):
        ...
        try:
            pyarmor_init(path, is_runtime=1, suffix=suffix, advanced=advanced)
            init_runtime()
        except Exception as e:
            if sys.flags.debug or hasattr(sys, '_catch_pyarmor'):
                raise
            sys.stderr.write("%s\n" % str(e))
            sys.exit(1)

Change the hanler of the exception as you desired.

If the scripts are obfuscated by super mode, this solution doesn't work. You may
create a script to catch exceptions raised by obfuscated script `foo.py`. For
example

.. code:: python

   try:
       import foo
   except Exception as e:
       print('something is wrong')

By this way not only the exceptions of pyarmor but also of normal scripts are
catched. In order to handle the exceptions of pyarmor only, first create runtime
package by :ref:`runtime`, and obfuscate the scripts with it::

    pyarmor runtime --advanced 2 -O dist
    pyarmor obfuscate --advanced 2 --runtime @dist foo.py

Then create a boot script ``dist/foo_boot.py`` like this

.. code:: python

   try:
       import pytransform_bootstrap
   except Exception as e:
       print('something is wrong')
   else:
       import foo

The script ``dist/pytransform_bootstrap.py`` is created by :ref:`runtime`, it's
obfuscated from an empty script, so only pyarmor bootstrap exceptions are raised
by it.


undefined symbol: PyUnicodeUCS4_AsUTF8String
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If Python interpreter is built with UCS2, it may raises this issue when running
super mode obufscated scripts. In this case, try to obfuscate script with
platform ``centos6.x86_64``, it's built with UCS2. For example::

    pyarmor obfuscate --advanced 2 --platform centos6.x86_64 foo.py


NameError: name '__armor_wrap__' is not defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If :ref:`Restrict Mode` is set to 4 or 5, it may report this issue. In this case
try to set restrict mode to 2.

If it's raised in the object method `__del__`, upgrade pyarmor to v6.7.3+, and
obfuscate the scripts again.

Also refer to :ref:`Using restrict mode with threading and multiprocessing` and
next question.

Object method `__del__` raise NameError exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If method `__del__` raises this exception::

    NameError: name '__armor_enter__' is not defined
    NameError: name '__armor_wrap__' is not defined

Please upgrade pyarmor to v6.7.3+, and obfuscate the scripts again, and make
sure new runtime package is generated.

If the scripts is obfuscated by non super mode and python is 3.7 and later,
please obfuscate the scrits by super mode. Or refine the scripts, do not
obfuscate the object method `__del__`. For example

.. code:: python

    class MyData:

        ...

        def lambda_del(self):
           # Real code for method __del__
           ...

        __del__ = lambda_del

Any function name which starts with `lambda_` will not be obfuscated by pyarmor,
in above example, the method `lambda_del` is not obfuscated, so `__del__`  is.

The other solution is not obfuscating the script which includes ``__del__`` by
copying the plain script to overwrite the obfsucated one. Or obfuscate this
script by ``--obf-code 0``.

SystemError: module filename missing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When obfsucating the scripts by super mode, and with outer license, it may
complain of this error if the obfuscated scripts could not find the license file
`license.lic` in the current path.

If `license.lic` is in the other path, set environment variable `PYARMOR_LICNSE`
to it with full path, for example::

    export PYARMOR_LICNSE=/path/to/license.lic

Android protection problem
~~~~~~~~~~~~~~~~~~~~~~~~~~

Most of Android system don't allow load dynamic library in the data path, but
there is one `_pytransform.so` in the runtime package of the obfuscated scripts,
so it may raise exception like this::

    dlopen failed: couldn't map "/storage/emulated/0/dist/_pytransform.so"
    segment 1: Operation not permitted

Please consult Android development document, copy the whole folder `pytransform`
to right location where Android allow to load dynamic library, and set
`PYTHONPATH` or any other way only if Python could find and import it.

libpython3.9.so.1.0: cannot open shared object file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If missing any python core library such as `python39.dll`, `libpython3.9.so`,
etc, make sure this python interpreter is built with `--enable-shared`. By
default, the runtime extension `pytransform` is linked to python dynamic
library.

In Linux platform, try to install `libpython3.9` by `apt` or any other
pacakge manage tool.

Packing Obfuscated Scripts Problem
----------------------------------

The final bundle does not work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First of all, please read the man page of :ref:`pack` completely.

Next make sure the scripts could pack by PyInstaller directly and the final
bundle works. For example::

  pyinstaller foo.py
  dist/foo/foo

If the final bundle complains of no module found, it need some extra PyInstaller
options, please refer to https://pyinstaller.readthedocs.io

Then make sure the obfuscated scripts could work without packing. For example::

  pyarmor obfuscate foo.py
  python dist/foo.py

If both of them OK, remove the output path `dist` and PyInstaller cached path
`build`, then pack the script with ``--debug``::

    pyarmor pack --debug foo.py

The build files will be kept, the patched `foo-patched.spec` could be used by
pyinstaller to pack the obfuscated scripts directly, for example::

    pyinstaller -y --clean foo-patched.spec

Check this patched `.spec` and change options in this `.spec` file, make sure
the final bundle could work.

Also refer to :ref:`repack pyinstaller bundle with obfuscated scripts`, make
sure it works by this way.

No module name pytransform
~~~~~~~~~~~~~~~~~~~~~~~~~~
If report this error as running command `pyarmor pack`:

* Make sure the script specified in the command line is not obfuscated
* Run `pack` with extra option ``--clean`` to remove cached `myscript.spec`::

    pyarmor pack --clean foo.py

NameError: name ‘__pyarmor__’ is not defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Check the traceback to find which script raises this exception, it's helpful to
find the problem:

* If `pytransform.py` or `pytransform/__init__.py` raises this exception. Make
  sure it is not obfuscated, it must be plain script.
* Also check system module `os`, `ctypes`, make sure they're not obfuscated. In
  this case, try to exclude the Python system library path, for example::
    pyarmor pack -x " --exclude venv" foo.py
  More information refer to :ref:`pack`
* Try to only copy your own scripts to an empty path, then pack it in this path.
* If it works in trial version, but fails after pyarmor is registered, try to
  make a :ref:`clean uninstallation`

PyArmor Registration Problem
----------------------------

Purchased pyarmor is not private
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Even obfuscated with purchased version, license from trial version works:

* Make sure command `pyarmor register` shows correct registration information
* Make a :ref:`clean uninstallation`, and register again
* Make sure the current user is same as the one to register pyarmor
* Make sure environment variable `PYARMOR_HOME` is not set
* Try to reboot system.

Could not query registration information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I tried to register in pyarmor with using the command and log::

    ~ % pyarmor register pyarmor-regfile-1.zip
    INFO     PyArmor Version 6.5.2
    INFO     Start to register keyfile: pyarmor-regfile-1.zip
    INFO     Save registration data to: /Users/Jondy/.pyarmor
    INFO     Extracting license.lic
    INFO     Extracting .pyarmor_capsule.zip
    INFO     This keyfile has been registered successfully.

Watching whether I am registered, I got this output::

    ~ % pyarmor register
    INFO     PyArmor Version 6.5.2
    PyArmor Version 6.5.2
    Registration Code: pyarmor-vax-000383
    Because of internet exception, could not query registration information.

Ping domain `api.dashingsoft.com`, make sure ip address is resolved like this::

    ~ % ping api.dashingsoft.com

    PING api.dashingsoft.com (119.23.58.77): 56 data bytes
    Request timeout for icmp_seq 0
    Request timeout for icmp_seq 1

If not, add one line in the ``/etc/hosts``::

    119.23.58.77 pyarmor.dashingsoft.com

Known Issues
------------

Obfuscate scripts in cross platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
From v5.6.0 to v5.7.0, there is a bug for cross platform. The scripts obfuscated
in linux64/windows64/darwin64 don't work after copied to one of this target
platform::

    armv5, android.aarch64, ppc64le, ios.arm64, freebsd, alpine, alpine.arm, poky-i586

License Questions
-----------------
Refer to :ref:`License Questions`

Misc. Questions
---------------

How easy is to recover obfuscated code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If someone tries to break the obfuscation, he first must be an expert in the
field of reverse engineer, and be an expert of Python, who should understand the
structure of code object of python, how python interpreter each instruction. If
someone of them start to reverse, he/she must step by step thousands of machine
instruction, and research the algorithm by machine codes. So it's not an easy
thing to reverse pyarmor.


How to get receipt or invoice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MyCommerce handles all the sales of pyarmor

Please get help from this page for order/recipt/invoice issue

https://www.mycommerce.com/shopper-support/

Or contact "ClientSupport@MyCommerce.com" directly

Would pyarmor be able to provide an evaluation license
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sorry, pyarmor license could be work even offline, so there is no evaluation
license.

Generally the obfuscated scripts could replace the original scripts
seamlessly. Excpet it uses the features changed by pyarmor, here list all
:ref:`The Differences of Obfuscated Scripts`

Most of packages could work with pyarmor, for a few packages, pyamor also works
after patching these packages simplify. Only those packages which visit byte
code or something like this could not work with pyarmor at all.

.. include:: _common_definitions.txt
