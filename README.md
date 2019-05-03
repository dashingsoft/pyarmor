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

About the license file of obfuscated scripts, refer to [The License File for Obfuscated Script](https://pyarmor.readthedocs.io/en/latest/understand-obfuscated-scripts.html#the-license-file-for-obfuscated-script)

A registration code is required to obfuscate big code object or
generate private obfuscated scripts.

- Personal user: one registration code is enough.
- Company user: one registration code is only used for one project/product.

For details, refer to [About License](https://pyarmor.readthedocs.io/en/latest/license.html).

### Purchase

Click [Purchase](https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1),

A registration code will be sent to your immediately after payment is completed successfully.

After you receive the email which includes registration code, run the
following command to make it effective::

    pyarmor register CODE

Note that command `register` is introduced from `PyArmor` 5.3.3,
please upgrade the old version to the latest one, or directly replace
the content of `license.lic` in the `PyArmor` installed path with the
registration code only (no newline).

Check new license works

    pyarmor --version

**The registration code is valid forever, it can be used permanently.**

## [Change Log](docs/change-logs.rst)

## [Report issuses](https://github.com/dashingsoft/pyarmor/issues)

Any question feel free email to <jondy.zhao@gmail.com>, or click here
to [report an issue](https://github.com/dashingsoft/pyarmor/issues)
