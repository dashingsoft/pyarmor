PyArmor's 文档
==============

:版本: |PyArmorVersion|
:主页: |Homepage|
:联系方式: jondy.zhao@gmail.com
:作者: 赵俊德

PyArmor 是一个用于加密和保护 Python 源代码的小工具。它能够在运行时刻保护 Python
脚本的二进制代码不被泄露，设置加密后 Python 源代码的有效期限，绑定加密后的Python
源代码到硬盘、网卡等硬件设备。它的保障机制主要包括

* 加密编译后的代码块，保护模块中的字符串和常量
* 在脚本运行时候动态加密和解密每一个函数（代码块）的二进制代码
* 代码块执行完成之后清空堆栈局部变量
* 通过授权文件限制加密后脚本的有效期和设备环境

|PyArmor| 支持 Python 2.6, 2.7 和 Python 3

|PyArmor| 在下列平台进行了充分测试: ``Windows``, ``Mac OS X``, and ``Linux``

|PyArmor| 已经成功应用于 ``FreeBSD`` 和嵌入式系统，例如 ``Raspberry
Pi``, ``Banana Pi``, ``Orange Pi``, ``TS-4600 / TS-7600`` 等，但是这些
平台下面没有进行充分测试。


内容:

.. toctree::
   :maxdepth: 2

   installation
   usage
   pytransform
   security
   understand-obfuscated-scripts
   how-to-do
   pack-obfuscated-scripts
   project
   differences
   advanced
   man
   questions
   license

.. include:: _common_definitions.txt
