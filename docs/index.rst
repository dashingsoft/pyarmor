.. pyarmor documentation master file, created by
   sphinx-quickstart on Sat Dec  1 11:22:25 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyArmor's Documentation
=======================

:Version: |PyArmorVersion|
:Homepage: |Homepage|
:Contact: jondy.zhao@gmail.com
:Authors: Jondy Zhao
:Copyright: This document has been placed in the public domain.


|PyArmor| is a command line tool used to obfuscate python scripts,
bind obfuscated scripts to fixed machine or expire obfuscated
scripts. It protects Python scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate co_code of each function (code object) in runtime.
* Clear f_locals of frame as soon as code object completed execution.
* Verify the license file of obfuscated scripts while running it.

|PyArmor| supports Python 2.6, 2.7 and Python 3.

|PyArmor| is tested against ``Windows``, ``Mac OS X``, and ``Linux``.

|PyArmor| has been used successfully with ``FreeBSD`` and embedded
platform such as ``Raspberry Pi``, ``Banana Pi``, ``Orange Pi``, ``TS-4600 / TS-7600`` etc.
but is not fullly tested against them.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   usage
   advanced
   examples
   project
   man
   understand-obfuscated-scripts
   how-to-do
   pytransform
   platforms
   mode
   performance
   security
   questions
   license
   change-logs

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: _common_definitions.txt
