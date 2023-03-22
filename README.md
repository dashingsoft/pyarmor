# Pyarmor

Pyarmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

## Key features

* The obfuscated scritpt is still a normal `.py` script, in most of
  cases the original python scripts can be replaced with obfuscated
  scripts seamlessly.
* Provide many ways to obfuscate the scripts to balance security and
  performance
* Rename functions/methods/classes/variables/arguments, irreversible
  obfuscation
* Convert part of Python functions to C functions, compile them to machine
  instructions by high optimize option, irreversible obfuscation
* Bind obfuscated scripts to fixed machine or expire obfuscted scripts
* Protect obfuscated scripts by Themida (Only for Windows)

## Support platforms

* Python 2 and Python 3[^1]
* Windows
* Many linuxs, include embedded systems, Raspberry Pi etc.
* Apple Intel and Apple Silicon
* Support arches: x86_64, aarch64, armv7 etc.[^2]

[^1]: some features may only for Python3
[^2]: some features may only for special arch.

## Quick start

Install

    pip install pyarmor

Obfuscate the script `foo.py`

    pyarmor gen foo.py

This command generates an obfuscated script `dist/foo.py` like this:

```python
    from pyarmor_runtime import __pyarmor__
    __pyarmor__(__name__, __file__, b'\x28\x83\x20\x58....')
```

Run it

    python dist/foo.py

Also look at the [getting started][tutorial]

[tutorial]: https://pyarmor.readthedocs.io/en/stable/tutorial/getting-started.html

## License

Pyarmor is published as shareware, free trial version never expires, but there are
some limitations.

[Pyarmor licenses][licenses] introduces license type, features and
limitations for each license type and how to purchase Pyarmor license.

Also read [EULA of Pyarmor](LICENSE)

[licenses]: https://pyarmor.readthedocs.io/en/stable/licenses.html

## Getting help

Having trouble?

Read this [Pyarmor 8.0 Documentation][doc] at first.

Try the [FAQ][faq] – it's got answers to many common questions.

Looking for specific information? Try the documentation [index][genindex],
or [the detailed table of contents][mastertoc].

Not found anything? See [asking questions in github][asking].

[Report bugs][issues] according to the issue template.

Send email to <pyarmor@163.com> for business and security issue.

[faq]: https://pyarmor.readthedocs.io/en/stable/questions.html
[issues]: https://github.com/dashingsoft/pyarmor/issues
[genindex]: https://pyarmor.readthedocs.io/en/stable/genindex.html
[mastertoc]: https://pyarmor.readthedocs.io/en/stable/index.html#table-of-contents
[asking]: https://pyarmor.readthedocs.io/en/stable/questions.html#asking-questions-in-github
[doc]: https://pyarmor.readthedocs.io/en/stable/

## Resources

* [Website](https://pyarmor.dashingsoft.com)
* [Documentation 8.0][doc]
* [Documentation 7.x](https://pyarmor.readthedocs.io/en/v7.7/)

中文资源

* [Pyarmor 网站](https://pyarmor.dashingsoft.com/index-zh.html)
* [Pyarmor 8.0 在线文档](https://pyarmor.readthedocs.io/zh/stable/)
* [Pyarmor 7.x 在线文档](https://pyarmor.readthedocs.io/zh/v7.x/))

## Change logs

There are significant changes in Pyarmor 8.0. Pyarmor 8.0 has been rewritten,
and new features are implemented by new commands: `gen`, `reg`, `cfg`. And they
only works for Python 3.7+.

At first release, only x86_64 for windows, linux, macosx works (2023-03-08), and
aarch64 for linux and macosx works soon (before 2023-04-01), armv7 and x86 will
work about 2023-06-01. For all the other arches only on demand.

For compatibility the old commands like `obfuscate` etc. are still available,
but they're not belong to Pyarmor 8.0

Users prior to 8.0 should read this [Import Notes][import-notes] to make judge
whether upgrade Pyarmor

Each major version has one file to log changes, it describes the fixed issues,
new features, incompatible issues in different versions

It's important to read this carefully before upgrading pyarmor.

* [Pyarmor 8.x Change Logs](docs/ChangeLogs.8)

[import-notes]: #import-notes-for-pyarmor-prior-to-80

## Import Notes for Pyarmor prior to 8.0

In future only bug fix for old modes, no new features for old modes.

Most of the old commands could be used normally, but there still have some
changes.

There are 3 cases for old users after Pyarmor 8.0 is released:

* Never upgrade to 8.0+

  - SPP mode doesn't work

    In order to use SPP mode, it's necessary to upgrade Pyarmor to 8.0+

  - Command `pyarmor register` without any argument return `404` error

    It is used to query registration information in old Pyarmor, but now license
    server doesn't serve this web api.

    Instead use `pyarmor -v` to make sure it's not trial version.

  - Registering Pyarmor by `pyarmor register pyarmor-regcode-xxxxxx.txt` can be
    used no more than 10 times

    If using Pyarmor in CI server or docker, regsiter Pyarmor by the second
    method described in the registration file "pyarmor-regcode-xxxxxx.txt"

* Upgrade to 8.0 but only use old features

  - Command `pyarmor -v` only checks and prints new Pyarmor License
  - Command `pyarmor -h` only prints help for new cli

  There are 2 solutions to make command `pyarmor` same as before:

  - Export environment variable `PYARMOR_CLI=7`
  - Recreate command `pyarmor` link to `python -m pyarmor.pyarmor`

* Upgrade to 8.0 and use new features

  - Follow new [EULA of Pyarmor](LICENSE). Especially for old personal license
    and it's used in many products, new license only allows one proudct.

  - Not all old licenses could be upgraded to new license freely, refer to
    [Pyarmor licenses][licenses]

  - The old features need not internect connection, but new features need

  - The old features support Python 2.7~3.10, but new features only support
    Python 3.7+
