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

Show License Information
------------------------

Maybe you'd like to show how many days left when you issue an expired
license for obfuscated scripts.

Use ``get_license_info`` function in the module :file:`pytransform.py`
of :ref:`Runtime Files` to get license information of obfuscated
scripts.

Here it's an example which explains how to do. Suppose there is a
script :file:`foo.py` will be obfuscated and distributed to the
customer, it will print expired date and license code, then do
something.

The content of foo.py::

    def show_license_code():
        from pytransfrom import get_license_info

        info = get_license_info()
        print('This script is only for %s' % info['CODE]')
        print('This script will expired on %s' % info['expired'])

    if __name__ == '__main__':
        show_license_code()
        do_something()

Let's obfuscate foo.py at first::

  pyarmor obfuscate foo.py
  pyarmor licenses --expired 2019-01-01 Brave-Tom
  cp licenses/Brave-Tom/license.lic dist/license.ic

Then run this obfuscated script in the output path ``dist``::

  cd dist/
  python foo.py

The output will be::

  This script is only for Brave-Tom
  This script will expired on 2019-01-01


.. include:: _common_definitions.txt
