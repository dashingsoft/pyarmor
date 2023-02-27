# Pyarmor

* [Homepage](https://pyarmor.dashingsoft.com) ([中文版网站](https://pyarmor.dashingsoft.com/index-zh.html))
* [Documentation](https://pyarmor.readthedocs.io/en/latest/)([中文版](https://pyarmor.readthedocs.io/zh/latest/))

Pyarmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts. It
protects Python scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate co_code of each function (code object) in runtime.
* Clear f_locals of frame as soon as code object completed execution.
* Verify the license file of obfuscated scripts while running it.

Also refer to [The Security of Pyarmor](https://pyarmor.readthedocs.io/en/latest/security.html)

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
* [Using Pyarmor](https://pyarmor.readthedocs.io/en/latest/usage.html)
* [Advanced Usage](https://pyarmor.readthedocs.io/en/latest/advanced.html)
* [Man Page](https://pyarmor.readthedocs.io/en/latest/man.html)
* [Sample Shell Scripts](src/examples/README.md)

## License & Purchase

Pyarmor is published as shareware, free trial version never expires, but there are
some limitations:

* The trial version could not obfuscate the big scripts
* The trial version uses same public capsule other than private capsule
* The trial version could not download the latest dynamic library of extra platforms
* The super plus mode is not available in the trial version

For details, refer to [Pyarmor License](https://pyarmor.readthedocs.io/en/latest/license.html).

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

## Release Plan

In order to improve security and support Python 3.11, there are significant
changes in the next major version Pyarmor 8.0

Pyarmor 8.0 release date is about 2023-03-08 (March 8, 2023) (delay one week)

The main features for Pyarmor 8.0

* Support Python 3.11
* BCC mode for x86_64 and arm64, the enhancement of spp mode, Irreversible
* RFT mode, rename function/method/class/variable/argument, Irreversible
* Customize and localize runtime error messages

The scheduled features for Pyarmor 8.0+ (not released with 8.0)

* BCC mode for armv7 and x86
* Support Python 3.12

Pyarmor status will be stable by the end of 2024 (Dec. 31, 2024)

### New EULA

The big changes of EULA for Pyarmor 8.0+

* For non-profit usage, one license is OK.
* For commercial usage, one product one license.

There are only 2 new license types for Pyarmor 8.0+

* pyarmor-basic, one license price 52$
* pyarmor-pro, one license price 89$

The main differences for each type

* pyarmor-pro: 2 irreversible obfuscation modes BCC/RFT
* pyarmor-basic: no BCC/RFT modes
* pyarmor trial version: can't obfuscate big file

The old license code starts with "pyarmor-vax-" could be upgraded to
pyarmor-basic without extra fee following new EULA. If it's personal
license type, it need provide the product name bind to pyarmor-basic
for commercial usage.

## IMPORTANT NOTE

A few features may not work once Pyarmor 8.0.1 is released:

* SPP mode doesn't work for Pyarmor prior to 8.0.1

  In order to use SPP mode, it's necessary to upgrade Pyarmor to 8.0+

* Querying registration information by "pyarmor register" (no arguments)
  doesn't work in future, it always return error even there is a valid
  license

  The command "pyarmor -v" could be used to check whether the registration
  is successful

* Registering Pyarmor by "pyarmor register pyarmor-vax-xxxxxx.txt" can be
  used no more than 10 times

  If using Pyarmor in CI server or docker, regsiter Pyarmor by the second
  method described in the registration file "pyarmor-vax-xxxxxx.txt"
