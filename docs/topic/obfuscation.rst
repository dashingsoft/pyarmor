========================
Insight Into Obfuscation
========================

.. highlight:: bash

Filter scripts by finder
========================

Script ext is not .py, list it in command line. For example, ``my.config`` is a python script but not standard extension name::

  pyarmor gen main.py my.config

To include special script in package. For example::

  pyarmor cfg finder:includes="lib/my.config"
  pyamor gen -r lib

To exclude "test" and all the path "test"::

  pyarmor cfg finder:excludes + "*/test"

Include data files, these data file will be copied to output::

  pyarmor cfg finder:data_files="lib/readme.txt"
  pyamor gen -r lib

It uses :mod:`fnmatch` to match pattern. For example, the test-project hierarchy is as follows::

    $ tree test-project

    test-project
    ├── MANIFEST.in
    ├── pyproject.toml
    ├── setup.cfg
    └── src
        └── parent
            ├── child
            │   └── __init__.py
            └── __init__.py

Include data files, these data file will be copied to output::

    $ cd test-project
    $ pyarmor cfg finder:exclude + "*__pycache__ */test.py"
    $ pyamor gen -r src/parent

The following tests are executed:

.. code-block:: python

    fnmatch("src/parent/__init__.py", "*__pycache__")
    fnmatch("src/parent/__init__.py", "*/test.py")

    fnmatch("src/parent/child", "*__pycache__")
    fnmatch("src/parent/child", "*/test.py")

    fnmatch("src/parent/child/__init__.py", "*__pycache__")
    fnmatch("src/parent/child/__init__.py", "*/test.py")

.. include:: ../_common_definitions.txt
