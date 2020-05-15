.. _support platforms:

Support Platfroms
=================

The core of PyArmor is written by C, the prebuilt dynamic libraries include the
common platforms and some embeded platforms.

Some of them are distributed with PyArmor source package, in these
platforms, `pyarmor` could run without downloading anything. Refer to
`Prebuilt Libraries Distributed with PyArmor`_.

For the other platforms, `pyarmor` first searches path
``~/.pyarmor/platforms/SYSTEM/ARCH``, ``SYSTEM.ARCH`` is one of
`Standard Platform Names`_. If there is none, PyArmor will download it
from remote server automatically. Refer to `The Others Prebuilt
Libraries For PyArmor`_.

Since v6.2.0, :ref:`super mode` is introduced, it uses the extension module
``pytransform`` directly. All the prebuilt extension files list in the table
`The Prebuilt Extensions For Super Mode`_

For all the latest platforms, refer to
https://github.com/dashingsoft/pyarmor-core/blob/master/platforms/index.json

There may be serveral dynamic libraries with different features in each
platform. The platform name with feature number suffix combines an unique
name.

Each feature has its own bit:

  - 1: Anti-Debug
  - 2: JIT
  - 4: ADV, advanced mode
  - 8: SUPER, super mode

For example, ``windows.x86_64.7`` means anti-debug(1), JIT(2) and andvanced
mode(4) supported, ``windows.x86_64.0`` means no any feature, so highest speed.

Note that zero feature dynamic library isn't compatible with any featured
library. For security reason, the zero feature library uses different alogrithm
to obfuscate the scripts. So the platform ``windows.x86_64.7`` can not share the
same obfuscated scripts with platform ``linux.armv7.0``.

In some platforms, `pyarmor` doesn't know it but there is available dynamic
library in the table `The Others Prebuilt Libraries For PyArmor`_. Just download
it and save it in the path ``~/.pyarmor/platforms/SYSTEM/ARCH``, this command
``pyarmor -d download`` will also display this path at the beginning. It's
appreicated to send this platform information to jondy.zhao@gmail.com so that it
could be recognized by `pyarmor` automatically.

This script will display the required information by `pyarmor`:

.. code-block:: python

   from platform import *
   print('system name: %s' % system())
   print('machine: %s' % machine())
   print('processor: %s' % processor())
   print('aliased terse platform: %s' % platform(aliased=1, terse=1))

   if system().lower().startswith('linux'):
       print('libc: %s' % libc_ver())
       print('distribution: %s' % linux_distribution())

Contact jondy.zhao@gmail.com if you'd like to run PyArmor in other platform.

.. _standard platform names:

Standard Platform Names
-----------------------

These names are used in the command :ref:`obfuscate`, :ref:`build`,
:ref:`runtime`, :ref:`download` to specify platform.

* windows.x86
* windows.x86_64
* linux.x86
* linux.x86_64
* darwin.x86_64
* vs2015.x86
* vs2015.x86_64
* linux.arm
* linux.armv6
* linux.armv7
* linux.aarch32
* linux.aarch64
* android.aarch64
* android.armv7 (New in 5.9.3)
* uclibc.armv7 (New in 5.9.4)
* linux.ppc64
* darwin.arm64
* freebsd.x86_64
* alpine.x86_64
* alpine.arm
* poky.x86

Platform Tables
---------------

.. list-table:: Table-1. Prebuilt Libraries Distributed with PyArmor
   :widths: 10 10 10 20 10 40
   :name: Prebuilt Libraries Distributed with PyArmor
   :header-rows: 1

   * - Name
     - Platform
     - Arch
     - Features
     - Download
     - Description
   * - windows.x86
     - Windows
     - i686
     - Anti-Debug, JIT, ADV
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/latest/win32/_pytransform.dll>`_
     - Cross compile by i686-pc-mingw32-gcc in cygwin
   * - windows.x86_64
     - Windows
     - AMD64
     - Anti-Debug, JIT, ADV
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/latest/win_amd64/_pytransform.dll>`_
     - Cross compile by x86_64-w64-mingw32-gcc in cygwin
   * - linux.x86
     - Linux
     - i686
     - Anti-Debug, JIT, ADV
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/linux_i386/_pytransform.so>`_
     - Built by GCC
   * - linux.x86_64
     - Linux
     - x86_64
     - Anti-Debug, JIT, ADV
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/linux_x86_64/_pytransform.so>`_
     - Built by GCC
   * - darwin.x86_64
     - MacOSX
     - x86_64, intel
     - Anti-Debug, JIT, ADV
     - `_pytransform.dylib <http://pyarmor.dashingsoft.com/downloads/latest/macosx_x86_64/_pytransform.dylib>`_
     - Built by CLang with MacOSX10.11


.. list-table:: Table-2. The Others Prebuilt Libraries For PyArmor
   :name: The Others Prebuilt Libraries For PyArmor
   :widths: 10 10 10 20 10 40
   :header-rows: 1

   * - Name
     - Platform
     - Arch
     - Features
     - Download
     - Description
   * - vs2015.x86
     - Windows
     - x86
     -
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/latest/vs2015/x86/_pytransform.dll>`_
     - Built by VS2015
   * - vs2015.x86_64
     - Windows
     - x64
     -
     - `_pytransform.dll <http://pyarmor.dashingsoft.com/downloads/latest/vs2015/x64/_pytransform.dll>`_
     - Built by VS2015
   * - linxu.arm
     - Linux
     - armv5
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/armv5/_pytransform.so>`_
     - 32-bit Armv5 (arm926ej-s)
   * - linxu.armv6
     - Linux
     - armv6
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/linux.armv6.0/_pytransform.so>`_
     - 32-bit Armv6 (-marm -march=armv6 -mfloat-abi=hard)
   * - linux.armv7
     - Linux
     - armv7
     - Anti-Debug, JIT
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/armv7/_pytransform.so>`_
     - 32-bit Armv7 Cortex-A, hard-float, little-endian
   * - linux.aarch32
     - Linux
     - aarch32
     - Anti-Debug, JIT
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/armv8.32-bit/_pytransform.so>`_
     - 32-bit Armv8 Cortex-A, hard-float, little-endian
   * - linux.aarch64
     - Linux
     - aarch64
     - Anti-Debug, JIT
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/armv8.64-bit/_pytransform.so>`_
     - 64-bit Armv8 Cortex-A, little-endian
   * - linux.ppc64
     - Linux
     - ppc64le
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/ppc64le/_pytransform.so>`_
     - For POWER8
   * - darwin.arm64
     - iOS
     - arm64
     -
     - `_pytransform.dylib <http://pyarmor.dashingsoft.com/downloads/latest/ios.arm64/_pytransform.dylib>`_
     - Built by CLang with iPhoneOS9.3.sdk
   * - freebsd.x86_64
     - FreeBSD
     - x86_64
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/freebsd/_pytransform.so>`_
     - Not support harddisk serial number
   * - alpine.x86_64
     - Alpine Linux
     - x86_64
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/alpine/_pytransform.so>`_
     - Built with musl-1.1.21 for Docker
   * - alpine.arm
     - Alpine Linux
     - arm
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/alpine.arm/_pytransform.so>`_
     - Built with musl-1.1.21, 32-bit Armv5T, hard-float, little-endian
   * - poky.x86
     - Inel Quark
     - i586
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/intel-quark/_pytransform.so>`_
     - Cross compile by i586-poky-linux
   * - android.aarch64
     - Android
     - aarch64
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/android.aarch64/_pytransform.so>`_
     - Build by android-ndk-r20/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang
   * - android.armv7
     - Android
     - armv7l
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/android.armv7.0/_pytransform.so>`_
     - Build by android-ndk-r20/toolchains/llvm/prebuilt/linux-x86_64/bin/armv7a-linux-android21-clang
   * - uclibc.armv7
     - Linux
     - armv7l
     -
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/uclibc.armv7.0/_pytransform.so>`_
     - Build by armv7-buildroot-uclibceabihf-gcc

.. list-table:: Table-3. The Prebuilt Extensions For Super Mode
   :name: The Prebuilt Extensions For Super Mode
   :widths: 10 10 10 20 10 40
   :header-rows: 1

   * - Name
     - Platform
     - Arch
     - Features
     - Download
     - Description
   * - darwin.x86_64.11.py37
     - MacOSX
     - x86_64, intel
     - Anti-Debug, JIT, SUPER
     - `_pytransform.cpython-37m-darwin.so <http://pyarmor.dashingsoft.com/downloads/latest/darwin.x86_64.11.py37/_pytransform.cpython-37m-darwin.so>`_
     - Built by CLang with MacOSX10.11
   * - darwin.x86_64.11.py27
     - MacOSX
     - x86_64, intel
     - Anti-Debug, JIT, SUPER
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/latest/darwin.x86_64.11.py27/_pytransform.so>`_
     - Built by CLang with MacOSX10.11
