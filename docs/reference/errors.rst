================
 Error Messages
================

.. highlight:: none

Here list all the errors when running :command:`pyarmor` or obfuscated scripts.

If something is wrong, search error message here to find the reason.

If no exact error message found, most likely it's not caused by Pyarmor, search it in google or any other search engine to find the solution.

Building Errors
===============

Here list all the errors when run :command:`pyarmor` in building machine

.. list-table:: Table-1. Build Errors
   :name: pyarmor errors
   :widths: 10 20
   :header-rows: 1

   * - Error
     - Reasons
   * - out of license
     - Using not available features, for example, big script

       Purchasing license to unlock the limitations, refer to :doc:`../licenses`
   * - not machine id
     - This machine is not registered, or the hardware information is changed.

       Try to register Pyarmor again to fix it.
   * - query machine id failed
     - Could not get hardware information in this machine

       Pyarmor need query harddisk serial number, mac address etc.

       If it could not get hardware information, it complains of this.

The following errors may occur when registering Pyarmor

.. list-table:: Table-1.1 Register Errors
   :name: register errors
   :widths: 10 20
   :header-rows: 1

   * - Error
     - Reasons
   * - HTTP Error 400: Bad Request
     - 1. Running upgrading command `pyarmor -u` more than once

          Try to register Pyarmor again with zip, for example::
             pyarmor reg pyarmor-regfile-xxxxxx.zip
   * - HTTP Error 401: Unauthorized
     - Using old pyarmor commands with new license

       Please using Pyarmor 8 commands to obfuscate the scripts
   * - HTTP Error 503: Service Temporarily Unavailable
     - Invoking too many register command in 1 minute

       For security reason, the license server only allows 3 register request in 1 minute
   * - unknown license type OLD
     - Using old license in Pyarmor 8, the old license only works for Pyarmor 7.x

       Here are :doc:`the latest licenses <../licenses>`

       Please use ``pyarmor-7`` or downgrade pyarmor to 7.7.4
   * - This code has been used too many times
     -

Runtime Errors
==============

.. list-table:: Table-2. Runtime Errors of Obfuscated Scripts
   :name: runtime errors
   :widths: 10 20
   :header-rows: 1

   * - Error Message
     - Reasons
   * - error code out of range
     -
   * - this license key is expired
     -
   * - this license key is not for this machine
     -
   * - missing license key to run the script
     -
   * - unauthorized use of script
     -
   * - this Python version is not supported
     -
   * - the script doesn't work in this system
     -
   * - the format of obfuscated script is incorrect
     - 1. the obfuscated script is made by other Pyarmor version
       2. can not get runtime package path
   * - the format of obfuscated function is incorrect
     -

Outer Errors
============

Here list some outer errors. Most of them are caused by missing some system libraries, or unexpected configuration. It need nothing to do by Pyarmor, just install necessary libraries or change system configurations to fix the problem.

By searching error message in google or any other search engine to find the solution.

- **Operation did not complete successfully because the file contains a virus or is potentially unwanted software question**

  It's caused by Windows Defender, not Pyarmor. I'm sure Pyarmor is safe, but it uses some technics which let anti-virtus tools make wrong decision. The solutions what I thought of

  1. Check documentation of Windows Defender
  2. Ask question in MSDN
  3. Google this error message

.. include:: ../_common_definitions.txt
