.. highlight:: console

==============================
 Using Pyarmor in CI Pipeline
==============================

Pyarmor could be used in CI/CD pipeline directly, but there are some limitions:

- Group License generally doesn't work in CI/CD pipeline
- It only allows 3 runs in 1 minutes for Basic/Pro license
- It only allows 100 runs in 24 hours for Basic/Pro license

  - If need more than 100 runs, refer to :ref:`Using Pyarmor CI Quota`

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

For all the other runners, they need not install Pyarmor, just checkout branch `master-obf`, and work as before.

.. _using pyarmor ci quota:

Using Pyarmor CI Quota
======================

Pyarmor CI Quota is one experimental solution for this issue:

- Basic/Pro license only allow 100 runs in CI/CD pipeline in 24 hours

Each ci quota allows 2,000 extra runs after 100 runs in 24 hours.

.. list-table:: Table-1. Pyarmor CI Quota Price
   :header-rows: 1

   * - Extra Runs
     - Net Price($)
     - Remark
   * - 2,000
     - 10
     -

1. First check your license no. by `pyarmor -v`::

     $ pyarmor -v
     Pyarmor 8.5.11 (pro), 005068, btarmor

     License Type    : pyarmor-pro
     License No.     : pyarmor-vax-005068
     License To      : Tester
     License Product : btarmor
     ...

2. Then purchasing Pyarmor CI Quota in MyCommerce website

   https://order.mycommerce.com/product?vendorid=200089125&productid=301123145

3. When placing order, fill "License to" with Pyarmor License No. For example, ``pyarmor-vax-005068``

4. Once payment is completed, this license will has one Pyarmor CI Quota

   If no more than 100 runs in 24 hours, it doesn't consume CI Quota.

.. list-table:: Table-2. Pyarmor CI Quota Usage Example
   :header-rows: 1

   * - Date
     - Runs in CI/CD pipeline
     - Used Quota
     - Left Quota
     - Remark
   * - 2024-05-01
     -
     -
     - 2000
     - Init quota
   * - 2024-05-02
     - 80
     - 0
     - 2000
     -
   * - 2024-05-03
     - 120
     - 20
     - 1080
     -
   * - 2024-05-04
     - 160
     - 60
     - 1020
     -
   * - 2024-05-05
     - 90
     - 0
     - 1020
     -
   * - 2024-05-06
     - 101
     - 1
     - 1019
     -

5. When ci quota is exhausted, it need purchase new Pyarmor CI Quota

.. include:: ../_common_definitions.txt
