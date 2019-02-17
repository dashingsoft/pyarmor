Protect Python Scripts By PyArmor
=================================

PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts. It
protects Python scripts by the following ways:

* Obfuscate code object to protect constants and literal strings.
* Obfuscate co_code of each function (code object) in runtime.
* Clear f_locals of frame as soon as code object completed execution.
* Verify the license file of obfuscated scripts while running it.

Look at what happened after ``foo.py`` is obfuscated by PyArmor. Here
are the files list in the output path ``dist``::

    foo.py

    _pytransform.so, or _pytransform.dll in Windows, or _pytransform.dylib in MacOS
    pytransform.py
    pytransform.key
    license.lic

``dist/foo.py`` is obfuscated script, the content is::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...', 1)

All the other extra files called ``Runtime Files``, which are required to run or
import obfuscated scripts. So long as runtime files are in any Python path,
obfuscated script ``dist/foo.py`` can be used as normal Python script.

**The original python scripts can be replaced with obfuscated scripts seamlessly.**

For details to visit `protect-python-scripts-by-pyarmor.md <https://github.com/dashingsoft/pyarmor/blob/master/docs/protect-python-scripts-by-pyarmor.md>`_

Support Platforms
-----------------

* Python 2.5, 2.6, 2.7 and Python3
* win32, win_amd64, linux_i386, linux_x86_64, macosx_x86_64
* Embedded Platform: Raspberry Pi, Banana Pi, Orange Pi, TS-4600 / TS-7600

Quick Start
-----------

Install::

    pip install pyarmor

Obfuscate scripts::

    pyarmor obfuscate examples/simple/queens.py

Run obfuscated scripts::

    cd dist
    python queens.py

Pack obfuscated scripts with PyInstaller, py2exe, cx_Freeze etc.::

    pip install pyinstaller
    pyarmor pack examples/py2exe/hello.py

Generate an expired license and run obfuscated scripts with new license::

    pyarmor licenses --expired 2018-12-31 Customer-Jondy
    cp licenses/Customer-Jondy/license.lic dist/

    cd dist/
    python queens.py

Start webui, open web page in browser for basic usage of PyArmor::

    pyarmor-webui

More Resources
--------------

- `Website <http://pyarmor.dashingsoft.com>`_
  `中文网站 <http://pyarmor.dashingsoft.com/index-zh.html>`_
- `Documentation <https://pyarmor.readthedocs.io/en/latest/>`_
- `WebUI Demo <http://pyarmor.dashingsoft.com/demo/index.html>`_
- `Source Code <https://github.com/dashingsoft/pyarmor>`_
- `Examples <https://github.com/dashingsoft/pyarmor/blob/master/src/examples>`_
