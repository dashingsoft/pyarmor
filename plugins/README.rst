Plugins
=======

Plugin usually is used to extend license type.

Example 1: Check All the Mac Address
------------------------------------

Here is an example show how to check all the mac addresses.

There are 2 files in this plugin::

    extra_hdinfo.c
    check_multi_mac.py

The dynamic library `extra_hdinfo.so` exports one function
`get_multi_mac` which could get all the mac addresses.

The script `check_multi_mac.py` will get the multiple mac address by
calling `get_multi_mac` in the dynamic library `extra_hdinfo.so`, then
compare the expected mac address saved in the `license.lic` of the
obfuscated scripts, check whether it's expected.

It will also check the file `extra_hdinfo.so` to be sure it's not
changed by someone else.

First build dynamic library `extra_hdinfo.so` used to get all mac
addresses::

    gcc -shared -o extra_hdinfo.so -fPIC extra_hdinfo.c

Get sha384 of `extra_hdinfo.so`::

    sha384sum extra_hdinfo.so

Edit the file `check_multi_mac.py`, replace the value of
`lib_hdinfo_checksum` got above.

Next edit the entry script `foo.py`, insert two comment lines::

    import logging
    import sys

    # {PyArmor Plugins}

    def main():
        # PyArmor Plugin: check_multi_mac()
        logging.info("Hello World!")


    if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO)
        main()

Now, obfuscate the script with this plugin::

    pyarmor obfuscate --plugin check_multi_mac foo.py

The content of `check_multi_mac.py` will be insert after the first
comment line `# {PyArmor Plugins}`

And the prefix of second comment will be stripped::

    def main():
        check_multi_mac()
        logging.info("Hello World!")

So the plugin takes effect.

If the plugin file isn’t in the current path, use absolute path instead::

    pyarmor obfuscate --plugin /path/to/check_multi_mac foo.py

The last step is to generate the license file for the obfuscated script.

1. Run the following command to get all mac addresses in target machine::

    gcc -DAPP -o hdinfo extra_hdinfo.c
    ./hdinfo

2. Generate the license file and copy it to dist path::

    pyarmor licenses 70:f1:a1:23:f0:94.08:00:27:51:d9:fe
    cp licenses/70:f1:a1:23:f0:94.08:00:27:51:d9:fe/license.lic ./dist

Distributing the obfuscated scripts to target machine:

* Copy all the files in the `dist` path to target machine
* Copy `extra_hdinfo.so` to `/usr/lib` in target machine

Example 2: Check Docker Container ID
------------------------------------

First write the plugin `check_docker.py`::

    from pytransform import get_license_code
    
    
    def check_docker_id():
        cid = None
        with open("/proc/self/cgroup") as f:
            for line in f:
                if line.split(':', 2)[1] == 'name=systemd':
                    cid = line.strip().split('/')[-1]
                    break
    
        if cid is None or cid != get_license_code():
            raise RuntimeError('license not for this machine')
    

Then edit the entry script `foo.py`, insert two comment lines::

    import logging
    import sys

    # {PyArmor Plugins}

    def main():
        # PyArmor Plugin: check_docker_id()
        print("Hello World!")


    if __name__ == '__main__':
        main()

Now, obfuscate the script with this plugin::

    pyarmor obfuscate --plugin check_docker foo.py
        
If the plugin file isn’t in the current path, use absolute path instead::

    pyarmor obfuscate --plugin /path/to/check_docker foo.py
    
The last step is to generate the license file for the obfuscated script::

    pyarmor licenses f56b1824e453126ab5426708dbbed41d0232f6f2ab21de1c40da934b68a5d8a2
    cp licenses/f56b1824e453126ab5426708dbbed41d0232f6f2ab21de1c40da934b68a5d8a2/license.lic ./dist
