.. _license:

License
=======

The software is distributed as Free To Use But Restricted. Free trial
version never expires, the limitations are

- The trial version could not obfuscate the big scripts.
- The scripts obfuscated by trial version are not private. It means
  anyone could generate the license file for these obfuscated scripts.
- The trial version could not download the latest dynamic library of
  extra platforms, the old versions still are available.
- The super plus mode is not availaible in the trial version.
- Without permission the trial version may not be used to obfuscate
  the Python scripts of any commercial product.

About the license file of obfuscated scripts, refer to :ref:`The
License File for Obfuscated Script`

A license code is required to unlock all the above limitations.

There are 2 basic types of licenses issued for the software:

* A personal license for home users. The user purchases one license to
  use the software on his own computer. When placing an order of this
  kind of license, please fill real name as registration name, this
  software is only authorized to this registration name.

  Home users may use their personal license to obfuscate all the
  python scripts which are property of the license owner, to generate
  private license files for the obfuscated scripts and distribute them
  and all the required files to any other machine or device.

  Home users could NOT obfuscate any python script which is NOT
  property of the license owner.

* A enterprise license for business users. The user purchases one
  license to use the software for one product serials of an
  organization. When placing an order of this kind of license, please
  fill orginization name plus product name, this software is only
  authorized to this registration name.

  One product serials include the current version and any other latter
  versions of the same product.

  Business users may use their enterprise license on all computers and
  embedded devices to obfuscate all the python scripts of this product
  serials, to generate private license files for these obfuscated
  scripts and distribute them and all the required files to any other
  machine and device.

  Without permission of the software owner the license purchased for
  one product serials should not be used for other product
  serials. Business users should purchase new license for different
  product serials.

  In any case, the software is only used to obfuscate the Python scripts
  owned by the authorized person or enterprise.

Purchase
--------

To buy a license, please run command

    pyarmor register --buy

Or open the following url in any web browser

https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1

For personal license, please fill the registeration name with real name when
placing an order.

For enterprise license, please fill the registeration name with enterprise name,
and also fill "License To Product" with the product name which will use this
software.

A registration file generally named "pyarmor-regcode-xxxx.txt" will be sent by
email immediately after payment is completed successfully.

Save it to disk, then run the following command to register PyArmor

    pyarmor register /path/to/pyarmor-regcode-xxxx.txt

Check the registration information:

    pyarmor register

After registration successfully, remove all the obfuscated scripts by trial
version, then obfuscate them again.

.. note::

    If the version of PyArmor < 6.5.2, please open the registration file
    "pyarmor-regcode-xxxx.txt" by any text editor, following the guide in it to
    register PyArmor

.. important::

    The registration code is valid forever, it can be used permanently, but it
    may not work with future versions.

Upgrade Notes
-------------

The license purchased before **2019-10-10** don't support to upgrade the latest
version. A new license is required to use the latest version.

Technical Support
-----------------

If there is any question, first check these `questions and solutions
<https://pyarmor.readthedocs.io/en/latest/questions.html>`_, it may help you
solve the problem quickly.

If there is no solution, for technical issue, click here to `report an issue
<https://github.com/dashingsoft/pyarmor/issues>`_ according to the issue
template, for business and security issue send email to pyarmor@163.com

Generally all the other issues sent by email will be ignored.

There are 3 kinds of issues:

1. The limitation of obfuscated scripts, or called known issues.
2. PyArmor defect.
3. Wrong usage.

For the first catalog, it can't be fixed. For example, use ``inspect`` to visit
co_code of code object, use ``pdb`` to trace obfuscated scripts. All of these
don't work, they're known issues. Here list all the known issues :ref:`The
Differences of Obfuscated Scripts`.

For the second catalog, it's my due to fix it.

For the rests, it's your due to read the documentation and fix it. I'll give you
hints and maybe examples, but I will not hand by hand tell you which comand and
options should be used to obfuscate your scripts.

Suppose you purchase Microsoft Excel, and want to make a complex chart. You must
learn the advanced features of Excel, then make this chart by yourself. You can
not ask Microsoft to make the complex chart for you.

Similarly pyarmor provides a lot of features and well document, but you need
learn them by yourself. For example, the restrict mode is advanced feature of
PyArmor, my due is to implement it as described in the document, you need learn
this advanced feature and refine you code to adapt it. It's not my due to read
your scripts and adapt your scripts to restrict mode.

If you plan to obfuscate or use any third-party package, I also can't obfuscate
this package for you and make sure it's compatible with pyarmor. Here is a list
about all of :ref:`The Differences of Obfuscated Scripts`. If the package uses
these features changed by obfuscated scripts, it will not work with pyarmor.

There are countless big packages in Python world, many packages I never use and
even don't know at all. It's also not easy for me to research a complex package
to find which line conflicts with pyarmor, and it's difficult for me to run all
of these complex packages in my local machine.

Generally in this case users provide the simple snapshot code around exception,
or some running information, I analysis them to find where it may conflict with
pyarmor and try to find the solution.

Q & A
-----

1. Single PyArmor license purchased can be used on various machines for
   obfuscation? or its valid only on one machine? Do we need to install license
   on single machine and distribute obfuscate code?

   | It can be used on various machines, but one license only for one product.

2. Single license can be used to obfuscate Python code that will run various
   platforms like windows, various Linux flavors?

   | For all the features of current version, it's yes. But in future versions,
   | I'm not sure one license could be used in all of platforms supported by
   | PyArmor.

3. How long the purchased license is valid for? is it life long?

   | It's life long. But I can't promise it will work for the future version of PyArmor.

4. Can we use the single license to obfuscate various versions of Python
   package/modules?

   | Yes, only if they're belong to one product.

5. Is there support provided in case of issues encountered?

   | Report issue in github or send email to me.

6. Does Pyarmor works on various Python versions?

   | Most of features work on Python27, and Python30~Python38, a few features
   | may only work for Python27, Python35 later.

7. Are there plans to maintain PyArmor to support future released Python
   versions?

   | Yes. The goal of PyArmor is let Python could be widely used in the
   | commercial softwares.

8. What is the mechanism in PyArmor to identify whether modules belong to same
   product? how it identifies product?

   | PyArmor could not identify it by itself, but I can check the obfuscated
   | scripts to find which registerred user distributes them. So I can find two
   | products are distributed by one same license.

9. If product undergoes revision ie. version changes, can same license be used
   or need new license?

   | Same license is OK.

10. What means a product serials under PyArmor EULA?

   | A product serial means a sale unit and its upgraded versions. For
   | example, AutoCAD 2003, 2010 could be taken as a product serials.

.. include:: _common_definitions.txt
