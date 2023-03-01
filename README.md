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
* Convert part of Python functions to C function, compile to binary by
  high optimize option, irreversible obfuscation
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

[Pyarmor licenses][licneses] introduces license type, features and
limitations for each license type and how to purchase Pyarmor license.

Also read [Pyarmor End User License Agreement](LICENSE)

[licenses]: https://pyarmor.readthedocs.io/en/latest/licenses.html

## Getting help

Having trouble?

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

## Change logs

It's important to read this carefully before upgrading pyarmor.

Each major version has one file to log changes, it describes the fixed
issues, new features, incompatible issues in different versions

* [Pyarmor 8.x Change Logs](docs/ChangeLogs.8)

There are significant changes in Pyarmor 8.0, users prior to 8.0 should be
read this to make judge whether upgrade Pyarmor

* [Pyarmor 8.0 Release Notes](docs/ReleaseNotes.8)

## Resources

* [Website](https://pyarmor.dashingsoft.com)
* [Documentation](https://pyarmor.readthedocs.io/)
* [Documentation 7.x](https://pyarmor.readthedocs.io/en/v7.7/)

中文资源

* [Pyarmor 网站](https://pyarmor.dashingsoft.com/index-zh.html)
* [Pyarmor 在线文档](https://pyarmor.readthedocs.io/zh/)
* [Pyarmor 7.x 在线文档](https://pyarmor.readthedocs.io/zh/v7.x/))
