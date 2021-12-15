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

``pyarmor.build_meta`` also supports pip configuration ``pyarmor.advanced`` to
build a pyarmored wheel with :ref:`Super Mode`.

First run `pip config <https://pip.pypa.io/en/stable/cli/pip_config/>`_ ::

    pip config set pyarmor.advanced 2

Then::

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

It only implements basic functions, pull request for this feature is welcomed
if there is any further requirement.

.. include:: _common_definitions.txt
