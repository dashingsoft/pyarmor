.. _advanced topics:

Advanced Topics
===============

.. _obfuscating many packages:

Obfuscating Many Packages
-------------------------

There are 3 packages: `pkg1`, `pkg2`, `pkg2`. All of them will be
obfuscated, and use shared runtime files.

First change to work path, create 3 projects::

    mkdir build
    cd build

    pyarmor init --src /path/to/pkg1 --entry __init__.py pkg1
    pyarmor init --src /path/to/pkg2 --entry __init__.py pkg2
    pyarmor init --src /path/to/pkg3 --entry __init__.py pkg3

Then make the :ref:`runtime package`, save it in the path `dist`::

    pyarmor build --output dist --only-runtime pkg1

Next obfuscate 3 packages, save them in the `dist`::

    pyarmor build --output dist --no-runtime pkg1
    pyarmor build --output dist --no-runtime pkg2
    pyarmor build --output dist --no-runtime pkg3

Check all the output and test these obfuscated packages::

    ls dist/

    cd dist
    python -c 'import pkg1
    import pkg2
    import pkg3'

.. note::

   The runtime package `pytransform` in the output path `dist` also could be
   move to any other Python path, only if it could be imported.

.. _distributing obfuscated scripts to other platform:

Distributing Obfuscated Scripts To Other Platform
-------------------------------------------------

First list all the prebuilt dynamic libraries by command :ref:`download`::

    pyarmor download --list

Find the right one for target platform, download it by platform id::

    pyarmor download armv7

Then specify platform id when obfuscating the scripts::

    pyarmor obfuscate --platform armv7 foo.py

For project::

    pyarmor build --platform armv7


.. note::

   From v5.6.0 to v5.7.0, there is a bug for cross platform. The scripts
   obfuscated in linux64/windows64/darwin64 don't work after copied to one of
   this target platform::

       armv5, android.aarch64, ppc64le, ios.arm64, freebsd, alpine, alpine.arm, poky-i586

   After v5.7.0, if the obfuscated scripts still don't work in these platforms,
   set environment variable `PYARMOR_PLATFORM` to `simple`, then obfuscate the
   scripts again::

       PYARMOR_PLATFORM=simple pyarmor obfuscate --platform armv5 foo.py

       # For windows
       SET PYARMOR_PLATFORM=simple
       pyarmor obfuscate --platform armv5 foo.py

.. _obfuscating scripts by different python version:

Obfuscating Scripts By Other Version Of Python
----------------------------------------------

If there are multiple Python versions installed in the machine, the
command `pyarmor` uses default Python. In case the scripts need to be
obfuscated by other Python, run `pyarmor` by this Python explicitly.

For example, first find :file:`pyarmor.py`::

    find /usr/local/lib -name pyarmor.py

Generally it should be in the
`/usr/local/lib/python2.7/dist-packages/pyarmor` in most of linux.

Then run pyarmor as the following way::

    /usr/bin/python3.6 /usr/local/lib/python2.7/dist-packages/pyarmor/pyarmor.py

It's convenient to create a shell script `/usr/local/bin/pyarmor3`, the content is::

    /usr/bin/python3.6 /usr/local/lib/python2.7/dist-packages/pyarmor/pyarmor.py "$*"

And ::

    chmod +x /usr/local/bin/pyarmor3

then use `pyarmor3` as before.

In the Windows, create a bat file `pyarmor3.bat`, the content would be like this::

    C:\Python36\python C:\Python27\Lib\site-packages\pyarmor\pyarmor.py %*

.. _let python interpreter recognize obfuscated scripts automatically:

Let Python Interpreter Recognize Obfuscated Scripts Automatically
-----------------------------------------------------------------

In a few cases, if Python Interpreter could recognize obfuscated
scripts automatically, it will make everything simple:

* Almost all the obfuscated scripts will be run as main script
* In the obfuscated scripts call `multiprocessing` to create new process
* Or call `Popen`, `os.exec` etc. to run any other obfuscated scripts
* ...

Here are the base steps:

1. First create the :ref:`runtime package` with empty entry script::

    echo "" > pytransform_bootstrap.py
    pyarmor obfuscate pytransform_bootstrap.py

2. Move the :ref:`runtime package` `dist/pytransform` to Python system library. For
   example::

    # For windows
    mv dist/pytransform C:/Python37/Lib/site-packages/

    # For linux
    mv dist/pytransform /usr/local/lib/python3.5/dist-packages/

3. Move obfuscated bootstrap script `dist/pytransform_bootstrap.py` to Python
   system library::

     mv dist/pytransform_bootstrap.py C:/Python37/Lib/
     mv dist/pytransform_bootstrap.py /usr/lib/python3.5/

4. Edit `lib/site.py` (on Windows) or `lib/pythonX.Y/site.py` (on Linux), import
   `pytransform_bootstrap` before the line `if __name__ == '__main__'`::

    import pytransform_bootstrap

    if __name__ == '__main__':
        ...

It also could be inserted into the end of function `site.main`, or anywhere they
could be executed as module `site` is imported.

After that `python` could run the obfuscated scripts directly, becausee the
module `site` is automatically imported during Python initialization.

Refer to https://docs.python.org/3/library/site.html

.. note::

    Before v5.7.0, you need create the :ref:`runtime package` by the
    :ref:`runtime files` manually.

Obfuscating Python Scripts In Different Modes
---------------------------------------------

:ref:`Advanced Mode` is introduced from PyArmor 5.5.0, it's disabled by
default. Specify option `--advanced` to enable it::

    pyarmor obfuscate --advanced 1 foo.py

    # For project
    cd /path/to/project
    pyarmor config --advanced 1
    pyarmor build -B

From PyArmor 5.2, the default :ref:`Restrict Mode` is 1. It could be changed by
the option `--restrict`::

    pyarmor obfuscate --restrict=2 foo.py
    pyarmor obfuscate --restrict=3 foo.py

    # For project
    cd /path/to/project
    pyarmor config --restrict 4
    pyarmor build -B

All the restricts could be disabled by this way if required::

    pyarmor obfuscate --restrict=0 foo.py

    # For project
    pyarmor config --restrict=0
    pyarmor build -B

The modes of :ref:`Obfuscating Code Mode`, :ref:`Wrap Mode`, :ref:`Obfuscating
module Mode` could not be changed in command :ref:`obfucate`. They only could be
changed by command :ref:`config` when :ref:`Using Project`. For example::

    pyarmor init --src=src --entry=main.py .
    pyarmor config --obf-mod=1 --obf-code=1 --wrap-mode=0
    pyarmor build -B

.. _using plugin to extend license type:

Using Plugin to Extend License Type
-----------------------------------

PyArmor could extend license type for obfuscated scripts by
plugin. For example, check internet time other than local time.

First create plugin :file:`check_ntp_time.py`:

.. code-block:: python

    # Uncomment the next 2 lines for debug as the script isn't obfuscated,
    # otherwise runtime module "pytransform" isn't available in development
    # from pytransform import pyarmor_init
    # pyarmor_init()

    from ntplib import NTPClient
    from time import mktime, strptime
    import sys

    def get_license_data():
        from ctypes import py_object, PYFUNCTYPE
        from pytransform import _pytransform
        prototype = PYFUNCTYPE(py_object)
        dlfunc = prototype(('get_registration_code', _pytransform))
        rcode = dlfunc().decode()
        index = rcode.find(';', rcode.find('*CODE:'))
        return rcode[index+1:]

    def check_expired():
        NTP_SERVER = 'europe.pool.ntp.org'
        EXPIRED_DATE = get_license_data()
        c = NTPClient()
        response = c.request(NTP_SERVER, version=3)
        if response.tx_time > mktime(strptime(EXPIRED_DATE, '%Y%m%d')):
            sys.exit(1)

Then insert 2 comments in the entry script :file:`foo.py`::

    ...

    # {PyArmor Plugins}

    ...

    def main():
        # PyArmor Plugin: check_expired()

    if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO)
        main()

Now obfuscate entry script::

    pyarmor obfuscate --plugin check_ntp_time foo.py

By this way, the content of :file:`check_ntp_time.py` will be insert
after the first comment::

    # {PyArmor Plugins}

    ... the conent of check_ntp_time.py

At the same time, the prefix of second comment will be stripped::

    def main():
        # PyArmor Plugin: check_expired()
        check_expired()

So the plugin takes effect.

If the plugin file isn't in the current path, use absolute path instead::

    pyarmor obfuscate --plugin /usr/share/pyarmor/check_ntp_time foo.py

Or set environment variable `PYARMOR_PLUGIN`. For example::

    export PYARMOR_PLUGIN=/usr/share/pyarmor/plugins
    pyarmor obfuscate --plugin check_ntp_time foo.py

Finally generate one license file for this obfuscated script::

    pyarmor licenses -x 20190501 MYPRODUCT-0001
    cp licenses/MYPRODUCT-0001/license.lic dist/

.. note::

   It's better to insert the content of `ntplib.py` into the plugin so
   that `NTPClient` needn't be imported out of obfuscated scripts.

.. _bundle obfuscated scripts to one executable file:

Bundle Obfuscated Scripts To One Executable File
------------------------------------------------

Run the following command to pack the script `foo.py` to one
executable file `dist/foo.exe`. Here `foo.py` isn't obfuscated, it
will be obfuscated before packing::

    pyarmor pack -e " --onefile" foo.py
    dist/foo.exe

If you don't want to bundle the `license.lic` of the obfuscated
scripts into the executable file, but put it outside of the executable
file. For example::

    dist/
        foo.exe
        license.lic

So that we could generate different licenses for different users
later easily. Here are basic steps:

1. First create runtime-hook script `copy_licese.py`::

    import sys
    from os.path import join, dirname
    with open(join(dirname(sys.executable), 'license.lic'), 'rb') as fs:
        with open(join(sys._MEIPASS, 'license.lic'), 'wb') as fd:
            fd.write(fs.read())

2. Then pack the scirpt with extra options::

    pyarmor pack --clean --without-license \
            -e " --onefile --icon logo.ico --runtime-hook copy_license.py" foo.py

  Option `--without-license` tells `pyamor` not to bundle the `license.lic` of
  obfuscated scripts to the final executable file. By option `--runtime-hook` of
  `PyInstaller`, the specified script `copy_licesen.py` will be executed before
  any obfuscated scripts are imported. It will copy outer `license.lic` to right
  path.

  Try to run `dist/foo.exe`, it should report license error.

3. Finally run `pyarmor licenses` to generate new license for the
   obfuscated scripts, and copy new `license.lic` and `dist/foo.exe`
   to end users::

    pyarmor licenses -e 2020-01-01 tom
    cp license/tom/license.lic dist/

    dist/foo.exe

.. _improving the security by restrict mode:

Improving The Security By Restrict Mode
---------------------------------------

By default the scripts are obfuscated by restrict mode 1, that is, the
obfuscated scripts can't be changed. In order to improve the security,
obfuscating the scripts by restrict mode 2 so that the obfuscated scripts can't
be imported out of the obfuscated scripts. For example::

    pyarmor obfuscate --restrict 2 foo.py

Or obfuscating the scripts by restrict mode 3 for more security. It will even
check each function call to be sure all the functions are called in the
obfuscated scripts. For example::

    pyarmor obfuscate --restrict 3 foo.py

However restrict mode 2 and 3 aren't applied to Python package. There is another
solutiion for Python package to improve the security:

* The `.py` files which are used by outer scripts are obfuscated by restrice mode 1
* All the other `.py` files which are used only in the package are obfuscated by restrict mode 4

For example::

    cd /path/to/mypkg
    pyarmor obfuscate --exact __init__.py exported_func.py
    pyarmor obfuscate --restrict 4 --recursive \
            --exclude __init__.py --exclude exported_func.py .

More information about restrict mode, refer to :ref:`Restrict Mode`

Checking Imported Function Is Obfuscated
----------------------------------------

Sometimes it need to make sure the imported functions from other module are
obfuscated. For example, there are 2 scripts `main.py` and `foo.py`::

    $ cat main.py

    import foo

    def start_server():
        foo.connect('root', 'root password')

    $ cat foo.py

    def connect(username, password):
        mysql.dbconnect(username, password)

In the obfuscated `main.py`, it need to be sure `foo.connect` is
obfuscated. Otherwise the end users may replace the obfuscated `foo.py` with
this plain code::

    def connect(username, password):
        print('password is %s', password)

One solution is to check imported functions by decorator `assert_armored` in the
`main.py`. For example::

    import foo

    def assert_armored(*names):
        def wrapper(func):
            def _execute(*args, **kwargs):
                for s in names:
                    # For Python2
                    # if not (s.func_code.co_flags & 0x20000000):
                    # For Python3
                    if not (s.__code__.co_flags & 0x20000000):
                        raise RuntimeError('Access violate')
                return func(*args, **kwargs)
            return _execute
        return wrapper

    @assert_armored(foo.connect, foo.connect2)
    def start_server():
        foo.connect('root', 'root password')
        foo.connect2('user', 'user password')

About Third-Party Interpreter
-----------------------------

About third-party interperter, for example Jython, and any embeded
Python C/C++ code, they should satisfy the following conditions at
least to run the obfuscated scripts:

* They must be load offical Python dynamic library, which should be
  built from the soure https://github.com/python/cpython , and the
  core source code should not be modified.

* On Linux, `RTLD_GLOBAL` must be set as loading `libpythonXY.so` by
  `dlopen`, otherwise obfuscated scripts couldn't work.

.. note::  

   Boost::python does not load `libpythonXY.so` with `RTLD_GLOBAL` by
   default, so it will raise error "No PyCode_Type found" as running
   obfuscated scripts. To solve this problem, try to call the method
   `sys.setdlopenflags(os.RTLD_GLOBAL)` as initializing.

* The module `ctypes` must be exists and `ctypes.pythonapi._handle`
  must be set as the real handle of Python dynamic library, PyArmor
  will query some Python C APIs by this handle.
        
.. customizing protection code:

.. include:: _common_definitions.txt
