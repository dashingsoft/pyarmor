=================================
 Highest security and performace
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

* :option:`--enable-rft` almost doesn't impact performace
* :option:`--enable-bcc` even a little faster than plain script, but consume more memory to load binary code
* :option:`--enable-jit` prevents from static decompilation
* :option:`--enable-themida` prevents from most of debuggers, only available in Windows, and reduce permormance remarkable
* :option:`--mix-str` protects string constant in the script
* `pyarmor cfg mix_argnames=1` may broken annotations

The following options hide module attributes

* :option:`--private` for script or :option:`--restrict` for package

The following options prevent from injecting functions into obfusated modules

* :option:`--assert-call`
* :option:`--assert-import`

What're the best performace pyarmor could do?
=============================================

Using default options and the following settings

* :option:`--obf-code` ``0``
* :option:`--obf-module` ``0``
* `pyarmor cfg restrict_module=0`

By these options, the security is almost same as `.pyc`

In order to improve security, and doesn't reduce performace, also enable RFT mode

* :option:`--enable-rft`

If there are sensitive string, enable mix-str with filter

* `pyarmor cfg mix.str:includes "/regular expression/"`
* :option:`--mix-str`

Without filter, all of string constants in the scripts are encrypte, it may reduce performance. Using filter only encrypt the sensitive string may balace security and performance.

Recommened options for different applications
=============================================

**1. For django application or serving web request**

   If RFT mode is safe enough, you can check the transformed scripts to make decision, using these options

   * :option:`--enable-rft`
   * :option:`--obf-code` ``0``
   * :option:`--obf-module` ``0``
   * :option:`--mix-str` with filter

   If RFT mode is not safe enought, using these options

   * :option:`--enable-rft`
   * :option:`--no-wrap`
   * :option:`--mix-str` with filter

2. For most of applications and packages

   If RFT mode and BCC mode are available

   * :option:`--enable-rft`
   * :option:`--enable-bcc`
   * :option:`--mix-str` with filter
   * :option:`assert-import`

   If not

   * :option:`--enable-jit`
   * :option:`--private` for scripts, or :option:`--restrict` for packages
   * :option:`--mix-str` with filter
   * :option:`--assert-import`

   If care about injecting track, also

   * :option:`--assert-call` with inline marker to make sure all the key functions are protected

   If it's not perfomace sensitive, using :option:`--enable-themida` prevent from debuggers

.. include:: ../_common_definitions.txt
