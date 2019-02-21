.. _如何打包加密脚本:

如何打包加密脚本
================

虽然加密脚本可以无缝替换原来的脚本，但是打包的时候还是存在一个问题:

**加密之后所有的依赖包无法自动获取**

解决这个问题的基本思路是

1. 使用没有加密的脚本找到所有的依赖文件
2. 使用加密脚本替换原来的脚本
3. 添加加密脚本需要的运行辅助文件到安装包
4. 替换主脚本，因为主脚本会被编译成为可执行文件

PyArmor 使用 `PyInstaller` 完成打包的大部分工作，如果没有安装的话，首先执
行下面的命令进行安装::

    pip install pyinstaller

当运行 `pyarmor pack` 命令进行打包的时候， PyArmor 会进行如下的工作

第一步是加密所有的脚本，保存到 ``dist/obf``::

    pyarmor obfuscate --output dist/obf hello.py

第二步是生成 `.spec` 文件，这是 `PyInstaller` 需要的，把加密脚本需要的
运行辅助文件也添加到里面::

    pyinstaller --add-data dist/obf/*.lic
                --add-data dist/obf/*.key
                --add-data dist/obf/_pytransform.*
                hello.py dist/obf/hello.py

第三步是修改 `hello.spec`, 在 `Analysis` 之后插入下面的语句，主要作用是
打包的时候使用加密后的脚本，而不是原来的脚本::

    a.scripts[0] = 'hello', 'dist/obf/hello.py', 'PYSOURCE'
    for i in range(len(a.pure)):
        if a.pure[i][1].startswith(a.pathex[0]):
            a.pure[i] = a.pure[i][0], a.pure[i][1].replace(a.pathex[0], os.path.abspath('dist/obf'), a.pure[i][2]

最后运行这个修改过的文件，生成最终的安装包::

    pyinstaller hello.spec

检查一下安装包中的脚本是否已经加密::

   # It works
   dist/hello/hello.exe

   rm dist/hello/license.lic

   # It should not work
   dist/hello/hello.exe

.. include:: _common_definitions.txt
