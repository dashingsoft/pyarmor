# Downlaods for Pyarmor Prebuilt Dynamic Library #

Latest version: **3.2.1**

Build date: 2018-3-16

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

### 3.2.1

* Change armor code, set module attribute ```__file__``` to filename in target machine other than in build machine.

### 3.2.0

* Clear CO_ENCRYPT flag after byte-code is restored.

* Add builtin ```__wraparmor__``` to obfuscate func_code when function returns.

### 3.1.9

* DO NOT run obfuscated scripts when Py_InteractiveFlag or Py_InspectFlag is set

* Add restrict mode to avoid obfuscated scripts observed from no obfuscated scripts
