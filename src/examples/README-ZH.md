# 示例

[English Version](README.md)

好的示例就是最好的老师，是最快的学习方式。在 Pyarmor 发布的包里面，就包
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

* [build-for-exe.bat](build-for-exe.bat) / [build-for-freeze.bat](build-for-freeze.bat)

    这个脚本模板展示了如何使用 py2exe 或者 cx_Freeze 等来打包发布被 Pyarmor 加密过
    的脚本。对于 py2app 和 PyInstaller ，也完全可以参考使用。

除了这些脚本之外，这里还有一些真实的例子。现在打开一个命令窗口，按照下
面文档中的说明，一步一步来学习 Pyarmor 的常用功能。

在下面的章节中，假定 Python 已经安装，并且可以使用 `python` 直接调用，
Pyarmor 的安装路径是 `/path/to/pyarmor`

示例命令格式是 Linux 的脚本命令，Windows 上使用需要转换成为对应的命令。

## 实例 1: 加密脚本

从这个例子中，可以学习到

* 如何加密所有在路径 `examples/simple` 的 Python 脚本
* 如何运行加密后的脚本
* 如何发布加密后的脚本

```
    cd /path/to/pyarmor

    # 使用 pyarmor 提供的命令 obfuscate 加密路径下 `examples/simple` 的所有脚本
    python pyarmor.py obfuscate --recursive --src examples/simple --entry queens.py

    # 加密后的脚本存放在 `dist`
    cd dist

    # 运行加密脚本
    python queens.py

    # 运行加密需要的所有文件都在 `dist` 下面，压缩之后就可以发给客户
    zip queens-obf.zip .
```

## 实例 2:  加密包（Package）

从这个例子中，可以学习到

* 如何加密一个 Python 包 `mypkg`，它所在的路径是 `examples/testpkg`
* 如何设置加密包的运行期限
* 如何使用外部脚本 `main.py` 来导入和使用加密后 `mypkg` 包中的函数
* 如何发布加密后的包给用户

```
    cd /path/to/pyarmor

    # 使用 pyarmor 提供的命令 obfuscate 去加密包，加密后的脚本存放在 `dist/mypkg`
    # python pyarmor.py obfuscate --src "examples/testpkg/mypkg" --entry "__init__.py" --output "dist/mypkg"

    # 使用命令 license 生成一个有效期到 2019-01-01 的授权文件
    python pyarmor.py licenses --expired 2019-01-01 mypkg2018

    # 使用新的授权文件覆盖默认的授权文件
    cp licenses/mypkg2018/license.lic dist/mypkg

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
    python pyarmor.py init --src=examples/simple --entry=queens.py projects/simple

    # 切换到新创建的工程
    cd projects/simple

    # 这儿自动生成有一个脚本 `pyarmor`，在 Windows 下面名字是 `pyarmor.bat`
    # 使用命令 `build` 加密工程中所有的 `.py` 文件，加密脚本存放在 `dist` 下面
    ./pyarmor build

    # 生成不同的授权文件
    #
    # 为 John 生成的限时许可，新的许可文件存放在 "licenses/john/license.lic"
    ./pyarmor licenses --expired 2019-03-05 john

    # 为 Lily 生成的硬盘许可，新的许可文件存放在 "licenses/lily/license.lic"
    ./pyarmor licenses --bind-disk '100304PBN2081SF3NJ5T' lily

    # 为 Tom 生成的限时和网卡绑定许可，新的许可文件存放在 "licenses/tom/license.lic"
    ./pyarmor licenses --bind-mac '70:f1:a1:23:f0:94' --expired 2019-03-05 tom

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

## 实例 4: 使用第三方发布工具打包加密脚本

从这个例子中，可以学习到

* 如何修改工程的配置
* 如何过滤工程中的脚本，例如，所有的测试脚本都不需要加密
* 如何只生成运行需要的辅助文件
* 如何只加密脚本，不生成额外的运行辅助文件
* 如何使用 py2exe 打包加密脚本（其他类似工具例如 PyInstaller, cx_Freeze 基本也适用）

运行这个例子，需要安装 py2exe 和 zip。在 `examples/py2exe` 下面，
py2exe 会把启动脚本 `hello.py` 生成 `hello.exe`，然后把该目录下的其他
Python 源文件编译后生成压缩包 `library.zip`。Pyarmor 则需要加密所有脚本，
然后用加密脚本替换 `library.zip` 的同名文件，并拷贝运行辅助文件到
py2exe 的输出路径。

这里面主要面临的问题是，如何让 py2exe 正确找到加密脚本所依赖的系统库，
包括 Pyarmor 运行需要的库，例如 `ctypes`

因为一旦加密之后，py2exe 就无法知道该模块使用了那些其他的包


```bash
    cd /path/to/pyarmor

    # 创建一个工程
    python pyarmor.py init --src=examples/py2exe --entry="hello.py" projects/py2exe

    # 切换到该工程
    cd projects/py2exe

    # 修改工程设置
    #
    # 设置 `--runtime-path` 为空字符串，否则加密脚本找不到动态链接库 `_pytransform`
    #
    # 设置 `--disable-restrict-mode` 为 1，否则加密脚本可能会报错:
    #
    #     SystemError: error return without exception set
    #
    # 使用选项 `--mantifest` 来过滤脚本，排除到不需要加密的的脚本和相关路径
    # 关于过滤器的格式参考 https://docs.python.org/2/distutils/sourcedist.html#commands
    #
    # 至于为什么启动脚本 `hello.py` 也不能被加密，下面会有说明
    #
    ./pyarmor config --runtime-path='' --disable-restrict-mode=1 \
                     --manifest "global-include *.py, exclude hello.py setup.py pytransform.py, prune dist, prunde build"

    # 加密工程中指定的所有脚本，不生成运行辅助文件
    ./pyarmor build --no-runtime

    # 把修改后的启动脚本拷贝到源路径下面，之前先备份一下
    cp ../../examples/py2exe/hello.py hello.py.bak
    mv dist/hello.py ../../examples/py2exe

    # 拷贝引用到的模块到源路径下面
    cp ../../pytransform.py ../../examples/py2exe

    # 注意这里除了启动脚本被修改过之外，其他的都还没有变，启动脚本的
    # 最前面插入了两行语句
    #
    #     from pytransform import pyarmor_runtime
    #     pyarmor_runtime
    #
    # 这样可以让 py2exe 把模块 pytransform 和其需要的其他系统模块，
    # 例如 `ctypes` 打到包里面
    #
    # 启动脚本也不能加密，主要也是因为加密之后，这个脚本依赖的其他模块
    # 就都找不到了，这样最后打的包里面可能会缺少很多需要的系统文件
    #
    # 在源路径里面运行 py2exe，生成 `hello.exe`，`library.zip`，存放在 `dist` 下面
    ( cd ../../examples/py2exe; python setup.py py2exe )

    # 打包之后，恢复主脚本
    mv hello.py.bak ../../examples/py2exe/hello.py

    # 把所有加密脚本编译成为 .pyc（Python 3.2 之前不需要 -b 选项）
    python -m compileall -b dist

    # 更新 `library.zip`，使用加密脚本替换原来的脚本
    ( cd dist; zip -r ../../../examples/py2exe/dist/library.zip *.pyc )

    # 生成运行需要的辅助文件，保存在 `runtimes`
    ./pyarmor build --only-runtime --output runtimes

    # 拷贝运行辅助文件到 py2exe 的输出路径
    cp runtimes/* ../../examples/py2exe/dist

    # 现在，运行 `hello.exe`
    cd ../../examples/py2exe/dist
    ./hello.exe
```
