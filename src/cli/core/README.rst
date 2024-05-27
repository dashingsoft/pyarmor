pyarmo.cli.core
===============

Pyarmor_ is a command line tool used to obfuscate python scripts, bind obfuscated scripts to fixed machine or expire obfuscated scripts.

This package provides prebuilt `extension module`_ ``pytransform3`` and ``pyarmor_runtime`` required by Pyarmor_

It includes prebuilt extensions support the following platforms for Python 3.7+:

.. table:: Supported Platforms (1)
   :widths: auto

   ======== ======== ===== ========= ========= ======= ======= ==========
    Arch     x86_64   x86   aarch64   aarch32   armv7   armv6    Remark
   ======== ======== ===== ========= ========= ======= ======= ==========
   Darwin      Y      No      Y         No       No      No      [#]_
   Linux       Y      Y       Y         (?)      (?)     (?)     [#]_
   Windows     Y      Y       (?)       No       No      No      [#]_
   Android     Y      Y       Y         No       Y       No      [#]_
   Alpine      Y      (?)     Y         (?)      (?)     (?)
   FreeBSD     Y      No      No        No       No      No
   ======== ======== ===== ========= ========= ======= ======= ==========


.. table:: Supported Platforms (2) [#]_
   :widths: auto

   ======== ========= ============= ========= ==========
    Arch     ppc64le   mips32/64el   riscv64    Remark
   ======== ========= ============= ========= ==========
   Darwin      No          No          No
   Linux       Y           Y           Y        [#]_
   Windows     No          No          No
   Android     No          No          No
   Alpine      Y           Y           Y
   FreeBSD     No          No          No
   ======== ========= ============= ========= ==========

* Y: already available
* No: no support plan
* (?): not available now, maybe work in future

.. [#] Apple Silicon only works for Python 3.9+
.. [#] This is built with glibc
.. [#] Themedia protection extensions are introduced in v3.2.3
.. [#] All below platforms are introduced in v3.2.3
.. [#] All of these platforms are introduced in v6.5.2
.. [#] Arch riscv64 only works for Python 3.10+

.. _Pyarmor: https://pypi.python.org/pypi/pyarmor/
.. _Extension Module: https://packaging.python.org/en/latest/glossary/#term-Extension-Module
