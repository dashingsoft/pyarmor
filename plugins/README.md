# Plugins

***This document is written for Pyarmor 7***

***All examples in this folder not work in Pyarmor 8+***

Plugin usually is used to extend license type, or insert some extra check code
to obfuscated scripts to improve the security.

Here are some examples:

* [Check all the mac address](#example-1-check-all-the-mac-address)
* [Check docker container id](#example-2-check-docker-container-id)
* [Check internet time](#example-3-check-internet-time)
* [Check GPU](#example-5-check-gpu)


**The sample code is only a guide, it's strongly recommended to write your
private code in plugin script**

##  Example 1: Check All the Mac Address

Here is an example show how to check all the mac addresses.

There are 2 files in this plugin

    extra_hdinfo.c
    check_multi_mac.py

The dynamic library `extra_hdinfo.so` exports one function `get_multi_mac` which
could get all the mac addresses.

The script [check_multi_mac.py](check_multi_mac.py) will get the multiple mac
address by calling `get_multi_mac` in the dynamic library `extra_hdinfo.so`,
then compare the expected mac address saved in the `license.lic` of the
obfuscated scripts, check whether it's expected.

It will also check the file `extra_hdinfo.so` to be sure it's not changed by
someone else.

First build [extra_hdinfo.c](extra_hdinfo.c):

    gcc -shared -o extra_hdinfo.so -fPIC extra_hdinfo.c

Get sha384 of `extra_hdinfo.so`:

    sha384sum extra_hdinfo.so

Edit the file [check_multi_mac.py](check_multi_mac.py), replace the value of
`lib_hdinfo_checksum` got above.

Then edit the entry script [foo.py](foo.py), insert two comment lines:

    # {PyArmor Plugins}
    # PyArmor Plugin: check_multi_mac()

Now, obfuscate the script with this plugin:

    pyarmor obfuscate --plugin check_multi_mac foo.py

The content of [check_multi_mac.py](check_multi_mac.py) will be insert after the
first comment line `# {PyArmor Plugins}`

And the prefix of second comment will be stripped as:

    check_multi_mac()

So the plugin takes effect.

If the plugin file isn't in the current path, use absolute path instead:

    pyarmor obfuscate --plugin /path/to/check_multi_mac foo.py

The last step is to generate the license file for the obfuscated script.

1. Run the following command to get all mac addresses in target machine

        gcc -DAPP -o hdinfo extra_hdinfo.c
        ./hdinfo

2. Generate the license file and copy it to dist path

        pyarmor licenses -x 70:f1:a1:23:f0:94.08:00:27:51:d9:fe CODE-0001
        pyarmor obfuscate --plugin /path/to/check_multi_mac \
                          --with-license licenses/CODE-0001/license.lic foo.py

Distributing the obfuscated scripts to target machine:

* Copy all the files in the `dist` path to target machine
* Copy `extra_hdinfo.so` to `/usr/lib` in target machine

## Example 2: Check Docker Container ID

First write the plugin [check_docker.py](check_docker.py)

Then edit the entry script [foo.py](foo.py), insert two comment lines:

    # {PyArmor Plugins}
    # PyArmor Plugin: check_docker()

Now, obfuscate the script with this plugin:

    pyarmor obfuscate --plugin check_docker foo.py

If the plugin file isn’t in the current path, use absolute path instead:

    pyarmor obfuscate --plugin /path/to/check_docker foo.py

The last step is to generate the license file for the obfuscated script:

    pyarmor licenses -x f56b1824e453126ab5426708dbbed41d0232f6f2ab21de1c40da934b68a5d8a2 CODE-0002
    pyarmor obfuscate --with-license licenses/CODE-0002/license.lic \
                      --plugin check_docker foo.py

## Example 3: Check Internet Time

First write the plugin [check_ntp_time.py](check_ntp_time.py), you may change
`NTP_SERVER` to your prefer.

Then edit the entry script [foo.py](foo.py), insert two comment lines:

    # {PyArmor Plugins}
    # PyArmor Plugin: check_ntp_time()

Now, obfuscate the script with this plugin:

    pyarmor obfuscate --plugin check_ntp_time foo.py

The last step is to generate the license file for the obfuscated script, which
expired on Oct 31, 2020:

    pyarmor licenses -x 20201031 CODE-0003
    pyarmor obfuscate --with-license licenses/CODE-0003/license.lic \
                      --plugin check_ntp_time foo.py

## Example 4: Create License For Multiple Machines

First write the plugin [check_multiple_machine.py](check_multiple_machine.py).

Then edit the entry script [foo.py](foo.py), insert two comment lines:

    # {PyArmor Plugins}
    # PyArmor Plugin: check_multiple_machine()

Now, obfuscate the script with this plugin:

    pyarmor obfuscate --plugin check_multiple_machine foo.py

The last step is to generate the license file for 3 machines, suppose the serial
number of hard disk in these machines are `ta1`, `ta2`, `ta3`:

    pyarmor licenses -x "ta1;ta2;ta3" CODE-0004
    pyarmor obfuscate --with-license licenses/CODE-0004/license.lic \
                      --plugin check_multiple_machine foo.py

## Example 5: Check GPU

If you are obfuscating the code that should run mostly on GPU (the calculations), there is an easy and straight-forward way to tie your code to a particular GPU.

This [plugin example](https://github.com/dashingsoft/pyarmor/blob/master/plugins/check_gpu.py) is written for Nvidia GPUs. The GPU UUID reported by `nvidia-smi -L` is supposed to be globally unique. I have tested this example in the `super` mode.

To use this plugin:

- Copy this `check_gpu.py` plugin file to some folder;
- Create a simple test script like this (i.e. `test_gpu.py`) in the same folder:
```
# {PyArmor Plugins}
# PyArmor Plugin: check_gpu()
def test():
    print(`It works!`)
```
- You can use the `get_gpu_list()` function from `check_gpu.py` to learn your GPU UUID(s), or you can just run `nvidia-smi -L`;
- Note that the example is written for a use case with only one GPU and its UUID should be in lowercase, amend for your case;
- Create a separate license file: `pyarmor licenses --expired 2022-02-21 -x gpu-70ef1701-4072-9722-cc0b-7c7e75ff76db gpu_test_license`;
- Obfuscate your test script: `pyarmor obfuscate --plugin check_gpu --with-license licenses/gpu_test_license/license.lic --advanced 2 --exact test_gpu.py`;
- Note that since we are using the `super` mode, at the moment of writing this guide there was some [discrepancy](https://github.com/dashingsoft/pyarmor/issues/474) between the public docs and the actual behaviour of runtime module [pytransform](https://pyarmor.readthedocs.io/en/latest/pytransform.html);
