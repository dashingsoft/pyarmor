# Downlaods for Pyarmor Prebuilt Dynamic Library #

Latest version: **3.3.6**

Build date: 2018-4-16

The core of Pyarmor is written by C, the prebuilt dynamic libraries
include the common platforms and some embeded platforms. It's not
difficult to build for any other platform, even for embeded system
(the only dependency is libc).

Contact <jondy.zhao@gmail.com> if you'd like to run encrypted scripts
in other platform.

## Platforms

The name of platform is decomposed from distutils.util.get_platform()

* [win32](http://pyarmor.dashingsoft.com/downloads/platforms/win32/_pytransform.dll)

* [win_amd64](http://pyarmor.dashingsoft.com/downloads/platforms/win_amd64/_pytransform.dll)

* [linux_i386](http://pyarmor.dashingsoft.com/downloads/platforms/linux_i386/_pytransform.so)

* [linux_x86_64](http://pyarmor.dashingsoft.com/downloads/platforms/linux_x86_64/_pytransform.so)

* [macosx_intel](http://pyarmor.dashingsoft.com/downloads/platforms/macosx_intel/_pytransform.dylib)

## Embedded Platforms

* [Raspberry Pi](http://pyarmor.dashingsoft.com/downloads/platforms/raspberrypi/_pytransform.so)

    * Apply for RPI serials https://www.raspberrypi.org
    * Cross compile by https://github.com/raspberrypi/tools

* [Banana Pi](http://pyarmor.dashingsoft.com/downloads/platforms/bananapi/_pytransform.so)

    * Apply for BPI serials http://www.banana-pi.com/eindex.asp
    * Cross compile by https://github.com/BPI-SINOVOIP/BPI-M3-bsp.git

* [TS-4600/TS-7600](http://pyarmor.dashingsoft.com/downloads/platforms/ts-4600/_pytransform.so)

    * Apply for ts-4600/ts-7600 https://wiki.embeddedarm.com/wiki/TS-4600 / https://wiki.embeddedarm.com/wiki/TS-7600
    * Cross compile by https://github.com/embeddedarm/linux-2.6.35.3-imx28

## Change Logs

### 3.3.6

* Fix auto-wrap mode crash in win32/linux32 platforms by increasing `co->stacksize`
* Remove `func.__refcalls__` from `__wraparmor__`

### 3.3.5

* Fix shared code object issue in `__wraparmor__`

### 3.3.4

* Clear frame as long as `tb` is not `Py_None` in `__wraparmor__`
* Generator will not be obfucated in `__wraparmor__`

### 3.3.3

* Add co_flag `CO_WRAPARMOR` (0x20000000), set it when call `__wraparmor__(func)`
* Refine getter of `frame.f_locals`, return an empty dictionary if `CO_WRAPARMOR` is set

### 3.3.2

* Init getter of `frame.f_locals` on first time `__wraparmor__` is called

### 3.3.1

* `__wraparmor__` only clears frame of `wrapper` and wrapped function when exception raised.
* Refine setter of `frame.f_locals`, only `wrapper` and wrapped function return empty dictionary.

### 3.3.0

* Add extra argument `tb` when call `__wraparmor__` in decorator, None if no exception.
* Clear all frames in traceback by calling method `tp_clear` of `PyFrameType` when raise exception.
* Custom setter of `f_locals` for `PyFrameType`, return an empty dictionary always.

### 3.2.9

* Do not touch `frame.f_locals` in `__wraparmor__`, let decorator able to do any thing.

### 3.2.8

* Fix fast mode crashed problem in linux occasionally, because of copying overlapped memory.
* Remove freevar `func` from `frame.f_locals` when raise exception in `__wraparmor__`
* Set exception attribute `__traceback__` to `None` for Python3 when raise exception in `__wraparmor__`

### 3.2.7

* Set `__file__` to real filename when importing obfuscated scripts, keep co_filename as `<frozen modname>`

### 3.2.6

* Obfuscate core memebers of code object in `__wraparmor__`.

### 3.2.5

* Refine frozen module name when obfuscating scripts, remove dotted name if it's not a package.

### 3.2.4

* Strip `__init__` from filename when obfuscating scripts, replace it with package name.

### 3.2.3

* Remove bracket from filename when obfuscating scripts, and add dotted preifx.

### 3.2.2

* Change filename to `<frozen [modname]>` when obfuscate scripts, other than original filename

### 3.2.1

* Change armor code, set module attribute `__file__` to filename in target machine other than in build machine.

* Builtins function `__wraparmor__` only can be used in the decorator `wraparmor`

### 3.2.0

* Clear CO_ENCRYPT flag after byte-code is restored.

* Add builtin `__wraparmor__` to obfuscate func_code when function returns.

### 3.1.9

* DO NOT run obfuscated scripts when Py_InteractiveFlag or Py_InspectFlag is set

* Add restrict mode to avoid obfuscated scripts observed from no obfuscated scripts
