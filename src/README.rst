Pyarmor
=======

Pyarmor is a command line tool used to import or run encrypted python
scripts. Only by a few extra files, pyarmor can run and imported
encrypted files in the normal python environments. Here are the basic
steps:

- Generate project capsule
- Encrypt python scripts with project capsule
- Copy project capsule and encrypted scripts to runtime environments.

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

- Prebuilt Platform: win32, win_amd64, linux_i386, linux_x86_64

Got prebuilt library `platforms.zip <https://github.com/dashingsoft/pyarmor/releases/download/v3.1.2/platforms.zip>`_
then extract it to src of Pyarmor

The core of Pyarmor is written by C, the only dependency is libc. So
it's not difficult to build for any other platform, even for embeded
system. Contact <jondy.zhao@gmail.com> if you'd like to run encrypted
scripts in other platform.

Installation
------------
Got source package from `pypi <https://pypi.python.org/pypi/pyarmor>`_

Pyarmor is a command line tool, main script is pyarmor.py. After you
got source package, unpack it to any path, then run paramor.py as
common python script

    python pyarmor.py

For more information, refer to `Pyarmor Homepage <https://github.com/dashingsoft/pyarmor>`_
