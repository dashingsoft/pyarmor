.. _加密脚本的性能:

加密脚本的性能
==============

运行命令 :ref:`benchmark` 可以检查加密脚本的性能::

    pyarmor benchmark

下面是输出结果的示例::


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

PyArmor 使用一个简单脚本 `bfoo.py` 来进行测试，里面有两个函数，

* one_thousand: 它的代码大小大约是 1K
* ten_thousand: 它的代码大小大约是 10K

第一个测试 `import_first_obfuscated_module` 包含了动态库的初始化，以及验证许可证
等其他额外时间，所以比普通脚本时间要长一些。而 `import_many_obfuscated_modules`
，这个测试中把原来的脚本拷贝成为 10 个其他脚本，然后使用新的名称导入，它花费的时
间就明显比没有加密的要快很多，这主要是因为加密脚本已经是编译好的代码，省去了编译
时间，而加密消耗的额外时间小于编译时间。

其他的测试，例如 `call_1000_no_obfuscated_1k_bytecode` ，它的意思是调用 1000 次
函数 `one_thousand` 所消耗的时间，通过比较 `call_1000_obfuscated_1k_bytecode` 的
结果，可以大概了解到加密后脚本性能。需要注意的是测试结果和多个因素有关，包括测试
脚本，加密模式，Python 版本等等，即便是在相同的机器，运行相同的命令，结果也会有
些微差别，所以需要根据实际环境下运行结果来进行评估。

另外也可以测试不同加密模式下的性能，使用下面的选项查看所有支持的模式::

    pyarmor benchmark -h

然后传入不同的参数，测试不同加密模式的性能。例如::

    pyarmor benchmark --wrap-mode 0 --obf-code 2

查看测试命令使用的脚本，使用选项 ``--debug`` 保留生成的中间文件，所有的中间文件
保存在目录 `.benchtest` 下面::

    pyarmor benchmark --debug

.. _不同模式的性能比较:

不同模式的性能比较
------------------

模块加密模式 `obf-mod` 的两种加密模式 `1` 和 `2` 应该说后者在安全性和
性能上都更好一些，从 6.3.0 开始引入之后就作为默认的加密模式取代了 `1` 。

函数加密模式 `obf-code` 的两种加密模式 `1` 和 `2` 应该是后者安全行更高
一些，速度稍微慢一些，但是也不是慢的太多。

包裹模式 `wrap-mode` 是否启用可能会对性能造成显著影响，模式 `0` 意味着
一旦函数解密之后，就不会被再次加密，当然也无需解密。而模式 `1` 每次函
数开始执行之前需要解密，而执行完成都会重新加密。所以如果大部分的函数是
被调用多次的话，后者明显要比前者慢一些。

而 :ref:`高级模式` 和 :ref:`超级模式` 相比较，两者差别不对，甚至后者有
时候会更快一些。但是 :ref:`虚拟模式` 会明显慢一些，因为核心算法使用的
虚拟指令。

使用 cProfile 测试加密脚本性能
------------------------------

加密脚本可以使用 `cProfile` 或者 `profile` 来测试性能，例如::

  pyarmor obfuscate foo.py

  python -m cProfile dist/foo.py

有些加密脚本使用 `cProfile` 或者 `profile` 运行可能会抛出异常，请根据
异常信息对系统脚本 `cProfile.py` 或者 `profile.py` 打补丁，使之能够正
常处理加密脚本中的一些特殊情况。

.. note::

   老版本的 pyarmor 并不支持 `cProfile` 和 `profile` ，请升级 pyarmor
   并重新加密脚本，然后重新运行。

超级大脚本的运行性能
--------------------

下面是测试了一个大小为 81M 的脚本的运行性能，测试平台为 MacOS 10.14，
双核 8G 内存，Python 3.7。

测试脚本 ``big.py`` 定义了多个相同内容但是名称不同的函数，大小为 81M

.. code:: python

    def fib0(n):   # return Fibonacci series up to n
        result = []
        a, b = 0, 1
        while a < n:
            result.append(a)
            a, b = b, a+b
        return result


    def fib1(n):   # return Fibonacci series up to n
        result = []
        a, b = 0, 1
        while a < n:
            result.append(a)
            a, b = b, a+b
        return result


    def fib2(n):   # return Fibonacci series up to n
        result = []
        a, b = 0, 1
        while a < n:
            result.append(a)
            a, b = b, a+b
        return result

    ...

主脚本 ``main.py`` 如下

.. code:: python

    import sys
    import time

    def metricmethod(func):
        if not hasattr(time, 'process_time'):
            time.process_time = time.clock

        def wrap(*args, **kwargs):
            t1 = time.process_time()
            result = func(*args, **kwargs)
            t2 = time.process_time()
            print('%-50s: %10.6f ms' % (func.__name__, (t2 - t1) * 1000))
            return result
        return wrap

    @metricmethod
    def import_big_module(name):
        return __import__(name)

    @metricmethod
    def call_module_function(m):
        m.fib2(20)

    name = sys.argv[1] if len(sys.argv) > 1 else 'big'
    call_module_function(import_big_module(name))

运行 ``python3 main.py`` 在不同情况下进行测试。

没有加密的测试结果，在测试之前删除 ``__pycache__``::

   import_big_module      : 52905.399000 ms
   call_module_function   :   0.020000 ms

存在 ``__pycache__`` 情况下的测试结果::

   import_big_module      : 2065.303000 ms
   call_module_function   :   0.011000 ms

使用下面的命令加密::

   pyarmor obfuscate big.py

测试结果如下::

   import_big_module      : 8690.256000 ms
   call_module_function   :   0.015000 ms

.. include:: ../_common_definitions.txt
