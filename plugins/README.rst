Plugins
=======

Plugin usually is used to extend license type.

Example 1: Check All the Mac Address
------------------------------------

Here is an example show how to check all the mac addresses.

There are 2 files in this plugin::

    extra_hdinfo.c
    check_multi_mac.py

The dynamic library `extra_hdinfo.so` exports one function `get_multi_mac` which
could get all the mac addresses.

The script `check_multi_mac.py`_ will get the multiple mac address by calling
`get_multi_mac` in the dynamic library `extra_hdinfo.so`, then compare the
expected mac address saved in the `license.lic` of the obfuscated scripts, check
whether it's expected.

It will also check the file `extra_hdinfo.so` to be sure it's not changed by
someone else.

First build `extra_hdinfo.c`_::

    gcc -shared -o extra_hdinfo.so -fPIC extra_hdinfo.c

Get sha384 of `extra_hdinfo.so`::

    sha384sum extra_hdinfo.so

Edit the file `check_multi_mac.py`_, replace the value of `lib_hdinfo_checksum`
got above.

Then edit the entry script `foo.py <foo.py>`_ , insert two comment lines::

    # {PyArmor Plugins}
    # PyArmor Plugin: check_multi_mac()

Now, obfuscate the script with this plugin::

    pyarmor obfuscate --plugin check_multi_mac foo.py

The content of `check_multi_mac.py`_ will be insert after the first
comment line `# {PyArmor Plugins}`

And the prefix of second comment will be stripped as::

    check_multi_mac()

So the plugin takes effect.

If the plugin file isn’t in the current path, use absolute path instead::

    pyarmor obfuscate --plugin /path/to/check_multi_mac foo.py

The last step is to generate the license file for the obfuscated script.

1. Run the following command to get all mac addresses in target machine::

    gcc -DAPP -o hdinfo extra_hdinfo.c
    ./hdinfo

2. Generate the license file and copy it to dist path::

    pyarmor licenses -x 70:f1:a1:23:f0:94.08:00:27:51:d9:fe CODE-0001
    cp licenses/CODE-0001/license.lic ./dist

Distributing the obfuscated scripts to target machine:

* Copy all the files in the `dist` path to target machine
* Copy `extra_hdinfo.so` to `/usr/lib` in target machine

Example 2: Check Docker Container ID
------------------------------------

First write the plugin `check_docker.py`_::

    from pytransform import _pytransform
    from ctypes import py_object, PYFUNCTYPE

    def get_license_data():
        prototype = PYFUNCTYPE(py_object)
        dlfunc = prototype(('get_registration_code', _pytransform))
        rcode = dlfunc().decode()
        index = rcode.find(';', rcode.find('*CODE:'))
        return rcode[index+1:]

    def check_docker():
        cid = None
        with open("/proc/self/cgroup") as f:
            for line in f:
                if line.split(':', 2)[1] == 'name=systemd':
                    cid = line.strip().split('/')[-1]
                    break

        if cid is None or cid != get_license_data():
            raise RuntimeError('license not for this machine')


Then edit the entry script `foo.py`_ , insert two comment lines::

    # {PyArmor Plugins}
    # PyArmor Plugin: check_docker()

Now, obfuscate the script with this plugin::

    pyarmor obfuscate --plugin check_docker foo.py

If the plugin file isn’t in the current path, use absolute path instead::

    pyarmor obfuscate --plugin /path/to/check_docker foo.py

The last step is to generate the license file for the obfuscated script::

    pyarmor licenses -x f56b1824e453126ab5426708dbbed41d0232f6f2ab21de1c40da934b68a5d8a2 CODE-0002
    cp licenses/CODE-0002/license.lic ./dist


.. _foo.py: foo.py
.. _extra_hdinfo.c: extra_hdinfo.c
.. _check_multi_mac.py: check_multi_mac.py
.. _check_docker.py: check_docker.py
