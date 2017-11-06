Pyarmor
=======

Pyarmor is a command line tool used to import or run encrypted python
scripts. Only by a few extra files, pyarmor can run and imported
encrypted files in the normal python environments.

Pyarmor just likes an enhancement which let python could run or import
encrypted files.

Main Features
-------------

- Run encrypted script or import encrypted module
- Run or import encrypted compiled python files (.pyc, .pyo)
- Mixed encrypted files with normal python files.
- Expire encrypted files
- Bind encrypted files to harddisk

Support Platforms
-----------------

- Python 2.5, 2.6, 2.7 and Python3

- Prebuilt Platform: win32, win_amd64, linux_i386, linux_x86_64, darwin_x86_64

The core of Pyarmor is written by C, the only dependency is libc. So
it's easy to build for any other platform, even for embeded
system. Contact <jondy.zhao@gmail.com> if you'd like to run encrypted
scripts in other platform.

Installation
------------

Got source package from `pypi/pyarmor <https://pypi.python.org/pypi/pyarmor>`_

Pyarmor is a command line tool, main script is pyarmor.py. After you
got source package, unpack it to any path, then run paramor.py as
common python script

    python pyarmor.py

Web App
-------

Pyarmor Web App is a gui interface of Pyarmor, visit `Pyarmor Web App Online Version <http://pyarmor.dashingsoft.com:9096>`_

For more information, refer to `Pyarmor Homepage <https://github.com/dashingsoft/pyarmor>`_
