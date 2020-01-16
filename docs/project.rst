.. _using project:

Using Project
=============

Project is a folder include its own configuration file, which used to
manage obfuscated scripts.

There are several advantages to manage obfuscated scripts by Project:

* Increment build, only updated scripts are obfuscated since last build
* Filter obfuscated scripts in the project, exclude some scripts
* Obfuscate the scripts with different modes
* More convenient to manage obfuscated scripts

Managing Obfuscated Scripts With Project
----------------------------------------

Use command :ref:`init` to create a project::

    cd examples/pybench
    pyarmor init --entry=pybench.py

It will create project configuration file :file:`.pyarmor_config` in
the current path. Or create project in another path::

    pyarmor init --src=examples/pybench --entry=pybench.py projects/pybench

The project path `projects/pybench` will be created, and
:file:`.pyarmor_config` will be saved there.

The common usage for project is to do any thing in the project path::

    cd projects/pybench

Show project information::

    pyarmor info

Obfuscate all the scripts in this project by command :ref:`build`::

    pyarmor build

Change the project configuration by command :ref:`config`.

For example, exclude the :file:`dist`, :file:`test`, the `.py` files in these
folder will not be obfuscated::

    pyarmor config --manifest "include *.py, prune dist, prune test"

Force rebuild::

    pyarmor build --force

Run obfuscated script::

    cd dist
    python pybench.py

After some scripts changed, just run :ref:`build` again::

    cd projects/pybench
    pyarmor build

.. _obfuscating scripts with different modes:

Obfuscating Scripts With Different Modes
----------------------------------------

First configure the different modes, refer to :ref:`The Modes of Obfuscated Scripts`::

    pyarmor config --obf-mod=1 --obf-code=0

Then obfuscating scripts in new mode::

    pyarmor build -B

.. _project configuration file:

Project Configuration File
--------------------------

Each project has a configure file. It's a json file named
:file:`.pyarmor_config` stored in the project path.

- name

    Project name.

- title

    Project title.

- src

    Base path to match files by manifest template string.

    It could be absolute path, or relative path based on project folder.

* manifest

    A string specifies files to be obfuscated, same as MANIFEST.in of
    Python Distutils, default value is::

        global-include *.py

    It means all files anywhere in the `src` tree matching.

    Multi manifest template commands are spearated by comma, for example::

        global-include *.py, exclude __mainfest__.py, prune test

    Refer to
    https://docs.python.org/2/distutils/sourcedist.html#commands

* is_package

    Available values: 0, 1, None

    When it's set to 1, the basename of `src` will be appended to `output` as
    the final path to save obfuscated scripts, but runtime files are still in
    the path `output`

    When init a project and no ``--type`` specified, it will be set to 1 if
    there is `__init__.py` in the path `src`, otherwise it's None.

* restrict_mode

    Available values: 0, 1, 2, 3, 4

    By default it's set to 1.

    Refer to :ref:`Restrict Mode`

* entry

    A string includes one or many entry scripts.

    When build project, insert the following bootstrap code for each
    entry::

        from pytransform import pyarmor_runtime
        pyarmor_runtime()

    The entry name is relative to `src`, or filename with absolute
    path.

    Multi entries are separated by comma, for example::

        main.py, another/main.py, /usr/local/myapp/main.py

    Note that entry may be NOT obfuscated, if `manifest` does not
    specify this entry.

* output

    A path used to save output of build. It's relative to project path.

* capsule

    .. warning:: Removed since v5.9.0

    Filename of project capsule. It's relative to project path if it's
    not absolute path.

* obf_code

    How to obfuscate byte code of each code object, refer to :ref:`Obfuscating Code Mode`:

        - 0

        No obfuscate

        - 1 (Default)

        Obfuscate each code object by default algorithm

        - 2

        Obfuscate each code object by more complex algorithm

* wrap_mode

    Available values: 0, 1, None

    Whether to wrap code object with `try..final` block.

    The default value is `1`, refer to :ref:`Wrap Mode`

* obf_mod

    How to obfuscate whole code object of module, refer to :ref:`Obfuscating Module Mode`:

        - 0

        No obfuscate

        - 1 (Default)

        Obfuscate byte-code by DES algorithm

* cross_protection

    How to proect dynamic library in obfuscated scripts:

        - 0

        No protection

        - 1

        Insert proection code with default template, refer to
        :ref:`Special Handling of Entry Script`

        - Filename

        Read the template of protection code from this file other than
        default template.

* runtime_path

    None or any path.

    When run obfuscated scripts, where to find dynamic library
    `_pytransform`. The default value is None, it means it's within the
    :ref:`runtime package` or in the same path of :file:`pytransform.py`.

    It's useful when obfuscated scripts are packed into a zip file,
    for example, use py2exe to package obfuscated scripts. Set
    runtime_path to an empty string, and copy :ref:`Runtime Files` to
    same path of zip file, will solve this problem.

* plugins

    None or list of string

    Extend license type of obfuscated scripts, multi-plugins are
    supported. For example::

        plugins: ["check_ntp_time", "show_license_info"]

    About the usage of plugin, refer to :ref:`Using Plugin to Extend License Type`

* package_runtime

    How to save the runtime files:

       - 0

       Save them in the same path with the obufscated scripts

       - 1 (Default)

       Save them in the sub-path `pytransform` as a package

* enable_suffix

    .. note:: New in v5.8.7

    How to generate runtime package (module) and bootstrap code, it's useful as
    importing the scripts obfuscated by different developer:

       - 0 (Default)

       There is no suffix for the name of runtime package (module)

       - 1

       The name of runtime package (module) has a suffix, for example,
       ``pytransform_vax_00001``

* platform

    .. note:: New in v5.9.0

    A string includes one or many platforms. Multi platforms are separated by
    comma.

    Leave it to None or blank if not cross-platform obfuscating

* license_file

    .. note:: New in v5.9.0

    Use this license file other than the default one.

    Leave it to None or blank to use the default one.

* bootstrap_code

    .. note:: New in v5.9.0

    How to generate :ref:`Bootstrap Code` for the obfuscated entry scripts:

      - 0

      Do not insert bootstrap code into entry script

      - 1 (Default)

      Insert the bootstrap code into entry script. If the script name is
      ``__init__.py``, make a relative import with leading dots, otherwise make
      absolute import.

      - 2

      The bootstrap code will always be made an absolute import without leading
      dots in the entry script.

      - 3

      The bootstrap code will always be made a relative import with leading dots
      in the entry script.

.. include:: _common_definitions.txt
