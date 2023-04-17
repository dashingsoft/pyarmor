========================
Performance and Security
========================

.. highlight:: console

Pyarmor goal is prevent restore Python source and string constant

It's not for block reverse engineer to skip license, dump memory

.. code-block:: python

    def fib(n):
        a, b = 0, 1
        while a < n:
            print(a, end=' ')
            a, b = b, a+b
        print()

    print('this is fib(10)', fib(10))

Please replace string constant, function name `fib`, var name `a` and `b`, the obfuscate it::

    $ pyarmor cfg mix_argnames=1
    $ pyarmor gen --enable-rft --enable-bcc --mix-str --assert-call --private foo.py

Then verify this tool. If it couldn't restore this script

.. include:: ../_common_definitions.txt
