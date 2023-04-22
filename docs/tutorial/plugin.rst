=============================
 Customization and Extension
=============================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen


Create hook script in the `.pyarmor/hooks/foo.py`

.. code-block:: python

    from http.client import HTTPSConnection
    expire = __pyarmor__(1, None, b'keyinfo', 1)
    host = 'worldtimeapi.org'
    path = '/api/timezone/Europe/Paris'
    conn = HTTPSConnection(host)
    conn.request("GET", path)
    res = conn.getresponse()
    if res.code == 200:
        data = res.read()
        s = data.find(b'"unixtime":')
        n = data.find(b',', s)
        current = int(data[s+11:n])
        if current > expire:
            raise RuntimeError('license is expired')
     else:
         host = 'timeapi.io'
         path = '/api/Time/current/zone?timeZone=Europe/Amsterdam'
         ...

Then generate script with local time::

    $ pyarmor gen -e .30 foo.py

.. include:: ../_common_definitions.txt
