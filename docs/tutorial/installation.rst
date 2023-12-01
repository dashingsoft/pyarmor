==============
 Installation
==============

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

Prerequisite
============

Pyarmor_ requires shared Python runtime library and C library.

In Linux, please install shared Python runtime library when needed. For example, install Python 3.10 shared runtime library::

    $ apt install libpython3.10

In Darwin, make sure the file ``@rpath/lib/libpythonX.Y.dylib`` exists. ``X.Y`` stands for  Python major and minor version.

For example::

    @rpath/lib/libpython3.10.dylib

``@rpath`` is one of:

- @executable_path/..
- @loader_path/..
- /System/Library/Frameworks/Python.framework/Versions/3.10
- /Library/Frameworks/Python.framework/Versions/3.10

If there is no this file, please install necessary packages or re-build Python with enable shared option, or using `install_name_tool` to adapt current Python installation, refer to :doc:`../question`.

.. _install-pypi:

Installation from PyPI
======================

Pyarmor_ packages are published on the PyPI_. The preferred tool for installing packages from PyPI_ is :command:`pip`. This tool is provided with all modern versions of Python.

On Linux or MacOS, you should open your terminal and run the following command::

    $ pip install pyarmor

On Windows, you should open Command Prompt (:kbd:`Win-r` and type :command:`cmd`) and run the same command:

.. code-block:: doscon

    C:\> pip install pyarmor

After installation, type :command:`pyarmor --version` on the command prompt. If everything worked fine, you will see the version number for the Pyarmor_ package you just installed.

If you need generate obfuscated scripts to run in other platforms, install the corresponding packages::

    $ pip install pyarmor.cli.core.windows
    $ pip install pyarmor.cli.core.themida
    $ pip install pyarmor.cli.core.linux
    $ pip install pyarmor.cli.core.darwin
    $ pip install pyarmor.cli.core.freebsd
    $ pip install pyarmor.cli.core.android

Not all the platforms are supported, more information check :doc:`../reference/environments`

.. note::

    If only using Pyarmor 8+ features, installing :mod:`pyarmor.cli` instead :mod:`pyarmor`, could significantly decrease downloaded file size. For example::

        $ pip install pyarmor.cli

Installed command
-----------------

* :program:`pyarmor` is the main command to do everything. See :doc:`../reference/man`.
* :program:`pyarmor-7` is used to call old commands, it equals bug fixed Pyarmor 7.x
* :program:`pyarmor-auth` used by Group License to support unlimited docker containers

Start Pyarmor by Python interpreter
-----------------------------------

:program:`pyarmor` is same as the following command::

    $ python -m pyarmor.cli

Using virtual environments
==========================

When installing Pyarmor_ using :command:`pip`, use *virtual environments* which could isolate the installed packages from the system packages, thus removing the need to use administrator privileges.  To create a virtual environment in the ``.venv`` directory, use the following command::

    $ python -m venv .venv

You can read more about them in the `Python Packaging User Guide`_.

.. _Python Packaging User Guide: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment

Installation from source
========================

.. deprecated:: 8.2.9

You can install Pyarmor_ directly from a clone of the `Git repository`__.  This can be done either by cloning the repo and installing from the local clone, on simply installing directly via :command:`git`::

    $ git clone https://github.com/dashingsoft/pyarmor
    $ cd pyarmor
    $ pip install .

You can also download a snapshot of the Git repo in either `tar.gz`__ or `zip`__ format.  Once downloaded and extracted, these can be installed with :command:`pip` as above.

.. note::

   Do not use this method, it may not work since v8.2.9

__ https://github.com/dashingsoft/pyarmor
__ https://github.com/dashingsoft/pyarmor/archive/master.tar.gz
__ https://github.com/dashingsoft/pyarmor/archive/master.zip

Installation in offline device
==============================

All the Pyarmor pacakges are published in the PyPI_, download them and copy to offlice device.

First install :mod:`pyarmor.cli.core`

Next install :mod:`pyarmor` or :mod:`pyarmor.cli`

For example, install offline Pyarmor 8.2.9 in Linux for Python 3.10::

    $ pip install pyarmor.cli.core-3.2.9-cp310-none-manylinux1_x86_64.whl
    $ pip install pyarmor-8.2.9.zip

In Android or FreeBSD, there is no wheel in :mod:`pyarmor.cli.core`, it should install source distribution and extra package :mod:`pyarmor.cli.core.android` or :mod:`pyarmor.cli.core.freebsd`. For example, install offline Pyarmor in Android for Python 3.10::

    $ pip install pyarmor.cli.core-3.2.9.zip
    $ pip install pyarmor.cli.core.android-3.2.9-cp310-none-any.whl
    $ pip install pyarmor-8.2.9.zip

If need cross platform obfuscation, also install the corresponding platform package

- :mod:`pyarmor.cli.core.freebsd`
- :mod:`pyarmor.cli.core.android`
- :mod:`pyarmor.cli.core.windows`
- :mod:`pyarmor.cli.core.themida`
- :mod:`pyarmor.cli.core.linux`
- :mod:`pyarmor.cli.core.alpine`
- :mod:`pyarmor.cli.core.darwin`

For example, if need Themida protection, then install themida package::

    $ pip install pyarmor.cli.themida-3.2.9-cp310-none-any.whl

In Linux to generate for Windows, install windows package::

    $ pip install pyarmor.cli.windows-3.2.9-cp310-none-any.whl

If only using Pyarmor 8+ features, it's recommend to install :mod:`pyarmor.cli` instead :mod:`pyarmor`, the former file size is significantly less than the latter. For example::

    $ pip install pyarmor.cli-8.2.9.zip

Termux issues
=============

In Termux, after installation it need patch extensions. For example::

    $ patchelf --add-needed /data/data/com.termux/files/usr/lib/python3.11/site-packages/pyarmor/cli/core/android/aarch64/pytransform3.so
    $ patchelf --add-needed /data/data/com.termux/files/usr/lib/python3.11/site-packages/pyarmor/cli/core/android/aarch64/pyarmor_runtime.so

Sometimes, it need set runpath too. For example::

    $ patchelf --set-rpath /data/data/com.termux/files/usr/lib /path/to/{pytransform3,pyarmor_runtime}.so

Otherwise it will raise error `dlopen failed: cannot locate symbol "PyFloat_Type"`

Run Pyarmor from Python script
==============================

Create a script :file:`tool.py`, pass arguments by yourself

.. code-block:: python

    from pyarmor.cli.__main__ import main_entry

    args = ['gen', 'foo.py']
    main_entry(args)

Run it by Python interpreter::

    $ python tool.py

Clean uninstallation
====================

Run the following commands to make a clean uninstallation::

    $ pip uninstall pyarmor
    $ pip uninstall pyarmor.cli.core

    $ pip uninstall pyarmor.cli.runtime
    $ pip uninstall pyarmor.cli.core.windows
    $ pip uninstall pyarmor.cli.core.themida
    $ pip uninstall pyarmor.cli.core.linux
    $ pip uninstall pyarmor.cli.core.darwin
    $ pip uninstall pyarmor.cli.core.freebsd
    $ pip uninstall pyarmor.cli.core.android

    $ rm -rf ~/.pyarmor
    $ rm -rf ./.pyarmor

.. note::

   The path ``~`` may be different when logging by different user. ``$HOME`` is home path of current logon user, check the environment variable ``HOME`` to get the real path.

.. highlight:: default

.. Most Windows users do not have Python installed by default, so we begin with the installation of Python itself.  To check if you already have Python installed, open the *Command Prompt* (:kbd:`Win-r` and type :command:`cmd`). Once the command prompt is open, type :command:`python --version` and press Enter.  If Python is installed, you will see the version of Python printed to the screen.  If you do not have Python installed, refer to the `Hitchhikers Guide to Python's`__ Python on Windows installation guides. You must install `Python 3`__.

   Once Python is installed, you can install Sphinx using :command:`pip`.  Refer to the :ref:`pip installation instructions <install-pypi>` below for more information.

   __ https://docs.python-guide.org/
   __ https://docs.python-guide.org/starting/install3/win/


.. include:: ../_common_definitions.txt
