.. _module pytransform:

Runtime Module `pytransform`
============================

If you have realized that the obfuscated scripts are black box for end
users, you can do more in your own Python scripts.In these cases,
:mod:`pytransform` would be useful.

The :mod:`pytransform` module is distributed with obfuscated scripts,
and must be imported before running any obfuscated scripts. It also
can be used in your python scripts.

Contents
--------

.. exception:: PytransformError

   This is raised when any pytransform api failed. The argument to the
   exception is a string indicating the cause of the error.

.. function:: get_expired_days()

   Return how many days left for time limitation license.

   >0: valid in these days

   -1: never expired

.. note::

   If the obfuscated script has been expired, it will raise exception
   and quit directly. All the code in the obfuscated script will not
   run, so this function will never return 0.

.. function:: get_license_info()

   Get license information of obfuscated scripts.

   It returns a dict with keys:

   * expired: Expired date
   * IFMAC: mac address bind to this license
   * HARDDISK: serial number of harddisk bind to this license
   * IPV4: ipv4 address bind to this license
   * DATA: any data stored in this licese, used by extending license type
   * CODE: registration code of this license

   The value `None` means no this key in the license.

   Raise :exc:`Exception` if license is invalid, for example, it has
   been expired.

.. function:: get_license_code()

   Return a string, which is specified as generating the licenses for
   obfucated scripts.

   Raise :exc:`Exception` if license is invalid.

.. function:: get_hd_info(hdtype, size=256)

   Get hardware information by *hdtype*, *hdtype* could one of

   *HT_HARDDISK* return the serial number of first harddisk

   *HT_IFMAC* return mac address of first network card

   Raise :exc:`Exception` if something is wrong.

.. attribute:: HT_HARDDISK, HT_IFMAC

   Constant for `hdtype` when calling :func:`get_hd_info`

Examples
--------

Copy those example code to any script, for example `foo.py`, obfuscate
it, then run the obfuscated script.

Show left days of license

.. code-block:: python

   from pytransform import PytransformError, get_license_info, get_expired_days
   try:
       code = get_license_info()['CODE']
       left_days = get_expired_days()
       if left_days == -1:
           print('This license for %s is never expired' % code)
       else:
           print('This license for %s will be expired in %d days' % (code, left_days))
   except Exception as e:
       print(e)

More usage refer to :ref:`Using Plugin to Extend License Type`

.. note::

   Though `pytransform.py` is not obfuscated when running the obfuscated script,
   it's also protected by `PyArmor`. If it's changed, the obfuscated script will
   raise protection exception.

   Refer to :ref:`special handling of entry script`
