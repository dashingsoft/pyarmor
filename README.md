# PyArmor

* [Homepage](https://pyarmor.dashingsoft.com) ([中文版网站](https://pyarmor.dashingsoft.com/index-zh.html))
* [Documentation](https://pyarmor.readthedocs.io/en/latest/)([中文版](https://pyarmor.readthedocs.io/zh/latest/))

PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts. It
protects Python scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate co_code of each function (code object) in runtime.
* Clear f_locals of frame as soon as code object completed execution.
* Verify the license file of obfuscated scripts while running it.

Also refer to [The Security of PyArmor](https://pyarmor.readthedocs.io/en/latest/security.html)

## Support Platforms

- Python 2.5, 2.6, 2.7 and Python3
- Prebuilt Platform: win32, win_amd64, linux_i386, linux_x86_64, macosx_x86_64
- Embedded Platform: Raspberry Pi, Banana Pi, Orange Pi, TS-4600 / TS-7600

Refer to [Standard Platform Names](https://pyarmor.readthedocs.io/en/latest/platforms.html#standard-platform-names)

## Quick Start

Installation

    pip install pyarmor

Obfuscate scripts

    pyarmor obfuscate foo.py

Run obfuscated scripts

    python dist/foo.py

Pack obfuscated scripts into one bundle

    pip install pyinstaller
    pyarmor pack foo.py

Obfuscate scripts with an expired license

    pyarmor licenses --expired 2018-12-31 r001
    pyarmor obfuscate --with-license licenses/r001/license.lic foo.py

There is also a web-ui package [pyarmor-webui](https://github.com/dashingsoft/pyarmor-webui)

    pip install pyarmor-webui

Start webui, open web page in browser ([snapshots](https://github.com/dashingsoft/pyarmor-webui/tree/master/snapshots))

    pyarmor-webui

More usage, refer to

* [Examples](https://pyarmor.readthedocs.io/en/latest/examples.html)
* [Using PyArmor](https://pyarmor.readthedocs.io/en/latest/usage.html)
* [Advanced Usage](https://pyarmor.readthedocs.io/en/latest/advanced.html)
* [Man Page](https://pyarmor.readthedocs.io/en/latest/man.html)
* [Sample Shell Scripts](src/examples/README.md)

## License

PyArmor is published as shareware, free trial version never expires, but there are
some limitations:

* The maximum size of code object is about 32768 bytes in trial version
* All the trial version uses same public capsule other than private capsule
* In trial version the module could not be obfuscated by advanced mode
  if there are more than about 30 functions (code objects) in this module.
* ...

For details, refer to [PyArmor License](https://pyarmor.readthedocs.io/en/latest/license.html).

### Purchase

Click [Purchase](https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1),

A registration keyfile generally named "pyarmor-regfile-1.zip" will be sent to
your by email immediately after payment is completed successfully. There are 3
files in the archive:

* REAME.txt
* license.lic (registration code)
* .pyarmor_capsule.zip (private capsule)

Run the following command to take this keyfile effects:

    pyarmor register /path/to/pyarmor-regfile-1.zip

Check the registeration information:

    pyarmor register

**The registration code is valid forever, it can be used permanently. But it may
not work with new versions, although up to now it works with all of versions.**

## [Change Logs](docs/change-logs.rst)

## [Report issuses](https://github.com/dashingsoft/pyarmor/issues)

Any question feel free email to <jondy.zhao@gmail.com>, or click here
to [report an issue](https://github.com/dashingsoft/pyarmor/issues)
