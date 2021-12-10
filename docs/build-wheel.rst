.. _build pyarmored wheel:

Build pyarmored wheel
=====================

Modern Python packages can contain a `pyproject.toml
<https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/>`_ file,
first introduced in PEP 518 and later expanded in PEP 517, PEP 621 and
PEP 660. This file contains build system requirements and information, which are
used by pip to build the package.

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

First of all, make sure this package could be built by PEP 517 with backend
`setuptools.build_meta`. If it doesn't work, please learn the related knowledges
and make it works::

    cd mypkg/
    pip wheel .

The python scripts obfuscated by pyarmor are same as normal python scripts with
an extra dynamic library or extension. Since v7.2.0, pyarmor could be as PEP 517
backend to build a pyarmored wheel based on `setuptools.build_meta`.

Change ``pyproject.toml`` to this::

    [build-system]
    requires = ["setuptools", "wheel", "pyarmor>=7.2.0"]
    build-backend = "pyarmor.build_meta"

Now build a pyarmored wheel by same commands::

    cd mypkg/
    pip wheel .

Or build a pyarmored wheel with :ref:`Super Mode` by passing extra settings to
pip ``--global-option``::

    cd mypkg/
    pip wheel --global-option="--super-mode" .

.. include:: _common_definitions.txt
