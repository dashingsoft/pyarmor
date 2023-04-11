==============
 Environments
==============

.. highlight:: none

Building Device
===============

Building device is to run :command:`pyarmor` to geneate obfuscated scripts and all the other required files.

Supported Platforms:

* Windows
* Linux
* Darwin

Support Arches:

* x86_64
* x86
* aarch64
* armv7

Supported Pyton versions:

* Python 3.7 ~ Python 3.11

Command line options and environment variables are described in :doc:`man`

Configuration files
-------------------

There are 3 kinds of configuration files

* global: an ini file :file:`~/.pyarmor/config/global`
* local: an ini file :file:`.pyarmor/config`
* private: each module may has one ini file in :term:`Local Configuration Path`. For example, :file:`.pyarmor/foo.rules` is private configuration of module ``foo``


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
