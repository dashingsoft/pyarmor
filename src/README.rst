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

    pytransform/
        __init__.py
        _pytransform.so or _pytransform.dll or _pytransform.dylib

``dist/foo.py`` is obfuscated script, the content is::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'\x06\x0f...', 1)

There is an extra folder ``pytransform`` called ``Runtime Package``,
which are the only required to run or import obfuscated scripts. So
long as this package is in any Python path, the obfuscated script
``dist/foo.py`` can be used as normal Python script.

**The original python scripts can be replaced with obfuscated scripts seamlessly.**

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

    pyarmor obfuscate foo.py

Run obfuscated scripts::

    cd dist
    python foo.py

Obfuscate scripts with an expired license::

    pyarmor licenses --expired 2018-12-31 r001
    pyarmor obfuscate --with-license licenses/r001/license.lic foo.py

Pack obfuscated scripts to one bundle::

    pip install pyinstaller
    pyarmor pack foo.py

There is also a web-ui package `pyarmor-webui`::

    pip install pyarmor-webui

Start webui, open web page in browser::

    pyarmor-webui

More Resources
--------------

- `Website <http://pyarmor.dashingsoft.com>`_
  `中文网站 <http://pyarmor.dashingsoft.com/index-zh.html>`_
- `Documentation <https://pyarmor.readthedocs.io/en/latest/>`_
- `pyarmor-webui <http://github.com/dashingsoft/pyarmor-webui>`_
- `Source Code <https://github.com/dashingsoft/pyarmor>`_
- `Examples <https://github.com/dashingsoft/pyarmor/blob/master/src/examples>`_
