.. highlight:: console

==============================
 Using Pyarmor in CI Pipeline
==============================

Pyarmor could be used in CI/CD pipeline directly, but there are some limitions:

- Group License generally doesn't work in CI/CD pipeline
- It only allows 3 runs in 1 minutes for Basic/Pro license
- It only allows 100 runs in 24 hours for Basic/Pro license

Pyarmor recommends to use Pyarmor in CI/CD pipeline by this way:

- First obfuscate the scripts by a few runner and store them to another branch like `master-obf`
- Then all the other runners continue the rest pipeline based on this branch like before

Because only first step runners need register Pyarmor, so it could solve run limitions in most of cases.

Suppose test-project locates at `https://github.com/dashingsoft/test-project`, the directory tree as follows::

    $ tree test-project

    test-project
    └── src
        ├── main.py
        ├── utils.py
        └── parent
            ├── child
            │   └── __init__.py
            └── __init__.py

The first runner will obfuscate the scripts and store them into another branch. Here it's an example bash script:

.. code-block:: bash

    $ git clone https://github.com/dashingsoft/test-project

    $ pip install pyarmor
    $ pyarmor reg /path/to/pyarmor-regfile-5068.zip

    # Create new branch
    # git checkout -B master-obf

    # Create output path "dist" link to project path
    $ ln -s test-project dist

    # Obfuscate the script to "dist", which is same as "test-project"
    # So "dist/src/main.py" is same as "test-project/src/main.py"
    $ pyarmor gen -O dist -r --platform windows.x86_64,linux.x86_64,darwin.x86_64 test_project/src

    # Add runtime package to this branch
    $ git add -f test_project/pyarmor_runtime_5068/*

    # Commit the results
    $ git commit -m'Build obfuscated scripts' .

    # Push new branch to remote server
    $ git push -u origin master-obf

For all the other runners, they need not install Pyarmor, just checkout branch `master-obf`, and work as before.

.. include:: ../_common_definitions.txt
