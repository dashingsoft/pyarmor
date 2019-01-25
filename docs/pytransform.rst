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

   0: has been expired

   -1: never expired

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

   from pytransform import PytransformError, get_license_info, get_trial_days
   try:
       code = generate_license_info()['CODE']
       left_days = get_trial_days()
       if left_days == -1:
           print('This license for %s is never expired' % code)
       else:
           print('This license %s will be expired in %d days' % (code, left_days))
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

    from ntplib import NTPClient
    from time import mktime, strptime

    NTP_SERVER = 'europe.pool.ntp.org'
    EXPIRED_DATE = '20190202'

    c = NTPClient()
    response = c.request(NTP_SERVER, version=3)
    if response.tx_time > mktime(strptime(EXPIRED_DATE, '%Y%m%d')):
        sys.exit(1)
