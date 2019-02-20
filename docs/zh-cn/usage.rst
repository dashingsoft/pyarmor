.. _使用 PyArmor:


使用 PyArmor
============

命令 ``pyarmor`` 的基本语法为:

    ``pyarmor`` [command] [options]

加密脚本
--------

命令 ``obfuscate`` 用来加密脚本。最常用的一种情况是切换到脚本
`myscript.py` 所在的路径，然后执行::

    pyarmor obfuscate myscript.py

PyArmor 会加密 :file:`myscript.py` 和相同目录下面的所有 :file:`*.py` 文件:

* 在用户根目录下面创建 :file:`.pyarmor_capsule.zip` （仅当不存在的时候创建）
* 创建输出子目录 :file:`dist`
* 生成加密的主脚本 :file:`myscript.py` 保存在输出目录 :file:`dist`
* 加密相同目录下其他所有 :file:`*.py` 文件，保存到输出目录 :file:`dist`
* 生成运行加密脚本所需要的全部辅助文件，保存到输出目录 :file:`dist`

输出目录 :file:`dist` 包含运行加密脚本所需要的全部文件::

    myscript.py

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pytransform.key
    license.lic

除了加密脚本之外，其他文件都叫做 ``辅助文件`` ，它们都是运行加密脚本不
可缺少的文件。

通常情况下第一个脚本叫做主脚本，它加密后的内容如下::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...')

其中前两行是 ``引导代码``, 它们只在主脚本出现，并且只能被运行一次。对于
其他所有加密脚本，只有这样一行::

    __pyarmor__(__name__, __file__, b'\x0a\x02...')

运行加密脚本::

    cd dist
    python myscript.py

默认情况下，只有和主脚本相同目录的其他 :file:`*.py` 会被同时加密。如果
想递归加密子目录下的所有 :file:`*.py` 文件，使用下面的命令::

    pyarmor obfuscate --recursive myscript.py

发布加密的脚本
--------------

发布加密脚本给客户只需要把输出路径 `dist` 的所有文件拷贝过去即可，客户
并不需要安装 PyArmor

关于加密脚本的安全性的说明，参考 :ref:`PyArmor 的安全性`

生成新的许可文件
----------------

命令 ``licenses`` 用来为加密脚本生成新的许可文件 :file:`license.lic`

默认情况下，加密脚本的同时会在输出目录下面生成一个许可文件
:file:`dist/license.lic` ，它允许加密脚本运行在任何设备上并且永不过期。

如果需要设置加密脚本的使用期限，首先使用下面的命令生成一个带有效期的认
证文件::

    pyarmor licenses --expired 2019-01-01 code-001

执行这条命令，PyArmor 会生成新的许可文件:

* 从 :file:`.pyarmor_capsule.zip` 读取相关数据
* 创建 :file:`license.lic` ，保存在 ``licenses/code-001``
* 创建 :file:`license.lic.txt` ，保存在 ``licenses/code-001``

然后，使用新生成的许可文件覆盖默认的许可文件::

    cp licenses/code-001/license.lic dist/

这样，加密脚本在2009年1月1日之后就无法在运行了。

如果想绑定加密脚本到固定机器上，首先在该机器上面运行下面的命令获取硬件
信息::

    pyarmor hdinfo

然后在生成绑定到固定机器的许可文件::

    pyarmor licenses --bind-disk '100304PBN2081SF3NJ5T' --bind-mac '20:c1:d2:2f:a0:96' code-002

同样，覆盖默认许可文件，这样加密脚本就只能在指定机器上运行::

    cp licenses/code-002/license.lic dist/

    cd dist/
    python myscript.py

扩展其他认证方式
----------------

除了上述认证方式之外，还可以在 Python 脚本中增加其他任何认证代码，因为
加密的脚本对于客户来说就是黑盒子。例如，使用网络时间来设置加密脚本的使
用期限::

    import ntplib
    from time import mktime, strptime
    c = ntplib.NTPClient()
    response = c.request('europe.pool.ntp.org', version=3)
    if response.tx_time > mktime(strptime('20190202', '%Y%m%d')):
        sys.exit(1)


打包加密脚本
------------

命令 ``pack`` 用来打包并加密脚本

首先需要安装 `PyInstaller`::

    pip install pyinstaller

然后运行下面的命令::

    pyarmor pack myscript.py

PyArmor 加密 :file:`myscript.py` 并将所有需要的文件打包成为一个独立可运
行的安装包:

* 执行 ``pyarmor obfuscate`` 加密脚本 :file:`myscript.py` 和同目录下的所有其他脚本
* 执行 ``pyinstaller myscipt.py`` 创建 :file:`myscript.spec`
* 修改 :file:`myscript.spec`, 把原来的脚本替换成为加密后的脚本
* 再次执行 ``pyinstaller myscript.spec`` ，生成最终的安装包

输出的文件在目录 ``dist/myscript`` ，这里面包含了脱离 Python 环境可以运行的所有文件。

运行打包好的可执行文件::

    dist/myscript/myscript

检查脚本是否加密。如果加密，下面的第二条命令应该执行失败::

    rm dist/myscript/license.lic
    dist/myscript/myscript

为加密脚本设置有效期::

    pyarmor licenses --expired 2019-01-01 code-003
    cp licenses/code-003/license.lic dist/myscript

    dist/myscript/myscript

需要注意的是如果 ``.spec`` 文件需要定制， ``pack`` 命令也许无法正常使用，
这时候要对 ``.spec`` 进行相应修改，具体操作参考 :ref:`如果打包加密脚本`

.. include:: _common_definitions.txt
