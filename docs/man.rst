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
    pack         Pack obfuscated scripts to one bundle
    hdinfo       Show hardware information
    runtime      Generate runtime package separately

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

See `pyarmor <command> -h` for more information on a specific command.

.. note::

   From v5.7.1, the first character is command alias for most usage commands::

       obfuscate, licenses, pack, init, config, build

   For example::

       pyarmor o => pyarmor obfuscate

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
--advanced <0,1>              Disable or enable advanced mode
--restrict <0,1,2,3,4>        Set restrict mode
-n, --no-runtime              DO NOT generate runtime files
--package-runtime <0,1>       Save the runtime files as package or not
--enable-suffix               Generate the runtime package with unique name

**DESCRIPTION**

PyArmor first checks whether :ref:`Global Capsule` exists in the ``HOME``
path. If not, make it.

Then find all the scripts to be obfuscated. There are 3 modes to search the
scripts:

* Normal: find all the `.py` files in the same path of entry script
* Recursive: find all the `.py` files in the path of entry script recursively
* Exact: only these scripts list in the command line

If there is an entry script, PyArmor will modify it, insert cross protection
code into the entry script.

Next obfuscate all these scripts in the default output path `dist`.

After that make the :ref:`runtime package` in the `dist` path.

Finally insert the :ref:`bootstrap code` into entry script.

If ``--exact`` is set, all the scripts in the command line are taken as entry
scripts. Otherwise only the first script is entry script.

Option ``--src`` used to specify source path if entry script is not in the top
most path. For example::

    # if no option --src, the "./mysite" is the source path
    pyarmor obfuscate --src "." --recursive mysite/wsgi.py

Option ``--plugin`` is used to extend license type of obfuscated scripts, it
will inject the content of plugin into the obfuscated scripts. The corresponding
filename of plugin is `NAME.py`. `Name` may be absolute path if it's not in the
current path, or specify plugin path by environment variable `PYARMOR_PLUGIN`.

More information about plugin, refer to :ref:`How to Deal with Plugins`, and
here is a real example to show usage of plugin :ref:`Using Plugin to Extend
License Type`

Option ``--platform`` is used to specify the target platform of obfuscated
scripts if target platform is different from build platform. Use this option
multiple times if the obfuscated scripts are being to run many platforms. From
v5.7.5, the platform names are standardized, command `download` could list all
the available platform names.

Option ``--restrict`` is used to set restrict mode, :ref:`Restrict Mode`

**RUNTIME FILES**

By default the runtime files will be saved in the separated folder ``pytransform``
as package::

    pytransform/
        __init__.py
        _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
        pytransform.key
        license.lic

But if ``--package-runtime`` is `0`, they will be saved in the same path with
obfuscated scripts as four separated files::

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pytransform.key
    license.lic

If the option ``--enable-suffix`` is set, the runtime package or module name
will be ``pytransform_xxx``, here ``xxx`` is unique suffix based on the
registration code of PyArmor.

**BOOTSTRAP CODE**

By default, the following :ref:`bootstrap code` will be inserted into the entry
script::

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

* Obfuscate the scripts in Macos and run obfuscated scripts in
  Ubuntu::

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

Another example, bind obfuscated scripts in mac address and expired on
2019-10-10::

    pyarmor licenses --expired 2019-10-10 --bind-mac 2a:33:50:46:8f tom
    cp licenses/tom/license.lic dist/pytransform/

Before this, run command `hdinfo`_ to get hardware information::

    pyarmor hdinfo

By option `-x` any data could be saved into the license file, it's mainly used
to extend license tyoe. For example::

    pyarmor licenses -x "2019-02-15" tom

In the obfuscated scripts, the data passed by `-x` could be got by this way::

    from pytransfrom import get_license_info
    info = get_license_info()
    print(info['DATA'])

It also could output the license key in the stdout other than a file::

    pyarmor --silent licenses --output stdout -x "2019-05-20" reg-0001

.. note::

   Here is a real example :ref:`Using Plugin to Extend License Type`

.. _pack:

pack
----

Obfuscate the scripts and pack them into one bundle.

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
name is same as entry script. The options specified by ``--options`` will be
pass to `PyInstaller`_ to generate `.spec` file. It could any option accepted by
`PyInstaller`_ except ``--distpath``.

If there is in trouble, make sure this `.spec` works with `PyInstaller`_. For
example::

    pyinstaller myscript.spec

Then `pack`_ will obfuscates all the `.py` files in the same path of entry
script. It will call `pyarmor obfuscate` with options ``-r``, ``--output``, and
the extra options specified by ``--xoptions``.

Next `pack`_ patches the `.spec` file so that the original scripts could be
replaced with the obfuscated ones.

Finally `pack`_ call `PyInstaller`_ with this pacthed `.spec` file to generate
the final distributions.

For more information, refer to :ref:`How to pack obfuscated scripts`.

.. note::

   Since v5.9.0, possible pack one project directly by specify the project path
   in the command line. For example, create a project in the current path, then
   pack it::

     pyarmor init --entry main.py
     pyarmor pack .

   By this way the obfuscated scripts could be fully controlled.

.. important::

   The command `pack` will obfuscate the scripts automatically, do not
   try to pack the obfuscated the scripts.

.. comment:

    If you have a `.spec` file worked, specified by ``-s``, thus `pack`_ will use it
    other than generate new one ::

    pyarmor pack -s /path/to/myself.spec foo.py


**EXAMPLES**

* Obfuscate `foo.py` and pack them into the bundle `dist/foo`::

    pyarmor pack foo.py

* Remove the build folder, and start a clean pack::

    pyarmor pack --clean foo.py

* Pack the obfuscated scripts by an exists `myfoo.spec`::

    pyarmor pack -s myfoo.spec foo.py

* Pass extra options to run `PyInstaller`::

    pyarmor pack -e " -w --icon app.ico" foo.py

* Pass extra options to obfuscate scripts::

    pyarmor pack -x " --exclude venv --exclude test" foo.py

* Pack the obfuscated script to one file and in advanced mode::

    pyarmor pack -e " --onefile" -x " --advanced" foo.py

* Pack the obfuscated scripts and expired on 2020-12-25::

    pyarmor licenses -e 2020-12-25 cy2020
    pyarmor pack --with-license licenses/cy2020/license.lic foo.py

* Change the final bundle name to `my_app` other than `foo`::

    pyarmor pack --name my_app foo.py

* Pack a project with advanced mode::

    pyarmor init --entry main.py
    pyarmor config --advanced 1
    pyarmor pack .

.. _hdinfo:

hdinfo
------

Show hardware information of this machine, such as serial number of hard disk,
mac address of network card etc. The information got here could be as input data
to generate license file for obfuscated scripts.

**SYNOPSIS**::

    pyarmor hdinfo

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
--obf-mod <0,1>                 Disable or enable to obfuscate module
--obf-code <0,1,2>              Disable or enable to obfuscate function
--wrap-mode <0,1>               Disable or enable wrap mode
--advanced <0,1>                Disable or enable advanced  mode
--cross-protection <0,1>        Disable or enable to insert cross protection code into entry script
--runtime-path RPATH            Set the path of runtime files in target machine
--plugin NAME                   Insert extra code to entry script, it could be used multiple times
--package-runtime <0,1>         Save the runtime files as package or not
--bootstrap <0,1,2,3>           How to insert bootstrap code to entry script
--enable-suffix <0,1>           Generate the runtime package with unique name
--with-license FILENAME         Use this license file other than the default one

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

* Obfuscate script with wrap mode off::

    pyarmor config --wrap-mode 0

* Set plugin for entry script. The content of `check_ntp_time.py` will
  be insert into entry script as building project::

    pyarmor config --plugin check_ntp_time.py

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

**DESCRIPTION**

Run this command in project path::

    pyarmor build

Or specify the project path at the end::

    pyarmor build /path/to/project

The option ``--no-runtime`` may impact on the :ref:`bootstrap code`, the
bootstrap code will make absolute import without leading dots in entry script.

About option ``--platform`` and ``--package-runtime``, refer to command `obfuscate`_

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

banchmark
---------

Check the performance of obfuscated scripts.

**SYNOPSIS**::

    pyarmor benchmark <options>

**OPTIONS**:

-m, --obf-mode <0,1>     Whether to obfuscate the whole module
-c, --obf-code <0,1,2>   Whether to obfuscate each function
-w, --wrap-mode <0,1>    Whether to obfuscate each function with wrap mode
--debug                  Do not remove test path

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

This command is used to register the purchased keyfile to take it effects::

    pyarmor register /path/to/pyarmor-regfile-1.zip

Show registration information::

    pyarmor register

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
-L, --with-license FILE       Replace default license with this file
--platform NAME               Generate runtime package for specified platform
--enable-suffix               Generate the runtime package with unique name

**DESCRIPTION**

This command is used to generate the runtime package separately.

The :ref:`runtiem package` could be shared if the scripts are obufscated by same
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

About option ``--platform`` and ``--enable-suffix``, refer to command
`obfuscate`_

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

.. include:: _common_definitions.txt
