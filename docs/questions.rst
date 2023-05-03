==========
 FAQ
==========

.. highlight:: none

.. _asking questions:

Asking questions in Github
==========================

Before ask question, please try these solutions:

- If using :command:`pyarmor-7` or Pyarmor < 8.0, please check `Pyarmor 7.x Doc`_

- Check :ref:`the detailed table of contents <mastertoc>`

- If you have not read :doc:`tutorial/getting-started`, read it

- Check :doc:`reference/errors`

- If you have trouble in pack, check :doc:`topic/repack`

- If you have trouble in :term:`RFT Mode`, check :ref:`using rftmode`

- If you have trouble in :term:`BCC Mode`, check :ref:`using bccmode`

- If you have trouble with third-party libraries, check :doc:`how-to/third-party`

- If it's related to security and performance, check :doc:`topic/performance`

- Look through this page

- Enable debug mode and trace log, check console log and trace log to find more information

- Make sure the scripts work without obfuscation

- Do a simple test, obfuscate a hello world script, and run it with python

- If not using latest Pyarmor version, try to upgrade Pyarmor to latest version.

- Search in the Pyarmor `issues`_

- Search in the Pyarmor `discussions`_

Please report bug in `issues`_ and ask questions in `discussions`_

When report bug in `issues`_, please copy the whole command line :command:`pyarmor gen` and first 4 lines in the console, do not mask version and platform information, and do not paste snapshot image::

    $ pyarmor gen -O dist --assert-call foo.py
    INFO     Python 3.10.0
    INFO     Pyarmor 8.1.1 (trial), 000000, non-profits
    INFO     Platform darwin.x86_64

Packing
=======

**In the old pyarmor 7, I'm using "pyarmor pack ...", I could not find any relate information for this in the pyarmor 8.2. How to solve this?**

  There is no identical pack in Pyarmor 8, Pyarmor 8+ only provide repack function to handle bundle of PyInstaller. Refer to basic tutorial, topic `insight into pack`__ and this solved issue `Pyarmor pack missing in pyarmor 8.0`__

__ https://pyarmor.readthedocs.io/en/stable/topic/repack.html
__ https://github.com/dashingsoft/pyarmor/discussions/1107

License
=======

**we use Docker to build/obfuscate the code locally then publish the Dockerfile to the client. After the build stage, the whole environment (and the license) is gone. I wonder how the workflow would be? Can I add the license file to the pipeline and register everytime and build?**

  It's no problem to run Pyarmor in Docker or CI pipeline to obfuscate application. Each build registering pyarmor with :file:`pyarmor-regfile-xxxx.zip` which is generated in initial registration. But It's not allowed to distribute pakcage pyarmor and :term:`Pyarmor Basic`, :term:`Pyarmor Pro`, :term:`Pyarmor Group` License to customer, and don't run too many build dockers.

**We are currently using a trial license for testing, but unfortunately our scripts are big and we are not able to statistically test the operation of Pyarmor. Do you have a commercial trial license for a certain trial period so that we can test the operation of Pyarmor for our scripts?**

  Sorry, Pyarmor is a small tool and only cost small money, there is no demo license plan.

  Most of features could be verified in trial version, other advanced features, for example, mix-str, bcc mode and rft mode, could be configured to ignore one function or one script so that all the others could work with these advanced features.

**Is the Internet connection only required to generate the obfuscated script? No internet connection is required on the target device that uses such script?**

  No internet connection is required on target device.

  Pyarmor has no any control or limitation to obfuscated scripts, the behaviours of obfuscated scripts are totally defined by user.

  Please check Pyarmor EULA 3.4.1

**I am interested to know if the users are entitled to updates to ensure compatibility with future versions of Python.**

  No. Pyarmor license works with current Pyarmor version forever, but may not work with future Pyarmor version. I can't make sure current Pyarmor version could support all the future versions of Python, so the answer is no.

**If we buy version 8 license, is it compatible with earlier versions like 6.7.2?**

  No. Pyarmor 8 license can't be used with earlier versions, it may report HTTP 401 error or some unknown errors.

**Our company has a suite of products that we offer together or separately to our clients. Do we need a different license for each of them?**

  For a suite of products, if each product is different totally, for example, a suite "Microsoft Office” includes “Microsoft Excel”, “Microsoft Word”, each product need one license.

  If a suite of products share most of Python scripts, as long as the proportion of the variable part of each product is far less than that of the common part, they’re considered as "one product".

  If each product in a suite of products is functionally complementary, for example, product "Editor" for editing the file, product "Viewer" for view the file, they’re considered as "one product"

Upgrading
---------

**Can we obfuscate our codebase with the same level as current? (we are obfuscating our code using super plus mode ("--advanced 5"). Is that available on PyArmor Basic?**

  The old license is valid for ever. In this case need not upgrade old license to Pyarmor Basic licnse, just install Pyarmor 8.x, and using :command:`pyarmor-7` with old license.

  Check :doc:`licenses` for more information about upgrading

**If we upgrade the old license, will the current license expire? (no more available in terms of PyArmor v7?**

  If upgrade old license to any Pyarmor 8 license, the current license is no more available in the terms of Pyarmor 7.

**How long is the current license valid? Is there a published end-of-support schedule?**

  The license is valid for ever with Pyarmor version when purchasing this license, but may not work for future Pyarmor, there is no schedule about in which version current license doesn't work.

  Since the first release Pyarmor changed its license 3 times

  - the intial license issued around year 2010 (I forget the exact date)
  - the second license issued on 2019-10-10
  - this is the third license, issued on 2023-03-10.

Purchasing
==========

**How to refund my order?**

  If this order isn't activated and in 30 days since purchasing, you can refund the order by one of ways

  1. Email to Ordersupport@mycommerce.com with order information and ask for refund.
  2. Or click `FindMyOrder page`_ to submit refund request

.. _FindMyOrder page: https://www.findmyorder.com/store?Action=DisplayEmailCustomerServicePage&Env=BASE&Locale=en_US&SiteID=findmyor

.. include:: _common_definitions.txt
