# Downloads for Pyarmor Prebuilt Dynamic Library #

Latest version: **4.0.4**

Build date: 2018-12-16

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

* [macosx_x86_64](http://pyarmor.dashingsoft.com/downloads/platforms/macosx_x86_64/_pytransform.dylib)

## Embedded Platforms

* [Armv7](http://pyarmor.dashingsoft.com/downloads/platforms/armv7/_pytransform.so)

    * 32-bit Armv7 Cortex-A, hard-float, little-endian
    * Cross compile by https://releases.linaro.org/components/toolchain/binaries/latest-7/arm-linux-gnueabihf/gcc-linaro-7.3.1-2018.05-x86_64_arm-linux-gnueabihf.tar.xz
    
* [Armv8 32-bit](http://pyarmor.dashingsoft.com/downloads/platforms/armv8.32-bit/_pytransform.so)

    * 32-bit Armv8 Cortex-A, hard-float, little-endian
    * Cross compile by https://releases.linaro.org/components/toolchain/binaries/latest-7/armv8l-linux-gnueabihf/gcc-linaro-7.3.1-2018.05-x86_64_armv8l-linux-gnueabihf.tar.xz
    
* [Armv8 64-bit](http://pyarmor.dashingsoft.com/downloads/platforms/armv8.64-bit/_pytransform.so)

    * 64-bit Armv8 Cortex-A, little-endian
    * Cross compile by https://releases.linaro.org/components/toolchain/binaries/latest-7/aarch64-linux-gnu/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz
    
* [Raspberry Pi](http://pyarmor.dashingsoft.com/downloads/platforms/raspberrypi/_pytransform.so)

    * Apply for RPI serials https://www.raspberrypi.org
    * Cross compile by https://github.com/raspberrypi/tools

* [Banana Pi](http://pyarmor.dashingsoft.com/downloads/platforms/bananapi/_pytransform.so)

    * Apply for BPI serials http://www.banana-pi.com/eindex.asp
    * Cross compile by https://github.com/BPI-SINOVOIP/BPI-M3-bsp.git

* [Orange Pi](http://pyarmor.dashingsoft.com/downloads/platforms/orangepi/_pytransform.so)

    * Apply for OPI serials http://www.orangepi.org/
    * Cross compile by https://github.com/orangepi-xunlong/OrangePiH5_toolchain

* [NVIDIA Jetson](http://pyarmor.dashingsoft.com/downloads/platforms/nvidia_jetson/_pytransform.so)

    * Quad ARM® A57/2 MB L2
    * Cross compile by https://developer.nvidia.com/embedded/dlc/l4t-gcc-toolchain-64-bit-31-1-0
    * Not https://developer.nvidia.com/embedded/dlc/l4t-gcc-toolchain-32-bit-28-2-ga

* [TS-4600/TS-7600](http://pyarmor.dashingsoft.com/downloads/platforms/ts-4600/_pytransform.so)

    * Apply for ts-4600/ts-7600 https://wiki.embeddedarm.com/wiki/TS-4600 / https://wiki.embeddedarm.com/wiki/TS-7600
    * Cross compile by https://github.com/embeddedarm/linux-2.6.35.3-imx28

## Change Logs

## 4.0.4

* Fix EXTENDED_ARG instruction crash issue for Python3.6

## 4.0.3

* Fix stack overflow issue when decoding license file

## 4.0.2

* Add option `g_use_trial_license`
* Check trial license only if `g_use_trial_license` is set

## 4.0.1

* Add anti-debug code for linux, window, macosx

## 3.3.11

* Fix license issue when binding to fixed file

## 3.3.10

* Set `c_profilefunc` and `c_tracefunc` to NULL for autowrap mode

## 3.3.9

* Increae co_stacksize to fix segmentation fault issues in `asyncio`, `typing` modules
* Do not obfuscate code object which is CO_ASYNC_GENERATOR

### 3.3.8

* Fix windows 10 issue: access violation reading 0x000001ED00000000

### 3.3.7

* Fix module attribute `__file__` is not really path in module code

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
