.. _change logs:

Change Logs
===========

5.4.1
-----
* New feature: do not obfuscate functions which name starts with `lambda_`
* Fix issue: it will raise `Protection Fault` as packing obfuscated scripts to one file

5.4.0
-----
* Do not obfuscate lambda functions by default
* Fix issue: local variable `platname` referenced before assignment

5.3.13
------
* Add option `--url` for command `download`
  
5.3.12
------
* Add integrity checks for the downloaded binaries (#85)
  
5.3.11
------
* Fix issue: get wrong harddisk's serial number for some special cases in Windows

5.3.10
------
* Query harddisk's serial number without administrator in Windows

5.3.9
-----
* Remove the leading and trailing whitespace of harddisk's serial number

5.3.8
-----
* Fix non-ascii path issue in Windows

5.3.7
-----
* Fix bug: the bootstrap code isn't inserted correctly if the path of entry script is absolute path.

5.3.6
-----
* Fix bug: protection code can't find the correct dynamic library if distributing obfuscated scripts to other platforms.
* Document how to distribute obfuscated scripts to other platforms
  https://pyarmor.readthedocs.io/en/latest/advanced.html#distributing-obfuscated-scripts-to-other-platform

5.3.5
-----
* The bootstrap code could run many times in same Python interpreter.
* Remove extra `.` from the bootstrap code of `__init__.py` as building project without runtime files.

5.3.4
-----
* Add command `download` used to download platform-dependent dynamic libraries
* Keep shell line for obfuscated entry scripts if there is first line starts with `#!`
* Fix issue: if entry script is not in the `src` path, bootstrap code will not be inserted.

5.3.3
-----
* Refine `benchmark` command
* Document the performance of obfuscated scripts https://pyarmor.readthedocs.io/en/latest/performance.html
* Add command `register` to take registration code effects
* Rename trial license file `license.lic` to `license.tri`

5.3.2
-----
* Fix bug: if there is only one comment line in the script it will raise IndexError as obfuscating this script.

5.3.1
-----
* Refine `pack` command, and make output clear.
* Document plugin usage to extend license type for obufscated scripts. Refer to
  https://pyarmor.readthedocs.io/en/latest/advanced.html#using-plugin-to-extend-license-type

5.3.0
-----
* In the trial version of PyArmor, it will raise error as obfuscating the code object which size is greater than 32768 bytes.
* Add option `--plugin` in command `obfuscate`
* Add property `plugins` for Project, and add option `--plugin` in command `config`
* Change default build path for command `pack`, and do not remove it after command finished.

5.2.9
-----
* Fix segmentation fault issue for python3.5 and before: run too big obfuscated code object (>65536 bytes) will crash (#67)
* Fix issue: missing bootstrap code for command `pack` (#68)
* Fix issue: the output script is same as original script if obfuscating scripts with option `--exact`

5.2.8
-----
* Fix issue: `pyarmor -v` complains `not enough arguments for format string`

5.2.7
-----
* In command `obfuscate` add new options `--exclude`, `--exact`,
  `--no-bootstrap`, `--no-cross-protection`.
* In command `obfuscate` deprecate the options `--src`, `--entry`,
  `--cross-protection`.
* In command `licenses` deprecate the option `--bind-file`.

5.2.6
-----
* Fix issue: raise codec exception as obfuscating the script of utf-8 with BOM
* Change the default path to user home for command `capsule`
* Disable restrict mode by default as obfuscating special script `__init__.py`
* Refine log message

5.2.5
-----
* Fix issue: raise IndexError if output path is '.' as building project
* For Python3 convert error message from bytes to string as checking license failed
* Refine version information

5.2.4
-----
* Fix arm64 issue: verify rsa key failed when running the obufscated scripts(#63)
* Support ios (arm64) and ppc64le for linux

5.2.3
-----
* Refine error message when checking license failed
* Fix issue: protection code raises ImportError in the package file `__init.py__`

5.2.2
-----
* Improve the security of dynamic library.

5.2.1
-----
* Fix issue: in restrict mode the bootstrap code in `__init__.py` will raise exception.
* Add option `--cross-protection` in command `obfuscate`

5.2.0
-----
* Use global capsule as default capsule for project, other than creating new one for each project
* Add option `--obf-code`, `--obf-mod`, `--wrap-mode`, `--cross-protection` in command `config`
* Add new attributes for project: `obf_code`, `obf_mod`, `wrap_mode`, `cross_protection`
* Deprecrated project attributes `obf_code_mode`, `obf_module_mode`, use `obf_code`, `obf_mod`, `wrap_mode` instead
* Change the behaviours of `restrict mode`, refer to https://pyarmor.readthedocs.io/en/latest/advanced.html#restrict-mode
* Change option `--restrict` in command `obfuscate` and `licenses`
* Remove option `--no-restrict` in command `obfuscate`
* Remove option `--clone` in command `init`

5.1.2
-----
* Improve the security of PyArmor self

5.1.1
-----
* Refine the procedure of encrypt script
* Reform module `pytransform.py`
* Fix issue: it will raise exception if no entry script when obfuscating scripts
* Fix issue: 'gbk' codec can't decode byte 0xa1 in position 28 (#51)
* Add option `--upgrade` for command `capsule`
* Merge runtime files `pyshield.key`, `pyshield.lic` and `product.key` into `pytransform.key`

**Upgrade notes**

The capsule created in this version will include a new file
`pytransform.key` which is a replacement for 3 old runtime files:
`pyshield.key`, `pyshield.lic` and `product.key`.

The old capsule which created in the earlier version still works, it
stills use the old runtime files. But it's recommended to upgrade the
old capsule to new version. Just run this command::

    pyarmor capsule --upgrade

All the license files generated for obfuscated scripts by old capsule
still work, but all the scripts need to be obfuscated again to take
new capsule effects.

5.1.0
-----
* Add extra code to protect dynamic library `_pytransform` when obfuscating entry script
* Fix compling error when obfuscating scripts in windows for Python 26/30/31 (newline issue)

5.0.5
-----
* Refine `protect_pytransform` to improve security, refer to https://pyarmor.readthedocs.io/en/latest/security.html

5.0.4
-----
* Fix `get_expired_days` issue, remove decorator `dllmethod`
* Refine output message of `pyarmor -v`

5.0.3
-----
* Add option `-q`, `--silent`, suppress all normal output when running any PyArmor command
* Refine runtime error message, make it clear and more helpful
* Add new function `get_hd_info` in module `pytransform` to get hardware information
* Remove function `get_hd_sn` from module `pytransform`, use `get_hd_info` instead
* Remove useless function `version_info`, `get_trial_days` from module `pytransform`
* Remove attribute `lib_filename` from module `pytransform`, use `_pytransform._name` instead
* Add document https://pyarmor.readthedocs.io/en/latest/pytransform.html
* Refine document https://pyarmor.readthedocs.io/en/latest/security.html

5.0.2
-----
* Export `lib_filename` in the module pytransform in order to protect
  dynamic library `_pytransform`.  Refer to

  https://pyarmor.readthedocs.io/en/latest/security.html

5.0.1
-----

Thanks to GNU lightning, from this version, the core routines are
protected by JIT technicals. That is to say, there is no binary code
in static file for core routines, they're generated in runtime.

Besides, the pre-built dynamic library for linux arm32/64 are packed
into the source package.

Fixed issues:

* The module `multiprocessing` starts new process failed in obfuscated script:

    `AttributeError: '__main__' object has no attribute 'f'`

4.6.3
-----
* Fix backslash issue when running `pack` command with `PyInstaller`
* When PyArmor fails, if `sys.flags.debug` is not set, only print error message, no traceback printed

4.6.2
-----
* Add option `--options` for command `pack`
* For Python 3, there is no new line in the output when `pack` command fails

4.6.1
-----
* Fix license issue in 64-bit embedded platform

4.6.0
-----
* Fix crash issue for special code object in Python 3.6

4.5.5
-----
* Fix stack overflow issue

4.5.4
-----
* Refine platform name to search dynamic library `_pytransform`

4.5.3
-----
* Print the exact message when checking license failed to run obfuscated scripts.

4.5.2
-----
* Add documentation https://pyarmor.readthedocs.io/en/latest/
* Exclude `dist`, `build` folder when executing `pyarmor obfuscate --recursive`

4.5.1
-----
* Fix #41: can not find dynamic library `_pytransform`

4.5.0
-----
* Add anti-debug code for dynamic library `_pytransform`

4.4.2
-----
* Change default capsule to user home other than the source path of `pyarmor`

4.4.2
-----
This patch mainly changes webui, make it simple more:

* WebUI : remove source field in tab Obfuscate, and remove ipv4 field in tab Licenses
* WebUI Packer: remove setup script, add output path, only support PyInstaller

4.4.1
-----
* Support Py2Installer by a simple way
* For command `obfuscate`, get default `src` and `entry` from first argument, `--src` is not required.
* Set no restrict mode as default for new project and command `obfuscate`, `licenses`

4.4.0
-----

* Pack obfuscated scripts by command `pack`

In this version, introduces a new command `pack` used to pack
obfuscated scripts with `py2exe` and `cx_Freeze`. Once the setup
script of `py2exe` or `cx_Freeze` can bundle clear python scripts,
`pack` could pack obfuscated scripts by single command: `pyarmor
pack --type cx_Freeze /path/to/src/main.py`

* Pack obfuscated scripts by WebUI packer

WebUI is well reformed, simple and easy to use.

http://pyarmor.dashingsoft.com/demo/index.html

4.3.4
-----
* Fix start pyarmor issue for `pip install` in Python 2

4.3.3
-----
* Fix issue: missing file in wheel

4.3.2
-----
* Fix `pip` install issue in MacOS
* Refine sample scripts to make workaround for py2exe/cx_Freeze simple

4.3.1
-----
* Fix typos in examples
* Fix bugs in sample scripts

4.3.0
-----
In this version, there are three significant changes:

[Simplified WebUI](http://pyarmor.dashingsoft.com/demo/index.html)
[Clear Examples](src/examples/README.md), quickly understand the most features of Pyarmor
[Sample Shell Scripts](src/examples), template scripts to obfuscate python source files

* Simply webui, easy to use, only input one filed to obfuscate python scripts
* The runtime files will be always saved in the same path with obfuscated scripts
* Add shell scripts `obfuscate-app`, `obfuscate-pkg`,
  `build-with-project`, `build-for-2exe` in `src/examples`, so that
  users can quickly obfuscate their python scripts by these template
  scripts.
* If entry script is `__init__.py`, change the first line of bootstrap
  code `from pytransform import pyarmor runtime` to `from .pytransform
  import pyarmor runtime`
* Rewrite examples/README.md, make it clear and easy to understand
* Do not generate entry scripts if only runtime files are generated
* Remove choice `package` for option `--type` in command `init`, only `pkg` reserved.

4.2.3
-----
* Fix `pyarmor-webui` can not start issue
* Fix `runtime-path` issue in webui
* Rename platform name `macosx_intel` to `macosx_x86_64` (#36)

4.2.2
-----
* Fix webui import error.

4.2.1
-----
* Add option `--recursive` for command `obfuscate`

4.1.4
-----
* Rewrite project long description.

4.1.3
-----
* Fix Python3 issue for `get_license_info`

4.1.2
-----
* Add function `get_license_info` in `pytransform.py` to show license information

4.1.1
-----
* Fix import `main` from `pyarmor` issue

4.0.3
-----
* Add command `capsule`
* Find default capsule in the current path other than `--src` in command `obfuscate`
* Fix pip install issue #30

4.0.2
-----
* Rename `pyarmor.py` to `pyarmor-depreted.py`
* Rename `pyarmor2.py` to `pyarmor.py`
* Add option `--capsule`, `-disable-restrict-mode` and `--output` for command `licenses`

4.0.1
-----
* Add option `--capsule` for command `init`, `config` and `obfuscate`
* Deprecate option `--clone` for command `init`, use `--capsule` instead
* Fix `sys.settrace` and `sys.setprofile` issues for auto-wrap mode

3.9.9
-----
* Fix segmentation fault issues for `asyncio`, `typing` modules

3.9.8
-----
* Add documentation for examples (examples/README.md)

3.9.7
-----
* Fix windows 10 issue: access violation reading 0x000001ED00000000

3.9.6
-----
* Fix the generated license bind to fixed machine in webui is not correct
* Fix extra output path issue in webui

3.9.5
-----
* Show registration code when printing version information

3.9.4
-----
* Rewrite long description of package in pypi

3.9.3
-----
* Fix issue: `__file__` is not really path in main code of module when import obfuscated module

3.9.2
-----
* Replace option `--disable-restrict-mode` with `--no-restrict` in command `obfuscate`
* Add option `--title` in command `config`
* Change the output path of entry scripts when entry scripts belong to package
* Refine document `user-guide.md` and `mechanism.md`

3.9.1
-----
* Add option `--type` for command `init`
* Refine document `user-guide.md` and `mechanism.md`

3.9.0
-----
This version introduces a new way `auto-wrap` to protect python code when it's imported by outer scripts.

Refer to [Mechanism Without Restrict Mode](src/mechanism.md#mechanism-without-restrict-mode)

* Add new mode `wrap` for `--obf-code-mode`
* Remove `func.__refcalls__` in `__wraparmor__`
* Add new project attribute `is_package`
* Add option `--is-package` in command `config`
* Add option `--disable-restrict-mode` in command `obfuscate`
* Reset `build_time` when project configuration is changed
* Change output path when `is_package` is set in command `build`
* Change default value of project when find `__init__.py` in comand `init`
* Project attribute `entry` supports absolute path

3.8.10
------
* Fix shared code object issue in `__wraparmor__`

3.8.9
-----
* Clear frame as long as `tb` is not `Py_None` when call `__wraparmor__`
* Generator will not be obfucated in `__wraparmor__`

3.8.8
-----
* Fix bug: the `frame.f_locals` still can be accessed in callback function

3.8.7
-----
* The `frame.f_locals` of `wrapper` and wrapped function will return an empty dictionary once `__wraparmor__` is called.

3.8.6
-----
* The `frame.f_locals` of `wrapper` and wrapped function return an empty dictionary, all the other frames still return original value.

3.8.5
-----
* The `frame.f_locals` of all frames will always return an empty dictionary to protect runtime data.
* Add extra argument `tb` when call `__wraparmor__` in decorator `wraparmor`, pass None if no exception.

3.8.4
-----
* Do not touch `frame.f_locals` when raise exception, let decorator `wraparmor` to control everything.

3.8.3
-----
* Fix issue: option `--disable-restrict-mode` doesn't work in command `licenses`
* Remove freevar `func` from `frame.f_locals` when raise exception in decorator `wraparmor`

3.8.2
-----
* Change module filename to `<frozen modname>` in traceback, set attribute `__file__` to real filename when running obfuscated scripts.

3.8.1
-----
* Try to access original func_code out of decorator `wraparmor` is forbidden.

3.8.0
-----
* Add option `--output` for command `build`, it will override the value in project configuration file.
* Fix issue: defalut project output path isn't relative to project path.
* Remove extra file "product.key" after obfuscating scripts.

3.7.5
-----
* Remove dotted name from filename in traceback, if it's not a package.

3.7.4
-----
* Strip `__init__` from filename in traceback, replace it with package name.

3.7.3
-----
* Remove brackets from filename in traceback, and add dotted prefix.

3.7.2
-----
* Change filename in traceback to `<frozen [modname]>`, other than original filename

3.7.1
-----
* Fix issue #12: module attribute `__file__` is filename in build machine other than filename in target machine.
* Builtins function `__wraparmor__` only can be used in the decorator `wraparmor`

3.7.0
-----
* Fix issue #11: use decorator "wraparmor" to obfuscate func_code as soon as function returns.
* Document usage of decorator "wraparmor",  refer to **src/user-guide.md#use-decorator-to-protect-code-objects-when-disable-restrict-mode**

3.6.2
-----
* Fix issue #8 (Linux): option --manifest broken in shell script

3.6.1
-----
* Add option "Restrict Mode" in web ui
* Document restrict mode in details (user-guide.md)

3.6.0
-----
* Introduce restrict mode to avoid obfuscated scripts observed from no obfuscated scripts
* Add option --disable-restrict-mode for command "config"

3.5.1
-----
* Support pip install pyarmor

3.5.0
-----
* Fix Python3.6 issue: can not run obfuscated scripts, because it uses a 16-bit wordcode instead of bytecode
* Fix Python3.7 issue: it adds a flag in pyc header
* Fix option --obf-module-mode=none failed
* Add option --clone for command "init"
* Generate runtime files to separate path “runtimes" when project runtime-path is set
* Add advanced usages in user-guide

3.4.3
-----
* Fix issue: raise exception when project entry isn't obfuscated

3.4.2
-----
* Add webui to manage project

3.4.1
-----
* Fix README.rst format error.
* Add title attribute to project
* Print new command help when option is -h, --help

3.4.0
-----
Pyarmor v3.4 introduces a group new commands. For a simple package,
use command **obfuscate** to obfuscate scripts directly. For
complicated package, use Project to manage obfuscated scripts.

Project includes 2 files, one configure file and one project
capsule. Use manifest template string, same as MANIFEST.in of Python
Distutils, to specify the files to be obfuscated.

To create a project, use command **init**, use command **info** to
show project information. **config** to update project settings, and
**build** to obfuscate the scripts in the project.

Other commands, **benchmark** to metric performance, **hdinfo** to
show hardware information, so that command **licenses** can generate
license bind to fixed machine.

All the old commands **capsule**, **encrypt**, **license** are
deprecated, and will be removed from v4.

A new document [src/user-guide.md](src/user-guide.md) is written for
this new version.

3.3.1
-----
* Remove unused files in distribute package

3.3.0
-----
In this version, new obfuscate mode 7 and 8 are introduced. The main
difference is that obfuscated script now is a normal python file (.py)
other than compiled script (.pyc), so it can be used as common way.

Refer to https://github.com/dashingsoft/pyarmor/blob/v3.3.0/src/mechanism.md

* Introduce new mode: 7, 8
* Change default mode from 3 to 8
* Change benchmark.py to test new mode
* Update webapp and tutorial
* Update usage
* Fix issue of py2exe, now py2exe can work with python scripts obfuscated by pyarmor
* Fix issue of odoo, now odoo can load python modules obfuscated by pyarmor

3.2.1
-----
* Fix issue: the traceback of an exception contains the name "<pytransform>" instead of the correct module name
* Fix issue: All the constant, co_names include function name, variable name etc still are in clear text.
  Refer to https://github.com/dashingsoft/pyarmor/issues/5

3.2.0
-----
From this version, a new obfuscation mode is introduced. By this way,
no import hooker, no setprofile, no settrace required. The performance
of running or importing obfuscation python scripts has been remarkably
improved. It's significant for Pyarmor.

* Use this new mode as default way to obfuscate python scripts.
* Add new script "benchmark.py" to check performance in target machine: python benchmark.py
* Change option "--bind-disk" in command "license",  now it must be have a value

3.1.7
-----
* Add option "--bind-mac", "--bind-ip", "--bind-domain" for command "license"
* Command "hdinfo" show more information(serial number of hdd, mac address, ip address, domain name)
* Fix the issue of dev name of hdd for Banana Pi

3.1.6
-----
* Fix serial number of harddisk doesn't work in mac osx.

3.1.5
-----
* Support MACOS

3.1.4
-----
* Fix issue: load _pytransfrom failed in linux x86_64 by subprocess.Popen
* Fix typo in error messge when load _pytransfrom failed.

3.1.3
-----
A web gui interface is introduced as Pyarmor WebApp， and support MANIFEST.in

* In encrypt command, save encrypted scripts with same file structure of source.
* Add a web gui interface for pyarmor.
* Support MANIFEST.in to list files for command encrypt
* Add option --manifest, file list will be written here
* DO NOT support absolute path in file list for command encrypt
* Option --main support format "NAME:ALIAS.py"

3.1.2
-----
* Refine decrypted mechanism to improve performance
* Fix unknown opcode problem in recursion call
* Fix wrapper scripts generated by -m in command 'encrypt' doesn't work
* Raise ImportError other than PytransformError when import encrypted module failed

3.1.1
-----
In this version, introduce 2 extra encrypt modes to improve
performance of encrypted scripts.

* Fix issue when import encrypted package
* Add encrypted mode 2 and 3 to improve performance
* Refine module pyimcore to improve performance

3.0.1
-----
It's a milestone for Pyarmor, from this version, use ctypes import
dynamic library of core functions, other than by python extensions
which need to be built with every python version.

Besides, in this version, a big change which make Pyarmor could avoid
soure script got by c debugger.

* Use ctypes load core library other than python extentions which need
  built for each python version.
* "\__main__" block not running in encrypted script.
* Avoid source code got by c debugger.
* Change default outoupt path to "build" in command "encrypt"
* Change option "--bind" to "--bind-disk" in command "license"
* Document usages in details

2.6.1
-----
* Fix encrypted scripts don't work in multi-thread framework (Django).

2.5.5
-----
* Add option '-i' for command 'encrypt' so that the encrypted scripts will be saved in the original path.

2.5.4
-----
* Verbose tracelog when checking license in trace mode.
* In license command, change default output filename to "license.lic.txt".
* Read bind file when generate license in binary mode other than text mode.

2.5.3
-----
* Fix problem when script has line "from __future__ import with_statement"
* Fix error when running pyarmor by 32bit python on the 64bits Windows.
* (Experimental)Support darwin_15-x86_64 platform by adding extensions/pytransform-2.3.3.darwin_15.x86_64-py2.7.so

2.5.2
-----
* License file can mix expire-date with fix file or fix key.
* Fix log error: not enough arguments for format string

2.5.1
-----
* License file can bind to ssh private key file or any other fixed file.

2.4.1
-----
* Change default extension ".pyx" to ".pye", because it confilcted with CPython.
* Custom the extension of encrypted scripts by os environment variable: PYARMOR_EXTRA_CHAR
* Block the hole by which to get bytescode of functions.

2.3.4
-----
* The trial license will never be expired (But in trial version, the
  key used to encrypt scripts is fixed).

2.3.3
-----
* Refine the document

2.3.2
-----
* Fix error data in examples of wizard

2.3.1
-----
* Implement Run function in the GUI wizard
* Make license works in trial version

2.2.1
-----
* Add a GUI wizard
* Add examples to show how to use pyarmor

2.1.2
-----
* Fix syntax-error when run/import encrypted scripts in linux x86_64

2.1.1
-----
* Support armv6

2.0.1
-----
* Add option '--path' for command 'encrypt'
* Support script list in the file for command 'encrypt'
* Fix issue to encrypt an empty file result in pytransform crash

1.7.7
-----

* Add option '--expired-date' for command 'license'
* Fix undefined 'tfm_desc' for arm-linux
* Enhance security level of scripts

1.7.6
-----

* Print exactaly message when pyarmor couldn't load extension
  "pytransform"

* Fix problem "version 'GLIBC_2.14' not found"

* Generate "license.lic" which could be bind to fixed machine.

1.7.5
-----

* Add missing extensions for linux x86_64.

1.7.4
-----

* Add command "licene" to generate more "license.lic" by project
  capsule.

1.7.3
-----

* Add information for using registration code

1.7.2
-----

* Add option --with-extension to support cross-platform publish.
* Implement command "capsule" and add option --with-capsule so that we
  can encrypt scripts with same capsule.
* Remove command "convert" and option "-K/--key"

1.7.1
-----

* Encrypt pyshield.lic when distributing source code.

1.7.0
-----

* Enhance encrypt algorithm to protect source code.
* Developer can use custom key/iv to encrypt source code
* Compiled scripts (.pyc, .pyo) could be encrypted by pyshield
* Extension modules (.dll, .so, .pyd) could be encrypted by pyshield
