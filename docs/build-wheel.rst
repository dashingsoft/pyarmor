.. _build pyarmored wheel:

Build Pyarmored Wheel
=====================

Modern Python packages can contain a `pyproject.toml
<https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/>`_ file,
first introduced in PEP 518 and later expanded in PEP 517, PEP 621 and
PEP 660. This file contains build system requirements and information, which are
used by pip to build the package.

Since v7.2.0, pyarmor could be as PEP 517 backend to build a pyarmored wheel
based on `setuptools.build_meta`.

Here an example package structure::

  mypkg/
      setup.py
      pyproject.toml
      src/
          __init__.py
          ...

The `pyproject.toml` may like this::

    [build-system]
    requires = ["setuptools", "wheel"]
    build-backend = "setuptools.build_meta"

First make sure backend ``setuptools.build_meta`` works by running the following
commands to build wheel. If it doesn't work, please learn the related knowledges
`pip wheel <https://pip.pypa.io/en/stable/cli/pip_wheel/>`_ and make it works::

    cd mypkg/
    pip wheel .

Now edit ``pyproject.toml``, change build backend to ``pyarmor.build_meta``::

    [build-system]
    requires = ["setuptools", "wheel", "pyarmor>7.2.0"]
    build-backend = "pyarmor.build_meta"

Build a pyarmored wheel by same commands::

    cd mypkg/
    pip wheel .

Or build a pyarmored wheel with :ref:`Super Mode` by setting extra obfuscation
options in environment variable ``PIP_PYARMOR_OPTIONS``::

    cd mypkg/

    # In Windows
    set PIP_PYARMOR_OPTIONS=--advanced 2
    pip wheel .

    # In Linux or MacOs
    PIP_PYARMOR_OPTIONS="--advanced 2" pip wheel .

Since v7.2.4 pip configuration ``pyarmor.advanced`` also could be used to build
a pyarmored wheel with :ref:`Super Mode`.

First run `pip config <https://pip.pypa.io/en/stable/cli/pip_config/>`_ ::

    pip config set pyarmor.advanced 2

Then run the building command::

    cd mypkg/
    pip wheel .

Removing this configuration by this way::

    pip config unset pyarmor.advanced

How does it work
----------------

The Python scripts obfuscated by pyarmor are same as normal Python scripts with
an extra dynamic library or extension. So ``pyarmor.build_meta`` just does

1. Call ``setuptools.build_meta`` to build wheel
2. Unpack wheel
3. Obfuscate all the .py files in the unpacking path
4. Append the pyarmor runtime files to wheel file ``RECORD``
5. Repack the patched wheel

About the details, please refer to function `bdist_wheel` in the
`pyarmor/build_meta.py
<https://github.com/dashingsoft/pyarmor/blob/master/src/build_meta.py#L86>`_

It's a simple script, and only implements basic functions, if something is wrong
with the script, do it manully or write a shell script as the following steps:

1. Build wheel with original package
2. Unpack this wheel to temporary path by this command::
     python3 -m wheel unpack --dest /path/to/temp xxx.whl
3. Obfuscate the scripts by `pyarmor obfuscate`, then overrite all the `.py`
   files in the unpack path with the obfuscated ones.
4. Append the pyarmor runtime files to wheel file ``RECORD``, search it in the
   unpack path, the format please refer to the existing items
5. Repack the patched wheel::
     python3 -m wheel pack /path/to/temp

Pull request for this feature is welcomed if there is any further requirement.

.. important::

    Build pyarmored wheel is a helper function, there is no more support for
    this.

    If you don't know how to build a wheel from a package which includes binary
    file, please learn it by yourself, then take the obfuscated scripts as the
    normal scripts, refer to :ref:`Key Points to Use Obfuscated Scripts`.

.. include:: _common_definitions.txt
