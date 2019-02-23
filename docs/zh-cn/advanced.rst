.. _高级用法:

高级用法
========

使用不同的模式来加密脚本
------------------------

.. _代码加密模式:

代码加密模式
~~~~~~~~~~~~
一个 Python 文件中，通常有很多个函数（代码块）

* obf_code == 0

不会加密函数对应的代码块

* obf_code == 1

在这种情况下，会加密每一个函数对应的代码块，根据 :ref:`包裹模式` 的设
置，使用不同的加密方式

.. _包裹模式:

包裹模式
~~~~~~~~~
* wrap_mode == 0

当包裹模式关闭，代码块使用下面的方式进行加密::

    0   JUMP_ABSOLUTE            n = 3 + len(bytecode)

    3    ...
         ... 这里是加密后的代码块
         ...

    n   LOAD_GLOBAL              ? (__armor__)
    n+3 CALL_FUNCTION            0
    n+6 POP_TOP
    n+7 JUMP_ABSOLUTE            0

在开始插入了一条绝对跳转指令，当执行加密后的代码块时

1. 首先执行 JUMP_ABSOLUTE, 直接跳转到偏移 n

2. 偏移 n 处是调用一个 PyCFunction `__armor__` 。这个函数的功能会恢复
   上面加密后的代码块，并且把代码块移动到最开始（向前移动3个字节）

3. 执行完函数之后，跳转到偏移 0，开始执行原来的函数。

这种模式下，除了函数的第一次调用需要额外的恢复之外，随后的函数调用就和
原来的代码完全一样。

* wrap_mode == 1

当打开包裹模式之后，代码块会使用 `try...finally` 语句包裹起来::

    LOAD_GLOBALS    N (__armor_enter__)     N = co_consts 的长度
    CALL_FUNCTION   0
    POP_TOP
    SETUP_FINALLY   X (jump to wrap footer) X = 原来代码块的长度

    这里是加密的后的代码块

    LOAD_GLOBALS    N + 1 (__armor_exit__)
    CALL_FUNCTION   0
    POP_TOP
    END_FINALLY

这样，当被加密的函数开始执行的时候

1. 首先会调用 `__armor_enter__` 恢复加密后的代码块

2. 然后执行真正的函数代码

3. 在函数执行完成之后，进入 `final` 块，调用 `__armor_exit__` 重新加密
   函数对应的代码块

在这种模式下，函数的每一次执行完成都会重新加密，每一次执行都需要恢复。

.. _模块加密模式:

模块加密模式
~~~~~~~~~~~~
* obf_mod == 1

在这种模式下，最终生成的加密脚本如下::

    __pyarmor__(__name__, __file__, b'\x02\x0a...', 1)

其中第三个参数是代码块转换而成的字符串，它通过下面的伪代码生成::

    PyObject *co = Py_CompileString( source, filename, Py_file_input );
    obfuscate_each_function_in_module( co, obf_mode );
    char *original_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( original_code  );
    sprintf( buffer, "__pyarmor__(__name__, __file__, b'%s', 1)", obfuscated_code );

* obf_mod == 0

在这种模式下，最终生成的代码如下（最后一个参数为 0）::

    __pyarmor__(__name__, __file__, b'\x02\x0a...', 0)

第三个参数的生成方式和上面的基本相同，除了最后一条语句替换为::

    sprintf( buffer, "__pyarmor__(__name__, __file__, b'%s', 0)", original_code );

使用方法请参考 :ref:`使用不同加密模式`

.. _约束模式:

约束模式
--------

在约束模式下，加密脚本必须是下面的形式之一::

    __pyarmor__(__name__, __file__, b'...')

    Or

    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')

    Or

    from pytransform import pyarmor_runtime
    pyarmor_runtime('...')
    __pyarmor__(__name__, __file__, b'...')

并且加密脚本只能从被加密的脚本中导入，不能从任何其他非加密的脚本导入。

例如，下面的加密脚本能够运行::

    $ cat a.py
    
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')

    $ python a.py

而下面的这个就无法运行，因为加密脚本中有一条额外的语句 `print`::

    $ cat b.py
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')
    print(__name__)

    $ python b.py

下面的导入方式正确，从加密脚本 `d.py` 导入 `c.py`::

    $ cat d.py
    import c
    c.hello()

    # Then obfuscate d.py
    $ cat d.py
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    __pyarmor__(__name__, __file__, b'...')


    $ python d.py

而下面的导入方式不工作，因为加密模块 `c.py` 不能从非加密的模块中导入::

    $ cat c.py
    __pyarmor__(__name__, __file__, b'...')

    $ cat main.py
    from pytransform import pyarmor_runtime
    pyarmor_runtime()
    import c

    $ python main.py

从 PyArmor 5.2 开始, 约束模式是默认设置。如果需要禁用约束模式，例如，
在一个普通脚本中导入加密的模块。那么使用下面的命令加密脚本::

    pyarmor obfuscate --restrict=0 foo.py

需要注意的是，如果加密脚本禁用了约束模式，那么为加密脚本生成新的许可的
时候，也要禁用约束模式::

    pyarmor licenses --restrict=0 --expired 2019-01-01 mycode

.. 定制保护代码:

.. include:: _common_definitions.txt
