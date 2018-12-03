.. _license:

License
=======

Pyarmor is published as shareware. Free trial version never expires,
the limitation is

* :ref:`Global Capsule` in trial version is fixed.

There are 2 basic types of licenses issued for the software. These are:

* A natural person usage license for home users. The user purchases one
  license to use the software on his own computer.

  Home users may use their natural person usage license on all computers
  and embedded devices which are property of the license owner.

* A juridical person usage license for business users. The user purchases
  one license to use the software for one product or one project of an
  organization.

  Business users may use their juridical person usage license on all
  computers and embedded devices for one product or project. But they
  require another license for different product or project.


Purchase
--------

To buy a license, please visit the following url

https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1

A registration code will be sent to your immediately after payment is
completed successfully.

After you receive the email which includes registration code, copy
registration code only (no newline), then replace the content of
:file:`{pyarmor-folder}/license.lic` with it.

Note that there are 2 types of :file:`license.lic`, this one locates
in the source path of |PyArmor|. It's used by |PyArmor|. The other
locates in the same path as obfuscated scripts, It's used by
obfuscated scripts.

Check new license works, execute this command::

    pyarmor --version

The result should show ``Pyarmor Version X.Y.Z`` and registration code.

After new license takes effect, you need obfuscate the scripts again,
and a random :ref:`Global Capsule` will be generated implicitly when
you run command ``pyarmor obfuscate``

**The registration code is valid forever, it can be used permanently.**

.. include:: _common_definitions.txt
