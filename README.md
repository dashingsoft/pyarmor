# PyArmor

* [Homepage](http://pyarmor.dashingsoft.com) ([中文版网站](http://pyarmor.dashingsoft.com/index-zh.html))
* [Documentation](https://pyarmor.readthedocs.io/en/latest/)
* [WebUI Demo](http://pyarmor.dashingsoft.com/demo/index.html)
* [Examples](src/examples)

PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts. It
protects Python scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate co_code of each function (code object) in runtime.
* Clear f_locals of frame as soon as code object completed execution.
* Verify the license file of obfuscated scripts while running it.

Refer to [Protect Python Scripts By PyArmor](docs/protect-python-scripts-by-pyarmor.md)

## Support Platforms

- Python 2.5, 2.6, 2.7 and Python3
- Prebuilt Platform: win32, win_amd64, linux_i386, linux_x86_64, macosx_x86_64
- Embedded Platform: Raspberry Pi, Banana Pi, Orange Pi, TS-4600 / TS-7600

Refer to [docs/platforms.rst](docs/platforms.rst)

## Quick Start

Installation

    pip install pyarmor

Obfuscate scripts

    pyarmor obfuscate examples/simple/queens.py

Run obfuscated scripts

    cd dist
    python queens.py

Pack obfuscated scripts with `PyInstaller`, `py2exe`, `cx_Freeze` etc.

    pip install pyinstaller
    pyarmor pack examples/py2exe/hello.py

Generate an expired license and run obfuscated scripts with new license

    pyarmor licenses --expired 2018-12-31 Customer-Jondy
    cp licenses/Customer-Jondy/license.lic dist/

    cd dist/
    python queens.py

Start webui, open web page in browser for basic usage of PyArmor

    pyarmor-webui

More usage, refer to [Examples](src/examples/README.md), [Documentation](https://pyarmor.readthedocs.io/en/latest/)

## License

PyArmor is published as shareware. Free trial version never expires, the limitations are

- The maximum size of code object is 35728 bytes in trial version
- The scripts obfuscated by trial version are not private. It means
  anyone could generate the license file which works for these
  obfuscated scripts.

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

**The registration code is valid forever, it can be used permanently.**

## [Change Log](docs/change-logs.rst)

## [Report issuses](https://github.com/dashingsoft/pyarmor/issues)

Any question feel free email to <jondy.zhao@gmail.com>, or click here
to [report an issue](https://github.com/dashingsoft/pyarmor/issues)
