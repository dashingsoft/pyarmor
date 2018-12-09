.. _questions:

When Things Go Wrong
====================

Could not load `_pytransform`
-----------------------------

Generally, the dynamic library `_pytransform` is in the same path of
obfuscated scripts. It may be:

* `_pytransform.so` in Linux
* `_pytransform.dll` in Windows
* `_pytransform.dylib` in MacOS

First check whether the file exists. If it exists:

* Check the permissions of dynamic library

    If there is no execute permissions in Windows, it will complain:
    `[Error 5] Access is denied`

* Check whether `ctypes` could load `_pytransform`::

    from pytransform import _load_library
    m = _load_library(path='/path/to/dist')

* Try to set the runtime path in the :ref:`Bootstrap Code` of entry
  script::

    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/dist')

Still doesn't work, report an issue_

.. include:: _common_definitions.txt
