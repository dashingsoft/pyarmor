=======================
 Using Pyarmor License
=======================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor reg

Prerequisite
============

First of all

1. An :term:`activation file` of :term:`Pyarmor License` like :file:`pyarmor-regcode-xxxx.txt`, refer to :doc:`../licenses` to purchase right one
2. Pyarmor 8.2+
3. Internet connection
4. Product name bind to this license, for non-commercial use, product name is ``non-profits``

Using Pyarmor Baisc or Pro
==========================

Basic use steps:

1. Using :term:`activation file` to initial registration, set product name bind to this license
2. Once initial registration completed, a :term:`registration file` is generated
3. Using :term:`registration file` to register Pyarmor in other devices

Initial registration
--------------------

Using :option:`-p` to specify product name for this license, for non-commercial use, set product name to ``non-profits``.

Assume this license is used to protect your product ``XXX``, initial registration by this command::

    $ pyarmor reg -p "XXX" pyarmor-regcode-xxxx.txt

Pyarmor will show registration information and ask for your confirmation. If everything is fine, type :kbd:`yes` and :kbd:`Enter` to continue. Any other input aborts registration.

If initial registration is successful, it prints final license information in the console. And a :term:`registration file` like :file:`pyarmor-regfile-xxxx.zip` is generated in the current path at the same time. This file is used for subsequent registration in other machines.

Once initial registration completed, activation file :file:`pyarmor-regcode-xxxx.txt` is invalid, do not use it again.

Once initial registration completed, product name can't be changed.

Please backup registration file :file:`pyarmor-regfile-xxxx.zip` carefully. If lost, Pyarmor is not responsible for keeping this license and no lost-found service.

Product name is not decided
---------------------------

When product is in developing, and product name is not decided. Set product name to ``TBD`` on initial registration. For example::

    $ pyarmor reg -p "TBD" pyarmor-regcode-xxxx.txt

In 6 months real product name must be set by this command::

    $ pyarmor reg -p "XXX" pyarmor-regcode-xxxx.txt

If it's not changed after 6 months, the product name will be set to ``non-profits`` automatically and can't be changed again.

Registering in other machines
-----------------------------

Copy :term:`registration file` :file:`pyarmor-regfile-xxxx.zip` to other machines, run the following command::

    $ pyarmor reg pyarmor-regfile-xxxx.zip

Check the registration information::

    $ pyarmor -v

After successful registration, all obfuscations will automatically apply this license, and each obfuscation requires online license verification.

Registering in Docker or CI pipeline
------------------------------------

It's no problem to run Pyarmor in Docker or CI pipeline to obfuscate user's application. Register pyarmor with :file:`pyarmor-regfile-xxxx.zip` same as above. **But It's not allowed to distribute pyarmor self and any Pyarmor License to customer**

Don't run too many build dockers, maximum is 100.

Using group license
===================

.. versionadded:: 8.2

Each :term:`Pyarmor Group` could have 100 offline devices, each device has its own number, from 1 to 100.

Basic use steps:

1. Using activate file :file:`pyarmor-regcode-xxxx.txt` to initial registration, set product name bind to this license, and generate :term:`registration file`
2. Generating group device file separately on each offline device
3. Using :term:`registration file` and group device file to generate device registration file.
4. Using device registration file to register Pyarmor on offline device [#]_

.. [#] The device registration file is bind to specified device, each device has its own device regfile

Initial registration
--------------------

After purchasing :term:`Pyarmor Group`, an activate file :file:`pyarmor-regcode-xxxx.txt` is sent to registration email.

Initial registration need internet connection and Pyarmor 8.2+. Suppose product name is ``XXX``, then run this command::

    $ pyarmor reg -p XXX pyarmor-regcode-xxxx.txt

After initial registration completed, a :term:`registration file` ``pyarmor-regfile-xxxx.zip`` will be generated.

Group device file
-----------------

On each offline device, install Pyarmor 8.2+, and generate group device file. For example, on device no. 1, run this command::

    $ pyarmor reg -g 1

It will generate group device file ``pyarmor-group-device.1``.

Generating offline device regfile
---------------------------------

Generating offline device regfile need internet connection, Pyarmor 8.2+, group device file  ``pyarmor-group-device.1`` and group license :term:`registration file` ``pyarmor-regfile-xxxx.zip``.

Copying group device file ``pyarmor-group-device.1`` to initial registration device which has internet connection, this file must be saved in the path ``.pyarmor/group/``, then run this command to generate device regfile ``pyarmor-device-regfile-xxxx.1.zip``::

    $ mkdir -p .pyarmor/group
    $ cp pyarmor-group-device.1 .pyarmor/group/

    $ pyarmor reg -g 1 /path/to/pyarmor-regfile-xxxx.zip

Registering Pyarmor in offline device
-------------------------------------

Once device regfile is generated, copy it to the corresponding device, run this command to register Pyarmor::

    $ pyarmor reg pyarmor-device-regfile-xxxx.1.zip

Check registration information::

    $ pyarmor -v

After successful registration, all obfuscations will automatically apply this group license, and each obfuscation need not online license verification.

Upgrading old Pyarmor license
=============================

Refer to :ref:`upgrade old license <upgrading old license>`

.. include:: ../_common_definitions.txt
