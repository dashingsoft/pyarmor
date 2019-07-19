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

.. customizing protection code:

.. include:: _common_definitions.txt
