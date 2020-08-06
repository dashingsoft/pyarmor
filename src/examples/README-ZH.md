# 示例（[English Version](README.md)）

好的示例就是最好的老师，是最快的学习方式。在 PyArmor 发布的包里面，就包
含了针对不同使用场景的脚本模板。这些脚本里面的注释很详细，按照里面的说
明进行正确的设置，就可以快速加密 Python 脚本。扩展名为 `.bat` 在
Windows 下使用，`.sh` 的在 Linux，MacOS 等上面使用。他们都存放在子目录
`examples` 下面:

* [obfuscate-app.bat](obfuscate-app.bat) / [obfuscate-app.sh](obfuscate-app.sh)

    入门脚本，你的最初选择，用来快速加密脚本。

* [obfuscate-pkg.bat](obfuscate-pkg.bat) / [obfuscate-pkg.sh](obfuscate-pkg.sh)

    如果 Python 源代码是使用包（Package）的方式发布，也就是说，允许第三
    方的脚本导入你所发布的包里面的函数，那么参考这个脚本进行加密。

* [build-with-project.bat](build-with-project.bat) / [build-with-project.sh](build-with-project.sh)

    当上面的两个脚本都不能满足你的需要的时候，尝试使用 Project 来管理加
    密脚本，Project 提供了更丰富的功能。

* [pack-obfuscated-scripts.bat](pack-obfuscated-scripts.bat) / [pack-obfuscated-scripts.sh](pack-obfuscated-scripts.sh)

    使用这个脚本模板通过第三方工具 PyInstaller 来打包加密的脚本。


除了这些脚本之外，这里还有一些真实的例子。现在打开一个命令窗口，按照下
面文档中的说明，一步一步来学习 PyArmor 的常用功能。

在下面的章节中，假定 Python 已经安装，并且可以使用 `python` 直接调用，
PyArmor 的安装路径是 `/path/to/pyarmor`

示例命令格式是 Linux 的脚本命令，Windows 上使用需要转换成为对应的命令。

## 实例 1: 加密脚本

从这个例子中，可以学习到

* 如何加密所有在路径 `examples/simple` 的 Python 脚本
* 如何运行加密后的脚本
* 如何发布加密后的脚本
* 如何使用许可证来设置加密脚本的使用期限

```
    cd /path/to/pyarmor

    # 使用 obfuscate 加密路径 `examples/simple` 的下面的所有脚本
    pyarmor obfuscate --recursive examples/simple/queens.py

    # 加密后的脚本存放在 `dist`
    cd dist

    # 运行加密脚本
    python queens.py

    # 运行加密需要的所有文件都在 `dist` 下面，压缩之后就可以发给客户
    zip queens-obf.zip .

    # 如果需要设置加密脚本的使用期限，那么
    cd /path/to/pyarmor

    # 使用命令 licenses 生成一个有效期到 2020-10-01 的授权文件，存放在 licenses/r001 下面
    pyarmor licenses --expired 2020-10-01 r001

    # 使用 --with-license 指定上面生成的许可文件
    pyarmor obfuscate --recursive --with-license licenses/r001/license.lic examples/simple/queens.py

    # 压缩加密脚本给客户
    cd dist
    zip queens-obf.zip .
```

## 实例 2:  加密包（Package）

从这个例子中，可以学习到

* 如何加密一个 Python 包 `mypkg`，它所在的路径是 `examples/testpkg`
* 如何使用外部许可证设置加密包的运行期限
* 如何使用外部脚本 `main.py` 来导入和使用加密后 `mypkg` 包中的函数
* 如何发布加密后的包给用户

```
    cd /path/to/pyarmor

    # 使用 obfuscate 去加密包，加密后的脚本存放在 `dist/mypkg`
    # 使用选项 --with-license outer 指定使用外部的许可证
    pyarmor obfuscate --output=dist/mypkg --with-license outer examples/testpkg/mypkg/__init__.py

    # 使用命令 licenses 生成一个有效期到 2020-10-01 的授权文件
    pyarmor licenses --expired 2020-10-01 r002

    # 使用新的授权文件覆盖默认的授权文件
    cp licenses/r002/license.lic dist/mypkg

    # 使用第三方脚本 `main.py` 导入加密库
    cd dist
    cp ../examples/testpkg/main.py ./
    python main.py

    # 打包整个路径 `mypkg`，发布给客户
    zip -r mypkg-obf.zip mypkg
```

## 实例 3: 使用 Project 来管理和加密脚本

从这个例子中，可以学习到

* 如何使用 Project 管理加密脚本
* 如何绑定加密脚本到硬盘、网卡等
* 如何跨平台发布加密脚本
* 如何为不同客户定制授权认证文件

这是一个更接近真实场景的例子，加密后的脚本 `queens.py` 会以不同的授权方
式发布给不同的客户:

* John: 运行在 64位 Ubuntu 上面，2019年5月5号过期，之后就无法在使用
* Lily: 运行在一台 64位 Win10 上面，这台机器的硬盘序列号必须是 `100304PBN2081SF3NJ5T`
* Tom: 运行在一台嵌入式设备 Raspberry Pi 上面，网卡Mac地址必须是 `70:f1:a1:23:f0:94`，并且2019年5月5号过期

```
    cd /path/to/pyarmor

    # 使用命令 init 创建一个工程
    pyarmor init --src=examples/simple --entry=queens.py projects/simple

    # 配置工程使用外部许可证
    pyarmor config --with-license=outer

    # 切换到新创建的工程
    cd projects/simple

    # 这儿自动生成有一个脚本 `pyarmor`，在 Windows 下面名字是 `pyarmor.bat`
    # 使用命令 `build` 加密工程中所有的 `.py` 文件，加密脚本存放在 `dist` 下面
    pyarmor build

    # 生成不同的授权文件
    #
    # 为 John 生成的限时许可，新的许可文件存放在 "licenses/john/license.lic"
    pyarmor licenses --expired 2019-03-05 john

    # 为 Lily 生成的硬盘许可，新的许可文件存放在 "licenses/lily/license.lic"
    pyarmor licenses --bind-disk '100304PBN2081SF3NJ5T' lily

    # 为 Tom 生成的限时和网卡绑定许可，新的许可文件存放在 "licenses/tom/license.lic"
    pyarmor licenses --bind-mac '70:f1:a1:23:f0:94' --expired 2019-03-05 tom

    # 创建给 John 的发布包
    #
    mkdir -p customers/john

    # 复制所有的加密脚本到新目录
    cp -a dist/ customers/john

    # 替换默认的许可文件
    cp licenses/john/license.lic customers/john/dist

    # 替换平台相关的动态链接库，从网站上下载适用 64位 Linux 的版本
    rm -f customer/john/dist/_pytransform.*
    wget http://pyarmor.dashingsoft.com/downloads/platforms/linux_x86_64/_pytransform.so -O customer/john/dist/_pytransform.so

    # 打包在路径 `customer/john/dist` 的所有文件，发布给 John

    # 对于 Lily 和 Tom 来说，基本操作都是一样，除了动态链接库需要根据不同的平台分别下载和替换
    #
    wget http://pyarmor.dashingsoft.com/downloads/platforms/win_amd64/_pytransform.dll
    wget http://pyarmor.dashingsoft.com/downloads/platforms/raspberrypi/_pytransform.so

```

## 实例 4: 打包加密脚本

从这个例子中，可以学习到

* 如何使用命令 `pack` 来打包加密的脚本

PyArmor 需要使用第三方的打包工具，推荐工具是 `PyInstaller`, 首先安装

    pip install pyinstaller

接着就可以运行命令 `pack` 打包加密脚本

    cd /path/to/pyarmor
    pyarmor pack -O dist examples/simple/queens.py

运行一下打包好的可执行文件

    dist/queens/queens
