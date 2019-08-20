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

Then make runtime files, save them in the path `dist`::

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

.. _distributing obfuscated scripts to other platform:

Distributing Obfuscated Scripts To Other Platform
-------------------------------------------------

First list and download dynalic library of target platform by command
:ref:`download`::

    pyarmor download --list
    pyarmor download linux_x86_64

Then specify platform name as obfuscating the scripts::

    pyarmor obfuscate --platform linux_x86_64 foo.py

For project::

    pyarmor build --platform linux_x86_64

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

1. First obfuscate all the scripts::

    pyarmor obfuscate --recursive foo.py

In the output path `dist`, there are 4 runtime files generated at the same time:

* pytransform.py
* pytransform.key
* _pytransform.so (.dll or .dylib)
* license.lic

2. Create a new path `pytransform` in the Python system library, it would be
   `lib/site-packages` (on Windows) or `lib/pythonX.Y/site-packages` (on Linux)

3. Copy 4 runtime files to this path, rename `pytransform.py` as `__init__.py`

4. Edit `lib/site.py` (on Windows) or `lib/pythonX.Y/site.py` (on Linux), insert
   :ref:`Bootstrap Code` before the line `if __name__ == '__main__'`::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

They also could be inserted into the end of function `site.main`, or anywhere
they could be executed as module `site` is imported.

After that `python` could run the obfuscated scripts directly, becausee the
module `site` is automatically imported during Python initialization.

Refer to https://docs.python.org/3/library/site.html

Obfuscating Python Scripts In Different Modes
---------------------------------------------

:ref:`Advanced Mode` is introduced from PyArmor 5.5.0, it's disabled by
default. Specify option `--advanced` to enable it::

    pyarmor obfuscate --advanced foo.py

From PyArmor 5.2, :ref:`Restrict Mode` is default setting. It could be disabled
by this way if required::

    pyarmor obfuscate --restrict=0 foo.py

The modes of :ref:`Obfuscating Code Mode`, :ref:`Wrap Mode`, :ref:`Obfuscating
module Mode` could not be changed in command :ref:`obfucate`. They only could be
changed in the :ref:`Using Project`. For example::

    pyarmor init --src=src --entry=main.py .
    pyarmor config --obf-mod=1 --obf-code=1 --wrap-mode=0
    pyarmor build

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

    from pytransform import get_license_code
    from ntplib import NTPClient
    from time import mktime, strptime
    import sys

    NTP_SERVER = 'europe.pool.ntp.org'
    EXPIRED_DATE = get_license_code()[4:]

    def check_expired():
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
        check_expired()

So the plugin takes effect.

If the plugin file isn't in the current path, use absolute path instead::

    pyarmor obfuscate --plugin /usr/share/pyarmor/check_ntp_time foo.py

Or set environment variable `PYARMOR_PLUGIN`. For example::

    export PYARMOR_PLUGIN=/usr/share/pyarmor/plugins
    pyarmor obfuscate --plugin check_ntp_time foo.py

Finally generate one license file for this obfuscated script::

    pyarmor licenses NTP:20190501

.. note::

   It's better to move `get_licese_code` to the obfuscated
   script. Here it's an example::

       def get_license_code():
           from ctypes import py_object, PYFUNCTYPE
           from pytransform import _pytransform
           prototype = PYFUNCTYPE(py_object)
           dlfunc = prototype(('get_registration_code', _pytransform))
           rcode = dlfunc().decode()
           index = rcode.find('*CODE:')
           return rcode[index+6:]

   Besides, insert the content of `ntplib.py` into the plugin so that
   `NTPClient` could be used locally.

.. note::

   The expired date may be encoded either. For example::

       pyarmor licenses xxxx

   Here "xxx" is encoded expired date, then decode it as checking the
   expired date in the obfuscated script.

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

    dist/foo.exe
    dist/license.lic

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
obfuscating the scripts by restrict mode 2 so that the obfuscated
scripts can't be imported out of the obfuscated scripts. For example::

    pyarmor obfuscate --restrict 2 foo.py

Or obfuscating the scripts by restrict mode 3 for more security. It
will even check each function call to be sure all the functions are
called in the obfuscated scripts. For example::

    pyarmor obfuscate --restrict 3 foo.py

However restrict mode 2 and 3 aren't applied to Python package. There is another
solutiion for Python package to improve the security:

* The `.py` files which are used by outer scripts are obfuscated by restrice mode 1
* All the other `.py` files which are used only in the package are obfuscated by restrict mode 4

Fro example::

    cd /path/to/mypkg
    pyarmor obfuscate --exact __init__.py exported_func.py
    pyarmor obfuscate --restrict 4 --recursive \
            --exclude __init__.py --exclude exported_func.py .

More information about restrict mode, refer to :ref:`Restrict Mode`

.. customizing protection code:

.. include:: _common_definitions.txt
