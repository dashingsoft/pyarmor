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

- Python 2.7 and Python3.0~Python3.10
- Prebuilt Platform: win32, win_amd64, linux_i386, linux_x86_64, macosx_x86_64
- Embedded Platform: Raspberry Pi, Banana Pi, Orange Pi, TS-4600 / TS-7600 and more

Refer to [support platforms](https://pyarmor.readthedocs.io/en/latest/platforms.html)

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

## License & Purchase

PyArmor is published as shareware, free trial version never expires, but there are
some limitations:

* The trial version could not obfuscate the big scripts
* The trial version uses same public capsule other than private capsule
* The trial version could not download the latest dynamic library of extra platforms
* The super plus mode is not available in the trial version

For details, refer to [PyArmor License](https://pyarmor.readthedocs.io/en/latest/license.html).

## [Change Logs](docs/change-logs.rst)

It describes the fixed issues, new features, incompatible issues in different
versions.

It's recommended to read this carefully before upgrading pyarmor.

## [Report issues](https://github.com/dashingsoft/pyarmor/issues)

If there is any question, first check these [questions and
solutions](https://pyarmor.readthedocs.io/en/latest/questions.html), it may help
you solve the problem quickly.

If there is no solution, for technical issue, click here to [report an
issue](https://github.com/dashingsoft/pyarmor/issues) according to the issue
template, for business and security issue send email to <pyarmor@163.com>.
