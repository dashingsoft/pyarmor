.. _命令手册:


命令手册
========

PyArmor 是一个命令行工具，用来加密脚本，绑定加密脚本到固定机器或者设置加密脚本的有效期。

`pyarmor` 的语法格式::

    pyarmor <command> [options]

常用的命令包括::

    obfuscate    加密脚本
    licenses     为加密脚本生成新的许可文件
    pack         打包加密脚本
    hdinfo       获取硬件信息

..
    The commands with project::

    init         Create a project to manage obfuscated scripts
    config       Update project settings
    build        Obfuscate all the scripts in the project

    info         Show project information
    check        Check consistency of project

可以运行 `pyarmor <command> -h` 查看各个命令的详细使用方法。

obfuscate
---------

加密 Python 脚本。

语法::

    pyarmor obfuscate <options> SCRIPT...

描述

PyArmor 首先检查用户根目录下面是否存在 :file:`.pyarmor_capsule.zip` ，
如果不存在，那么创建一个新的。

接着搜索主脚本所在目录下面的所有 `.py` 文件，加密所有的 `.py` 文件并保
存在输出目录 `dist`

然后为加密脚本生成默认的许可文件 :file:`license.lic` 和所有其他的
:ref:`运行辅助文件` ，也到保存到输出目录 `dist`

最后插入 :ref:`引导代码` 到主脚本。

.. _obfuscate 命令选项:

选项

-O PATH, --output PATH  输出路径
-r, --recursive         递归加密所有子目录

licenses
--------

为加密脚本生成新的许可文件

语法::

    pyarmor licenses <options> CODE

.. _licenses 命令选项:

选项:

-O OUTPUT, --output OUTPUT
                      输出路径
-e YYYY-MM-DD, --expired YYYY-MM-DD
                      加密脚本的有效期
-d SN, --bind-disk SN
                      绑定加密脚本到硬盘序列号
-4 IPV4, --bind-ipv4 IPV4
                      绑定加密脚本到指定IP地址
-m MACADDR, --bind-mac MACADDR
                      绑定加密脚本到网卡的Mac地址

pack
----

打包加密脚本

语法::

    pyarmor pack <options> SCRIPT

.. _pack 命令选项:

选项:

-t TYPE, --type TYPE  cx_Freeze, py2exe, py2app, PyInstaller(default).
-O OUTPUT, --output OUTPUT
                      输出路径

hdinfo
------

显示当前机器的硬件信息，例如硬盘序列号，网卡Mac地址等。

这些信息主要用来为加密脚本生成许可文件的时候使用。

语法::

    pyarmor hdinfo

.. include:: _common_definitions.txt
