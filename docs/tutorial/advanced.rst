.. highlight:: console

====================
 Advanced Tutorials
====================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

如何使用选项进行定制
====================

如何定制包的输出模块
--------------------

设置输出函数::

    $ pyarmor cfg exclude_restrict_modules="__init__ queens"

恢复默认值::

    $ pyarmor cfg --reset exclude_restrict_modules


如何定制错误处理方式
--------------------

当运行密钥已经过期，或者和当前设备不匹配，以及加密脚本保护异常，默认的处理方式是
抛出运行错误的异常，错误信息为上面定制的消息

如果需要直接退出，不显示任何信息，可以首先进行下面的配置::

    $ pyarmor cfg on_error=2

然后在进行加密::

    $ pyarmor gen foo.py

目前总共支持的处理方式有三种

* 0: 默认方式
* 1: 抛出系统退出异常，显示对应的错误信息
* 2: 直接退出，不显示任何信息

可以使用下面的命令恢复默认值::

    $ pyarmor cfg on_error=0

这个命令主要影响的运行辅助包和运行密钥。

Using rftmode
=============

Using bccmode
=============

Patching source by plugin marker
================================

Before obfuscating a script, Pyarmor scans each line, remove plugin marker plus
the following one whitespace, leave the rest as it is.

The default plugin marker is ``# pyarmor:``, any comment line with this prefix
will be as a plugin marker.

For example, these lines

.. code-block:: python
                :emphasize lines: 3,4

    print('start ...')

    # pyarmor: print('this is plugin code')
    # pyarmor: check_something()

will be changed to

.. code-block:: python
                :emphasize lines: 3,4

    print('start ...')

    print('this is plugin code')
    check_something()

Use cases:
1. change default language for runtime error messages
2. protect hidden imported modules

.. code-block:: python

    # pyarmor: sys._PARLANG = 'gbk'

    m = __import__('abc')
    # pyarmor: __assert_armored__(m)

Using hooks
===========

.. versionadded:: 8.1

Example of hook script :file:`hook.py`

.. code:: python

    {
       'period': '''def period_hook(*args): ...''',
       'boot': '''def boot_hook(*args): ...''',
       'import': '''def import_hook(*args): ...''',
    }

Save it to global or local configuration path

如何国际化错误信息
==================

定制的错误信息支持多语言，例如为中文繁体定制错误信息，其它都使用默认信息:

.. code:: ini

  [runtime.message]

  languages = zh_CN zh_TW

  error_1 = invalid license
  error_2 = invalid license
  error_3 = invalid license

  [runtime.message.zh_CN]

  error_1 = 脚本超期
  error_2 = 未授权设备
  error_3 = 非法使用

  [runtime.message.zh_TW]

  error_1 = 腳本許可證已經過期
  error_2 = 腳本許可證不可用於當前設備
  error_3 = 未經授權使用腳本

在运行脚本的时候，可以指定 sys._PARLANG 或者环境变量 LANG

也可以使用 plugin 指定语言

Generating cross platform scripts
=================================

Use :option:`--platform`

Obfuscating scripts for multiple Pythons
========================================

Use helper script `merge.py`

.. include:: ../_common_definitions.txt
