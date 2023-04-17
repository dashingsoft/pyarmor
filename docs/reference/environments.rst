.. highlight:: none

=======================
 Building Environments
=======================

Command :command:`pyarmor` runs in :term:`build machine` to geneate obfuscated scripts and all the other required files.

Here list everything related to :command:`pyarmor`.

Above all it only runs in the `supported platforms`_ by `supported Python versions`_.

Command line options, `configuration options`_, `plugin and hook`_  and a few environment variables control how to generate obfuscated scripts and runtime files.

All the command line options and environment variables are described in :doc:`man`

Supported Python versions
-------------------------

.. table:: Table-1. Supported Python Versions
   :widths: auto

   ===================  =====  =========  =========  ==========  ======  =======  ==============
   Python Version        2.7    3.0~3.4    3.5~3.6    3.7~3.10    3.11    3.12+   Remark
   ===================  =====  =========  =========  ==========  ======  =======  ==============
   pyarmor 8 RFT Mode    No       No         No          Y         Y       N/y      [#]_
   pyarmor 8 BCC Mode    No       No         No          Y         Y       N/y
   pyarmor 8 others      No       No         No          Y         Y       N/y
   pyarmor-7             Y        Y          Y           Y         No      No
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
   Themida Protection        Y           No        No         No          No       No        No
   pyarmor 8 RFT Mode        Y           Y         Y          Y           Y        Y         N/y
   pyarmor 8 BCC Mode        Y           Y         Y          Y           Y        N/y       No
   pyarmor 8 others          Y           Y         Y          Y           Y        Y         Y
   pyarmor-7 [#]_            Y           Y         Y          Y           Y        Y         Y
   ===================  ============  ========  =======  ============  =========  =======  =======

.. rubric:: notes

.. [#] ``N/y`` means not yet now, but will be supported in futer
.. [#] pyarmor-7 also supports more linux arches, refer to `Pyarmor 7.x platforms`__.

.. important::

   pyarmor-7 is bug fixed Pyarmor 7.x version, it's same as Pyarmor 7.x, and only works with old license. Do not use it with new license, it may report ``HTTP 401 error``.

__ https://pyarmor.readthedocs.io/en/v7.7/platforms.html

Configuration options
---------------------

There are 3 kinds of configuration files

* global: an ini file :file:`~/.pyarmor/config/global`
* local: an ini file :file:`.pyarmor/config`
* private: each module may has one ini file in :term:`Local Configuration Path`. For example, :file:`.pyarmor/foo.rules` is private configuration of module ``foo``

Use command :ref:`pyarmor cfg` to change options in configuration files.

Plugin and hook
---------------

.. versionadded:: 8.x
                  This feature is still not implemented


=================================
 Obfuscated Scripts Environments
=================================

Obfuscated scripts run in :term:`target device`, support platforms, arches and Python versions are same as `Building Environments`_

A few :mod:`sys` attributes and environment variables may change behaviours of obfuscated scripts.

:attr:`sys._MEIPASS`

      Borrowed from PyInstaller_, set search path for :term:`outer key`.

:attr:`sys._PARLANG`

      It's used to set runtime error language.

      If it's set, :envvar:`LANG` is ignored.

.. envvar:: LANG

      OS environment variable, used to select runtime error language.

.. envvar:: PYARMOR_LANG

      It's used to set language runtime error language.

      If it's set, both :envvar:`LANG` and :attr:`sys._PARLANG` are ignored.

.. envvar:: PYARMOR_RKEY

      Set search path for :term:`outer key`

Specialized builtin functions
-----------------------------

.. versionadded:: 8.x
                  This feature is still not implemented

There are 2 specialized builtin functions, both of them could be used without import in the obfuscated scripts.

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

         __pyarmor__(None, None, b'keyinfo', 1)   # return user data (bytes)

   Raise :exc:`RuntimeError` if something is wrong.

.. function:: __assert_armored__(arg)

   `arg` is a module or callable object, if `arg` is obfuscated, it return `arg` self, otherwise, raise protection error. For example

.. code-block:: python

    m = __import__('abc')
    __assert_armored__(m)

    def hello(msg):
        print(msg)

    __assert_armored__(hello)
    hello('abc')

.. include:: ../_common_definitions.txt
