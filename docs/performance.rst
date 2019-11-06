.. _the performance of obfuscated scripts:

The Performance of Obfuscated Scripts
=====================================

Run command :ref:`benchmark` to check the performance of obfuscated
scripts::

    pyarmor benchmark

Here it's sample output::

    INFO     Start benchmark test ...
    INFO     Obfuscate module mode: 1
    INFO     Obfuscate code mode: 1
    INFO     Obfuscate wrap mode: 1
    INFO     Benchmark bootstrap ...
    INFO     Benchmark bootstrap OK.
    INFO     Run benchmark test ...
    Test script: bfoo.py
    Obfuscated script: obfoo.py
    --------------------------------------

    load_pytransform: 28.429590911694085 ms
    init_pytransform: 10.701080723946758 ms
    verify_license: 0.515428636879825 ms
    total_extra_init_time: 40.34842417122847 ms

    import_no_obfuscated_module: 9.601499631936461 ms
    import_obfuscated_module: 6.858413569322354 ms

    re_import_no_obfuscated_module: 0.007263492985840059 ms
    re_import_obfuscated_module: 0.0058666674116400475 ms

    run_empty_no_obfuscated_code_object: 0.015085716201360122 ms
    run_empty_obfuscated_code_object: 0.0058666674116400475 ms

    run_one_thousand_no_obfuscated_bytecode: 0.003911111607760032 ms
    run_one_thousand_obfuscated_bytecode: 0.005307937181960043 ms

    run_ten_thousand_no_obfuscated_bytecode: 0.003911111607760032 ms
    run_ten_thousand_obfuscated_bytecode: 0.005587302296800045 ms

    --------------------------------------
    INFO     Remove test path: .\.benchtest
    INFO     Finish benchmark test.

The total extra init time is about `40ms`. It includes the time of
loading dynamic library, initialzing it and verifing license.

Note that the time of importing obfuscated module is less than of
importing no obfuscated module, because the obfuscated scripts has
been compiled as byte-code, the original scripts need extra time to
compile.

List all available options::

    pyarmor benchmark -h

Specify other options to check the performance in different mode. For
example::

    pyarmor benchmark --wrap-mode 0

Look at the scripts used to run benchmark test::

    pyarmor benchmark --debug

All the used files are saved in the folder `.benchtest`

.. include:: _common_definitions.txt
