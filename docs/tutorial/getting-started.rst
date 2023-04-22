=================
 Getting Started
=================

.. highlight:: console

.. contents:: Content
   :depth: 2
   :local:
   :backlinks: top

New to |Pyarmor|? Well, you came to the right place: read this material to quickly get up and running.

What's Pyarmor
==============

Pyarmor is a command-line tool designed for obfuscating Python scripts, binding obfuscated scripts to specific machines, and setting expiration dates for obfuscated scripts.

Key Features:

- **Seamless Replacement**: Obfuscated scripts remain as standard `.py` files, allowing them to seamlessly replace the original Python scripts in most cases.
- **Balanced Obfuscation**: Offers multiple ways to obfuscate scripts to balance security and performance.
- **Irreversible Obfuscation**: Renames functions, methods, classes, variables, and arguments.
- **C Function Conversion**: Converts some Python functions to C functions and compiles them into machine instructions using high optimization options for irreversible obfuscation.
- **Script Binding**: Binds obfuscated scripts to specific machines or sets expiration dates for obfuscated scripts.
- **Themida Protection**: Protects obfuscated scripts using Themida (Windows only).

Installation from PyPI
======================

Pyarmor_ packages are published on the PyPI_. The preferred tool for installing packages from PyPI_ is :command:`pip`. This tool is provided with all modern versions of Python.

On Linux or MacOS, you should open your terminal and run the following command::

    $ pip install -U pyarmor

On Windows, you should open Command Prompt (:kbd:`Win-r` and type :command:`cmd`) and run the same command:

.. code-block:: doscon

    C:\> pip install -U pyarmor

After installation, type :command:`pyarmor --version` on the command prompt. If everything worked fine, you will see the version number for the Pyarmor_ package you just installed.

Not all the platforms are supported, more information check :doc:`../reference/environments`

Obfuscating one script
======================

.. program:: pyarmor gen

Here it's the simplest command to obfuscate one script :file:`foo.py`::

    $ pyarmor gen foo.py

The command ``gen`` could be replaced with ``g`` or ``generate``::

    $ pyarmor g foo.py
    $ pyarmor generate foo.py

This command generates an obfuscated script :file:`dist/foo.py`, which is a valid Python script, run it by Python interpreter::

    $ python dist/foo.py

Check all generated files in the default output path::

    $ ls dist/
    ...    foo.py
    ...    pyarmor_runtime_000000

There is an extra Python package :file:`pyarmor_runtime_000000`, which is required to run the obfuscated script.

Distributing the obfuscated script
----------------------------------

Only copy :file:`dist/foo.py` to another machine doesn't work, instead copy all the files in the :file:`dist/`.

Why? It's clear after checking the content of :file:`dist/foo.py`:

.. code-block:: python

    from pyarmor_runtime_000000 import __pyarmor__
    __pyarmor__(__name__, __file__, ...)

Actually the obfuscaetd script can be taken as normal Python script with dependent package :mod:`pyarmor_runtime_000000`, use it as it's not obfuscated.

.. important::

   Please run this obfuscated in the machine with same Python version and same platform, otherwise it doesn't work. Because :mod:`pyarmor_runtime_000000` has an :term:`extension module`, it's platform-dependent and bind to Python version.

.. note::

   DO NOT install Pyarmor in the :term:`Target Device`, Python interpreter could run the obfuscated scripts without Pyarmor.

Obfuscating one package
=======================

Now let's do a package. :option:`-O` is used to set output path :file:`dist2` different from the default::

    $ pyarmor gen -O dist2 src/mypkg

Check the output::

    $ ls dist2/
    ...    mypkg
    ...    pyarmor_runtime_000000

    $ ls dist2/mypkg/
    ...          __init__.py

All the obfuscated scripts in the :file:`dist2/mypkg`, test it::

    $ cd dist2/
    $ python -C 'import mypkg'

If there are sub-packages, using :option:`-r` to enable recursive mode::

    $ pyarmor gen -O dist2 -r src/mypkg

Distributing the obfuscated package
-----------------------------------

Also it works to copy the whole path :file:`dist2` to another machine. But it's not convience, the better way is using :option:`-i` to generate all the required files inside package path::

    $ pyarmor gen -O dist3 -r -i src/mypkg

Check the output::

    $ ls dist3/
    ...    mypkg

    $ ls dist3/mypkg/
    ...          __init__.py
    ...          pyarmor_runtime_000000

Now everything is in the package path :file:`dist3/mypkg`, just copy the whole path to any target machine.

.. note::

   Comparing current :file:`dist3/mypkg/__init__.py` with above section :file:`dist2/mypkg/__init__.py` to understand more about obfuscated scripts

Expiring obfuscated scripts
===========================

It's easy to set expire date for obfuscated scripts by :option:`-e`. For example, generate obfuscated script with the expire date to 30 days::

    $ pyarmor gen -O dist4 -e 30 foo.py

Run the obfuscated scripts :file:`dist4/foo.py` to verify it::

    $ python dist4/foo.py

It checks network time, make sure your machine is connected to internet.

Let's use another form to set past date ``2020-12-31``::

    $ pyarmor gen -O dist4 -e 2020-12-31 foo.py

Now :file:`dist4/foo.py` should not work::

    $ python dist4/foo.py

If expire date has a leading ``.``, it will check local time other than NTP_ server. For examples::

    $ pyarmor gen -O dist4 -e .30 foo.py
    $ pyarmor gen -O dist4 -e .2020-12-31 foo.py

For this form internet connection is not required in target machine.

Distributing the expired script is same as above, copy the whole directory :file:`dist4/` to target machine.

Binding obfuscated scripts to device
====================================

Suppose got target machine hardware informations::

    IPv4:                        128.16.4.10
    Enternet Addr:               00:16:3e:35:19:3d
    Hard Disk Serial Number:     HXS2000CN2A

Using :option:`-e` to bind hardware information to obfuscated scripts. For example, bind :file:`dist5/foo.py` to enternet address::

    $ pyarmor gen -O dist5 -b 00:16:3e:35:19:3d foo.py

So :file:`dist5/foo.py` only could run in target machine.

It's same to bind IPv4 and serial number of hard disk::

    $ pyarmor gen -O dist5 -b 128.16.4.10 foo.py
    $ pyarmor gen -O dist5 -b HXS2000CN2A foo.py

It's possible to combine some of them. For example::

    $ pyarmor gen -O dist5 -b "00:16:3e:35:19:3d HXS2000CN2A" foo.py

Only both enternet address and hard disk are matched machine could run this obfuscated script.

Distributing scripts bind to device is same as above, copy the whole directory :file:`dist5/` to target machine.

Packaging obfuscated scripts
============================

Remeber again, the obfuscated script is normal Python script, use it as it's not obfuscated.

Suppose package ``mypkg`` structure like this::

    projects/
    └── src/
        └── mypkg/
            ├── __init__.py
            ├── utils.py
            └── config.json

First make output path :file:`projects/dist6` for obfuscated package::

    $ cd projects
    $ mkdir dist6

Then copy package data files to output path::

    $ cp -a src/mypkg dist6/

Next obfuscate scripts to overwrite all the ``.py`` files in :file:`dist6/mypkg`::

    $ pyarmor gen -O dist6 -i src/mypkg

The final output::

    projects/
    ├── README.md
    └── src/
        └── mypkg/
            ├── __init__.py
            ├── utils.py
            └── config.json
    └── dist6/
        └── mypkg/
            ├── __init__.py
            ├── utils.py
            ├── config.json
            └── pyarmor_runtime_000000/__init__.py

Comparing with :file:`src/mypkg`, the only difference is :file:`dist6/mypkg` has an extra sub-package ``pyarmor_runtime_000000``. The last thing is packaging :file:`dist6/mypkg` as your prefer way.

New to Python packaging? Refer to `Python Packaging User Guide`_

.. _Python Packaging User Guide: https://packaging.python.org

Something need to know
======================

There is binary `extension module`_ :mod:`pyarmor_runtime` in extra sub-package ``pyarmor_runtime_000000``, here it's package content::

    $ ls dist6/mypkg/pyarmor_runtime_000000
    ...    __init__.py
    ...    pyarmor_runtime.so

Generally using binary extensions means the obfuscated scripts require :mod:`pyarmor_runtime` be created for different platforms, so they

* only works for platforms which provides pre-built binaries
* may not be compatible with different builds of CPython interpreter
* often will not work correctly with alternative interpreters such as PyPy, IronPython or Jython

For example, when obfuscating scripts by Python 3.8, they can't be run by Python 3.7, 3.9 etc.

Another disadvantage of relying on binary extensions is that alternative import mechanisms (such as the ability to import modules directly from zipfiles) often won't work for extension modules (as the dynamic loading mechanisms on most platforms can only load libraries from disk).

What to read next
=================

There is a complete :doc:`installation <installation>` guide that covers all the possibilities:

* install pyarmor by source
* call pyarmor from Python script
* clean uninstallation

Next is :doc:`obfuscation`. It covers

* using more option to obfuscate script and package
* using outer file to store runtime key
* localizing runtime error messages
* packing obfuscated scripts and protect system packages

And then :doc:`advanced`, some of them are not available in trial pyarmor

* 2 irreversible obfuscation: RFT mode, BCC mode :sup:`pyarmor-pro`
* Customization error handler
* runtime error internationalization
* cross platform, multiple platforms and multiple Python version

Also you may be instersting in this guide :doc:`../how-to/security`

How the documentation is organized
==================================

|Pyarmor| has a lot of documentation. A high-level overview of how it's organized will help you know where to look for certain things:

* :doc:`Part 1: Tutorials <../part-1>` now you're reading.

* :doc:`Part 2: How To <../part-2>` guides are recipes. They guide you through the steps involved in addressing key problems and use-cases. They are more advanced than tutorials and assume some knowledge of how |Python| works.

* :doc:`Part 3: References <../part-3>` guides contain key concepts, man page, configurations and other aspects of |Pyarmor| machinery.

* :doc:`Part 4: Topics <../part-4>` guides insight into key topics and provide useful background information and explanation. They describe how it works and how to use it but assume that you have a basic understanding of key concepts.

* :doc:`Part 5: Licneses <../licenses>` describes EULA of |Pyarmor|, the different |Pyarmor| licenses and how to purchase |Pyarmor| license.

Looking for specific information? Try the :ref:`genindex`, or :ref:`the detailed table of contents <mastertoc>`.

.. include:: ../_common_definitions.txt
