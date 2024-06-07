.. highlight:: console

==============================
 Using Pyarmor in CI Pipeline
==============================

Pyarmor could be used in CI/CD pipeline directly, except for Group License which may only work on some special runners like Self-Host runner.

But it's recommend to use Pyarmor in CI/CD pipeline by another way. First obfuscate the scripts by a few runner and store them to another branch like `master-obf`, then all the other runners need not register Pyarmor, but continue the rest pipeline based on this branch like before. It also could solve this problem: Basic/Pro License only allows 100 runs in 24 hours.

The test-project hierarchy is as follows::

    $ tree test-project

    test-project
    └── src
        ├── main.py
        ├── utils.py
        └── parent
            ├── child
            │   └── __init__.py
            └── __init__.py

Suppose it locates at `https://github.com/dashingsoft/test-project`

The first runner will obfuscate the scripts and store them into another branch. Here it's an example bash script:

.. code-block:: bash

    $ git clone https://github.com/dashingsoft/test-project

    $ pip install pyarmor
    $ pyarmor reg /path/to/pyarmor-regfile-5068.zip

    # Create new branch
    # git checkout -B master-obf

    # So that the original script will be replaced directly by linking the source to output
    $ ln -s test-project dist

    # Obfuscate the script to "dist", which is save as "test-project"
    # So "dist/src/main.py" is same as "test-project/src/main.py"
    $ pyarmor gen -O dist -r --platform windows.x86_64,linux.x86_64,darwin.x86_64 test_project/src

    # Add runtime package to this branch
    $ git add -f test_project/pyarmor_runtime_5068/*

    # Commit the results
    $ git commit -m'Build obfuscated scripts' .

    # Push new branch to remote server
    $ git push -u origin master-obf

For all the other runners, they need not install Pyarmor, just pull branch `master-obf`, then work as before.

.. include:: ../_common_definitions.txt
