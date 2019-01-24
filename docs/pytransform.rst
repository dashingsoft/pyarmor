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

.. function:: get_license_info()

   Get license information of obfuscated scripts.

   It returns a dict with keys *expired*, *CODE*, *IFMAC*.

   The value of *expired* is == -1 means no time limitation.

   Raise :exc:`PytransformError` if license is invalid, for example,
   it has been expired.

.. function:: get_hd_info(hdtype, size=256)

   Get hardware information by *hdtype*, *hdtype* could one of

   *HT_HARDDISK* return the serial number of first harddisk

   *HT_IFMAC* return mac address of first network card

   Raise :exc:`PytransformError` if something is wrong.

.. attribute:: HT_HARDDISK, HT_IFMAC

   Constant for `hdtype` when calling :func:`get_hd_info`

Examples
--------

Show left days of license

.. code-block:: python

   from pytransform import PytransformError, get_license_info
   try:
       left_days = generate_license_info()['expired']
       if left_days == -1:
           print('This license is never expired')
       else:
           print('This license will be expired in %d days' % left_days)
   except PytransformError as e:
       print(e)

Double check harddisk information

.. code-block:: python

   from pytransform import get_hd_info, HT_IFMAC
   expected_mac_address = 'xx:xx:xx:xx:xx'
   if get_hd_info(HT_IFMAC) != expected_mac_address:
       sys.exit(1)

Check internet time by NTP server, expired on `2019-2-2`

.. code-block:: python

    from datetime import datetime
    if datetime.now() > datetime(2019, 2, 2):
        sys.exit(1)
