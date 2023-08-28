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

1. **Consult the [Pyarmor 8.0 Documentation][doc].**
2. **Check the [FAQ][faq] for answers to common questions.**
3. **Try the documentation [index][genindex] or the [detailed table of contents][mastertoc].**
4. **If you still can't find the information you need, see [asking questions on GitHub][asking].**
5. **[Report bugs][issues] following the issue template.**
6. **For business and security inquiries, send an email to <pyarmor@163.com>.**

[faq]: https://pyarmor.readthedocs.io/en/latest/questions.html
[issues]: https://github.com/dashingsoft/pyarmor/issues
[genindex]: https://pyarmor.readthedocs.io/en/stable/genindex.html
[mastertoc]: https://pyarmor.readthedocs.io/en/stable/index.html#table-of-contents
[asking]: https://pyarmor.readthedocs.io/en/latest/questions.html#asking-questions-in-github
[doc]: https://pyarmor.readthedocs.io/

## Resources

* [Website](https://pyarmor.dashingsoft.com)
* [Documentation 8.0][doc]
* [Documentation 7.x](https://pyarmor.readthedocs.io/en/v7.7/)

中文资源

* [Pyarmor 网站](https://pyarmor.dashingsoft.com/index-zh.html)
* [Pyarmor 8.0 在线文档](https://pyarmor.readthedocs.io/zh/latest/)
* [Pyarmor 7.x 在线文档](https://pyarmor.readthedocs.io/zh/v7.x/)

## Changelog

Pyarmor 8.0 introduces significant changes. It has been rewritten and new features are implemented through the new commands:
`gen`, `reg`, `cfg`. These commands only work for Python 3.7 and above.

Users of versions prior to 8.0 should read the [Import Notes][important-notes] section to decide whether to upgrade Pyarmor.

Each major version comes with a separate changelog file, detailing fixed issues, new features, and compatibility issues between different versions.

Make sure to read the changelog carefully before upgrading Pyarmor:
- [Pyarmor 8.x Changelog](docs/ChangeLogs.8)

**Full changelogs** at [releases](releases)

**Upcoming features** at [Pyarmor 8.x Release Plan](ReleasePlan.md)

[releases]: https://github.com/dashingsoft/pyarmor/releases

[important-notes]: #important-notes-for-users-of-pyarmor-prior-to-80

## Important Notes for Users of Pyarmor Prior to 8.0

Going forward, only bug fixes will be provided for older commands, such as `obfuscate` and `licenses`.
No new features will be added to these commands, but they will continue to be usable.

Upon the release of Pyarmor 8.0, there are three scenarios for existing users:

### 1. Never upgrade to version 8.0+

- **SPP mode will not work**
  - To use SPP mode, you must upgrade Pyarmor to version 8.0 or later.

- **`pyarmor register` command without arguments returns a `404` error**
  - This command was used to query registration information in earlier versions of Pyarmor. However, the license server no longer supports this web API. Use `pyarmor -v` to ensure you are not using a trial version.

- **Registering Pyarmor with `pyarmor register pyarmor-regcode-xxxxxx.txt` is limited to 10 uses**:
  - To use Pyarmor on a new machine, CI server, or Docker, refer to the second method described in the registration file "pyarmor-regcode-xxxxxx.txt":
```
Downloading "pyarmor-regfile-xxxxxx.zip" once, use this `.zip` file to register Pyarmor later.
```

### 2. Upgrade to version 8.0 but only use old features

By default, the `pyarmor` command only accepts the new commands.

To continue using older commands like `obfuscate` and `licenses`, you can:
- Use `pyarmor-7` instead of `pyarmor`
- Set the environment variable `PYARMOR_CLI=7` and continue using `pyarmor`
- Call the entry point `pyarmor.pyarmor:main_entry` in any other way

### 3. Upgrade to version 8.0 and use new features

- **New EULA**:
  - Adhere to the new [Pyarmor EULA](LICENSE). This is a significant change for users with old personal licenses, as the new license only allows one product.

- **License Upgrades**:
  - Not all old licenses can be freely upgraded to the new license. Please refer to the [Pyarmor licenses][licenses] for more information.

- **Internet Connection**:
  - Older commands do not require an internet connection, but new commands do.

- **Python Version Support**:
  - While older commands support Python 2.7-3.10, new commands only support Python 3.7+.
