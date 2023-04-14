==============
 Environments
==============

.. highlight:: none

Building Device for pyarmor
===========================

Building device is to run :command:`pyarmor` to geneate obfuscated scripts and all the other required files.

Here list anything related to :command:`pyarmor`. :command:`pyarmor` only run in the `supported platforms`_ by `supported Python versions`_. `Command line options`_, `configuration options`_, `plugin and hook`_ control how to generate obfuscated scripts and runtime files. A few environment variables changes :command:`pyarmor` behaviours.

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

Plugin and hook
---------------

Target Device for obfuscated scripts
====================================

Target device is to run the obfuscated scripts.

Do not install package pyarmor in the target device.

Support platforms, arches and Python versions are same as `Building device for pyarmor`_

The obfuscated scripts may use a few :mod:`sys` attributes, and a few environment variables.

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

Specialized builtin functions
-----------------------------

.. versionadded:: 8.x
                  This feature is still not implemented

There are 2 specialized builtin functions, both of them could be called without import in the obfuscated scripts.

Generally they're used with inline marker or in the hook scripts.

.. function:: __pyarmor__(arg, kwarg, name, flag)

   `name` must be byte string ``b'hdinfo'`` or ``b'keyinfo'``

   `flag` must be ``1``

   When `name` is ``b'hdinfo'``, call it to get hardware information.

   `arg` could be

   - 0: get the serial number of first harddisk
   - 1: get mac address of first network card
   - 2: get ipv4 address of first network card
   - 3: get target machine name

   For example,

   .. code-block:: python

         __pyarmor__(0, None, b'hdinfo', 1)
         __pyarmor__(1, None, b'hdinfo', 1)

   In Linux, `kwarg` is used to get named network card or named harddisk. For example:

   .. code-block:: python

         __pyarmor__(0, name="/dev/vda2", b'hdinfo', 1)
         __pyarmor__(1, name="eth2", b'hdinfo', 1)

   In Windows, `kwarg` is used to get all network cards and harddisks. For example:

   .. code-block:: python

         __pyarmor__(0, name="/0", b'hdinfo', 1)    # First disk
         __pyarmor__(0, name="/1", b'hdinfo', 1)    # Second disk

         __pyarmor__(1, name="*", b'hdinfo', 1)
         __pyarmor__(1, name="*", b'hdinfo', 1)


   When `name` is ``b'keyinfo'``, call it to query user data in the runtime key.

   For example,

   .. code-block:: python

         __pyarmor__(1, None, b'keyinfo', 1)    # return expired date
         __pyarmor__(2, None, b'keyinfo', 1)    # return user data

   Raise :exc:`RuntimeError` if something is wrong.

.. function:: __assert_armored__(arg)

   `arg` is a module or callable object, if `arg` is obfuscated, it return `arg` self, otherwise, raise protection exception. For example

.. code-block:: python

    m = __import__('abc')
    __assert_armored__(m)

    def hello(msg):
        print(msg)

    __assert_armored__(hello)
    hello('abc')

.. include:: ../_common_definitions.txt
