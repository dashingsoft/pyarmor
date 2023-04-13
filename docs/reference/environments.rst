==============
 Environments
==============

.. highlight:: none

Building Device
===============

Building device is to run :command:`pyarmor` to geneate obfuscated scripts and all the other required files.

Supported Python versions
-------------------------

.. table:: Table-1. Supported Python Versions
   :widths: auto

   ===================  =====  =========  =========  ==========  ======  =======  ==============
   Python Version        2.7    3.0~3.4    3.5~3.6    3.7~3.10    3.11    3.12+   Remark
   ===================  =====  =========  =========  ==========  ======  =======  ==============
   pyarmor 8 RFT Mode     N        N          N          Y         Y        Nx    [#]_
   pyarmor 8 BCC Mode     N        N          N          Y         Y        Nx
   pyarmor 8 others       N        N          N          Y         Y        Nx
   pyarmor-7              Y        Y          Y          Y         N        N
   ===================  =====  =========  =========  ==========  ======  =======  ==============

Supported platforms
-------------------

.. table:: Table-2. Supported Platforms
   :widths: auto

   ===================  ============  ========  =======  ============  =========  =======  =======
   OS                     Windows           Apple                    Linux
   -------------------  ------------  -----------------  -----------------------------------------
   Arch                  x86/x86_64    x86_64    arm64    x86/x86_64    aarch64    armv7    armv6
   ===================  ============  ========  =======  ============  =========  =======  =======
   Themida Protection        Y           N         N          N           N        N        N
   pyarmor 8 RFT Mode        Y           Y         Y          Y           Y        Y        Nx
   pyarmor 8 BCC Mode        Y           Y         Y          Y           Y        Nx       Nx
   pyarmor 8 others          Y           Y         Y          Y           Y        Y        Y
   pyarmor-7 [#]_            Y           Y         Y          Y           Y        Y        Y
   ===================  ============  ========  =======  ============  =========  =======  =======

.. rubric:: notes

.. [#] ``Nx`` means supported in futer
.. [#] need purchasing old license in order to use pyarmor-7 in most of platforms, and it also supports more linux arches, refer to `Pyarmor 7.x platforms`__

__ https://pyarmor.readthedocs.io/en/v7.7/platforms.html

Command line options
--------------------

Command line options and environment variables are described in :doc:`man`

Configuration options
---------------------

There are 3 kinds of configuration files

* global: an ini file :file:`~/.pyarmor/config/global`
* local: an ini file :file:`.pyarmor/config`
* private: each module may has one ini file in :term:`Local Configuration Path`. For example, :file:`.pyarmor/foo.rules` is private configuration of module ``foo``

Use command :ref:`pyarmor cfg` to change options in configuration files.

Target Device
=============

Target device is to run the obfuscated scripts.

Support platforms, arches and Python versions are same as `Building device`_

:attr:`sys._MEIPASS`

      Borrowed from PyInstaller_, set search path for :term:`outer key`.

:attr:`sys._PARLANG`

      It's used to set language for runtime error message.

      If it's set, :envvar:`LANG` is ignored.

.. envvar:: LANG

      OS environment variable, used to select language for runtime error message.

.. envvar:: PYARMOR_LANG

      It's used to set language for runtime error message.

      If it's set, both :envvar:`LANG` and :attr:`sys._PARLANG` are ignored.

.. envvar:: PYARMOR_RKEY

      Set search path for :term:`outer key`

.. include:: ../_common_definitions.txt
