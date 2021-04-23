.. _support platforms:

Support Platforms
=================

The core of PyArmor is written by C, the prebuilt dynamic libraries
include the common platforms and some embeded platforms.

Some of them are distributed with PyArmor source package. In these platforms,
`pyarmor` could run without downloading anything::

    windows.x86
    windows.x86_64
    linux.x86
    linux.x86_64
    darwin.x86_64

For the other platforms, when first run `pyarmor`, it will download the
corresponding dynamic library from the remote server automatically, and save it
to ``~/.pyarmor/platforms/SYSTEM/ARCH/N/``, ``SYSTEM.ARCH`` is one of `Standard
Platform Names`_. ``N`` is `features`_ number, which explained below. Here list
all the other supported platforms::

    darwin.aarch64
    ios.aarch64
    linux.arm
    linux.armv6
    linux.armv7
    linux.aarch32
    linux.aarch64
    linux.ppc64
    android.aarch64
    android.armv7
    android.x86
    android.x86_64
    uclibc.armv7
    centos6.x86_64
    freebsd.x86_64
    musl.x86_64
    musl.arm
    musl.mips32
    poky.x86

For Linux platforms, the first identifier stands for libc used in this
platform. ``linux`` stands for ``glibc``, ``centos6`` for ``glibc`` < 2.14,
``android`` for static libc, ``musl`` and ``uclibc`` as it is. Note that Docker
based on Alpine Linux, its identifier is ``musl``, not ``linux``.

:ref:`Super mode` uses the extension module ``pytransform`` directly, and it
will be saved in the path ``~/.pyarmor/platforms/SYSTEM/ARCH/N/pyXY``. For
example, ``linux/x86_64/11/py38``.

.. list-table:: Table-3. The Prebuilt Extensions For Super Mode
   :name: The Prebuilt Extensions For Super Mode
   :header-rows: 1

   * - Name
     - Arch
     - Feature
     - Python Versions
     - Remark
   * - darwin
     - x86_64
     - 11
     - 27, 37, 38, 39
     -
   * - darwin
     - aarch64
     - 11
     - 38, 39
     - Apple Silicon
   * - ios
     - aarch64
     - 11
     - 38, 39
     -
   * - linux
     - x86, x86_64, aarch64, aarch32, armv7
     - 11
     - 27, 37, 38, 39
     -
   * - centos6
     - x86_64
     - 11
     - 27
     - Linux with glibc < 2.14 and UCS2
   * - windows
     - x86, x86_64
     - 11, 25
     - 27, 37, 38, 39
     -

For all the latest platforms, refer to `pyarmor-core/platforms/index.json <https://github.com/dashingsoft/pyarmor-core/blob/master/platforms/index.json>`_

In some platforms, `pyarmor` doesn't know its standard name, just download the
right one and save it in the path ``~/.pyarmor/platforms/SYSTEM/ARCH/N/``.  Run
the command ``pyarmor -d download`` in this platform, and check the output log,
it can help you find where to save the download file.

If you're not sure this dynamic library is right for this platform, check it by
``ldd`` to print the dependent system libraries. For example::

    ldd /path/to/_pytransform.so

If there is no anyone available and you'd like to run `pyarmor` in this
platform, click here `submit a feature request for new platform
<https://github.com/dashingsoft/pyarmor/issues>`_

.. _features:

Features
--------

There may be serveral dynamic libraries with different features in each
platform. The platform name with feature number combines an unique name.

Each feature has its own bit

* 1: Anti-Debug
* 2: JIT
* 4: ADV, advanced mode
* 8: SUPER, super mode
* 16: VM, vm protection mode

For example, ``windows.x86_64.7`` means anti-debug(1), JIT(2) and advanced
mode(4) supported, its feature number is 7 = 1 + 2 + 4. ``windows.x86_64.0``
means no any feature, so highest speed.

For :ref:`Super mode`, there is an extra part to mark Python version. For
example, ``windows.x86.11.py37``, feature number 11 = 1 + 2 + 8

Note that zero feature dynamic library isn't compatible with any featured
library. For security reason, the zero feature library uses different alogrithm
to obfuscate the scripts. So the platform ``windows.x86_64.7`` can not share the
same obfuscated scripts with platform ``linux.armv7.0``.


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
* android.armv7
* android.x86
* android.x86_64
* uclibc.armv7
* linux.ppc64
* darwin.arm64
* freebsd.x86_64
* musl.x86_64
* musl.arm
* musl.mips32
* linux.mips64
* linux.mips64el
* poky.x86

.. note:: New platforms in differnt versions

   * v5.9.3: android.armv7
   * v5.9.4: uclibc.armv7
   * v6.3.1: musl.x86_64, musl.arm, musl.mips32, linux.mips64, linux.mips64el
   * v6.6.1: android.x86, android.x86_64

.. _downloading dynamic library by manual:

Downloading Dynamic Library By Manual
-------------------------------------

If the machine is not connected to internet, download the corresponding dynamic
library in other machine, then copy it in the right location.

First make sure there is platform index file ``platforms/index.json``. If not,
run any `pyarmor` command in target machine, it raises exception. For example::

    pyarmor.py o --advanced 2 foo.py

    INFO     PyArmor Version 6.4.2
    INFO     Target platforms: Native
    INFO     Getting remote file: https://github.com/dashingsoft/pyarmor-core/raw/r34.8/platforms/index.json
    INFO     Could not get file from https://github.com/dashingsoft/pyarmor-core/raw/r34.8/platforms: <urlopen error timed out>
    INFO     Getting remote file: https://pyarmor.dashingsoft.com/downloads/r34.8/index.json
    INFO     Could not get file from https://pyarmor.dashingsoft.com/downloads/r34.8: <urlopen error timed out>
    ERROR    No platform list file /data/user/.pyarmor/platforms/index.json found

There are 2 available urls in the log message, download one of them from other
machine, for example::

https://pyarmor.dashingsoft.com/downloads/r34.8/index.json

And copy it to the prompt path in target machine::

    /data/user/.pyarmor/platforms/index.json

Next run `pyarmor` command in target machine again, this time it will prompt the
download file and target path. For example::

    pyarmor o --advanced 2 foo.py

    ...
    INFO Use capsule: /root/.pyarmor/.pyarmor_capsule.zip
    INFO Output path is: /root/supervisor/dist
    INFO Taget platforms: []
    INFO Update target platforms to: [u'linux.x86_64.11.py27']
    INFO Generating super runtime library to dist
    INFO Search library for platform: linux.x86_64.11.py27
    INFO Found available libraries: [u'linux.x86_64.11.py27']
    INFO Target path for linux.x86_64.11.py27: /home/jondy/.pyarmor/platforms/linux/x86_64/11/py27
    INFO Downloading library file for linux.x86_64.11.py27 ...
    INFO Getting remote file: https://github.com/dashingsoft/pyarmor-core/raw/r34.8/platforms/linux.x86_64.11.py27/pytransform.so
    INFO Could not get file from https://github.com/dashingsoft/pyarmor-core/raw/r34.8/platforms: <urlopen error [Errno 111] Connection refused>
    INFO Getting remote file: https://pyarmor.dashingsoft.com/downloads/r34.8/linux.x86_64.11.py27/pytransform.so
    INFO Could not get file from https://pyarmor.dashingsoft.com/downloads/r34.8: <urlopen error [Errno 111] Connection refused>
    ERROR Download library file failed

Download it as before, for example

https://github.com/dashingsoft/pyarmor-core/raw/r34.8/platforms/linux.x86_64.11.py27/pytransform.so

And copy it to the path in the line ``INFO Target path``. Here it is::

    /home/jondy/.pyarmor/platforms/linux/x86_64/11/py27

Before PyArmor 6.5.5, no target path line. Save it to ``~/.pyarmor/platforms/``
plus platform path. For example, the target path of platform
``linux.x86_64.11.py27`` is ``~/.pyarmor/platforms/linux/x86_64/11/py27``.

All the available dynamic libraries are stored in the repos `pyarmor-core`

https://github.com/dashingsoft/pyarmor-core

Each pyarmor version has the corresponding tag, for example, PyArmor 6.4.2 ->
tag "r34.8". Switch this tag and download fiels from ``platforms``.
