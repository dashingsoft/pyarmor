================
 Error Messages
================

.. highlight:: none

.. program:: pyarmor gen

Here are all the list of errors when running :command:`pyarmor` or obfuscated scripts.

If something is wrong, search error message here to find the reason.

If no exact error message found, most likely it's not caused by Pyarmor, search it in google or any other search engine to find the solution.

Building Errors
===============

**Obfuscating Errors**

.. list-table:: Table-1. Build Errors
   :name: building errors
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

       Pyarmor need query hard disk serial number, mac address etc.

       If it could not get hardware information, it complains of this.

   * - relative import "%s" overflow
     - Obfuscating `.py` script which uses relative import

       Solution: obfuscating the whole package (path), instead of one module (file) separately

**Registering Errors**

.. list-table:: Table-1.1 Register Errors
   :name: register errors
   :widths: 10 20
   :header-rows: 1

   * - Error
     - Reasons
   * - HTTP Error 400: Bad Request
     - Please upgrade Pyarmor to 8.2+ to get the exact error message
   * - HTTP Error 401: Unauthorized
     - Using old pyarmor commands with new license

       Please using Pyarmor 8 commands to obfuscate the scripts
   * - HTTP Error 503: Service Temporarily Unavailable
     - Invoking too many register command in 1 minute

       For security reason, the license server only allows 3 register requests in 1 minute
   * - unknown license type OLD
     - Using old license in Pyarmor 8, the old license only works for Pyarmor 7.x

       Here are :doc:`the latest licenses <../licenses>`

       Please use ``pyarmor-7`` or downgrade pyarmor to 7.7.4
   * - This code has been used too many times
     - If this code is used in CI/Docker pipeline, please send **order information** by registration email of this code to pyarmor@163.com to unlock it. Do not send this code only, it doesn't make sense.
   * - update license token failed
     - If run register command more than 3 times in 1 minute, wait for 5 minutes, and try again.

       If not, try to open `http://pyarmor.dashingsoft.com//api/auth2/` in web browser

       If the page says `NO:missing parameters`, it means network is fine, and license server is fine.

       If Pyarmor is prior to v8.5.3, upgrade Pyarmor to v8.5.3+, then check Python interpreter by the following commands::

         $ python
         >>> from urllib.request import urlopen
         >>> res = urlopen('http://pyarmor.dashingsoft.com//api/auth2/')
         >>> print(res.read())
         b'NO:missing parameter'

       If not return this, but raises exception, it's firewall problem, please configure it to allow Python interpreter to visit `pyarmor.dashingsoft.com:80`

Runtime Errors
==============

**Error messages reported by pyarmor**

If it has an error code, it could be customized.

.. list-table:: Table-2. Runtime Errors of Obfuscated Scripts
   :name: runtime errors
   :widths: 10 10 20
   :header-rows: 1

   * - Error Code
     - Error Message
     - Reasons
   * -
     - error code out of range
     - Internal error
   * - error_1
     - this license key is expired
     -
   * - error_2
     - this license key is not for this machine
     -
   * - error_3
     - missing license key to run the script
     -
   * - error_4
     - unauthorized use of script
     -
   * - error_5
     - this Python version is not supported
     -
   * - error_6
     - the script doesn't work in this system
     -
   * - error_7
     - the format of obfuscated script is incorrect
     - 1. the obfuscated script is made by other Pyarmor version
       2. can not get runtime package path
   * - error_8
     - the format of obfuscated function is incorrect
     -
   * -
     - RuntimeError: Resource temporarily unavailable
     - When using option ``-e`` to obfuscate the script, the obfuscated script need connect to `NTP`_ server to check expire date. If network is not available, or something is wrong with network, it raises this error.

       Solutions:

       1. use local time if device is not connected to internet.

       2. try it again it may works.

       3. Upgrade to Pyarmor 8.4.4+, then check network time by http server. For example, set time server by this command `pyarmor cfg nts=http://your.http-server.com/api/v2/`

   * -
     - Protection Exception
     - If using :option:`--assert-call` or :option:`assert-import`, check section `Filter assert function and import` in the :doc:`../tutorial/advanced`, ignore those problem functions and modules by the traceback.

**Error messages reported by Python interpreter**

Generally they are not pyarmor issues. Please consult Python documentation or google error message to fix them.

.. list-table:: Table-2.1 Other Errors of Obfuscated Scripts
   :name: other runtime errors
   :widths: 10 20
   :header-rows: 1

   * - Error Message
     - Reasons
   * - ImportError: attempted relative import with no known parent package
     - 1. ``from .pyarmor_runtime_000000 import __pyarmor__``

           Do not use :option:`-i` or :option:`--prefix` if you don't know what they're doing.

       For all the other relative import issue, please check Python documentation to learn about relative import knowledge, then check Pyarmor :doc:`man` to understand how to generate runtime packages in different locations.


Outer Errors
============

Here is a list of some outer errors. Most of them are caused by missing some system libraries, or unexpected configuration. It has nothing to do with Pyarmor, just install necessary libraries or change system configurations to fix the problem.

By searching error message in google or any other search engine to find the solution.

**Operation did not complete successfully because the file contains a virus or is potentially unwanted software question**

  It's caused by Windows Defender, not Pyarmor. I'm sure Pyarmor is safe, but it uses some techniques which let anti-virus tools make wrong decision. The solutions what I thought of

  1. Check documentation of Windows Defender
  2. Ask question in MSDN
  3. Google this error message

**Library not loaded: '@rpath/Frameworks/Python.framework/Versions/3.9/Python'**

  When Python is not installed in the standard path, or this Python is not Framework, pyarmor reports this error. The solution is using ``install_name_tool`` to change ``pytransform3.so``. For example, in `anaconda3` with Python 3.9, first search which CPython library is installed::

    $ otool -L /Users/my_username/anaconda3/bin/python

  Find any line includes ``Python.framework``, ``libpython3.9.dylib``, or ``libpython3.9.so``, the filename in this line is CPython library. Or find it in the path::

    $ find /Users/my_username/anaconda3 -name "Python.framework/Versions/3.9/Python"
    $ find /Users/my_username/anaconda3 -name "libpython3.9.dylib"
    $ find /Users/my_username/anaconda3 -name "libpython3.9.so"

  Once find CPython library, using ``install_name_tool`` to change and codesign it again::

    $ install_name_tool -change @rpath/Frameworks/Python.framework/Versions/3.9/Python /Users/my_username/anaconda3/lib/libpython3.9.dylib /Users/my_username/anaconda3/lib/python3.9/site-packages/pyarmor/cli/core/pytransform3.so
    $ codesign -f -s - /Users/my_username/anaconda3/lib/python3.9/site-packages/pyarmor/cli/core/pytransform3.so

**ImportError: libdl.so: cannot open shared object file: No such file or directory**

  When running obfuscated scripts in unmatched platform, it may raise this error.

  In this case checking dependencies by `ldd /path/to/pyarmor_runtime.so` to make sure it works. If not, please select right `--platform` to obfuscate the scripts.

  For example, when obfuscating the scripts in Linux with target platform Termux, somethimes it need specify `--platform linux.aarch64`, not `--platform android.aarch64`, more information refer to `issue 1674`__

__ https://github.com/dashingsoft/pyarmor/discussions/1674

.. include:: ../_common_definitions.txt
