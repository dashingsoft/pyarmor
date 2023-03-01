==================
 Pyarmor Licenses
==================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

Introduction
============

This documentation is only apply to Pyarmor_ 8.0 plus.

Pyarmor is published as shareware, free trial version never expires, but there
are some limitations:

a. Can not obfuscate big scritps [1]_
b. Can not use feature mix-str [2]_ to obfuscate string constant in scripts
c. Can not RFT Mode [3]_, BCC Mode [4]_
d. Can not be used for any commercial product without permission

These limitations can be unlocked by different `License Types`_

License types
=============

Pyarmor has 3 kind of licenses:

.. glossary::

    Pyarmor Basic

        Basic license could unlock big script [1]_ and mix-str [2]_ feature.

        It requires internet connection to verify license

    Pyarmor Pro

        Pro license could unlock big script [1]_ and mix-str [2]_ feature.

        Pro license also unlocks BCC Mode [4]_ and RFT Mode [3]_

        It requires internet connection to verify license

    Pyarmor Group

        Group license unlocks all limitions and doesn't require internet.

Internet connection is only used to verify Pyarmor License in the build machine
to generate the obfuscated scripts.

For the obfuscated scripts generally run in the customer's device, Pyarmor has
no any limitions, it's controlled totally by users. Pyarmor only cares about
build machine.

Each license has an unique number, the format is ``pyarmor-vax-xxxxxx``, which x
stands for a digital.

Each product requires one License No. So any product in global also has an
unique number in Pyarmor world.

If user has many products, many license are required.

In details read `Pyarmor End User License Agreements`__

License features
----------------

.. table:: Table-1. License Features
   :widths: auto

   ===================  ========   ========   =========   ========  ==============
   Features             Trial      Basic      Pro         Group     Remark
   ===================  ========   ========   =========   ========  ==============
   Basic Obfuscation       Y          Y          Y           Y       [5]_
   Expired Script          Y          Y          Y           Y       [6]_
   Bind Device             Y          Y          Y           Y       [7]_
   JIT Protection          Y          Y          Y           Y       [8]_
   Assert Protection       Y          Y          Y           Y       [9]_
   Themedia Protection     Y          Y          Y           Y       [10]_
   Big Script              No         Y          Y           Y
   Mix Str                 No         Y          Y           Y
   RFT MODE                No         No         Y           Y
   BCC MODE                No         No         Y           Y
   ===================  ========   ========   =========   ========  ==============

.. rubric:: feature notes

.. [1] Big Script means file size exceeds a cerntain value.
.. [2] Mix Str: obfscating string constant in script
.. [3] RFT Mode: renaming function/class/method/variable in Python scripts
.. [4] BCC Mode: Transforming some Python functions in scripts to c functions,
       compile them to machine instructions directly
.. [5] Basic Obfuscation: obfuscating the scripts by default options
.. [6] Expired Script: obfuscated scripts has expired date
.. [7] Bind Device: obfuscated scripts only run in specified devices
.. [8] JIT Protection: processing some sentensive data by runtime generated
       binary code
.. [9] Assert Protection: preventing others from hacking obfuscated scripts
.. [10] Themedia Protection: using Themedia to protect Widnows dlls

__ https://github.com/dashingsoft/pyarmor/blob/master/LICENSE

Purchasing license
==================

除了购买软件许可的费用之外，没有其它任何费用。获得许可的用户可以使用本软件在许可
的范围之内加密任何脚本并自由发布，不需要在向许可人支付任何费用。

购买软件许可的费用是一次性收费，可以永久在购买本软件时候的版本中使用，但是许可证
可能在任何一个升级版本中失效，许可人不承诺许可证可以在今后所有的升级版本中使用。

.. list-table:: Table-2. License Prices
   :header-rows: 1

   * - License Type
     - Net Price($)
     - Remark
   * - Basic
     - 52
     -
   * - Pro
     - 89
     -
   * - Group
     - 158
     -

Refund policy
-------------

If license code isn't activated, since purchasing date in six months, refund is
accepted. Please send request to <pyarmor@163.com>, Pyarmor will refund the
order in a week. Out of six monthes, or license code has been activated, refund
request is not accepted.

Why no refund even if my PayPal account is hacked and someone else bought
Pyarmor by this PayPal account?

Imaging you lost cash €100, someone else got it and buys a cloth, then you think
the shopper should refund the money to you. It's same for money in PayPal, it's
your duty to keep your PayPal money safe, and bear the loss because of your own
fault.

Upgrading old license
=====================

.. list-table:: Table-3. Upgrade fee from old license
   :header-rows: 1

   * - License Type
     - Upgrading fee($)
     - Remark
   * - pyarmor-basic
     - 0
     - following new EULA and match conditions, see [#]_
   * - pyarmor-pro
     - 50
     -
   * - pyarmor-group
     - N/A
     -

.. [#] The old license code starts with "pyarmor-vax-" could be upgraded to
       pyarmor-basic without extra fee following new EULA. If it's personal
       license type, it need provide the product name bind to pyarmor-basic for
       commercial usage.

.. include:: _common_definitions.txt
