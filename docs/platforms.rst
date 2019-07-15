.. _support platforms:

Support Platfroms
=================

The core of PyArmor is written by C, the prebuilt dynamic libraries
include the common platforms and some embeded platforms.

Some of them are distributed with PyArmor package, refer to
`Prebuilt Libraries Distributed with PyArmor`_.

Some of them are not, refer to `All The Others Prebuilt Libraries For
PyArmor`_. In these platforms, in order to run pyarmor, first
download the corresponding prebuilt dynamic library, then put it in
the installed path of PyArmor package.

Contact jondy.zhao@gmail.com if you'd like to run PyArmor in other
platform.

.. list-table:: Table-1. Prebuilt Libraries Distributed with PyArmor
   :widths: 10 10 20 60
   :name: Prebuilt Libraries Distributed with PyArmor
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

.. list-table:: Table-2. All The Others Prebuilt Libraries For PyArmor
   :name: All The Others Prebuilt Libraries For PyArmor
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
     - 32-bit Armv5 (arm926ej-s)
   * - Linux
     - armv7
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/armv7/_pytransform.so>`_
     - 32-bit Armv7 Cortex-A, hard-float, little-endian
   * - Linux
     - aarch32
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/armv8.32-bit/_pytransform.so>`_
     - 32-bit Armv8 Cortex-A, hard-float, little-endian
   * - Linux
     - aarch64
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/armv8.64-bit/_pytransform.so>`_
     - 64-bit Armv8 Cortex-A, little-endian
   * - Linux
     - ppc64le
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/ppc64le/_pytransform.so>`_
     - For POWER8
   * - iOS
     - arm64
     - `_pytransform.dylib <http://pyarmor.dashingsoft.com/downloads/platforms/ios.arm64/_pytransform.dylib>`_
     - Built by CLang with iPhoneOS9.3.sdk
   * - FreeBSD
     - x86_64
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/freebsd/_pytransform.so>`_
     - Not support harddisk serial number
   * - Alpine Linux
     - x86_64
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/alpine/_pytransform.so>`_
     - Built with musl-1.1.21 for Docker
   * - Inel Quark
     - i586
     - `_pytransform.so <http://pyarmor.dashingsoft.com/downloads/platforms/intel-quark/_pytransform.so>`_
     - Cross compile by i586-poky-linux
