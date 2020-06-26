.. _advanced topics:

Advanced Topics
===============

.. _using super mode:

Using Super Mode
----------------

The :ref:`Super mode` is introduced since v6.2.0, there is only one extension
module required to run the obfuscated scripts, and the :ref:`bootstrap code`
which may confused some users before is gone now, all the obfuscated scripts are
same. It improves the security remarkably, and makes the usage simple. The only
problem is that only the latest Python versions 2.7, 3.7 and 3.8 are supported.

Enable super mode by option ``--advanced 2``, for example::

  pyarmor obfuscate --advanced 2 foo.py

When distributing the obfuscated scripts to any other machine, so long as
extension module :mod:`pytransform` in any Python path, the obfuscated scrips
could work well.

In order to restirct the obfuscated scripts, generate a ``license.lic`` in
advanced. For example::

  pyarmor licenses --bind-mac xx:xx:xx:xx regcode-01

Then specify this license with option ``--with-license``, for example::

  pyarmor obufscate --with-license licenses/regcode-01/license.lic \
                    --advanced 2 foo.py

By this way the specified license file will be embedded into the extension
module :mod:`pytransform`. If you prefer to use outer ``license.lic``, so it can
be replaced with the others easily, just set option ``--with-license`` to
special value ``outer``, for example::

  pyarmor obfuscate --with-license outer --advanced 2 foo.py

When the obfuscated scripts start, it will search ``license.lic`` in order:

#. Check environment variable ``PYARMOR_LICENSE``, if set, use this filename
#. If it's not set, search ``license.lic`` in the current path
#. If not found, search the path of extension module :mod:`pytransform`
#. Raise exception if there is still not found

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

   The runtime package :mod:`pytransform` in the output path `dist` also could
   be move to any other Python path, only if it could be imported.

   From v5.7.2, the :ref:`runtime package` also could be generate by command
   :ref:`runtime` separately::

       pyarmor runtime


.. _obfuscating package no conflict with others:

.. _solve conflicts with other obfuscated libraries:

Solve Conflicts With Other Obfuscated Libraries
-----------------------------------------------

.. note:: New in v5.8.7

Suppose there are 2 packages obfuscated by different developers, could they be
imported in the same Python interpreter?

If both of them are obfuscated by trial version of pyarmor, no problem, the
answer is yes. But if anyone is obfuscated by registerred version, the answer is
no.

Since v5.8.7, the scripts could be obfuscated with option ``--enable-suffix`` to
generate the :ref:`Runtime Package` with an unique suffix, other than fixed name
``pytransform``. For example::

    pyarmor obfuscate --enable-suffix foo.py

The output would be like this::

    dist/
        foo.py
        pytransform_vax_000001/
            __init__.py
            ...

The suffix ``_vax_000001`` is based on the registration code of PyArmor.

For project, set ``enable-suffix`` by command :ref:`config`::

    pyarmor config --enable-suffix 1
    pyarmor build -B

Or disable it by this way::

    pyarmor config --enable-suffix 0
    pyarmor build -B

.. _distributing obfuscated scripts to other platform:

Distributing Obfuscated Scripts To Other Platform
-------------------------------------------------

First list all the avaliable platform names by command :ref:`download`::

    pyarmor download
    pyarmor download --help-platform

Display the detials with option ``--list``::

    pyarmor download --list
    pyarmor download --list windows
    pyarmor download --list windows.x86_64

Then specify platform name when obfuscating the scripts::

    pyarmor obfuscate --platform linux.armv7 foo.py

    # For project
    pyarmor build --platform linux.armv7

.. _obfuscating scripts with different features:

Obfuscating scripts with different features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There may be many available dynamic libraries for one same platform. Each one
has different features. For example, both of ``windows.x86_64.0`` and
``windows.x86_64.7`` work in the platform ``windwos.x86_64``. The last number
stands for the features:

  - 0: No anti-debug, JIT, advanced mode features, high speed
  - 7: Include anti-debug, JIT, advanced mode features, high security

It's possible to obfuscate the scripts with special feature. For example::

    pyarmor obfuscate --platform linux.x86_64.7 foo.py

Note that the dynamic library with different features aren't compatible. For
example, try to obfuscate the scripts with ``--platform linux.arm.0`` in
Windows::

    pyarmor obfuscate --platform linux.arm.0 foo.py

Because the default platform is full features ``windows.x86_64.7`` in Windows,
so PyArmor have to reboot with platform ``windows.x86_64.0``, then obfuscate the
script for this low feature platform ``linux.arm.0``.

It also could be set the enviornment variable ``PYARMOR_PLATFORM`` to same
feature platform as target machine. For example::

    PYARMOR_PLATFORM=windows.x86_64.0 pyarmor obfuscate --platform linux.arm.0 foo.py

    # In Windows
    set PYARMOR_PLATFORM=windows.x86_64.0
    pyarmor obfuscate --platform linux.arm.0 foo.py
    set PYARMOR_PLATFORM=


.. _running obfuscated scripts in multiple platforms:

Running Obfuscated Scripts In Multiple Platforms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From v5.7.5, the platform names are standardized, all the available platform
names list here :ref:`Standard Platform Names`. And the obfuscated scripts could
be run in multiple platforms.

In order to support multiple platforms, all the dynamic libraries for these
platforms need to be copied to :ref:`runtime package`. For example, obfuscating
a script could run in Windows/Linux/MacOS::

    pyarmor obfuscate --platform windows.x86_64 \
                      --platform linux.x86_64 \
                      --platform darwin.x86_64 \
                      foo.py

The :ref:`runtime package` also could be generated by command :ref:`runtime`
once, then obfuscate the scripts without runtime files. For examples::

    pyarmor runtime --platform windows.x86_64,linux.x86_64,darwin.x86_64
    pyarmor obfuscate --no-runtime --recursive \
                      --platform windows.x86_64,linux.x86_64,darwin.x86_64 \
                      foo.py

Because the obfuscated scripts will check the dynamic library, the platforms
must be specified even if there is option ``--no-runtime``. But if the option
``--no-cross-protection`` is specified, the obfuscated scripts will not check
the dynamic library, so no platform is required. For example::

    pyarmor obfuscate --no-runtime --recursive --no-cross-protection foo.py

.. note::

   If the feature number is specified in one of platform, for example, one is
   ``windows.x86_64.0``, then all the other platforms must be same feature.

.. note::

   If the obfuscated scripts don't work in other platforms, try to update all
   the downloaded files::

       pyarmor download --update

   If it still doesn't work, try to remove the cahced platform files in the path
   ``$HOME/.pyarmor``

.. _obfuscating scripts by different python version:

.. _obfuscating scripts by other python version:

Obfuscating Scripts By Other Python Version
-------------------------------------------

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

    /usr/bin/python3.6 /usr/local/lib/python2.7/dist-packages/pyarmor/pyarmor.py "$@"

And ::

    chmod +x /usr/local/bin/pyarmor3

then use `pyarmor3` as before.

In the Windows, create a bat file `pyarmor3.bat`, the content would be like this::

    C:\Python36\python C:\Python27\Lib\site-packages\pyarmor\pyarmor.py %*

.. _run bootstrap code in plain scripts:

Run bootstrap code in plain scripts
-----------------------------------

Before v5.7.0 the :ref:`bootstrap code` could be inserted into plain scripts
directly, but now, for the sake of security, the :ref:`bootstrap code` must be
in the obfuscated scripts. It need another way to run the :ref:`bootstrap code`
in plain scripts.

First create one bootstrap package :mod:`pytransform_bootstrap` by command
:ref:`runtime`::

    pyarmor runtime -i

Next move bootstrap package to the path of plain script::

    mv dist/pytransform_bootstrap /path/to/script

It also could be copied to python system library, for examples::

    mv dist/pytransform_bootstrap /usr/lib/python3.5/ (For Linux)
    mv dist/pytransform_bootstrap C:/Python35/Lib/ (For Windows)

Then edit the plain script, insert one line::

    import pytransform_bootstrap

Now any other obfuscated modules could be imported after this line.

.. note::

   Before v5.8.1, create this bootstrap package by this way::

    echo "" > __init__.py
    pyarmor obfuscate -O dist/pytransform_bootstrap --exact __init__.py

.. _run unittest of obfuscated scripts:

Run unittest of obfuscated scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In most of obfuscated scripts there are no :ref:`bootstrap code`. So the
unittest scripts may not work with the obfuscated scripts.

Suppose the test script is :file:`/path/to/tests/test_foo.py`, first patch this
test script, refer to `run bootstrap code in plain scripts`_

After that it works with the obfuscated modules::

    cd /path/to/tests
    python test_foo.py

The other way is patch system package :mod:`unittest` directly. Make sure the
bootstrap package :mod:`pytransform_bootstrap` is copied in the Python system
library, refer to `run bootstrap code in plain scripts`_

Then edit :file:`/path/to/unittest/__init__.py`, insert one line::

    import pytransform_bootstrap

Now all the unittest scripts could work with the obfuscated scripts. It's useful
if there are many unittest scripts.

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

1. First create one bootstrap package :mod:`pytransform_bootstrap`::

    pyarmor runtime -i

   Before v5.8.1, it need be created by obfuscating an empty package::

    echo "" > __init__.py
    pyarmor obfuscate -O dist/pytransform_bootstrap --exact __init__.py

2. Then create virtual python environment to run the obfuscated scripts, move
   the bootstrap package to virtual python library. For example::

    # For windows
    mv dist/pytransform_bootstrap venv/Lib/

    # For linux
    mv dist/pytransform_bootstrap venv/lib/python3.5/

4. Edit `venv/lib/site.py` or `venv/lib/pythonX.Y/site.py`, import
   `pytransform_bootstrap` before the main line::

    import pytransform_bootstrap

    if __name__ == '__main__':
        ...

It also could be inserted into the end of function ``main``, or anywhere they
could be executed as module :mod:`site` is imported.

After that in the virtual environment ``python`` could run the obfuscated
scripts directly, because the module :mod:`site` is automatically imported
during Python initialization.

Refer to https://docs.python.org/3/library/site.html

.. note::

    The command `pyarmor` doesn't work in this virtual environment, it's only
    used to run the obfuscated scripts.

.. note::

    Before v5.7.0, you need create the bootstrap package by the :ref:`runtime
    files` manually.


.. _obfuscating python scripts in different modes:

Obfuscating Python Scripts In Different Modes
---------------------------------------------

:ref:`Advanced Mode` is introduced from PyArmor 5.5.0, it's disabled by
default. Specify option ``--advanced`` to enable it::

    pyarmor obfuscate --advanced 1 foo.py

    # For project
    cd /path/to/project
    pyarmor config --advanced 1
    pyarmor build -B

From PyArmor 5.2, the default :ref:`Restrict Mode` is 1. It could be changed by
the option ``--restrict``::

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

PyArmor could extend license type for obfuscated scripts by plugin. For example,
check internet time other than local time.

First create plugin script `check_ntp_time.py
<https://github.com/dashingsoft/pyarmor/blob/master/plugins/check_ntp_time.py>`_. The
key function in this script is `check_ntp_time`, the other important function is
`_get_license_data` which used to get extra data from the `license.lic` of
obfuscated scripts.

Then insert 2 comments in the entry script `foo.py
<https://github.com/dashingsoft/pyarmor/blob/master/plugins/foo.py>`_::

    # {PyArmor Plugins}
    # PyArmor Plugin: check_ntp_time()

Now obfuscate entry script::

    pyarmor obfuscate --plugin check_ntp_time foo.py

If the plugin file isn't in the current path, use absolute path instead::

    pyarmor obfuscate --plugin /usr/share/pyarmor/check_ntp_time foo.py

Finally generate one license file for this obfuscated script, pass extra license
data by option ``-x``, this data could be got by function `_get_license_data` in
the plugin script::

    pyarmor licenses -x 20190501 rcode-001
    cp licenses/rcode-001/license.lic dist/

More examples, refer to https://github.com/dashingsoft/pyarmor/tree/master/plugins

About how plugins work, refer to :ref:`How to Deal With Plugins`

.. important::

   The output function name in the plugin must be same as plugin name, otherwise
   the plugin will not take effects.

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

1. First create runtime-hook script `copy_license.py`::

    import sys
    from os.path import join, dirname
    with open(join(dirname(sys.executable), 'license.lic'), 'rb') as fs:
        with open(join(sys._MEIPASS, 'license.lic'), 'wb') as fd:
            fd.write(fs.read())

2. Then pack the scirpt with extra options::

    pyarmor pack --clean --without-license -x " --exclude copy_license.py" \
            -e " --onefile --icon logo.ico --runtime-hook copy_license.py" foo.py

  Option ``--without-license`` tells :ref:`pack` not to bundle the `license.lic`
  of obfuscated scripts to the final executable file. By option
  ``--runtime-hook`` of `PyInstaller`_, the specified script
  :file:`copy_license.py` will be executed before any obfuscated scripts are
  imported. It will copy outer :file:`license.lic` to right path.

  Try to run :file:`dist/foo.exe`, it should report license error.

3. Finally run :ref:`licenses` to generate new license for the obfuscated
   scripts, and copy new :file:`license.lic` and :file:`dist/foo.exe` to end
   users::

    pyarmor licenses -e 2020-01-01 code-001
    cp license/code-001/license.lic dist/

    dist/foo.exe

.. _bundle obfuscated scripts with customized spec file:

Bundle obfuscated scripts with customized spec file
---------------------------------------------------

If there is a customized .spec file works, for example::

    pyinstaller myscript.spec

It could be used to pack obfuscated scripts directly::

    pyarmor pack -s myscript.spec myscript.py

If it raises this error::

    Unsupport .spec file, no XXX found

Check .spec file, make sure there are 2 lines in top level (no identation)::

    a = Analysis(...

    pyz = PYZ(...

And there are 3 key parameters when creating an `Analysis` object, for example::

    a = Analysis(
        ...
        pathex=...,
        hiddenimports=...,
        hookspath=...,
        ...
    )

PyArmor will append required options to these lines automatically. But before
v5.9.6, it need to be patched by manual:

* Add module ``pytransform`` to `hiddenimports`
* Add extra path ``DISTPATH/obf/temp`` to `pathex` and `hookspath`

After changed, it may be like this::

    a = Analysis(['myscript.py'],
                 pathex=[os.path.join(DISTPATH, 'obf', 'temp'), ...],
                 binaries=[],
                 datas=[],
                 hiddenimports=['pytransform', ...],
                 hookspath=[os.path.join(DISTPATH, 'obf', 'temp'), ...],
                 ...

.. note::

   This featuer is introduced since v5.8.0

   Before v5.8.2, the extra path is ``DISTPATH/obf``, not ``DISTPATH/obf/temp``

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
solution for Python package to improve the security:

* The `.py` files which are used by outer scripts are obfuscated by restrice mode 1
* All the other `.py` files which are used only in the package are obfuscated by restrict mode 4

For example::

    cd /path/to/mypkg
    pyarmor obfuscate --exact __init__.py exported_func.py
    pyarmor obfuscate --restrict 4 --recursive \
            --exclude __init__.py --exclude exported_func.py .

More information about restrict mode, refer to :ref:`Restrict Mode`


.. _using plugin to improve security:

Using Plugin To Improve Security
--------------------------------

By plugin any private checkpoint could be injected into the obfuscated scripts,
and it doesn't impact the original scripts. Most of them must be run in the
obfuscated scripts, if they're not commented as plugin, it will break the plain
scripts.

No one knows your check logic, and you can change it in anytime. So it's more
security.

Using Inline Plugin To Check Dynamic Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Althouth `PyArmor` provides cross protection, it also could check the dynamic
library in the startup to make sure it's not changed by others. This example
uses inline plugin to check the modified time protecting the dynamic library by
inserting the following comment to ``main.py``

.. code:: python

  # PyArmor Plugin: import os
  # PyArmor Plugin: libname = os.path.join( os.path.dirname( __file__ ), '_pytransform.so' )
  # PyArmor Plugin: if not os.stat( libname ).st_mtime_ns == 102839284238:
  # PyArmor Plugin:     raise RuntimeError('Invalid Library')

Then obfuscate the script and enable inline plugin by this way::

  pyarmor obfuscate --plugin on main.py

Once the obfuscated script starts, the following plugin code will be run at
first

.. code:: python

  import os
  libname = os.path.join( os.path.dirname( __file__ ), '_pytransform.so' )
  if not os.stat( libname ).st_mtime_ns == 102839284238:
      raise RuntimeError('Invalid Library')

.. _checking imported function is obfuscated:

Checking Imported Function Is Obfuscated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it need to make sure the imported functions from other module are
obfuscated. For example, there are 2 scripts `main.py` and `foo.py`

.. code:: python


    #
    # This is main.py
    #

    import foo

    def start_server():
        foo.connect('root', 'root password')
        foo.connect2('user', 'user password')

    #
    # This is foo.py
    #

    def connect(username, password):
        mysql.dbconnect(username, password)

    def connect2(username, password):
        db2.dbconnect(username, password)

In the `main.py`, it need to be sure `foo.connect` is obfuscated. Otherwise the
end users may replace the obfuscated `foo.py` with this plain script, and run
the obfuscated `main.py`

.. code:: python

    def connect(username, password):
        print('password is %s', password)

The password is stolen, in order to avoid this, use decorator function
to make sure the function `connect` is obfuscated by plugin.

From v6.0.2, the :ref:`runtime package` :mod:`pytransform` provides internal
decorator `assert_armored`, it can be used to check all the list functions are
pyarmored in the script. Now let's edit `main.py`, insert inline plugin code

.. code:: python

    import foo

    # PyArmor Plugin: from pytransform import assert_armored

    # PyArmor Plugin: @assert_armored(foo.connect, foo.connect2)
    def start_server():
        foo.connect('root', 'root password')

Then obfuscate it with plugin on::

    pyarmor obfuscate --plugin on main.py

The obfuscated script would be like this

.. code:: python

    import foo

    from pytransform import assert_armored

    @assert_armored(foo.connect, foo.connect2)
    def start_server():
        foo.connect('root', 'root password')

Before call ``start_server``, the decorator function ``assert_armored`` will
check both ``connect`` functions are pyarmored, otherwise it will raise
exception.

In order to improve security further, we implement the decorator function in the
script, instead of importing it. First create script ``assert_armored.py`` in the
current path

.. code:: python

    from pytransform import _pytransform, PYFUNCTYPE, py_object

    def assert_armored(*names):
        prototype = PYFUNCTYPE(py_object, py_object)
        dlfunc = prototype(('assert_armored', _pytransform))

        def wrapper(func):
            def _execute(*args, **kwargs):

                # Call check point provide by PyArmor
                dlfunc(names)

                # Add your private check code
                for s in names:
                    if s.__name__ == 'connect':
                        if s.__code__.co_code[10:12] != b'\x90\xA2':
                            raise RuntimeError('Access violate')

                return func(*args, **kwargs)
            return _execute
        return wrapper

Next edit `main.py` , insert plugin markers

.. code:: python

    import foo

    # {PyArmor Plugins}

    # PyArmor Plugin: @assert_armored(foo.connect, foo.connect2)
    def start_server():
        foo.connect('root', 'root password')

Then obfuscate it with this command::

    pyarmor obfuscate --plugin assert_armored main.py

.. note::

   Since v6.2.0, if obfuscating scripts by :ref:`super mode`, it's enough to
   import `assert_armored` from :mod:`pytransform`, do not create outer script,
   it doesn't work.


.. _call pyarmor from python script:

Call `pyarmor` From Python Script
---------------------------------

It's also possible to call PyArmor methods inside Python script not by `os.exec`
or `subprocess.Popen` etc. For example

.. code-block:: python

    from pyarmor.pyarmor import main as call_pyarmor
    call_pyarmor(['obfuscate', '--recursive', '--output', 'dist', 'foo.py'])

In order to suppress all normal output of pyarmor, call it with ``--silent``

.. code-block:: python

    from pyarmor.pyarmor import main as call_pyarmor
    call_pyarmor(['--silent', 'obfuscate', '--recursive', '--output', 'dist', 'foo.py'])

From v5.7.3, when `pyarmor` called by this way and something is wrong, it will
raise exception other than call `sys.exit`.

Generating license key by web api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's also possible to generate license key as string other than writing to a
file inside Python script. It may be useful in case the new license need to be
generated by web api.

.. code-block:: python

    from pyarmor.pyarmor import licenses as generate_license_key
    lickey = generate_license_key(name='reg-001',
                                  expired='2020-05-30',
                                  bind_disk='013040BP2N80S13FJNT5',
                                  bind_mac='70:f1:a1:23:f0:94',
                                  bind_ipv4='192.168.121.110',
                                  bind_data='any string')
    print('Generate key: %s' % lickey)

If there are more than one product need generate licenses from one Web API, set
keyword `home` to each registerred product. For example

.. code-block:: python

    from pyarmor.pyarmor import licenses as generate_license_key
    lickey = generate_license_key(name='product-001',
                                  expired='2020-06-15',
                                  home='~/.pyarmor-2')
    print('Generate key for product 1: %s' % lickey)

    lickey = generate_license_key(name='product-002',
                                  expired='2020-05-30',
                                  home='~/.pyarmor-2')
    print('Generate key for product 2: %s' % lickey)


.. _check license periodly when the obfuscated script is running:

Check license periodly when the obfuscated script is running
------------------------------------------------------------

Generally only at the startup of the obfuscated scripts the license is
checked. Since v5.9.3, it also could check the license per hour. Just generate a
new license with ``--enable-period-mode`` and overwrite the default one. For
example::

    pyarmor obfuscate foo.py
    pyarmor licenses --enable-period-mode code-001
    cp licenses/code-001/license.lic ./dist


.. _work with nuitka:

Work with Nuitka
----------------

Because the obfuscated scripts could be taken as normal scripts with an extra
runtime package `pytransform`, they also could be translated to C program by
Nuitka. When obfuscating the scprits, the option ``--restrict 0`` and
``--no-cross-protection`` should be set, otherwise the final C program could not
work. For example, first obfustate the scripts::

    pyarmor obfuscate --restrict 0 --no-cross-protection foo.py

Then translate the obfuscated one as normal python scripts by Nuitka::

    cd ./dist
    python -m nuitka --include-package pytransform foo.py
    ./foo.bin

There is one problem is that the imported modules (packages) in the obfuscated
scripts could not be seen by Nuitka. To fix this problem, first generate the
corresponding ``.pyi`` with original script, then copy it within the obfuscated
one. For example::

    # Generating "mymodule.pyi"
    python -m nuitka --module mymodule.py

    pyarmor obfuscate --restrict 0 --no-bootstrap mymodule.py
    cp mymodule.pyi dist/

    cd dist/
    python -m nuitka --module mymodule.py

But it may not take advantage of Nuitka features by this way, because most of
byte codes aren't translated to c code indeed.

.. note::

   So long as the C program generated by Nuitka is linked against libpython to
   execute, pyarmor could work with Nuitka. But in the future, just as said in
   the Nuitka official website::

       It will do this - where possible - without accessing libpython but in C
       with its native data types.

   In this case, pyarmor maybe not work with Nuitka.


.. _work with cython:

Work with Cython
----------------

Here it's an example show how to `cythonize` a python script `foo.py` obfuscated
by pyarmor with Python37::

    print('Hello Cython')

First obfuscate it with some extra options::

    pyarmor obfuscate --package-runtime 0 --no-cross-protection --restrict 0 foo.py

The obfuscated script and runtime files will be saved in the path `dist`, about
the meaning of each options, refer to command :ref:`obfuscate`.

Next `cythonize` both `foo.py` and `pytransform.py` with extra options ``-k``
and ``--lenient`` to generate `foo.c` and `pytransform.c`::

    cd dist
    cythonize -3 -k --lenient foo.py pytransform.py

Without options ``-k`` and ``--lenient``, it will raise exception::

    undeclared name not builtin: __pyarmor__

Then compile `foo.c` and `pytransform.c` to the extension modules. In MacOS,
just run the following commands, but in Linux, with extra cflag ``-fPIC``::

    gcc -shared $(python-config --cflags) $(python-config --ldflags) \
         -o foo$(python-config --extension-suffix) foo.c

    gcc -shared $(python-config --cflags) $(python-config --ldflags) \
        -o pytransform$(python-config --extension-suffix) pytransform.c

Finally test it, remove all the `.py` files and import the extension modules::

    mv foo.py pytransform.py /tmp
    python -c 'import foo'

It will print `Hello Cython` as expected.


.. _work with pyupdater:

Work with PyUpdater
-------------------

PyArmor should work with `PyUpdater`_ by this way, for example, there is a
script `foo.py`:

1. Generate `foo.spec` by PyUpdater

2. Generate `foo-patched.spec` by pyarmor with option ``--debug``::

    pyarmor pack --debug -s foo.spec foo.py

    # If the final executable raises protection error, try to disable restirct mode
    # by the following extra options
    pyarmor pack --debug -s foo.spec -x " --restrict 0 --no-cross-protection" foo.py

This patched `foo-patched.spec` could be used by PyUpdater in build command

If your Python scripts are modified, just obfuscate them again, all the options
for command :ref:`obfuscate` could be got from the output of command :ref:`pack`

If anybody is having issues with the above. Just normally compiling it in
PyArmor then zipping and putting it into "/pyu-data/new" works. From there on
you can just normally sign, process and upload your update.

More information refer to the description of command :ref:`pack` and advanced
usage :ref:`bundle-obfuscated-scripts-with-customized-spec-file`


.. _binding obfuscated scripts to python interpreter:

Binding obfuscated scripts to Python interpreter
--------------------------------------------------

In order to improve the security of obfuscated scripts, it also could bind the
obfuscated scripts to one fixed Python interperter, the obfuscated scripts will
not work if the Python dynamic library are changed.

If you use command `obfuscate`, after the scripts are obfuscated, just generate
a new `license.lic` which is bind to the current Python and overwrite the
default license. For example::

  pyarmor licenses --fixed 1 -O dist/license.lic

When start the obfuscated scripts in target machine, it will check the Python
dynamic library, it may be pythonXY.dll, libpythonXY.so or libpythonXY.dylib in
different platforms. If this library is different from the python dynamic
library in build machine, the obfuscated script will quit.

If you use project to obfuscate scripts, first generate a fixed license::

  cd /path/to/project
  pyarmor licenses --fixed 1

By default it will be saved to `licenses/pyarmor/license.lic`, then configure
the project with this license::

  pyarmor config --license=licenses/pyarmor/license.lic

If obfuscate the scripts for different platform, first get the bind key in
target platform. Create a script then run it with Python interpreter which would
be bind to:

.. code-block:: python

  from ctypes import CFUNCTYPE, cdll, pythonapi, string_at, c_void_p, c_char_p
  from sys import platform


  def get_bind_key():

      if platform.startswith('win'):
          from ctypes import windll
          dlsym = windll.kernel32.GetProcAddressA
      else:
          prototype = CFUNCTYPE(c_void_p, c_void_p, c_char_p)
          dlsym = prototype(('dlsym', cdll.LoadLibrary(None)))

      refunc1 = dlsym(pythonapi._handle, b'PyEval_EvalCode')
      refunc2 = dlsym(pythonapi._handle, b'PyEval_GetFrame')

      size = refunc2 - refunc1
      code = string_at(refunc1, size)

      print('Get bind key: %s' % sum(bytearray(code)))


  if __name__ == '__main__':
      get_bind_key()

It will print the bind key `xxxxxx`, then generate one fixed license with this
bind key::

  pyarmor licenses --fixed xxxxxx -O dist/license.lic

It also could bind the license to many Python interpreters by passing multiple
keys separated by `,`::

  pyarmor licenses --fixed 1,key2,key3 -O dist/license.lic
  pyarmor licenses --fixed key1,key2,key3 -O dist/license.lic

The special key `1` means current Python interpreter.

.. note::

   Do not use this feature in 32-bit Windows, because the bind key is
   different in different machine, it may be changed even if python is
   restarted in the same machine.


.. _customizing cross protection code:

Customizing cross protection code
---------------------------------

In order to protect core dynamic library of PyArmor, the default protection code
will be injected into the entry scripts, refer to :ref:`Special Handling of
Entry Script`. However this public protection code may be bypassed deliberately,
the better way is to write your private protection code, it could improve the
security largely.

Since v6.2.0, command :ref:`runtime` could generate the default protection code,
it could be as template to write your own protection code. Of course, you may
write it by yourself. Only if it could make sure the runtime files aren't
changed by someone else as running the obfuscated scripts.

First generate protection script ``build/pytransform_protection.py``::

  pyarmor runtime --super-mode --output build

Then edit it with your private code, after that, obfuscate the scripts and set
option ``--cross-protection`` to this customized script, for example::

  pyarmor obfuscate --cross-protection build/pytransform_protection.py \
                --advanced 2 foo.py

Note that :ref:`super mode` is total different from other modes, don't specify
option ``--super-mode`` when generating runtime files for other modes, for
example::

  pyarmor runtime --output build

.. note::

   Obfuscating with ``--advanced 1`` is not super mode, only ``--advanced 2`` is
   super mode.


.. _storing runtime file license.lic to any location:

Storing runtime file license.lic to any location
------------------------------------------------

By creating a symbol link in the runtime package, it's easy to store runtime
file ``license.lic`` to any location when running the obfuscated scripts.

In linux, for example, store license file in ``/opt/my_app``::

  ln -s /opt/my_app/license.lic /path/to/obfuscated/pytransform/license.lic

In windows, store license file in ``C:/Users/Jondy/my_app``::

  mklink \path\to\obfuscated\pytransform\license.lic C:\Users\Jondy\my_app\license.lic

When distributing the obfuscated package, just run this function on post-install:

.. code:: python

   import os

   def make_link_to_license_file(package_path, target_license="/opt/mypkg/license.lic"):
       license_file = os.path.join(package_path, 'pytransform', 'license.lic')
       if os.path.exists(license_file):
           os.rename(license_file, target_license)
       os.symlink(target_license, license_file)


.. _register multiple pyarmor in same machine:

Register multiple pyarmor in same machine
-----------------------------------------

From v5.9.0, pyarmor reads license and capsule data from environment variable
`PYARMOR_HOME`, the default value is `~/.pyarmor`. So it's easy to register
multiple pyarmor in one machine by setting environment variable `PYARMOR_HOME`
to another path before run pyarmor.

It also could create a new command `pyarmor2` for the second project by the
following way.

In Linux, create a shell script :file:`pyarmor2`

.. code:: bash

    export PYARMOR_HOME=$HOME/.pyarmor_2
    pyarmor "$@"

Save it to `/usr/local/pyarmor2`, and change its mode::

    chmod +x /usr/local/pyarmor2

In Windows, create a bat script :file:`pyarmor2.bat`

.. code:: bat

    SET PYARMOR_HOME=%HOME%\another_pyarmor
    pyarmor %*

After that, run `pyarmor2` for the second project::

    pyarmor2 register pyarmor-regkey-2.zip
    pyarmor2 obfuscate foo2.py


How to get license information of one obfuscated package
--------------------------------------------------------

How to get the license information of one obfuscated package? Since v6.2.5, just
run this script in the path of runtime package :mod:`pytransform`

.. code-block:: python

   from pytransform import pyarmor_init, get_license_info
   pyarmor_init(is_runtime=1)
   licinfo = get_license_info()
   print('This obfuscated package is issued by %s' % licinfo['ISSUER'])
   print('License information:')
   print(licinfo)

For the scripts obfuscated by super mode, there is no package `pytransform`, but
an extension `pytransform`. It's simiar and more simple

.. code-block:: python

   from pytransform import get_license_info
   licinfo = get_license_info()
   print('This obfuscated package is issued by %s' % licinfo['ISSUER'])
   print('License information:')
   print(licinfo)

Since v6.2.7, it also could call the helper script by this way::

  cd /path/to/obfuscated_package
  python -m pyarmor.helper.get_license_info


.. _how to protect data files:

How to protect data files
-------------------------

This is still an experiment feature.

PyArmor does not touch data files, but it could wrap data file to python module,
and then obfuscate this data module by restrict mode 4, so that it only could be
imported from the obfuscated scripts. By this way, the data file could be
protected by PyArmor.

Since v6.2.7, there is a helper script which could create a python module from
data file, for example::

    python -m pyarmor.helper.build_data_module data.txt > data.py

Next obfuscate this data module with restrict mode 4::

    pyarmor obfuscate --exact --restrict 4 --no-runtime data.py

After that, use the data file in other obfuscated scripts. For example::

    import data

    # Here load the content of data file to memory variable "text"
    # And clear it from memory as exiting the context
    with data.Safestr() as text:
      ...

Before v6.2.7, download this helper script `build_data_module.py <https://github.com/dashingsoft/pyarmor/raw/master/src/helper/build_data_module.py>`_ and run it directly::

    python build_data_module.py data.txt > data.py

.. include:: _common_definitions.txt
