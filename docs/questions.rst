.. _questions:

When Things Go Wrong
====================

Turn on debugging output to get more error information::

    python -d pyarmor.py ...
    PYTHONDEBUG=y pyarmor ...

Segment fault
-------------

In the following cases, obfuscated scripts will crash

* Running obfuscated script by the debug version Python
* Obfuscating scripts by Python 2.6 but running the obfuscated scripts by Python 2.7

Could not find `_pytransform`
-----------------------------

Generally, the dynamic library `_pytransform` is in the same path of
obfuscated scripts. It may be:

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

The `license.lic` generated doesn't work
----------------------------------------

The key is that the capsule used to obfuscate scripts must be same as
the capsule used to generate licenses.

If obfuscate scripts by command `pyarmor obfuscate`, :ref:`Global
Capsule` is used implicitly. If obfuscate scripts by command `pyarmor
build`, the project capsule is used.

When generating new licenses for obfuscated scripts, if run command
`pyarmor licenses` in project path, the project capsule is used
implicitly, otherwise :ref:`Global Capsule`.

The :ref:`Global Capsule` will be changed if the trial license file of
|PyArmor| is replaced with normal one, or it's deleted occasionally
(which will be generated implicitly as running command `pyarmor
obfuscate` next time).

In any cases, generating new license file with the different capsule
will not work for the obfuscated scripts before. If the old capsule is
gone, one solution is to obfuscate these scripts by the new capsule
again.

NameError: name '__pyarmor__' is not defined
--------------------------------------------

No :ref:`Bootstrap Code` are executed before importing obfuscated
scripts.

When creating new process by `Popen` or `Process` in mod `subprocess`
or `multiprocessing`, to be sure that :ref:`Bootstrap Code` will be
called before importing any obfuscated code in sub-process. Otherwise
it will raise this exception.

Marshal loads failed when running xxx.py
----------------------------------------

1. Check whether the version of Python to run obfuscated scripts is
   same as the version of Python to obfuscate script

2. Check whether the capsule is generated based on current license of
   PyArmor. Try to move global capsule `~/.pyarmor_capsule.zip` to any
   other path, then obfuscate scripts again.

3. Be sure the capsule used to generated the license file is same as
   the capsule used to obfuscate the scripts. The filename of the
   capsule will be shown in the console when the command is running.

_pytransform can not be loaded twice
------------------------------------

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
--------------------------

Use obfuscated scripts in wrong way, by default all the obfuscated
scripts can't be changed any more.

For more information, refer to :ref:`Restrict Mode`

Protection Fault: unexpected xxx
--------------------------------

Use obfuscated scripts in wrong way, by default, all the runtime files
can't be changed any more. Do not touch the following files

* pytransform.py
* _pytransform.so/.dll/.dylib

For more information, refer to :ref:`Special Handling of Entry Script`

.. How easy is to recover obfuscated code?:

    If someone tries to break the obfuscation, he first must be an
    expert in the field of reverse engineer, and be an expert of
    Python, who should understand the structure of code object of
    python, how python interpreter each instruction. If someone of
    them start to reverse, he/she must step by step thousands of
    machine instruction, and research the algorithm by machine
    codes. So it's not an easy thing to reverse pyarmor.

.. include:: _common_definitions.txt
