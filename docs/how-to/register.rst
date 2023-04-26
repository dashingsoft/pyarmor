==================
 Register Pyarmor
==================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor reg

Initial Registration
====================

First read :doc:`Pyarmor License <../licenses>` to purchase one Pyarmor License.

An activation file like :file:`pyarmor-regcode-xxxx.txt` will be sent to you by email. This file is used to initial registration.

It need internet connection for intial registration.

For non-profits usage
---------------------

For any non-profits use, run this command::

    $ pyarmor reg -p non-profits pyarmor-regcode-xxxx.txt

For commercial usage
--------------------

Assume this license is used to protect your product ``Robot Studio``, initial registration by this command::

    $ pyarmor reg -p "Robot Studio" pyarmor-regcode-xxxx.txt

Pyarmor will show registration information and ask your confirmation. If everything is fine, type :kbd:`yes` and :kbd:`Enter` to continue.

If initial registration is successful, it prints final license information in the console. And a registration file named :file:`pyarmor-regfile-xxxx.zip` for this license is generated in the current path at the same time. This file is used for subsequent registration in other machines.

Once initial registration completed, activation file :file:`pyarmor-keycode-xxxx.txt` is invalid and can't be used.

Once initial registration completed, product name can't be changed.

Please keep registration file :file:`pyarmor-regfile-xxxx.zip` carefully. If lost, Pyarmor is not responsible for keeping this license. In this case, if continue to use Pyarmor, needs purchase new one.

Product name is not decided
---------------------------

When product is in developing, and product name is not decide. Initial registration with product ``TBD``. For example::

    $ pyarmor reg -p "TBD" pyarmor-regcode-xxxx.txt

It can be changed once later, before product starts selling, the real name must be set by this command::

    $ pyarmor reg -p "Robot Studio" pyarmor-regcode-xxxx.txt

Registeration in other machines
===============================

Once initial registeration successfully, it generates registration file named :file:`pyarmor-regfile-xxxx.zip` at the same time.

Copy this file to other machines, then run the following command::

    $ pyarmor reg pyarmor-regfile-xxxx.zip

Check the registration information::

    $ pyarmor -v

Registeration in Docker or CI pipeline
--------------------------------------

It's no problem to run Pyarmor in Docker or CI pipeline to obfuscate user's application. Register pyarmor with :file:`pyarmor-regfile-xxxx.zip` same as above. But It's not allowed to distribute pakcage pyarmor and any Pyarmor License to customer.

And don't run too many build dockers.

Using group license
===================

.. versionadded:: 8.2

**Initial Registration**

After purchasing :term:`Pyarmor Group`, an activate file :file:`pyarmor-regcode-xxxx.txt` is sent to registration email.

Initial registration need internet and Pyarmor 8.2+. Product name is required for :term:`Pyarmor Group`, and ``TBD`` is not valid. Suppose product name is ``Robot``, then run this command::

    $ pyarmor reg -p Robot pyarmor-regcode-xxxx.txt

If initial registration is successful, a regfile ``pyarmor-regfile-xxxx.zip`` will be generated.

**Offline device group info**

Each :term:`Pyarmor Group` could have 100 offline devices, each device has its ID, for 1 to 100.

In each offline device, install Pyarmor 8.2+, and generate group info file. For example, for device no. 1, run this command::

    $ pyarmor reg -g 1

It will generate group info file ``pyarmor-group-file.1``.

**Generate regfile for offline device**

Generating offline regfile need internet connection, Pyarmor 8.2+, group info file  ``pyarmor-group-file.1`` and :term:`registration file` ``pyarmor-regfile-xxxx.zip``.

Copying group info file ``pyarmor-group-file.1`` to initial registration device which has internet connection, this file must be saved in the current path ``.pyarmor/group/``, then run this command to generate regfile for offline device no. 1::

    $ mkdir -p .pyarmor/group
    $ cp pyarmor-group-file.1 .pyarmor/group/

    $ pyarmor reg -g 1 /path/to/pyarmor-regfile-xxxx.zip

It will generate offline regfile ``pyarmor-group-regfile-xxxx.1.zip``

**Register Pyarmor in offline device**

Once offline regfile is generated, copy it to corresponding device, then run this command to register Pyarmor::

    $ pyarmor reg pyarmor-group-regfile-xxxx.1.zip

Check registration information::

    $ pyarmor -v

For offline device no. 2, no. 3, ... repeat above steps.

Upgrading old Pyarmor license
=============================

Refer to :ref:`upgrade old license <upgrading old license>`

.. include:: ../_common_definitions.txt
