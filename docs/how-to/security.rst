=================================
 Highest security and performance
=================================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen

What's the most security pyarmor could do?
==========================================

The following options could improve security

* :option:`--enable-rft` almost doesn't impact performance
* :option:`--enable-bcc` may be a little faster than a plain script, but it consumes more memory to load binary code
* :option:`--enable-jit` prevents static decompilation
* :option:`--enable-themida` prevents most of debuggers, only available in Windows, and reduces performance remarkably
* :option:`--mix-str` protects string constants in the script
* ``pyarmor cfg mix_argnames=1`` may broken annotations
* :option:`--obf-code` ``2`` could make it more difficult to reverse byte code

The following options hide module attributes

* :option:`--private` for script or :option:`--restrict` for package

The following options prevent functions or modules from being replaced by hack code

* :option:`--assert-call`
* :option:`--assert-import`

What's the best performance pyarmor could do?
=============================================

Using default options and the following settings

* :option:`--obf-code` ``0``
* :option:`--obf-module` ``0``
* ``pyarmor cfg restrict_module=0``

With these options, the security is almost the same as `.pyc`

In order to improve security, and doesn't reduce performance, also enable RFT mode

* :option:`--enable-rft`

If there are sensitive strings, enable mix-str with filter

* ``pyarmor cfg mix.str:includes "/regular expression/"``
* :option:`--mix-str`

Without the filter, all of the string constants in the scripts are encrypted, which may reduce performance. Using filter only encrypt the sensitive string may balance security and performance.

Recommended options for different applications
==============================================

**For Django application or serving web request**

   If RFT mode is safe enough, you can check the transformed scripts to make a decision, using these options

   * :option:`--enable-rft`
   * :option:`--obf-code` ``0``
   * :option:`--obf-module` ``0``
   * :option:`--mix-str` with filter

   If RFT mode is not safe enough, using these options

   * :option:`--enable-rft`
   * :option:`--no-wrap`
   * :option:`--mix-str` with filter

**For most applications and packages**

   If RFT mode and BCC mode are available

   * :option:`--enable-rft`
   * :option:`--enable-bcc`
   * :option:`--mix-str` with filter
   * :option:`--assert-import`

   If RFT mode and BCC mode are not available

   * :option:`--enable-jit`
   * :option:`--private` for scripts, or :option:`--restrict` for packages
   * :option:`--mix-str` with filter
   * :option:`--assert-import`
   * :option:`--obf-code` ``2``

   If care about monkey trick, also

   * :option:`--assert-call` with inline marker to make sure all the key functions are protected

   If it's not performance sensitive, using :option:`--enable-themida` prevent from debuggers

Reforming scripts to improve security
=====================================

**Move main script module level code to other module**

Pyarmor will clear the module level code after the module is imported, the injected code could not get any module level code because it's gone.

But the main script module level code is never cleared, so moving unnecessary code here to another module could improve security.

.. include:: ../_common_definitions.txt
