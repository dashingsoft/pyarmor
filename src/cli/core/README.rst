pyarmo.cli.core
===============

Pyarmor_ is a command line tool used to obfuscate python scripts, bind obfuscated scripts to fixed machine or expire obfuscated scripts.

This package provides prebuilt `extension module`_ ``pytransform3`` and ``pyarmor_runtime`` required by Pyarmor_

It includes prebuilt extensions support the following platforms for Python 3.7+:

.. table::
   :widths: auto

   ======== ======== ======== ======== ======== ======== ======== ==========
    Arch     x86_64    i686   aarch64   aarch32  armv7    armv6    Remark
   ======== ======== ======== ======== ======== ======== ======== ==========
   Darwin     Y        No       Y        No        No       No      [#]_
   Linux      Y        Y        Y        (?)       (?)      (?)     [#]_
   Windows    Y        Y        (?)      No        No       No      [#]_
   Android    Y        Y        Y        No        Y        No      [#]_
   Alpine     Y        (?)      Y        (?)       (?)      (?)
   FreeBSD    Y        No       No       No        No       No
   ======== ======== ======== ======== ======== ======== ======== ==========

* Y: already available
* No: no support plan
* (?): not available now, maybe work in future

.. [#] Apple Silicon only for Python 3.9+
.. [#] This is built with glibc
.. [#] Themedia protection extensions are introduced in v3.2.3
.. [#] All below platforms are introduced in v3.2.3

.. _Pyarmor: https://pypi.python.org/pypi/pyarmor/
.. _Extension Module: https://packaging.python.org/en/latest/glossary/#term-Extension-Module
