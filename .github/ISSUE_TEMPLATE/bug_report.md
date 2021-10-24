---
name: Bug report
about: Report a bug of pyarmor
title: ''
labels: bug
assignees: jondy

---

It's more readable in the issue Preview mode for the hints

**IMPORTANT**
Please provide the necessary information according to this template when reporting bug. If missing necessay information, the issue will be marked as `invalid` and be closed directly.

**Hints**
Before report a bug, please read these common questions and solutions first
https://pyarmor.readthedocs.io/en/latest/questions.html

And remove all the above hints.

**Title**
A clear and concise description of what the bug is.

**Description**
1. The full pyarmor command and full output log (required)
2. If distributing the obfuscated script to other machine, which files are copied (optional)
3. The command to run the obfuscated scripts and full traceback when something is wrong

The output log could be redirected to a file by this way. For example,

    pyarmor obfuscate foo.py >log.txt 2>&1

Here is an issue instance

*Title*:

    cannot import name 'pyarmor' from 'pytransform'

*Description*:

1. On MacOS 10.14 run pyarmor to obfuscate the script
```
$ pyarmor obfuscate --exact main.py
INFO     Create pyarmor home path: /Users/jondy/.pyarmor
INFO     Create trial license file: /Users/jondy/.pyarmor/license.lic
INFO     Generating public capsule ...
INFO     PyArmor Trial Version 7.0.1
INFO     Python 3.7.10
INFO     Target platforms: Native
INFO     Source path is "/Users/jondy/workspace/pyarmor-webui/test/__runner__/__src__"
INFO     Entry scripts are ['main.py']
INFO     Use cached capsule /Users/jondy/.pyarmor/.pyarmor_capsule.zip
INFO     Search scripts mode: Exact
INFO     Save obfuscated scripts to "dist"
INFO     Read product key from capsule
INFO     Obfuscate module mode is 2
INFO     Obfuscate code mode is 1
INFO     Wrap mode is 1
INFO     Restrict mode is 1
INFO     Advanced value is 0
INFO     Super mode is False
INFO     Super plus mode is not enabled
INFO     Generating runtime files to dist/pytransform
INFO     Extract pytransform.key
INFO     Generate default license file
INFO     Update capsule to add default license file
INFO     Copying /Users/jondy/workspace/pyarmor-webui/venv/lib/python3.7/site-packages/pyarmor/platforms/darwin/x86_64/_pytransform.dylib
INFO     Patch library dist/pytransform/_pytransform.dylib
INFO     Patch library file OK
INFO     Copying /Users/jondy/workspace/pyarmor-webui/venv/lib/python3.7/site-packages/pyarmor/pytransform.py
INFO     Rename it to pytransform/__init__.py
INFO     Generate runtime files OK
INFO     Start obfuscating the scripts...
INFO     	/Users/jondy/workspace/pyarmor-webui/test/__runner__/__src__/main.py -> dist/main.py
INFO     Insert bootstrap code to entry script dist/foo.py
INFO     Obfuscate 1 scripts OK.
```
2. Copy the whole folder `dist/` to target machine Ubuntu
3. Failed to run the obfuscated script by Python 3.7 in Unbutu
```
$ cd dist/
$ python3 main.py
Traceback (most recent call last):
File "main.py", line 1, in <module>
  from pytransform import pyarmor
ImportError: cannot import name 'pyarmor' from 'pytransform' (/home/jondy/dist/pytransform/__init__.py)
```
