.. _the performance of obfuscated scripts:

The Performance of Obfuscated Scripts
=====================================

Run command :ref:`benchmark` to check the performance of obfuscated scripts::

    pyarmor benchmark

Here it's sample output::

    INFO     PyArmor Trial Version 6.3.0
    INFO     Python version: 3.7
    INFO     Start benchmark test ...
    INFO     Obfuscate module mode: 1
    INFO     Obfuscate code mode: 1
    INFO     Obfuscate wrap mode: 1
    INFO     Obfuscate advanced mode: 0
    INFO     Benchmark bootstrap ...
    INFO     Benchmark bootstrap OK.
    INFO     Run benchmark test ...

    Test script: bfoo.py
    Obfuscated script: obfoo.py
    --------------------------------------

    import_first_no_obfuscated_module                 :   6.177000 ms
    import_first_obfuscated_module                    :  15.107000 ms

    re_import_no_obfuscated_module                    :   0.004000 ms
    re_import_obfuscated_module                       :   0.005000 ms

    --- Import 10 modules ---
    import_many_no_obfuscated_modules                 :  58.882000 ms
    import_many_obfuscated_modules                    :  50.592000 ms

    run_empty_no_obfuscated_code_object               :   0.004000 ms
    run_empty_obfuscated_code_object                  :   0.003000 ms

    run_no_obfuscated_1k_bytecode                     :   0.010000 ms
    run_obfuscated_1k_bytecode                        :   0.027000 ms

    run_no_obfuscated_10k_bytecode                    :   0.053000 ms
    run_obfuscated_10k_bytecode                       :   0.119000 ms

    call_1000_no_obfuscated_1k_bytecode               :   2.411000 ms
    call_1000_obfuscated_1k_bytecode                  :   3.735000 ms

    call_1000_no_obfuscated_10k_bytecode              :  32.067000 ms
    call_1000_obfuscated_10k_bytecode                 :  42.164000 ms

    call_10000_no_obfuscated_1k_bytecode              :  22.387000 ms
    call_10000_obfuscated_1k_bytecode                 :  36.666000 ms

    call_10000_no_obfuscated_10k_bytecode             : 307.478000 ms
    call_10000_obfuscated_10k_bytecode                : 407.585000 ms

    --------------------------------------
    INFO     Remove test path: ./.benchtest
    INFO     Finish benchmark test.

It uses a simple script `bfoo.py` which include 2 functions

* one_thousand: the size of byte code is about 1k
* ten_thousand: the size of byte code is about 10k

The elapse time of `import_first_obfuscated_module` includes the initializing
time of dynamic library, the license checking time etc., so it spends more time
than normal script. However `import_many_obfuscated_modules` which simplely copy
the script to about 10 new files and import them by new names, it's sooner than
the normal script, because the obfuscated one has been compiled, the compile
time is saved.

The rest of tests, for example, `call_1000_no_obfuscated_1k_bytecode` which
stands for calling the function `one_thousand` 1000 times. Comparing the result
of `call_1000_obfuscated_1k_bytecode` to know about the performance of the
obfuscated scripts. Note that the result depends on the test scripts, Python
version, obfuscated mode etc. even in the same machine run the same command the
result may be different.

List all available options::

    pyarmor benchmark -h

Specify other options to check the performance in different mode. For example::

    pyarmor benchmark --wrap-mode 0 --obf-code 2

Look at the scripts used to run benchmark test::

    pyarmor benchmark --debug

All the used files are saved in the folder `.benchtest`

The performance in different modes
----------------------------------

.. include:: _common_definitions.txt
