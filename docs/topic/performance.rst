========================
Security and Performance
========================

.. highlight:: console

.. program:: pyarmor gen

**About Security**

Pyarmor focus on protecting Python scripts, by serval irreversible obfuscation methods, now Pyarmor make sure the obfuscated scripts can't be restored by any way.

Pyarmor provides rich options to obfuscate scripts to balance security and performance. If anyone announces he could broken pyarmor, please try a simple script with different security options, refer to :doc:`../how-to/security`. If any irreversible obfusation could be broken, report this security issue to |Contact|. Do not paste any hack link in pyarmor project.

However Pyarmor isn't good at memory protection and anti-debug. Generally even debugger tracing binary extension ``pyarmor_runtime`` could not help to restore obfuscated scripts, but it may bypass runtime key verification.

If you care about runtime memory data protection and anti-debug, check :doc:`../how-to/protection`

**About Performance**

Though the highest security could protect Python scripts from any hack method, but it may reduce performance. In most of cases, we need pick the right options to balance security and performance.

Here we test some options to understand their impact on performace. All the following tests use 2 scripts ``benchmark.py`` and ``testben.py``. Note that the test results are different even run same test script in same machine twice, not speak of different test script in different machine. So the test data in these tables are only guideline, not exact.

The content of ``benchmark.py``

.. code-block:: python

    import sys


    class BenTest(object):

        def __init__(self):
            self.a = 1
            self.b = "b"
            self.c = []
            self.d = {}


    def foo():
        ret = []
        for i in range(100000):
            ret.extend(sys.version_info[:2])
            ret.append(BenTest())
        return len(ret)


The content of ``testben.py``

.. code-block:: python

    import benchmark
    import sys
    import time


    def metric(func):
        if not hasattr(time, 'process_time'):
            time.process_time = time.clock

        def wrap(*args, **kwargs):
            t1 = time.process_time()
            result = func(*args, **kwargs)
            t2 = time.process_time()
            print('%-16s: %10.3f ms' % (func.__name__, ((t2 - t1) * 1000)))
            return result
        return wrap


    def test_import():
        t1 = time.process_time()
        import benchmark2 as m2
        t2 = time.process_time()
        print('%-16s: %10.3f ms' % ('test_import', ((t2 - t1) * 1000)))
        return m2


    @metric
    def test_foo():
        benchmark.foo()


    if __name__ == '__main__':
        print('Python %s.%s' % sys.version_info[:2])
        test_import()
        test_foo()

**Different Python Version Performance**

Frist obfuscate the scripts with default options, run it in different Python version, compare the elapase time with original scripts.

In order to test the difference without and with ``__pycache__``, run scripts twice.

There are 3 check points:

1. ``Import fresh module`` without ``__pycache__``
2. ``Import module 2nd`` with ``__pycache__``
3. ``Run function "foo"``, an obfuscated class is called 10,000 times

Here are test steps::

    $ rm -rf dist __pycache__

    $ cp benchmark.py benchmark2.py
    $ python testben.py

    Python 3.7
    test_import     :   1.303 ms
    test_foo        : 250.360 ms

    $ python testben.py

    Python 3.7
    test_import     :   0.290 ms
    test_foo        : 252.273 ms

    $ pyarmor gen testben.py benchmark.py benchmark2.py
    $ python dist/testben.py

    Python 3.7
    test_import     :   0.907 ms
    test_foo        : 311.076 ms

    $ python dist/testben.py

    Python 3.7
    test_import     :   0.454 ms
    test_foo        : 359.138 ms

.. table:: Table-1. Pyarmor Permormace with Python Version
   :widths: auto

   ==============  =========  =========  =========  =========  =========  =========
   Time (ms)       Import fresh module   Import module 2nd     Run function "foo"
   --------------  --------------------  --------------------  --------------------
   Python          Origin     Pyarmor    Origin     Pyarmor    Origin     Pyarmor
   ==============  =========  =========  =========  =========  =========  =========
   3.7             1.303      0.907      0.290      0.454      252.2      311.0
   3.8             1.305      0.790      0.286      0.338      272.232    295.973
   3.9             1.198      1.681      0.265      0.449      267.561    331.668
   3.10            1.070      1.026      0.408      0.300      281.603    322.608
   3.11            1.510      0.832      0.464      0.616      164.104    289.866
   ==============  =========  =========  =========  =========  =========  =========

**RFT Mode Performance**

RFT mode should be same fast as original scripts.

Here we compare RFT mode with default options, the test data is got by this way.

First obfuscate scripts with default options, then run it.

Then obfuscate scritps with RFT mode, and run it again::

    $ rm -rf dist
    $ pyarmor gen testben.py benchmark.py benchmark2.py
    $ python dist/testben.py

    $ rm -rf dist
    $ pyarmor gen --enable-rft testben.py benchmark.py benchmark2.py
    $ python dist/testben.py

.. table:: Table-2. Performace of RFT Mode
   :widths: auto

   ==============  =========  =========  =========  =========  ==================
   Time (ms)       Import fresh module   Run function "foo"    Remark
   --------------  --------------------  --------------------  ------------------
   Python          Pyarmor    RFT Mode   Pyarmor    RFT Mode
   ==============  =========  =========  =========  =========  ==================
   3.7             1.083      1.317      334.313    324.023
   3.8             0.774      1.109      239.217    241.697
   3.9             0.775      0.809      304.838    301.789
   3.10            2.182      1.049      310.046    339.414
   3.11            0.882      0.984      258.309    264.070
   ==============  =========  =========  =========  =========  ==================

Next, we compare RFT mode and :option:`--obf-code` ``0`` with original scritps by this way::

    $ rm -rf dist __pycache__
    $ python testben.py
    ...

    $ pyarmor gen --enable-rft --obf-code=0 testben.py benchmark.py benchmark2.py
    $ python testben.py
    ...

.. table:: Table-2.1 Performance of RFT Mode and obf-code 0
   :widths: auto

   ==============  =========  =========  =========  =========  ==================
   Time (ms)       Import fresh module   Run function "foo"    Remark
   --------------  --------------------  --------------------  ------------------
   Python          Pyarmor    RFT Mode   Pyarmor    RFT Mode
   ==============  =========  =========  =========  =========  ==================
   3.7             0.757      1.844      307.325    272.672
   3.8             0.791      0.747      276.865    243.436
   3.9             1.276      0.986      246.407    236.138
   3.10            2.563      1.142      256.583    260.196
   3.11            0.952      0.938      185.435    154.390
   ==============  =========  =========  =========  =========  ==================

They're almost same.

**BCC Mode Performance**

BCC mode converts some code to C function, it need extra time to load binary code, but function may be faster. The following test data got by this way::

    $ rm -rf dist __pycache__
    $ python testben.py
    ...

    $ python testben.py
    ...

    $ pyarmor gen --enable-bcc testben.py benchmark.py benchmark2.py
    $ python dist/testben.py
    ...

    $ python dist/testben.py
    ...

.. table:: Table-3. Performance of BCC Mode with Python Version
   :widths: auto

   ==============  =========  =========  =========  =========  =========  =========
   Time (ms)       Import fresh module   Import module 2nd     Run function "foo"
   --------------  --------------------  --------------------  --------------------
   Python          Origin     BCC Mode   Origin     BCC Mode   Origin     BCC Mode
   ==============  =========  =========  =========  =========  =========  =========
   3.7             1.086      1.177      0.342      0.391      344.640    271.426
   3.8             1.099      1.397      0.351      0.400      291.244    251.520
   3.9             1.229      1.076      0.538      0.362      306.594    254.458
   3.10            1.267      0.999      0.255      0.796      302.398    247.154
   3.11            1.146      1.056      0.273      0.536      206.311    189.582
   ==============  =========  =========  =========  =========  =========  =========

**Impact of Different Options**

In order to facilitate comparison, each option is used separately. For example, test :option:`--no-wrap` by this way::

    $ rm -rf dist __pycache__
    $ pyarmor testben.py
    ...

    $ pyarmor gen --no-wrap testben.py benchmark.py benchmark2.py
    $ pyarmor dist/testben.py

    Python 3.7
    test_import     :      0.971 ms
    test_foo        :    306.261 ms

.. list-table:: Table-4. Impact of Different Options
   :header-rows: 1

   * - Option
     - Performance
     - Security
   * - :option:`--no-wrap`
     - Increase
     - Reduce
   * - :option:`--obf-module` ``0``
     - Slightly increase
     - Slightly reduce
   * - :option:`--obf-code` ``0``
     - Remarkable increase
     - Remarkable reduce
   * - :option:`--obf-code` ``2``
     - Reduce
     - Increase
   * - :option:`--enable-rft`
     - Almost same
     - Remarkable increase
   * - :option:`--enable-themida`
     - Remarkable reduce
     - Remarkable increase
   * - :option:`--mix-str`
     - Reduce
     - Increase
   * - :option:`--assert-call`
     - Reduce
     - Increase
   * - :option:`--assert-import`
     - Slightly reduce
     - Increase
   * - :option:`--private`
     - Reduce
     - Increase
   * - :option:`--restrict`
     - Reduce
     - Increase

.. include:: ../_common_definitions.txt
