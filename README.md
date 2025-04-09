# Pyarmor

Pyarmor is a command-line tool designed for obfuscating Python scripts, binding obfuscated scripts to specific machines, and setting expiration dates for obfuscated scripts.

## Key Features

- **Seamless Replacement**: Obfuscated scripts remain as standard `.py` files, allowing them to seamlessly replace the original Python scripts in most cases.
- **Balanced Obfuscation**: Offers multiple ways to obfuscate scripts to balance security and performance.
- **Irreversible Obfuscation**: Renames functions, methods, classes, variables, and arguments.
- **C Function Conversion**: Converts some Python functions to C functions and compiles them into machine instructions using high optimization options for irreversible obfuscation.
- **Script Binding**: Binds obfuscated scripts to specific machines or sets expiration dates for obfuscated scripts.
- **Themida Protection**: Protects obfuscated scripts using Themida (Windows only).

## Supported Platforms

- Python 2 and Python 3[^1]
- Windows
- Various Linux distributions, including embedded systems and Raspberry Pi
- Apple Intel and Apple Silicon
- Supported architectures: x86_64, aarch64, armv7, etc.[^2]

For more information, check out the [Pyarmor Environments][encironments].

[^1]: Some features may be exclusive to Python 3.
[^2]: Some features may be exclusive to specific architectures.

[encironments]: https://pyarmor.readthedocs.io/en/stable/reference/environments.html

## Quick start

1. **Install Pyarmor**:
```shell
pip install pyarmor
```

2. **Obfuscate the `foo.py` script**:
```shell
pyarmor gen foo.py
```

This command generates an obfuscated script like this at `dist/foo.py`:

```python
from pyarmor_runtime import __pyarmor__
__pyarmor__(__name__, __file__, b'\x28\x83\x20\x58....')
```

3. **Run the obfuscated script**:
```shell
python dist/foo.py
```

For more information, check out the [getting started tutorial][tutorial].

[tutorial]: https://pyarmor.readthedocs.io/en/stable/tutorial/getting-started.html

## License

Pyarmor is published as shareware. The free trial version never expires, but has some limitations.

Refer to [Pyarmor licenses][licenses] for information on license types, features, limitations, and purchasing a Pyarmor license.

Please read the [Pyarmor EULA](LICENSE).

[licenses]: https://pyarmor.readthedocs.io/en/latest/licenses.html

## Getting Help

- **[Ask in learning system][askeke] or [look through check list][checklist]**
- **Consult the [Pyarmor Documentation][doc].**
- **Check the [FAQ][faq] for answers to common questions.**
- **Try the documentation [index][genindex] or the [detailed table of contents][mastertoc].**
- **If you still can't find the information you need, see [asking questions on GitHub][asking].**
- **[Report bugs][issues] following the issue template.**
- **For business and security inquiries, send an email to <pyarmor@163.com>.**

There is also one third-party learn platform

- **[Ask Pyarmor Guru][gurubase], it is a Pyarmor-focused AI to answer your questions** (not made by Pyarmor Team, the answer doesn't stand for Pyarmor Team's opinion)

## Resources

* [Website](https://pyarmor.dashingsoft.com)
* [Documentation][doc]
* [Documentation 8.x](https://pyarmor.readthedocs.io/en/v8.5.12/)
* [Documentation 7.x](https://pyarmor.readthedocs.io/en/v7.7/)
* [Pyarmor 9.1 new features](https://eke.dashingsoft.com/pyarmor/docs/en/index.html)
* [Pyarmor Learning System](https://eke.dashingsoft.com/pyarmor/)

中文资源

* [Pyarmor 网站](https://pyarmor.dashingsoft.com/index-zh.html)
* [Pyarmor 在线文档](https://pyarmor.readthedocs.io/zh/latest/)
* [Pyarmor 8.x 在线文档](https://pyarmor.readthedocs.io/zh/v8.5.12/)
* [Pyarmor 7.x 在线文档](https://pyarmor.readthedocs.io/zh/v7.x/)
* [Pyarmor 9.1 新功能](https://eke.dashingsoft.com/pyarmor/docs/zh/index.html)
* [Pyarmor 学习系统](https://eke.dashingsoft.com/pyarmor/)

## Changelog

Each major version comes with a separate changelog file, detailing fixed issues, new features, and compatibility issues between different versions.

Make sure to read the changelog carefully before upgrading Pyarmor:

- [Pyarmor 8.x Changelog](docs/ChangeLogs.8)
- [Pyarmor 9.x Changelog](docs/ChangeLogs.9)

**Full changelogs** at [releases][releases]

**Upcoming features** at [Pyarmor Release Plan](docs/ReleasePlan.md)

[releases]: https://github.com/dashingsoft/pyarmor/releases
[faq]: https://pyarmor.readthedocs.io/en/latest/questions.html
[issues]: https://github.com/dashingsoft/pyarmor/issues
[genindex]: https://pyarmor.readthedocs.io/en/stable/genindex.html
[mastertoc]: https://pyarmor.readthedocs.io/en/stable/index.html#table-of-contents
[asking]: https://pyarmor.readthedocs.io/en/latest/questions.html#asking-questions-in-github
[doc]: https://pyarmor.readthedocs.io/
[gurubase]: https://gurubase.io/g/pyarmor
[askeke]: https://eke.dashingsoft.com/pyarmor/ask
[checklist]: https://pyarmor.readthedocs.io/en/latest/reference/solutions.html
