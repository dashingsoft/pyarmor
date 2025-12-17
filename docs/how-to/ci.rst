.. highlight:: console

==============================
 Using Pyarmor in CI Pipeline
==============================

There are 2 ways to use Pyarmor in CI/CD pipeline:

- Direct way, it's simple, but only works for Trial, Basic and CI license, and there is rate limits
- Indirect way, it need change the original build workflow, but works for any type license

Direct Way
==========

**Trial Version** could be used in CI/CD pipeline by one step::

    pip install pyarmor

For :term:`Pyarmor Basic` and :term:`Pyarmor CI` License

- Refer to :ref:`initial registration`, first got :term:`registration file` like ``pyarmor-regfile-xxxx.zip``
- In local device run the following command to request one CI regfile ``pyarmor-ci-xxxx.zip``::

      $ pyarmor reg -C pyarmor-regfile-xxxx.zip

  Check CI license info in local machine::

      $ pyarmor --home temp reg pyarmor-ci-xxxx.zip

- In CI/CD pipeline, add 2 steps to register Pyarmor by CI regfile::

      # Please replace "9.X.Y" with current Pyarmor version
      pip install pyarmor=9.X.Y
      pyarmor reg pyarmor-ci-xxxx.zip

  Check registration information in CI/CD pipeline::

      pyarmor -v

Notes

* Do not request CI regfile in CI/CD pipeline
* CI regfile ``pyarmor-ci-xxxx.zip`` will be expired about in 360 days
* CI regfile may not work in future Pyarmor version
* Once CI regfile doesn't work, require new one
* One license can request <= 100 CI regfiles

.. note::

   In GitHub Action, it need one extra step, otherwise `CI license only works in CI/CD pipeline`

   1. For Ubuntu, add this step::

        - run: sudo mv /dev/disk /dev/disk-none

   2. For Darwin, add this step::

        - run: sudo mv /dev/rdisk0 /dev/rdisk0-none

   Refer to this thread `Error when using CI license in CI pipeline <https://github.com/dashingsoft/pyarmor/discussions/2004>`_

.. important::

   In CI/CD pipeline, each run `pyarmor gen` will send license and docker information to Pyarmor License Server, excessive requests or requests beyond normal usage may be rejected by Pyarmor License Server. Generally do not exceed any of these rate limits:

   - 1 run per second
   - 100 runs per hour
   - 1,000 runs per day
   - 10,000 runs per month

   If exceeds any of these limitions, please check the section `High frequency use solution`

.. important::

   It's not allowed to install and register Pyarmor in your customer's docker image, Pyarmor CI license is only be used in the build device.

When need to request new CI regfile
-----------------------------------

In the following cases, it need request one new CI regfile

- After :term:`Pyarmor CI` License is expired, all the previous CI regfiles don't work any longer. After the renewal is successful, it need request new CI regfile ``pyarmor-ci-N.zip``
- After Pyarmor is upgrade one new major/minor version, the old CI regfile may not work in the latest version (but it still works with old Pyarmor version). It need request one new CI regfile by new version. Note that the patch number has no effect for this case, for example, from v9.1.3 to v9.1.8, nothing changed.

High frequency use solution
---------------------------

.. versionadded:: 9.2.0

If many `pyarmor gen` commands are used in one workflow, try to merge them to one

For example::

    # Old workflow: there are 3 "pyarmor gen"
    pyarmor gen -R /path/to/package1
    pyarmor gen -R /path/to/package2
    pyarmor gen -R /path/to/package3

    # New workflow: merge 3 to one
    pyarmor gen -R /path/to/package1 /path/to/package2 /path/to/package2

Or create one Python script to execute all pyarmor commands in one process

For example, create one script `batch.py`:

.. code-block:: python

    import os
    import shlex

    from pyarmor.cli.__main__ import main_entry as pyarmor_run

    # Do not run `pyarmor reg pyarmor-ci-XXXX.zip` in the script

    # Run command: pyarmor gen -R /path/to/package1
    pyarmor_run(['gen', '-R', '/path/to/package1'])

    # Or more like shell command to run: pyarmor gen -R /path/to/package2
    cmdlist = shlex.split("pyarmor gen -R /path/to/package2")
    pyarmor_run(cmdlist[1:])

    # Or change path
    os.chdir('/path/to/other')

    # Execute any other pyarmor command
    cmdlist = shlex.split("pyarmor gen key -e 30")
    pyarmor_run(cmdlist[1:])

Then execute it in the workflow::

    $ pyarmor reg pyarmor-ci-8000.zip
    $ python3 batch.py

If merge solution doesn't work, or you don't want change the original workflow, it need request more quota.

Request More Quota
~~~~~~~~~~~~~~~~~~

The free quota is 10, 000 runs per month, exceed free quota, it need extra fees:

- 100,000 per month, extra fees: $10 for one year
- 200,000 per month, extra fees: $20 for one year
- 300,000 per month, extra fees: $30 for one year
- ...

The steps to request more quota

1. Send request to Pyarmor Team (pyarmor@163.com)

   Please provide the project information, web link, etc. Pyarmor team only use these information for internal review.

   And the quota per month. For example, 100, 000 per month.

2. Pyarmor Team send you PayPal invoice of extra fees.

   For example, if you request quota is 100, 000 per month, Pyarmor team will send you $10 invoice. One year later, when this CI license is expired and need renew, Pyarmor Team will send you $90 + $10 = $100 invoice

3. After invoice is paid, Pyarmor Team will send you notification email

4. You need request one new CI regfile with Pyarmor 9.2+

   Only Pyarmor 9.2+ support this feature.

Indirect Way
============

:term:`Pyarmor Pro` and :term:`Pyarmor Group` License can't be used in CI/CD pipeline directly, but this works

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
