.. _license:

License
=======

The software is distributed as Free To Use But Restricted. Free trial
version never expires, the limitations are

- The maximum size of code object is 35728 bytes in trial version
- The scripts obfuscated by trial version are not private. It means
  anyone could generate the license file which works for these
  obfuscated scripts.
- Without permission the trial version may not be used for the Python
  scripts of any commercial product.

About the license file of obfuscated scripts, refer to :ref:`The
License File for Obfuscated Script`

A registration code is required to obfuscate big code object or
generate private obfuscated scripts.

There are 2 basic types of licenses issued for the software. These are:

* A natural person usage license for home users. The user purchases one
  license to use the software on his own computer.

  Home users may use their natural person usage license to obfuscate
  all the python scripts which are property of the license owner, to
  generate private license files for the obfuscated scripts and
  distribute them and all the required files to any other machine or
  device.

* A juridical person usage license for business users. The user
  purchases one license to use the software for one product serials of
  an organization.

  Business users may use their juridical person usage license on all
  computers and embedded devices to obfuscate all the python scripts
  of this product serials, to generate private license files for these
  obfuscated scripts and distribute them and all the required files to
  any other machine and device.

  Without permission of the software owner the license purchased for
  one product serials should not be used for other product
  serials. Business users should purchase new license for different
  product serials.

Purchase
--------

To buy a license, please visit the following url

https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1

A registration code will be sent to your immediately after payment is
completed successfully.

After you receive the email which includes registration code, run the
following command to make it effective::

    pyarmor register CODE

Note that command `register` is introduced from `PyArmor` 5.3.3,
please upgrade the old version to the latest one, or directly replace
the content of `license.lic` in the `PyArmor` installed path with the
registration code only (no newline).

Check new license works by this command::

    pyarmor --version

The result should show ``PyArmor Version X.Y.Z`` and registration code.

After new license takes effect, you need obfuscate the scripts again,
and a random :ref:`Global Capsule` will be generated implicitly when
you run command ``pyarmor obfuscate``

**The registration code is valid forever, it can be used permanently.**

.. include:: _common_definitions.txt
