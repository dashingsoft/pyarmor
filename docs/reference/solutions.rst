====================
 Pyarmor Check List
====================

.. program:: pyarmor gen

Pyarmor team handles too many wrong usage issues, all of them are collected and organized into this document. When something is wrong, please check this doc at first.

.. _build device:

Build Device
============

If something is wrong in build device, check this section.

Bootstrap failed
----------------

1. Check package `pyarmor.cli.core` has been installed

   Search extension module `pytransform3.pyd` or `pytransform3.so` in `pyarmor` package source

   If not exists, please check installation documentation to install it

2. Check extension `pytransform3` is exact for this Python and platform

   Test it by Python interperter:

   .. code-block:: bash

       $ python
       >>> from pyarmor.cli.core import Pytransform3
       >>> Pytransform3.version()
       1
       >>>

   If not return this, check the dependencies of extension `pytransform3`

   In Linux

   .. code-block:: bash

       $ ldd /path/to/pytransform3.so

   In MacOS

   .. code-block:: bash

       $ codesign -v /path/to/pytransform3.so
       $ otool -L /path/to/pytransform3.so

   In Windows, download [cygcheck]_ then::

       C:\> cygcheck \path\to\pytransform3.pyd

   Or::

       C:\> dumpbin /dependents \path\to\pytransform3.pyd

   Try to install missed packages by error report to solve the problem

3. If nothing works, please check :doc:`environments` to make sure Pyarmor supports this platform

   For LINUX variant system, check the content of packages like `pyarmor.cli.core.linux`, `pyarmor.cli.core.alpine` , `pyarmor.cli.core.android` etc. Each package includes many prebuilt `pytransform.so`. For example::

       $ unzip ./pyarmor.cli.core.linux-6.5.3-cp310-none-any.whl

       Archive:  ./pyarmor.cli.core.linux-6.5.3-cp310-none-any.whl
         inflating: pyarmor/cli/core/linux/__init__.py
         inflating: pyarmor/cli/core/linux/aarch64/pyarmor_runtime.so
         inflating: pyarmor/cli/core/linux/aarch64/pytransform3.so
         inflating: pyarmor/cli/core/linux/armv7/pyarmor_runtime.so
         inflating: pyarmor/cli/core/linux/armv7/pytransform3.so
         inflating: pyarmor/cli/core/linux/loongarch64/pyarmor_runtime.so
         inflating: pyarmor/cli/core/linux/loongarch64/pytransform3.so
         inflating: pyarmor/cli/core/linux/mips32el/pyarmor_runtime.so
         inflating: pyarmor/cli/core/linux/mips32el/pytransform3.so
         ...

   Check each `pytransform3.so` by `ldd` to find which one works, then copy them to package `pyarmor.cli.core`. For example::

       $ cp pyarmor/cli/core/linux/loongarch64/*.so /path/to/pyarmor/cli/core
       $ pyarmor gen foo.py

   Or install this package and set environment variable like this::

       $ pip install ./pyarmor.cli.core.linux-6.5.3-cp310-none-any.whl
       $ export PYARMOR_PLATFORM=linux.loongarch64
       $ pyarmor gen foo.py

Registration Failed
-------------------

If it's using :term:`Activation File` (`pyarmor-regcode-xxxx.txt`), make sure this file is not used more than 3 times, generally once initial registration completed, activation file :file:`pyarmor-regcode-xxxx.txt` is invalid. It should use :term:`Registration File` ``pyarmor-regfile-xxxx.zip`` for any next registration.

**Basic/Pro License**

1. If the date time of this device has been changed, restore it to current time

2. If run register command more than 3 times in 1 minute, wait for 5 minutes, and try again.

3. If run more than 3 docker containers in 1 minute in same docker host, run only one at the same time.

4. If have 100 runs in different devices or docker containers in 24 hours, waiting for 24 hours since the first run

5. If not, try to open http://pyarmor.dashingsoft.com/api/auth2/ in web browser or test it by `curl`

   If return "NO:missing parameters", it means network is fine, and license server is fine

   Otherwise check network configuration

6. Check Python interpreter by the following commands (If there are many Python installed, make sure this Python interperter is used to execute Pyarmor)

   .. code-block:: bash

      $ python
      >>> from urllib.request import urlopen
      >>> res = urlopen('http://pyarmor.dashingsoft.com/api/auth2/')
      >>> print(res.read())
      b'NO:missing parameter'

If it raises exception or return something else, it’s firewall problem, please configure firwire to allow Python interpreter to visit pyarmor.dashingsoft.com and port 80 or 443

If it returns as above, but still failed to register, report issue with license no. like `pyarmor-vax-5068`

**Group License**

1. Check this offline device Machine ID is changed or not after reboot

   - It should make sure Pyarmor > 8.5.2, it's better to use the latest Pyarmor
   - Group License doesn't work in CI/CD pipeline with default runner

2. It's device registration file ``pyarmor-device-regfile-????.N.zip`` to be used to register Pyarmor in offline device. Do not use Group License :term:`Registration File` ``pyarmor-regfile-xxxx.zip`` to register Pyarmor in the offline device

3. Does device registration file ``pyarmor-device-regfile-????.N.zip`` match this device? Each device registration file has one machine id.

4. If device Machine ID is same after reboot, and device registration file is matched this device, please report issue with the following information:

   - Machine ID
   - Device type, it's physics device, vm, ECS, docker container or something else
   - Linux, Windows or MacOS and arches
   - For Linux/MacOS, also provide the output of `uname -a`

**Group License for docker container**

1. Check docker host and container network, make sure they're in same network

Obfuscation failed
------------------

**update license token failed**

Please check above section `Registration Failed`

**raise other exceptions**

1. Try to obfuscate simple hello world script

   If not, check above section `Bootstrap Failed`, make sure Pyarmor supports this platform

2. Try to ignore local and global configuration. For example

   Rename path `.pyarmor` to `.pyarmor.bak`

   Rename path `~/.pyarmor/config` to `~/.pyarmor/config.bak`

   Then try to obfuscate the scripts

3. Try to use few options, check it works or not, and get the problem option

4. When report issue, please use debug option :option:`-d` to generate `pyarmor.report.bug`, and

   - A script as simple as possible to reproduce issue
   - Do not use the options which doesn't make sense for this issue

Packing failed
--------------

1. Try to pack the original script by PyInstaller directly first, mkae sure it works and the final bundle works
2. Check :doc:`../topic/repack`

.. _target device:

Target Device
=============

If your own code in the obfuscated script still isn't executed, check `Bootstrap failed`, otherwise check `failed to run obfuscated scripts` or `failed to run the packed obfuscated scripts`

Bootstrap failed
----------------

1. Check is there :ref:`Runtime Package`

   In the output `dist` path, search `pyarmor_runtime.pyd` or `pyarmor_runtime.so`

   :ref:`Runtime Package` is a normal Python package, use it as third-party package, make sure it's in right place so that the obfuscated script could import it

2. Check the import statement in the obfuscated scripts

   Open the obfuscated script by any text editor, you can see the first statement is `from ... import`, make sure it works by Python import system

   If it doesn't work, try to use :option:`-i` or :option:`--prefix` to generate the obfuscated scripts again to fix it

**If target device is different from build device**

1. Make sure Python version (major.minor) is same in build/target device

2. If OS or arch is not same, make sure the right cross platform option :option:`--platform` is used

3. Check extension `pyarmor_runtime` works in target machine

   In Linux

   .. code-block:: bash

       $ ldd /path/to/pyarmor_runtime.so

   In MacOS

   .. code-block:: bash

       $ codesign -v /path/to/pyarmor_runtime.so
       $ otool -L /path/to/pyarmor_runtime.so

   In Windows, download [cygcheck]_ then::

       C:\> cygcheck \path\to\pyarmor_runtime.pyd

   Or::

       C:\> dumpbin /dependents \path\to\pyarmor_runtime.pyd

   Try to install missed packages by error report to solve the problem

If still not work, please check :doc:`environments` to make sure Pyarmor supports this platform

**unauthorized use of script**

1. Do not use restrict options like :option:`--private`, :option:`--restrict`, :option:`--assert-call`, :option:`--assert-import`
2. Use `pyarmor cfg assert.call:excludes "xxx"` and `pyarmor cfg assert.import:excludes "xxx"` to exclude problem modules and functions
3. Find the problem option, and report issue

Failed to run obfuscated scripts
--------------------------------

1. Do not use :option:`--enable-rft`, :option:`--enable-bcc` and any restrict options like :option:`--private`, :option:`--restrict`, :option:`--assert-call`, :option:`--assert-import`, check the obfuscated scripts work or not. If it works, check the solutions in the **RFT Mode Problem**, **BCC Mode Problem** and **unauthorized use of script**

2. If it doesn't work, try to obfuscate a hello world script, check it works or not

3. Add some print statement in the problem script, and get one script as simple as possible to reproduce the problem. It's better only use Python system packages. If really need third-parth library, check :doc:`../how-to/third-party` first

4. Report issue with necessare information

   - Minimum pyarmor options, do not commit non-sense option
   - A simple script which only imports Python system package
   - How to run the obfuscated scripts and full trackback when it fails

**RFT Mode Problem**

Check solutions in :ref:`using rftmode`

**BCC Mode Problem**

First use a hello world script to make sure it works. If it doesn't work, check your configuration and try again in clean environments

Check solutions in :ref:`using bccmode`

Failed to run the packed obfuscated scripts
-------------------------------------------

1. Do not pack the sciprt, just use same options to obfuscate the script, and run the obfuscated script in target device, make sure it works, otherwise check solutions in above section

2. Do not obfuscate the scripts, pack the original script by PyInstaller directly, and execute the final executable in target device, make sure it works. Otherwise check PyInstaller_ documentation to find solutions

3. Try to use a few options to repeat check point 1 and 2, find the problem option, and report issue

.. _platform issues:

Platform Issues
===============

Cygwin need create extra link `pythonXY.dll` to `libpythonX.Y.dll`

Darwin Apple Silicon may need codesign

.. rubric:: Notes

.. [cygcheck] How to get `cygcheck.exe`

   Download https://pyarmor.dashingsoft.com/downloads/tools/cygcheck.zip and unzip it

   Or get it from offical website

   - Open https://cygwin.com/mirrors.html
   - Select one mirror, enter pathes `x86_64/release/cygwin/`
   - Download the latest package `cygwin-3.5.3-1.tar.xz`
   - Extract `cygcheck.exe` from this file by `tar xJf cygwin-3.5.3-1.tar.xz`

.. include:: ../_common_definitions.txt
