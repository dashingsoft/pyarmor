.. highlight:: console

==============================
 Using Pyarmor in CI Pipeline
==============================

**Trial Version** could be used in CI/CD pipeline by one step::

    pip install pyarmor

For :term:`Pyarmor Basic` and :term:`Pyarmor CI` License

- Refer to :ref:`initial registration`, first got :term:`registration file` like ``pyarmor-regfile-xxxx.zip``
- In local device run the following command to request one CI regfile ``pyarmor-ci-xxxx.zip``::

      $ pyarmor reg -C pyarmor-regfile-xxxx.zip

  Check CI license info in local machine::

      $ pyarmor reg pyarmor-ci-xxxx.zip

- In CI/CD pipeline, add 2 steps to register Pyarmor by CI regfile::

      # Please replace "9.X.Y" with current Pyarmor version
      pip install pyarmor=9.X.Y
      pyarmor reg pyarmor-ci-xxxx.zip

- Check registration information in CI/CD pipeline::

      pyarmor -v

Notes

* Do not request CI regfile in CI/CD pipeline
* CI regfile ``pyarmor-ci-xxxx.zip`` will be expired about in 360 days
* CI regfile may not work in future Pyarmor version
* Once CI regfile doesn't work, require new one
* One license can request <= 100 CI regfiles

.. important::

   In CI/CD pipeline, each run will send license and docker information to Pyarmor License Server, excessive requests or requests beyond normal usage may be rejected by Pyarmor License Server

   It's not allowed to install Pyarmor in your customer's docker image

:term:`Pyarmor Pro` and :term:`Pyarmor Group` License can't be used in CI/CD pipeline directly, but there is one workaround

- First obfuscate the scripts in local device and store them to another branch like `master-obf`
- Then in CI/CD pipeline to check this new branch

Here is an example, suppose test-project locates at `https://github.com/dashingsoft/test-project`, the directory tree as follows::

    $ tree test-project

    test-project
    └── src
        ├── main.py
        ├── utils.py
        └── parent
            ├── child
            │   └── __init__.py
            └── __init__.py

In local device the scripts are obfuscated and are stored into another branch:

.. code-block:: bash

    $ git clone https://github.com/dashingsoft/test-project

    $ pip install pyarmor
    $ pyarmor reg /path/to/pyarmor-regfile-5068.zip

    # Create new branch
    $ git checkout -B master-obf

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

In CI/CD pipeline, it need not install Pyarmor, just checkout branch `master-obf`, and work as before.

.. include:: ../_common_definitions.txt
