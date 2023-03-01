.. highlight:: bash

======================
Localize Runtime Error
======================

默认语言的确定：

* 首先查看 :envvar:`PYARMOR_LANG`
* 其次查看 sys._PARLANG
* 最后查看 :envvar:`LANG`

错误信息的本地化处理机制

创建一个文件 :file:`messages.cfg` 在本地配置路径或者全局配置路径，替换
对应的错误信息，

.. code-block:: ini

  [runtime.message]

    error__1 = 错误代码超出范围

    error_1 = 脚本许可证已经过期
    error_2 = 脚本许可证不可用于当前设备
    error_3 = 非法使用脚本

    error_4 = 缺少运行许可文件
    error_5 = 脚本不支持当前 Python 版本
    error_6 = 脚本不支持当前系统
    error_7 = 加密模块的数据格式不正确

    error_8 = 加密函数的数据格式不正确

文件编码要使用 utf-8，如果需要使用其它编码，运行下面的命令::

    $ pyarmor cfg runtime messages=messages.cfg:gbk


.. include:: ../_common_definitions.txt
