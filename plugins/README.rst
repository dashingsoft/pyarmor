Plugins
=======

Plugin usually is used to extend license type.

Here is an example show how to check all the mac addresses.

There are 2 files in this plugin::

    extra_hdinfo.c
    check_multi_mac.py
    
First build dynamic library `extra_hdinfo.so` used to get all mac
addresses::

    gcc -shared -o extra_hdinfo.so -fPIC extra_hdinfo.c

The dynamic library `extra_hdinfo.so` exports one function
`get_multi_mac` which could get all the mac addresses.

The script `check_multi_mac.py` will call `get_multi_mac` in the
dynamic library `extra_hdinfo.so` by `ctypes`, and then check whether
it's expected.

Run the following command to get all mac addresses in target machine::

    gcc -DAPP -o hdinfo extra_hdinfo.c
    ./hdinfo

Edit the file `check_multi_mac.py`, replace the value of
`expected_mac_addresses` got above.

It will also check the file `extra_hdinfo.so` to be sure it's not
changed by someone else.

Get sha384 of `extra_hdinfo.so`::

    sha384sum extra_hdinfo.so

Edit the file `check_multi_mac.py`, replace the value of
`lib_hdinfo_checksum` got above.

Now edit the entry script `foo.py`, insert two comment lines::

    import logging
    import sys
    
    # {PyArmor Plugins}
    
    def main():
        # PyArmor Plugin: check_multi_mac()
        logging.info("Hello World!")
    
    
    if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO)
        main()
      
Finally, obfuscate the script with this plugin::

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

Distributing the obfuscated scripts to target machine:

* Copy all the files in the `dist` path to target machine
* Copy `extra_hdinfo.so` to `/usr/lib` in target machine
