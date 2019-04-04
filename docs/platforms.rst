.. _pyarmor prebuilt dynamic libraries:

PyArmor Prebuilt Dynamic Libraries
==================================

The core of PyArmor is written by C, the prebuilt dynamic libraries
include the common platforms and some embeded platforms.

Some of them are distributed with PyArmor package, refer to
`Prebuilt Libraries Distributed with PyArmor`_.

Some of them are not, refer to `All The Others Prebuilt Libraries For
PyArmor`_. In these platforms, in order to run pyarmor, first
download the corresponding prebuilt dynamic library, then put it in
the installed path of PyArmor package.

Contact <jondy.zhao@gmail.com> if you'd like to run PyArmor in other
platform.

Latest version: **5.1.5**

Build date: 2019-02-19

.. _prebuilt libraries distributed with pyarmor:

Prebuilt Libraries Distributed with PyArmor
-------------------------------------------

.. list-table:: Table-1. Prebuilt Libraries Distributed with PyArmor
   :widths: 10 10 20 60
   :header-rows: 1

   * - OS
     - Arch
     - Download
     - Description
   * - Windows
     - i686
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/platforms/win32/_pytransform.dll>`_
     - Cross compile by i686-pc-mingw32-gcc in cygwin
   * - Windows
     - AMD64
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/platforms/win_amd64/_pytransform.dll>`_
     - Cross compile by x86_64-w64-mingw32-gcc in cygwin
   * - Linux
     - i686
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/linux_i386/_pytransform.so>`_
     - Built by GCC
   * - Linux
     - x86_64
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/linux_x86_64/_pytransform.so>`_
     - Built by GCC
   * - MacOSX
     - x86_64, intel
     - `_pytransform.dylib <http://pyarmor.dashingsoft.com/downloads/platforms/macosx_x86_64/_pytransform.dylib>`_
     - Built by CLang with MacOSX10.11
   * - Linux
     - armv7
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/armv7/_pytransform.so>`_
     - Cross compile by GCC in ubuntu 16.04 (x86_64)
       32-bit Armv7 Cortex-A, hard-float, little-endian
   * - Linux
     - aarch64
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/armv8.64-bit/_pytransform.so>`_
     - Cross compile by GCC in ubuntu 16.04 (x86_64)
       64-bit Armv8 Cortex-A, little-endian

.. _all the others prebuilt libraries for pyarmor:

All The Others Prebuilt Libraries For PyArmor
---------------------------------------------

.. list-table:: Table-2. All The Others Prebuilt Libraries For PyArmor
   :widths: 10 10 20 60
   :header-rows: 1

   * - OS
     - Arch
     - Download
     - Description
   * - Windows
     - x86
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/platforms/vs2015/x86/_pytransform.dll>`_
     - Built by VS2015
   * - Windows
     - x64
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/platforms/vs2015/x64/_pytransform.dll>`_
     - Built by VS2015
   * - Linux
     - armv5
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/armv5/_pytransform.so>`_
     - Cross compile by GCC in ubuntu 16.04 (x86_64)
       32-bit Armv5 (arm926ej-s)
   * - Linux
     - aarch32
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/armv8.32-bit/_pytransform.so>`_
     - Cross compile by GCC in ubuntu 16.04 (x86_64)
       32-bit Armv8 Cortex-A, hard-float, little-endian
   * - Linux
     - ppc64le
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/ppc64le/_pytransform.so>`_
     - Cross compile by `gcc-powerpc64le-linux-gnu` in ubuntu 16.04 (x86_64) for POWER8
   * - iOS
     - arm64
     - `_pytransform.dylib <http://pyarmor.dashingsoft.com/downloads/platforms/ios.arm64/_pytransform.dylib>`_
     - Built by CLang with iPhoneOS9.3.sdk
   * - FreeBSD
     - x86_64
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/freebsd/_pytransform.so>`_
     - Cross compile by GCC in ubuntu 16.04 (x86_64)
       Not support harddisk serial number
   * - Alpine Linux
     - x86_64
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/alpine/_pytransform.so>`_
     - Cross compile by `musl-cross-make <https://github.com/richfelker/musl-cross-make>` in ubuntu 16.04 (x86_64)
       with musl-1.1.21

Change Logs
===========

5.1.5
-----

* Refine error message when checking license failed.

5.1.4
-----

* Improve the security of dynamic library.

5.1.3
-----

* Fix issue: in restrict mode the bootstrap code in `__init__.py` will raise exception.

5.1.2
-----

* Improve security of PyArmor self

5.1.1
-----

* Remove runtime files `pyshield.key`, `pyshield.lic` and `product.key`, use `pytransform.py` instead
* Refine `set_option`
* Add new api `generate_pytransform_key`
* Add new api `encrypt_code_object`

5.0.3
-----

* Fix newline issues for Python 26/30/31 in windows

5.0.2
-----

* Add `get_hd_info` to get hardware information, make others `get_xxx` static
* Refine runtime error handle, and call `Py_Exit` quit if fatal error occurred

5.0.1
-----

Thanks to GNU lightning, from this version, the core routines are
protected by JIT technicals. That is to say, there is no binary code
in static file for core routines, they're generated in runtime.

Fixed issues:

* The module `multiprocessing` starts new process failed: `AttributeError: '__main__' object has no attribute 'f'`

4.0.5
-----

* Remove memcpy wrapper for linux platform

4.0.4
-----

* Fix EXTENDED_ARG instruction crash issue for Python3.6

4.0.3
-----

* Fix stack overflow issue when decoding license file

4.0.2
-----

* Add option `g_use_trial_license`
* Check trial license only if `g_use_trial_license` is set

4.0.1
-----

* Add anti-debug code for linux, window, macosx

3.3.11
------

* Fix license issue when binding to fixed file

3.3.10
------

* Set `c_profilefunc` and `c_tracefunc` to NULL for autowrap mode

3.3.9
-----

* Increae co_stacksize to fix segmentation fault issues in `asyncio`, `typing` modules
* Do not obfuscate code object which is CO_ASYNC_GENERATOR

3.3.8
-----

* Fix windows 10 issue: access violation reading 0x000001ED00000000

3.3.7
-----

* Fix module attribute `__file__` is not really path in module code

3.3.6
-----

* Fix auto-wrap mode crash in win32/linux32 platforms by increasing `co->stacksize`
* Remove `func.__refcalls__` from `__wraparmor__`

3.3.5
-----

* Fix shared code object issue in `__wraparmor__`

3.3.4
-----

* Clear frame as long as `tb` is not `Py_None` in `__wraparmor__`
* Generator will not be obfucated in `__wraparmor__`

3.3.3
-----

* Add co_flag `CO_WRAPARMOR` (0x20000000), set it when call `__wraparmor__(func)`
* Refine getter of `frame.f_locals`, return an empty dictionary if `CO_WRAPARMOR` is set

3.3.2
-----

* Init getter of `frame.f_locals` on first time `__wraparmor__` is called

3.3.1
-----

* `__wraparmor__` only clears frame of `wrapper` and wrapped function when exception raised.
* Refine setter of `frame.f_locals`, only `wrapper` and wrapped function return empty dictionary.

3.3.0
-----

* Add extra argument `tb` when call `__wraparmor__` in decorator, None if no exception.
* Clear all frames in traceback by calling method `tp_clear` of `PyFrameType` when raise exception.
* Custom setter of `f_locals` for `PyFrameType`, return an empty dictionary always.

3.2.9
-----

* Do not touch `frame.f_locals` in `__wraparmor__`, let decorator able to do any thing.

3.2.8
-----

* Fix fast mode crashed problem in linux occasionally, because of copying overlapped memory.
* Remove freevar `func` from `frame.f_locals` when raise exception in `__wraparmor__`
* Set exception attribute `__traceback__` to `None` for Python3 when raise exception in `__wraparmor__`

3.2.7
-----

* Set `__file__` to real filename when importing obfuscated scripts, keep co_filename as `<frozen modname>`

3.2.6
-----

* Obfuscate core memebers of code object in `__wraparmor__`.

3.2.5
-----

* Refine frozen module name when obfuscating scripts, remove dotted name if it's not a package.

3.2.4
-----

* Strip `__init__` from filename when obfuscating scripts, replace it with package name.

3.2.3
-----

* Remove bracket from filename when obfuscating scripts, and add dotted preifx.

3.2.2
-----

* Change filename to `<frozen [modname]>` when obfuscate scripts, other than original filename

3.2.1
-----

* Change armor code, set module attribute `__file__` to filename in target machine other than in build machine.
* Builtins function `__wraparmor__` only can be used in the decorator `wraparmor`

3.2.0
-----

* Clear CO_ENCRYPT flag after byte-code is restored.
* Add builtin `__wraparmor__` to obfuscate func_code when function returns.

3.1.9
-----

* DO NOT run obfuscated scripts when Py_InteractiveFlag or Py_InspectFlag is set
* Add restrict mode to avoid obfuscated scripts observed from no obfuscated scripts
