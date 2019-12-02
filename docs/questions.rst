.. _questions:

When Things Go Wrong
====================

When there is in trouble, try to solve it by these ways.

As running ``pyarmor``:

* Check the console output, is there any wrong path, or any odd information
* Run `pyarmor` with debug option ``-d`` to get more information. For example::

      pyarmor -d obfuscate --recurisve foo.py
      PYTHONDEBUG=y pyarmor -d obfuscate --recurisve foo.py

As running the obfuscated scripts:

* Turn on Python debug option by ``-d`` to print more information. For example::

      python -d obf_foo.py
      PYTHONDEBUG=y python obf_foo.py

After python debug option is on, there will be a log file `pytransform.log`
generated in the current path, which includes more debug information.


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

   From v5.7.9, this patch is not required for any linux/x86_64 platform, for example, CentOS6.

   And the scripts also could be obfuscated in other platform by this command::

     pyarmor obfuscate --platform centos6.x86_64 foo.py


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
mode. So the code object is left as it's, but all the other code
objects still are obfuscated.

In later version, it will be obfuscated with non wrap mode.

In current version add some unused code in this function so that the
operand isn't the critical value may avoid this warning.

.. note::

   This has been fixed in v5.5.0.


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
1. Check whether the version of Python to run obfuscated scripts is
   same as the version of Python to obfuscate script

2. Run obfuscated script by `python -d` to show more error message.

3. Be sure the capsule used to generated the license file is same as
   the capsule used to obfuscate the scripts. The filename of the
   capsule will be shown in the console when the command is running.


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


Packing Obfuscated Scripts Problem
----------------------------------

No module name pytransform
~~~~~~~~~~~~~~~~~~~~~~~~~~
If report this error as running command `pyarmor pack`:

* Make sure the script specified in the command line is not obfuscated
* Run `pack` with extra option ``--clean`` to remove cached `myscript.spec`::

    pyarmor pack --clean foo.py


PyArmor Registration Problem
----------------------------

Purchased pyarmor is not private
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Even obfuscated with purchased version, license from trial version works:

* Make sure command `pyarmor register` shows correct registration information
* Make sure :ref:`global capsule` file `~/.pyarmor_capsule.zip` is same as the one in the keyfile `pyarmor-regfile-1.zip`
* Try to reboot system.


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

.. include:: _common_definitions.txt
