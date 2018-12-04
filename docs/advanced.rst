.. _advanced topics:

Advanced Topics
===============

Restrict Mode
-------------

|PyArmor| can obfuscate the scripts in restrict mode.

If the script is obfuscated in restrict mode:

* Each function (code object) will not be obfuscated again in runtime
* Any other code can not be insert into the obfuscated scripts
* The obfuscated module can not be imported from other clear python scripts

For examples, obfuscate :file:`foo.py` in restrict mode::

    pyarmor obfuscate --restrict foo.py

Each function is obfuscated before it's called. Once it's executed, it
will not be obfuscated again.

And if adding ``print`` in the obfuscated script::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')
    print('Something')

It will report error as running::

    python foo.py

In a short word, the obfuscated script in restrict mode runs quickly,
but maybe less security.

If the scripts is obfuscated in restrict mode, you should enable
restrict mode either as generating new licenses for it::

    pyarmor licenses --restrict --expired 2019-01-01 mycode

.. include:: _common_definitions.txt
