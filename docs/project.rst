.. _using project:

Using Project
=============

Project is a folder include its own configuration file, which used to
manage obfuscated scripts.

There are several advantages to manage obfuscated scripts by Project:

* Increment build, only updated scripts are obfuscated since last build
* Filter obfuscated scripts in the project, exclude some scripts
* More convenient to manage obfuscated scripts

Managing Obfuscated Scripts With Project
----------------------------------------

Use command ``init`` to create a project::

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

Obfuscate all the scripts in this project::

    pyarmor build

Exclude the :file:`dist`, :file:`test`, the `.py` files in these
folder will not be obfuscated::

    pyarmor config --manifest "include *.py, prune dist, prune test"

Force rebuild::

    pyarmor build --force

Run obfuscated script::

    cd dist
    python pybench.py

After some scripts changed, just run ``build`` again::

    cd projects/pybench
    pyarmor build

.. _obfuscating scripts with different modes:

Obfuscating Scripts With Different Modes
----------------------------------------

Configure mode to obfuscate scripts::

    pyarmor config --obf-mod=1 --obf-code=0

Obfuscating scripts in new mode::

    pyarmor build -B


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

    Generally it's absolute path.

* manifest

    A string specifies files to be obfuscated, same as MANIFEST.in of
    Python Distutils, default value is::

        global-include *.py

    It means all files anywhere in the `src` tree matching.

    Multi manifest template commands are spearated by comma, for
    example::

        global-include *.py, exclude __mainfest__.py, prune test

    Refer to
    https://docs.python.org/2/distutils/sourcedist.html#commands

* is_package

    Available values: 0, 1, None

    When it's set to 1, the basename of `src` will be appended to
    `output` as the final path to save obfuscated scripts, and
    runtime files are still in the path `output`

    When init a project and no `--type` specified, it will be set to
    1 if there is `__init__.py` in the path `src`, otherwise it's
    None.

* disable_restrict_mode

    Available values: 0, 1, None

    When it's None or 0, obfuscated scripts can not be imported from
    outer scripts.

    When it's set to 1, it the obfuscated scripts are allowed to be
    imported by outer scripts.

    By default it's set to 0.

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

    Filename of project capsule. It's relative to project path if it's
    not absolute path.

* obf_module_mode [DEPRECRATED]

    How to obfuscate whole code object of module:

        - none

        No obfuscate

        - des

        Obfuscate whole code object by DES algorithm

        The default value is `des`

* obf_code_mode [DEPRECRATED]

    How to obfuscate byte code of each code object:

        - none

        No obfuscate

        - des

        Obfuscate byte-code by DES algorithm

        - fast

        Obfuscate byte-code by a simple algorithm, it's faster than
        DES

        - wrap

        The wrap code is different from `des` and `fast`. In this
        mode, when code object start to execute, byte-code is
        restored. As soon as code object completed execution,
        byte-code will be obfuscated again.

    The default value is `wrap`.

* obf_code

  How to obfuscate byte code of each code object:

        - 0

        No obfuscate

        - 1

        Obfuscate each code object by default algorithm

  Refer to :ref:`Obfuscating Code Mode`

* wrap_mode

  Available values: 0, 1, None

  Whether to wrap code object with `try..final` block.

  Refer to :ref:`Wrap Mode`

* obf_mod

  How to obfuscate whole code object of module:

        - 0

        No obfuscate

        - 1

        Obfuscate byte-code by DES algorithm

  Refer to :ref:`Obfuscating Module Mode`

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
    `_pytransform`. The default value is None, it means it's in the
    same path of :file:`pytransform.py`.

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

.. include:: _common_definitions.txt
