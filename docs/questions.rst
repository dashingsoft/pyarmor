.. _questions:

When Things Go Wrong
====================

When there is in trouble, check the output log message, it may be helpful to
find the problem. And try these ways

As running ``pyarmor``:

* Check the console output, is there any wrong path, or any odd information
* Run `pyarmor` with debug option ``-d`` to get more information. For example::

      pyarmor -d obfuscate --recursive foo.py

As running the obfuscated scripts:

* Turn on Python debug option by ``-d`` to print more information. For example::

      python -d obf_foo.py

After python debug option is on, there will be a log file `pytransform.log`
generated in the current path, which includes more debug information.

.. note::

   There are a lot of reporeted `issues`_, search here first try to find same
   issue.


Segment fault
-------------

In the following cases, obfuscated scripts will crash

* Running obfuscated script by the debug version Python
* Obfuscating scripts by Python 2.6 but running the obfuscated scripts by Python 2.7

After PyArmor 5.5.0, some machines may be crashed because of advanced mode. A
quick workaround is to disable advanced mode by editing the file
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

Still doesn't work, report an issue_


ERROR: Unsupport platform linux.xxx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In some machines `pyarmor` could not recognize the platform and raise
error. If there is available dynamic library in the table :ref:`The
Others Prebuilt Libraries For PyArmor`. Just download it and save it
in the path ``~/.pyarmor/platforms/SYSTEM/ARCH``, this command
``pyarmor -d download`` will also display this path at the beginning.

If there is no any available one, contact jondy.zhao@gmail.com if
you'd like to run `pyarmor` in this platform.


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
No :ref:`Bootstrap Code` are executed before importing obfuscated
scripts.

When creating new process by `Popen` or `Process` in mod `subprocess`
or `multiprocessing`, to be sure that :ref:`Bootstrap Code` will be
called before importing any obfuscated code in sub-process. Otherwise
it will raise this exception.


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

For more information, refer to :ref:`Special Handling of Entry Script`


Run obfuscated scripts reports: Invalid input packet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
create boot script to catch exception raised by the obfuscated scripts. For
example

.. code:: python

   try:
       import obfuscated_script
   except Exception as e:
       print('something is wrong')

The disadvantage is that exceptions even raised by normal scripts are catched
either.

undefined symbol: PyUnicodeUCS4_AsUTF8String
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If Python interpreter is built with UCS2, it may raises this issue when running
super mode obufscated scripts. In this case, try to obfuscate script with
platform ``centos6.x86_64``, it's built with UCS2. For example::

    pyarmor obfuscate --advanced 2 --platform centos6.x86_64 foo.py


Packing Obfuscated Scripts Problem
----------------------------------

The final bundle does not work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First make sure the scripts could pack by PyInstaller directly and the final
bundle works.

Then make sure the obfuscated scripts could work without packing.

If both of them OK, remove the output path `dist` and PyInstaller cached path
`build`, then pack the script with ``--debug``::

    pyarmor pack --debug foo.py

The build files will be kept, the patched `foo-patched.spec` could be used by
pyinstaller to pack the obfuscated scripts directly, for example::

    pyinstaller -y --clean foo-patched.spec

Check this patched `.spec` and change options in this `.spec` file, make sure
the final bundle could work.

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
* Also check system module `os`, `ctypes`, make sure they're not obfuscated.
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

.. include:: _common_definitions.txt
