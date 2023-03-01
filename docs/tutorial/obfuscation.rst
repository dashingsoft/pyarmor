.. highlight:: console

===================
 Basic Obfuscation
===================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. program:: pyarmor gen

We'll assume you have Pyarmor 8.0+ installed already. You can tell Pyarmor is
installed and which version by running the following command in a shell prompt
(indicated by the $ prefix)::

    $ pyarmor --version

If Pyarmor is installed, you should see the version of your installation. If it
isn't, you'll get an error.

This tutorial is written for Pyarmor 8.0+, which supports Python 3.7 and
later. If the Pyarmor version doesn't match, you can refer to the tutorial for
your version of Pyarmor by using the version switcher at the bottom right corner
of this page, or update Pyarmor to the newest version.

Throughout this tutorial, assume run :command:`pyarmor` in project path which
includes::

    project/
        ├── foo.py
        ├── queens.py
        └── joker/
            ├── __init__.py
            ├── queens.py
            └── config.json

Pyarmor uses :ref:`pyarmor gen` with rich options to obfuscate scripts to meet
the needs of different applications.

Here only introduces common options in a short, using any combination of them as
needed. About usage of each option in details please refer to :ref:`pyarmor gen`

More options to protect script
==============================

For scripts, use these options to get more security::

    $ pyarmor gen --enable-jit --mix-str --assert-call foo.py

Using :option:`--enable-jit` tells Pyarmor processes some sentensive data by
``c`` function generated in runtime.

Using :option:`--mix-str` could mix the string constant (length > 4) in the scripts.

Using :option:`--assert-call` makes sure function is obfuscated, to prevent
called function from being replaced by special ways

For example,

.. code-block:: python
    :emphasize-lines: 1,10

    data = "abcxyz"

    def fib(n):
        a, b = 0, 1
        while a < n:
            print(a, end=' ')
            a, b = b, a+b

    if __name__ == '__main__':
        fib(n)

String constant ``abcxyz`` and function ``fib`` will be protected like this

.. code-block:: python
    :emphasize-lines: 1,10

    data = __mix_str__(b"******")

    def fib(n):
        a, b = 0, 1
        while a < n:
            print(a, end=' ')
            a, b = b, a+b

    if __name__ == '__main__':
        __assert_call__(fib)(n)

If function ``fib`` is obfuscated, ``__assert_call__(fib)`` returns original
function ``fib``. Otherwise it will raise protection exception.

More options to protect package
===============================

For package, append 2 extra options::

    $ pyarmor gen --enable-jit --mix-str --assert-call --assert-import --restrict joker/

Using :option:`--assert-import` prevents obfsucated modules from being replaced
with plain script. It checks each import statement to make sure the modules are
obfuscated.

Using :option:`--restrict` makes sure the obfuscated module is only available
inside package. It couldn't be imported from any plain script, also not be run
by Python interpreter.

By default ``__init__.py`` is not restricted, in order to let others use your
package functions, just import them in the ``__init__.py``, then others could
get exported functions in the public ``__init__.py``.

In this test package, ``joker/__init__.py`` is an empty file, so module
``joker.queens`` is not exported. Let's check this, first create a script
:file:`dist/a.py`

.. code-block:: python

    import joker
    print('import joker OK')
    from joker import queens
    print('import joker.queens OK')

Then run it::

    $ cd dist
    $ python a.py
    ... import joker OK
    ... RuntimeError: unauthorized use of script

In order to export ``joker.queens``, edit :file:`joker/__init__.py`, add one
line

.. code-block:: python

    from joker import queens

Then do above test again, now it should work::

    $ cd dist/
    $ python a.py
    ... import joker OK
    ... import joker.queens OK


Checking runtime key periodically
=================================

check runtime key periodically::

    $ pyarmor gen --period 1h foo.py
    $ pyarmor gen --period 30m foo.py

Binding to many machines
========================

Using :option:`-b` many times::

    $ pyarmor gen -b "" -b "" foo.py

Using outer file to store runtime key
=====================================

在加密脚本的时候指定使用外部密钥::

    $ pyarmor gen --outer foo.py

创建一个外部密钥 ``pyarmor.rkey``::

    $ pyarmor gen key -e 30

把外部密钥文件拷贝到发布包里面::

    $ cp dist/pyarmor.rkey dist/pyarmor_runtime_000000

再次发布新的许可证，生成一个新的::

    $ pyarmor gen key -O dist/key2 -b ""

    $ ls dist/key2/pyarmor.rkey

外部运行密钥必须至少包含一个约束条件，要么是有效期，要么是设备信息。

外部运行密钥的名称默认是 `pyarmor.rkey`

加密脚本在导入模块 pyarmor_runtime 的时候，pyarmor_runtime 会按照下面的顺序查找
外部许可证文件，一旦找到就停止后面的搜索

1. 首先在运行辅助包里面查找和运行密钥同名的文件 ``pyarmor.rkey``
2. 查找环境变量 :envvar:`PYARMOR_RKEY` 指定的路径下面是否有和运行密钥同名的文件
3. 查找 sys._MEIPASS 指定的路径下面是否有和运行密钥同名的文件
4. 查找当前路径是否存在和运行密钥同名的文件
5. 没有找到那么报错退出

外部运行密钥必须存放在以上任意一个路径下面。

Localization runtime error
==========================

如何本地化错误信息
==================

创建一个文件 :file:`.pyarmor/messages.cfg` 替换对应的错误信息，

.. code-block:: ini

  [runtime.message]

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


Packing obfuscated scripts
==========================

基本步骤

1. 使用 PyInstaller 打包::

     $ pyinstaller foo.py

2. 使用 Pyarmor 替换 .pyc 为加密后的脚本::

     $ pyarmor gen --pack dist/foo/foo foo.py

Protect system packages
=======================

.. versionadded:: 8.1
                  This feature is not implemented in 8.0

When packing the scripts, Pyarmor could also obfuscate system packages in the
bundle.

.. include:: ../_common_definitions.txt
