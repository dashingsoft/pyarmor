.. _常见问题:

常见问题
========

当出现问题的时候，首先使用下面的方式运行以得到更多的错误信息::

    python -d pyarmor.py ...
    PYTHONDEBUG=y pyarmor ...

Segment fault
-------------

下面的情况都会导致导致程序崩溃

* 使用调试版本的 Python 来运行加密脚本
* 使用 Python 2.6 加密脚本，但是却使用 Python 2.7 来运行加密脚本

Could not find `_pytransform`
-----------------------------

通常情况下动态库 `_pytransform` 和加密脚本在相同的目录下:

* `_pytransform.so` in Linux
* `_pytransform.dll` in Windows
* `_pytransform.dylib` in MacOS

首先检查文件是否存在。如果文件存在:

* 检查文件权限是否正确。如果没有执行权限，在 Windows 系统会报错::

    [Error 5] Access is denied

* 检查 `ctypes` 是否可以直接装载 `_pytransform`::

    from pytransform import _load_library
    m = _load_library(path='/path/to/dist')

* 如果上面的语句执行失败，尝试在 :ref:`引导代码` 中设置运行时刻路径::

    from pytransform import pyarmor_runtime
    pyarmor_runtime('/path/to/dist')

如果还是有问题，那么请报告 issue_

The `license.lic` generated doesn't work
----------------------------------------

通常情况下是因为加密脚本使用的密钥箱和生成许可文件时候使用的密钥箱不一
样，例如在试用版本加密脚本，但是在正式版本下面生成许可文件。

通用的解决方法就是重新把加密脚本生成一下，然后在重新生成许可文件。

NameError: name '__pyarmor__' is not defined
--------------------------------------------

原因是 :ref:`引导代码` 没有被执行。

当使用模块 `subprocess` 或者 `multiprocessing` ， 调用 `Popen` 或者
`Process` 创建新的进程的时候，确保 :ref:`引导代码` 在新进程中也得到执
行。否则新进程是无法使用加密脚本的。

Marshal loads failed when running xxx.py
----------------------------------------

当出现这个问题，依次进行下面的检查

1. 检查运行加密脚本的 Python 的版本和加密脚本的 Python 版本是否一致

2. 尝试移动全局密钥箱 `~/.pyarmor_capsule.zip` 到其他任何目录，然后重
   新加密脚本

3. 确保生成许可使用的密钥箱和加密脚本使用的密钥箱是相同的（当运行
   PyArmor 的命令时，该命令使用的密钥箱的文件名称会显示在控制台）

_pytransform can not be loaded twice
------------------------------------

如果 :ref:`引导代码` 被执行两次，就会报这个错误。通常的情况下，是因为
在加密模块中插入了 :ref:`引导代码` 。 因为引导代码在主脚本已经执行过，
所以导入这样的加密模块就出现了问题。

Check restrict mode failed
--------------------------

违反了加密脚本的使用约束，参考 :ref:`约束模式`

.. include:: _common_definitions.txt
