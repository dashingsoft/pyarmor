.. _man page:

Man Page
========

PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

The syntax of the ``pyarmor`` command is::

    pyarmor <command> [options]

The most commonly used pyarmor commands are::

    obfuscate    Obfuscate python scripts
    licenses     Generate new licenses for obfuscated scripts
    pack         Obfuscate scripts then pack them to one bundle
    hdinfo       Show hardware information

The commands for project::

    init         Create a project to manage obfuscated scripts
    config       Update project settings
    build        Obfuscate all the scripts in the project

    info         Show project information
    check        Check consistency of project

The other commands::

    benchmark    Run benchmark test in current machine
    register     Make registration file work
    download     Download platform-dependent dynamic libraries
    runtime      Generate runtime package separately

See `pyarmor <command> -h` for more information on a specific command.

.. note::

   From v5.7.1, the first character is command alias for most usage commands::

       obfuscate, licenses, pack, init, config, build

   For example::

       pyarmor o => pyarmor obfuscate


Common Options
--------------

-v, --version                Show version information
-q, --silent                 Suppress all normal output
-d, --debug                  Print exception traceback and debugging message
--home PATH                  Select home path, generally for multiple registerred pyarmor
--boot PLATID                Set boot platform, only for special usage

These options can be used after `pyarmor`, before sub-command. For example,
print debug information to locate the error::

    pyarmor -d obfuscate foo.py

Do not print log in the console::

    pyarmor --silent obfuscate foo.py

Obfuscate scripts with another purchased license::

    pyarmor --home ~/.pyarmor-2 register pyarmor-keyfile-2.zip
    pyarmor --home ~/.pyarmor-2 obfuscate foo.py


.. _obfuscate:

obfuscate
---------

Obfuscate python scripts.

**SYNOPSIS**::

    pyarmor obfuscate <options> SCRIPT...

**OPTIONS**

-O, --output PATH             Output path, default is `dist`
-r, --recursive               Search scripts in recursive mode
-s, --src PATH                Specify source path if entry script is not in the top most path
--exclude PATH                Exclude the path in recusrive mode. Multiple paths are allowed, separated by ",", or use this option multiple times
--exact                       Only obfuscate list scripts
--no-bootstrap                Do not insert bootstrap code to entry script
--bootstrap <0,1,2,3>         How to insert bootstrap code to entry script
--no-cross-protection         Do not insert protection code to entry script
--plugin NAME                 Insert extra code to entry script, it could be used multiple times
--platform NAME               Distribute obfuscated scripts to other platform
--advanced <0,1,2,3,4>        Enable advanced mode `1`, super mode `2`, vm mode `3` and `4`
--restrict <0,1,2,3,4>        Set restrict mode
-n, --no-runtime              DO NOT generate runtime files
--runtime PATH                Use prebuilt runtime package
--package-runtime <0,1>       Save the runtime files as package or not
--enable-suffix               Generate the runtime package with unique name
--obf-mod <0,1,2>             Disable or enable to obfuscate module
--obf-code <0,1,2>            Disable or enable to obfuscate function
--wrap-mode <0,1>             Disable or enable wrap mode
--with-license FILENAME       Use this licese, special value `outer` means no license
--cross-protection FILENAME   Specify customized protection script
--mix-str                     Obfuscate the string value

**DESCRIPTION**

PyArmor first checks whether :ref:`Global Capsule` exists in the ``HOME``
path. If not, make it.

Then find all the scripts to be obfuscated. There are 3 modes to search the
scripts:

* Normal: find all the `.py` files in the same path of entry script
* Recursive: find all the `.py` files in the path of entry script recursively
* Exact: only these scripts list in the command line

The default mode is `Normal`, option ``--recursive`` and ``--exact`` enable the
corresponding mode.

Note that only the `.py` files are touched by this command, all the other files
aren't copied to output path. If there are many data files in the package, first
copy the whole package to the output path, then obfuscate the `.py` files, thus
all the `.py` files in the output path are overwritten by the obfuscated ones.

If there is an entry script, PyArmor will modify it, insert cross protection
code into the entry script. Refer to :ref:`Special Handling of Entry Script`

If there is any plugin specified in the command line, PyArmor will scan all the
source scripts and inject the plugin code into them before obfuscating. Refer to
:ref:`How to Deal with Plugins`

Next obfuscate all found scripts, save them in the default output path `dist`.

After that make the :ref:`runtime package` in the `dist` path.

Finally insert the :ref:`bootstrap code` into entry script.

Option ``--src`` used to specify source path if entry script is not in the top
most path. For example::

    # if no option --src, the "./mysite" is the source path
    pyarmor obfuscate --src "." --recursive mysite/wsgi.py

Option ``--plugin`` is used to extend license type of obfuscated scripts, it
will inject the content of plugin script into the obfuscated scripts. The
corresponding filename of plugin is `NAME.py`. More information about plugin,
refer to :ref:`How to Deal with Plugins`, and here is a real example to show
usage of plugin :ref:`Using Plugin to Extend License Type`

Option ``--platform`` is used to specify the target platform of obfuscated
scripts if target platform is different from build platform. Use this option
multiple times if the obfuscated scripts are being to run many platforms. From
v5.7.5, the platform names are standardized, command `download` could list all
the available platform names.

Option ``--restrict`` is used to set restrict mode, :ref:`Restrict Mode`

Option ``--advanced`` is used to enable some advanced features to improve the
security. The available value for this option

* 0: Disable any advanced feature
* 1: Enable :ref:`Advanced Mode`
* 2: Enable :ref:`super mode`
* 3: Enable :ref:`advanced mode` and :ref:`vm mode`
* 4: Enable :ref:`super mode` and :ref:`vm mode`

For usage of option ``--runtime``, refer to command `runtime`_

**RUNTIME FILES**

If :ref:`super mode` is enabled, there is only one extension module::

  pytransform.pyd/.so

For all the others, the runtime files will be saved in the separated folder
``pytransform`` as package::

    pytransform/
        __init__.py
        _pytransform.so/.dll/.dylib

But if ``--package-runtime`` is `0`, they will be saved in the same path with
obfuscated scripts as four separated files::

    pytransform.py
    _pytransform.so/.dll/.dylib

If the option ``--enable-suffix`` is set, the runtime package or module name
will be ``pytransform_xxx``, here ``xxx`` is unique suffix based on the
registration code of PyArmor.


**BOOTSTRAP CODE**

If :ref:`super mode` is enabled, all the obfuscated scripts will import the
runtime module at the first line, this is super mode :ref:`bootstrap code`::

    from pytransform import pyarmor

For non-super mode, the following :ref:`bootstrap code` will be inserted into
the entry script only::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

If the entry script is ``__init__.py``, the :ref:`bootstrap code` will make a
relative import by using leading dots like this::

    from .pytransform import pyarmor_runtime
    pyarmor_runtime()

But the option ``--bootstrap`` is set to ``2``, the :ref:`bootstrap code` always
makes absolute import without leading dots. If it is set to ``3``, the
:ref:`bootstrap code` always makes relative import with leading dots.

If the option ``--enable-suffix`` is set, the bootstrap code may like this::

    from pytransform_vax_000001 import pyarmor_runtime
    pyarmor_runtime(suffix='vax_000001')

If ``--no-bootstrap`` is set, or ``--bootstrap`` is `0`, then no bootstrap code
will be inserted into the entry scripts.


**EXAMPLES**

* Obfuscate all the `.py` only in the current path::

     pyarmor obfuscate foo.py

* Obfuscate all the `.py` only in the current path and multiple entry scripts::

     pyarmor obfuscate foo.py foo-svr.py foo-client.py

* Obfuscate all the `.py` in the current path recursively::

     pyarmor obfuscate --recursive foo.py

* Obfuscate all the `.py` in the current path recursively, but entry script not
  in top most path::

     pyarmor obfuscate --src "." --recursive mysite/wsgi.py

* Obfuscate a script `foo.py` only, no runtime files::

    pyarmor obfuscate --no-runtime --exact foo.py

* Obfuscate all the `.py` in a path recursive, no entry script, no generate
  runtime package::

     pyarmor obfuscate --recursive --no-runtime .
     pyarmor obfuscate --recursive --no-runtime src/

* Obfuscate all the `.py` in the current path recursively, exclude all
  the `.py` in the path `build` and `tests`::

     pyarmor obfuscate --recursive --exclude build,tests foo.py
     pyarmor obfuscate --recursive --exclude build --exclude tests foo.py

* Obfuscate only two scripts `foo.py`, `moda.py` exactly::

     pyarmor obfuscate --exact foo.py moda.py

* Obfuscate all the `.py` file in the path `mypkg/`::

     pyarmor obfuscate --output dist/mypkg mypkg/__init__.py

* Obfuscate all the `.py` files in the current path, but do not insert
  cross protection code into obfuscated script :file:`dist/foo.py`::

     pyarmor obfuscate --no-cross-protection foo.py

* Obfuscate all the `.py` files in the current path, but do not insert
  bootstrap code at the beginning of obfuscated script
  :file:`dist/foo.py`::

     pyarmor obfuscate --no-bootstrap foo.py

* Insert the content of :file:`check_ntp_time.py` into `foo.py`, then
  obfuscating `foo.py`::

     pyarmor obfuscate --plugin check_ntp_time foo.py

* Only plugin `assert_armored` is called then inject it into the `foo.py`::

     pyarmor obfuscate --plugin @assert_armored foo.py

* If the script `foo.py` includes internal plugin, obfuscate it with special
  plugin name ``on``::

     pyarmor obfuscate --plugin on foo.py

* Obfuscate the scripts in Macos and run obfuscated scripts in Ubuntu::

    pyarmor obfuscate --platform linux.x86_64 foo.py

* Obfuscate the scripts in advanced mode::

    pyarmor obfuscate --advanced 1 foo.py

* Obfuscate the scripts with restrict mode 2::

    pyarmor obfuscate --restrict 2 foo.py

* Obfuscate all the `.py` files in the current path except `__init__.py` with
  restrice mode 4::

    pyarmor obfuscate --restrict 4 --exclude __init__.py --recursive .

* Obfuscate a package with unique runtime package name::

    cd /path/to/mypkg
    pyarmor obfuscate -r --enable-suffix --output dist/mypkg __init__.py

* Obfuscate scripts by super mode with expired license::

    pyarmor licenses -e 2020-10-05 regcode-01
    pyarmor obfuscate --with-license licenses/regcode-01/license.lic \
                      --advanced 2 foo.py

* Obfuscate scripts by super mode with customized cross protection scripts, and
  don't embed license file to extension module, but use outer ``license.lic``::

    pyarmor obfuscate --cross-protection build/pytransform_protection.py \
                      --with-license outer --advanced 2 foo.py

* Use prebuilt runtime package to obfuscate scripts::

    pyarmor runtime --advanced 2 --with-license outer -O myruntime-1
    pyarmor obfuscate --runtime myruntime-1 --with-license licenses/r001/license.lic foo.py
    pyarmor obfuscate --runtime @myruntime-1 --exact foo-2.py foo-3.py

.. _licenses:

licenses
--------

Generate new licenses for obfuscated scripts.

**SYNOPSIS**::

    pyarmor licenses <options> CODE

**OPTIONS**

-O, --output OUTPUT         Output path, `stdout` is supported
-e, --expired YYYY-MM-DD    Expired date for this license
-d, --bind-disk SN          Bind license to serial number of harddisk
-4, --bind-ipv4 IPV4        Bind license to ipv4 addr
-m, --bind-mac MACADDR      Bind license to mac addr
-x, --bind-data DATA        Pass extra data to license, used to extend license type
--disable-restrict-mode     Disable all the restrict modes
--enable-period-mode        Check license per hour when the obfuscated script is running
--fixed KEY                 Bind license to Python interpreter

**DESCRIPTION**

In order to run obfuscated scripts, it's necessarey to hava a `license.lic`. As
obfuscating the scripts, there is a default `license.lic` created at the same
time. In this license the obfuscated scripts can run on any machine and never
expired.

This command is used to generate new licenses for obfuscated scripts. For
example::

    pyarmor licenses --expired 2019-10-10 mycode

An expired license will be generated in the default output path plus code name
`licenses/mycode`, then overwrite the old one in the same path of obfuscated
script::

    cp licenses/mycode/license.lic dist/pytransform/

Since v6.3.0, the `license.lic` has been embedded into binary libraries by
default, so the copy mode doesn't work. Instead of using option
``--with-license`` when obfuscating the scripts, for example::

  pyarmor obfuscate --with-license licenses/mycode/license.lic foo.py

If you prefer the tradional way, refer to :ref:`How to use outer license file`

Another example, bind obfuscated scripts to mac address and expired on
2019-10-10::

    pyarmor licenses --expired 2019-10-10 --bind-mac f8:ff:c2:27:00:7f r001

Before this, run command `hdinfo`_ to get hardware information::

    pyarmor hdinfo

    Hardware informations got by PyArmor:
    Serial number of first harddisk: "FV994730S6LLF07AY"
    Default Mac address: "f8:ff:c2:27:00:7f"
    Ip address: "192.168.121.100"

If there are many network cards in the machine, pyarmor only checks the default
mac address which is printed by command `hdinfo`. For example::

    pyarmor licenses --bind-mac "f8:ff:c2:27:00:7f" r002

If binding to other network card, wrap the mac address with angle brackets. For
example::

    pyarmor licenses --bind-mac "<2a:33:50:46:8f>" r002

It's possible to bind all of mac addresses or some of them in same machine, for
example::

    pyarmor licenses --bind-mac "<2a:33:50:46:8f,f0:28:69:c0:24:3a>" r003

In Linux, it's possible to bind mac address with ifname, for example::

    pyarmor licenses --bind-mac "eth1/fa:33:50:46:8f:3d" r004

If there are many hard disks in the machine, pyarmor only checks the default
hard disk which is printed by command `hdinfo`. For example::

    pyarmor licenses --bind-disk "FV994730S6LLF07AY" r005

For binding other hard disk card, specify a name for it. For example::

    # In Windows, bind to the first, the second disk
    pyarmor licenses --bind-disk "/0:FV994730S6LLF07AY" r006
    pyarmor licenses --bind-disk "/1:KDX3298FS6P5AX380" r007

    # In Linux, bind to "/dev/vda2"
    pyarmor licenses --bind-disk "/dev/vda2:KDX3298FS6P5AX380" r008

By option `-x` any data could be saved into the license file, it's mainly used
to extend license type. For example::

    pyarmor licenses -x "2019-02-15" r005

In the obfuscated scripts, the data passed by `-x` could be got by this way::

    from pytransfrom import get_license_info
    info = get_license_info()
    print(info['DATA'])

It also could output the license key in the stdout other than a file::

    pyarmor --silent licenses --output stdout -x "2019-05-20" reg-0001

By option ``--fixed``, the license could be bind to Python interpreter. For
example, use special key `1` to bind the license to current Python interpreter::

    pyarmor licenses --fixed 1

It also could bind the license to many Python interpreters by passing multiple
keys separated by comma::

    pyarmor licenses --fixed 4265050,5386060

How to get bind key of Python interpreter, refer to :ref:`Binding obfuscated
scripts to Python interpreter`

Do not use this feature in 32-bit Windows, because the bind key is different in
different machine, it may be changed even if python is restarted in the same
machine.

.. note::

   Here is a real example :ref:`Using Plugin to Extend License Type`

.. _pack:

pack
----

Obfuscate the scripts or project and pack them into one bundle.

**SYNOPSIS**::

    pyarmor pack <options> SCRIPT | PROJECT

**OPTIONS**

-O, --output PATH       Directory to put final built distributions in.
-e, --options OPTIONS   Pass these extra options to `pyinstaller`
-x, --xoptions OPTIONS  Pass these extra options to `pyarmor obfuscate`
-s FILE                 Use external .spec file to pack the scripts
--without-license       Do not generate license for obfuscated scripts
--with-license FILE     Use this license file other than default one
--clean                 Remove cached files before packing
--debug                 Do not remove build files after packing
--name                  Name to assign to the bundled (default: the script’s basename)

**DESCRIPTION**

The command `pack`_ first calls `PyInstaller`_ to generate `.spec` file which
name is same as entry script. The options specified by ``--e`` will be pass to
`PyInstaller`_ to generate `.spec` file. It could be any option accepted by
`PyInstaller`_ except ``-y``, ``--noconfirm``, ``-n``, ``--name``,
``--distpath``, ``--specpath``.

If there is in trouble, make sure the script could be bundled by `PyInstaller`_
directly. For example::

    pyinstaller foo.py

So long as `PyInstaller`_ could work, just pass those options by ``-e``, the
command `pack`_ should work either.

Then `pack`_ will obfuscates all the `.py` files in the same path of entry
script recursively. It will call command `obfuscate`_ with options ``-r``,
``--output``, ``--package-runtime 0`` and the options specified by
``-x``. However if packing a project, `pack`_ will obfuscate the project by
command `build`_ with option ``-B``, and all the options specifed by ``-x`` will
be ignored. In this case config the project to control how to obfuscate the
scripts.

Next `pack`_ patches the `.spec` file so that the original scripts could be
replaced with the obfuscated ones.

Finally `pack`_ call `PyInstaller`_ with this pacthed `.spec` file to generate
the output bundle with obfuscated scripts. Refer to :ref:`How to pack obfuscated
scripts`.

If the option ``--debug`` is set, for example::

    pyarmor pack --debug foo.py

The following generated files will be kept, generally all of them are removed
after packing end::

    foo.spec
    foo-patched.spec
    dist/obf/temp/hook-pytransform.py
    dist/obf/*.py                       # All the obfuscated scripts

The patched `foo-patched.spec` could be used by pyinstaller to pack the
obfuscated scripts directly, for example::

    pyinstaller -y --clean foo-patched.spec

If some scripts are modified, just obfuscate them again, then run this command
to pack them quickly. All the options for command `obfuscate`_ could be got from
the output of command `pack`_.

If you'd like to change the final bundle name, specify the option ``--name``
directly, do not pass it by the option ``-e``, it need some special handling.

If you have a worked `.spec` file, just specify it by option ``-s`` (in this
case the option ``-e`` will be ignored), for example::

    pyarmor pack -s foo.spec foo.py

The main script (here it's `foo.py`) must be list in the command line, otherwise
`pack`_ doesn't know where to find the scripts to be obfuscated. More refer to
:ref:`Bundle obfuscated scripts with customized spec file`

If there are many data files or hidden imports, it's better to write a hook file
to find them easily. For example, create a hook file named ``hook-sys.py``::

    from PyInstaller.utils.hooks import collect_data_files, collect_all
    datas, binaries, hiddenimports = collect_all('my_module_name')
    datas += collect_data_files('submodule')
    hiddenimports += ['_gdbm', 'socket', 'h5py.defs']
    datas += [ ('/usr/share/icons/education_*.png', 'icons') ]

Then call `pack`_ with extra option ``--additional-hooks-dir .`` to tell
pyinstaller find the hook in the current path::

    pyarmor pack -e " --additional-hooks-dir ." foo.py

More information about pyinstaller hook, refer to
https://pyinstaller.readthedocs.io/en/stable/hooks.html#understanding-pyinstaller-hooks

When something is wrong, turn on PyArmor debug flag to print traceback::

    pyarmor -d pack ...

.. important::

   For option `-e` and `-x`, it need an extra whitespace in option value,
   otherwise it will complain of `error: unrecognized arguments`. For exmaple::

     # Wrong, no heading whitespace before --advanced 2
     pyarmor pack -x "--advanced 2" ...

     # Right
     pyarmor pack -x " --advanced 2" ...

**EXAMPLES**

* Obfuscate `foo.py` and pack them into the bundle `dist/foo`::

    pyarmor pack foo.py

* Remove the build folder, and start a clean pack::

    pyarmor pack --clean foo.py

* Pack the obfuscated scripts by an exists `myfoo.spec`::

    pyarmor pack -s myfoo.spec foo.py

* Pass extra options to run `PyInstaller`::

    pyarmor pack -e " -w --icon app.ico" foo.py
    pyarmor pack -e " --icon images\\app.ico" foo.py

* Pass extra options to obfuscate scripts::

    pyarmor pack -x " --exclude venv --exclude test" foo.py

* Pack the obfuscated script to one file and in advanced mode::

    pyarmor pack -e " --onefile" -x " --advanced 1" foo.py

* Pack the obfuscated scripts and expired on 2020-12-25::

    pyarmor licenses -e 2020-12-25 cy2020
    pyarmor pack --with-license licenses/cy2020/license.lic foo.py

* Change the final bundle name to `my_app` other than `foo`::

    pyarmor pack --name my_app foo.py

* Pack a project with advanced mode::

    pyarmor init --entry main.py
    pyarmor config --advanced 1
    pyarmor pack .

.. note::

   Since v5.9.0, possible pack one project directly by specify the project path
   in the command line. For example, create a project in the current path, then
   pack it::

     pyarmor init --entry main.py
     pyarmor pack .

   By this way the obfuscated scripts could be fully controlled.

.. note::

   In Windows, use double black splash in extra options. For example::

     pyarmor pack -e " --icon images\\app.ico" foo.py

.. note::

   For option ``-e`` and ``-x``, pass an extra leading whitespace to avoid
   command line error::

     pyarmor pack -e " --onefile" -x " --advanced 2" foo.py

.. important::

   The command `pack` will obfuscate the entry script automatically, DO NOT
   obfuscate the entry script before pack.

   By default the command `pack` obfuscates all the ``.py`` files only in the
   entry script's path recursively. It won't obfuscate all the dependencies out
   of this path.

.. comment:

    If you have a `.spec` file worked, specified by ``-s``, thus `pack`_ will use it
    other than generate new one ::

    pyarmor pack -s /path/to/myself.spec foo.py

.. _hdinfo:

hdinfo
------

Show hardware information of this machine, such as serial number of hard disk,
mac address of network card etc. The information got here could be as input data
to generate license file for obfuscated scripts.

**SYNOPSIS**::

    pyarmor hdinfo

Without argument, this command displays all available hardware information.

In Windows, it also supports to query named hard disk, for example, get serial
number from the first and third hard disk::

    pyarmor hdinfo /0 /2

In Linux, query named hard disk or network card, for example::

    pyarmor hdinfo /dev/vda2
    pyarmor hdinfo eth2

If `pyarmor` isn't installed, downlad this tool `hdinfo`

    https://github.com/dashingsoft/pyarmor-core/tree/master/#hdinfo

And run it directly::

    hdinfo

It will print the same hardware information as `pyarmor hdinfo`

.. _init:

init
----

Create a project to manage obfuscated scripts.

**SYNOPSIS**::

    pyarmor init <options> PATH

**OPTIONS**

-t, --type <auto,app,pkg>  Project type, default value is `auto`
-s, --src SRC              Base path of python scripts, default is current path
-e, --entry ENTRY          Entry script of this project

**DESCRIPTION**

This command will create a project in the specify `PATH`, and a file
`.pyarmor_config` will be created at the same time, which is project
configuration of JSON format.

If the option ``--type`` is set to `auto`, which is the default value, the
project type will set to `pkg` if the entry script is `__init__.py`, otherwise
to `app`.

The `init` command will set `is_package` to `1` if the new project is configured
as `pkg`, otherwise it's set to `0`.

After project is created, use command config_ to change the project settings.

**EXAMPLES**

* Create a project in the current path::

    pyarmor init --entry foo.py

* Create a project in the build path `obf`::

    pyarmor init --entry foo.py obf

* Create a project for package::

    pyarmor init --entry __init__.py

* Create a project in the path `obf`, manage the scripts in the path
  `/path/to/src`::

    pyarmor init --src /path/to/src --entry foo.py obf

.. _config:

config
------

Update project settings.

**SYNOPSIS**::

    pyarmor config <options> [PATH]

**OPTIONS**

--name NAME                     Project name
--title TITLE                   Project title
--src SRC                       Project src, base path for matching scripts
--output PATH                   Output path for obfuscated scripts
--manifest TEMPLATE             Manifest template string
--entry SCRIPT                  Entry script of this project
--is-package <0,1>              Set project as package or not
--restrict <0,1,2,3,4>          Set restrict mode
--obf-mod <0,1,2>               Disable or enable to obfuscate module
--obf-code <0,1,2>              Disable or enable to obfuscate function
--wrap-mode <0,1>               Disable or enable wrap mode
--advanced <0,1,2,3,4>          Enable advanced mode `1`, super mode `2`, vm mode `3` or `4`
--cross-protection <0,1>        Disable or enable to insert cross protection code into entry script,
                                it also could be a filename to specify customized protection script
--rpath RPATH                   Set the path of runtime files in target machine
--plugin NAME                   Insert extra code to entry script, it could be used multiple times
--package-runtime <0,1>         Save the runtime files as package or not
--bootstrap <0,1,2,3>           How to insert bootstrap code to entry script
--enable-suffix <0,1>           Generate the runtime package with unique name
--with-license FILENAME         Use this license file, special value `outer` means no license
--mixin NAME                    Available mixin `str`, used to obfuscate string value

**DESCRIPTION**

Run this command in project path to change project settings::

    pyarmor config --option new-value

Or specify the project path at the end::

    pyarmor config --option new-value /path/to/project

Option ``--manifest`` is comma-separated list of manifest template command, same
as MANIFEST.in of Python Distutils.

Option ``--entry`` is comma-separated list of entry scripts, relative to src
path of project.

If option ``--plugin`` is set to empty string, all the plugins will be removed.

For the details of each option, refer to :ref:`Project Configuration File`

**EXAMPLES**

* Change project name and title::

    pyarmor config --name "project-1"  --title "My PyArmor Project"

* Change project entries::

    pyarmor config --entry foo.py,hello.py

* Exclude path `build` and `dist`, do not search `.py` file from these
  paths::

    pyarmor config --manifest "global-include *.py, prune build, prune dist"

* Copy all the `.json` files in the src path to output path::

    pyarmor config --manifest "include *.py, include *.json"

* Obfuscate script with wrap mode off::

    pyarmor config --wrap-mode 0

* Obfuscate all string value in the scripts::

    pyarmor config --mixin str

    # Restore default value, no obfuscating strings
    pyarmor config --mixin ''

* Set plugin for entry script. The content of `check_ntp_time.py` will
  be insert into entry script as building project::

    pyarmor config --plugin check_ntp_time

* Remove all plugins::

    pyarmor config --plugin ''

.. _build:

build
-----

Build project, obfuscate all scripts in the project.

**SYNOPSIS**::

    pyarmor config <options> [PATH]

**OPTIONS**

-B, --force                   Force to obfuscate all scripts
-r, --only-runtime            Generate extra runtime files only
-n, --no-runtime              DO NOT generate runtime files
-O, --output OUTPUT           Output path, override project configuration
--platform NAME               Distribute obfuscated scripts to other platform
--package-runtime <0,1>       Save the runtime files as package or not
--runtime PATH                Use prebuilt runtime package

**DESCRIPTION**

Run this command in project path::

    pyarmor build

Or specify the project path at the end::

    pyarmor build /path/to/project

The option ``--no-runtime`` may impact on the :ref:`bootstrap code`, the
bootstrap code will make absolute import without leading dots in entry script.

About option ``--platform`` and ``--package-runtime``, refer to command `obfuscate`_

About option ``--runtime``, refer to command `runtime`_

**EXAMPLES**

* Only obfuscate the scripts which have been changed since last
  build::

    pyarmor build

* Force build all the scripts::

    pyarmor build -B

* Generate runtime files only, do not try to obfuscate any script::

    pyarmor build -r

* Obfuscate the scripts only, do not generate runtime files::

    pyarmor build -n

* Save the obfuscated scripts to other path, it doesn't change the
  output path of project settings::

    pyarmor build -B -O /path/to/other

* Build project in Macos and run obfuscated scripts in Ubuntu::

    pyarmor build -B --platform linux.x86_64

.. _info:

info
----

Show project information.

**SYNOPSIS**::

    pyarmor info [PATH]

**DESCRIPTION**

Run this command in project path::

    pyarmor info

Or specify the project path at the end::

    pyarmor info /path/to/project

.. _check:

check
-----

Check consistency of project.

**SYNOPSIS**::

    pyarmor check [PATH]

**DESCRIPTION**

Run this command in project path::

    pyarmor check

Or specify the project path at the end::

    pyarmor check /path/to/project

.. _benchmark:

benchmark
---------

Check the performance of obfuscated scripts.

**SYNOPSIS**::

    pyarmor benchmark <options>

**OPTIONS**:

-m, --obf-mod <0,1,2>        Whether to obfuscate the whole module
-c, --obf-code <0,1,2>       Whether to obfuscate each function
-w, --wrap-mode <0,1>        Whether to obfuscate each function with wrap mode
-a, --advanced <0,1,2,3,4>   Set advanced mode, super mode and vm mode
--debug                      Do not remove test path

**DESCRIPTION**

This command will generate a test script, obfuscate it and run it, then output
the elapsed time to initialize, import obfuscated module, run obfuscated
functions etc.

**EXAMPLES**

* Test performance with default mode::

    pyarmor benchmark

* Test performance with no wrap mode::

    pyarmor benchmark --wrap-mode 0

* Check the test scripts which saved in the path `.benchtest`::

    pyarmor benchmark --debug

.. _register:

register
--------

Make registration keyfile effect, or show registration information.

**SYNOPSIS**::

    pyarmor register [KEYFILE]

**DESCRIPTION**

This command is used to register the purchased key file or code file
to take it effects::

    pyarmor register /path/to/pyarmor-regfile-1.zip
    pyarmor register /path/to/pyarmor-keycode-1.txt

Show registration information::

    pyarmor register

Purchase one registration code::

    pyarmor register --buy

.. _download:

download
--------

List and download platform-dependent dynamic libraries.

**SYNOPSIS**::

    pyarmor download <options> NAME

**OPTIONS**:

--help-platform       Display all available standard platform names
-L, --list FILTER     List available dynamic libraries in different platforms
-O, --output PATH     Save downloaded library to this path
--update              Update all the downloaded dynamic libraries

**DESCRIPTION**

This command mainly used to download available dynamic libraries for cross
platform.

List all available standard platform names. For examples::

    pyarmor download
    pyarmor download --help-platform
    pyarmor download --help-platform windows
    pyarmor download --help-platform linux.x86_64

Then download one from the list. For example::

    pyarmor download linux.armv7
    pyarmor download linux.x86_64

By default the download file will be saved in the path ``~/.pyarmor/platforms``
with different platform names.

Option ``--list`` could filter the platform by name, arch, features, and display
the information in details. For examples::

    pyarmor download --list
    pyarmor download --list windows
    pyarmor download --list windows.x86_64
    pyarmor download --list JIT
    pyarmor download --list armv7

After `pyarmor` is upgraded, however these downloaded dynamic libraries won't be
upgraded. The option ``--update`` could be used to update all these downloaded
files. For example::

    pyarmor download --update

.. _runtime:

runtime
-------

Geneate :ref:`runtime package` separately.

**SYNOPSIS**::

    pyarmor runtime <options>

**OPTIONS**:

-O, --output PATH             Output path, default is `dist`
-n, --no-package              Generate runtime files without package
-i, --inside                  Generate bootstrap script which is used inside one package
-L, --with-license FILE       Replace default license with this file, special value `outer` means
                              no license
--platform NAME               Generate runtime package for specified platform
--enable-suffix               Generate the runtime package with unique name
--advanced <0,1,2,3,4>        Generate advanced runtime package

**DESCRIPTION**

This command is used to generate the runtime package separately.

The :ref:`runtime package` could be shared if the scripts are obufscated by same
:ref:`Global Capsule`. So generate it once, then need not generate the runtime
files when obfuscating the scripts later.

It also generates a bootstrap script ``pytransform_bootstrap.py`` in the output
path. This script is obfuscated from an empty script, and there is
:ref:`bootstrap code` in it. It's mainly used to run :ref:`bootstrap code` in
the plain script. For example, once it's imported, all the other obfuscated
modules could be imported in one plain script::

    import pytransform_bootstrap
    import obf_foo

If option ``--inside`` is specified, it will generate bootstrap package
``pytransform_bootstrap`` other than one single script.

The option ``--advanced`` is used to generate advanced runtime package, for
example, :ref:`super mode` etc.

About option ``--platform`` and ``--enable-suffix``, refer to command
`obfuscate`_

Since v6.2.0, it also generates protection script ``pytransform_protection.py``,
which is used to patch entry scripts. Refer to :ref:`Customizing cross protection code`

Since v6.3.7, the runtime package will remember the option `--advanced`,
`--platform`, `--enable-suffix`, and save them to cross protection script
`pytransform_protection.py` as leading comment. The advantage is when
obfuscating the scripts with option ``--runtime``, it could get these settings
automatically and use the same cross protection script. For example::

    pyarmor runtime --platform linux.armv7 --enable-suffix --advanced 1 -O myruntime-1
    pyarmor obfuscate --runtime myruntime-1 foo.py

The second command is same as::

    pyarmor obfuscate --platform linux.armv7 --enable-suffix --advanced 1 foo.py

With a leading ``@`` in the runtime path, it will not copy any runtime file, but
read the settings of runtime package. It's useful if there are multiple entry
scripts need to be obufscated. For example::

    pyarmor obfuscate --runtime @myruntime-1 --exact foo-2.py foo-3.py

For project, set option ``--runtime`` for command :ref:`build`. For example::

    pyarmor build --runtime @myruntime-1

**EXAMPLES**

* Generate :ref:`runtime package` ``pytransform`` in the default path `dist`::

    pyarmor runtime

* Not generate a package, but four separate files :ref:`runtime files`::

    pyarmor runtime -n

* Generate bootstrap package ``dist/pytransform_boostrap``::

    pyarmor runtime -i

* Generate :ref:`runtime package` for platform `armv7` with expired license::

    pyarmor licenses --expired 2020-01-01 code-001
    pyarmor runtime --with-license licenses/code-001/license.lic --platform linux.armv7

* Generate runtime module for super mode::

    pyarmor runtime --advanced 2

* Generate runtime module for super mode but with outer license::

    pyarmor runtime --advanced 2 --with-license outer

.. include:: _common_definitions.txt
