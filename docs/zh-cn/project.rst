.. _使用工程:

使用工程
========

工程是一个包含配置文件的目录，可以用来方便的管理加密脚本。

使用工程管理脚本的有下列优点:

* 可以递增式加密脚本，仅仅加密修改过的脚本，适用于需要加密脚本很多的项目
* 定制选择工程包含的脚本文件，而不是一个目录下全部脚本
* 设置加密模式和定制保护代码
* 更加方便的管理加密脚本

使用工程管理加密脚本
--------------------

首先使用命令 ``init`` 创建一个工程::

    pyarmor init --src=examples/pybench --entry=pybench.py projects/pybench

新创建的工程存放在 `projects/pybench` ，这个目录下面会有两个文件::

    .pyarmor_config
    pyarmor.bat or pyarmor

:file:`.pyarmor_config` 是 JSON 格式的配置文件。

另外一个文件是脚本文件，用来快捷调用 ``pyarmor`` 。使用工程的方式一般
是切换当前路径到工程目录，然后运行脚本文件::

    cd projects/pybench
    ./pyarmor info

使用下面的命令加密工程中包含的所有脚本::

    ./pyarmor build

当某些脚本修改之后，再次运行 `build` ，加密这些修改过的脚本::

    ./pyarmor build

选择设定工程脚本使用 `--manifest` 选项。下面示例是把 :file:`dist`,
:file:`test` 目录下面的所有 `.py` 排除在工程之外::

    ./pyarmor config --manifest "include *.py, prune dist, prune test"

默认情况下 `build` 仅仅加密修改过的文件，强制加密所有脚本::

    ./pyarmor build --force

运行加密后的脚本::

    cd dist
    python pybench.py

.. _使用不同加密模式:

使用不同加密模式
----------------

配置不同的加密模式::

    ./pyarmor config --obf-mod=1 --obf-code=0

使用新的加密模式重新加密脚本::

    ./pyarmor build -B


工程配置文件
------------

每一个工程都有一个 JSON 格式的工程配置文件，它包含的属性如下：

- name

    工程名称

- title

    工程标题

- src

    工程所包含脚本的路径，通常情况下是一个绝对路径

* manifest

    选择和设置工程包含的脚本，其支持的格式和 Python Distutils 中的
    MANIFEST.in 是一样的。默认值为 `src` 下面的所有 `.py` 文件::

        global-include *.py

    多个模式使用逗号分开，例如::

        global-include *.py, exclude __mainfest__.py, prune test

    关于所有支持的模式，参考
    https://docs.python.org/2/distutils/sourcedist.html#commands

* is_package

    可用值: 0, 1, None

    主要会影响到加密脚本的保存路径，如果设置为 1，那么输出路径会额外包
    含包的名称。

* disable_restrict_mode

    可用值: 0, 1, None    
    
    默认值为 0，即启用约束模式，禁止从非加密的脚本导入加密模块。

    参考 :ref:`约束模式`

* entry

    工程的主脚本，可以是多个，以逗号分开::

        main.py, another/main.py, /usr/local/myapp/main.py

    主脚本可以是绝对路径，也可以是相对路径，相对于工程路径。

* output

    输出路径，保存加密后的脚本和运行辅助文件，相对于工程路径。

* capsule

    工程使用的密钥箱，默认是 :ref:`全局密钥箱` 。

* obf_code

  是否加密每一个函数（代码块）:

        - 0

        不加密

        - 1

        加密每一个函数

  参考 :ref:`代码加密模式`

* wrap_mode

  是否使用 `try..final` 结构包裹原理的代码块

        - 0

        不包裹

        - 1

        包裹每一个代码块

  参考 :ref:`包裹模式`

* obf_mod

  是否加密整个模块:

        - 0

        不加密

        - 1

        加密模块

  参考 :ref:`模块加密模式`

* cross_protection

  是否在主脚本插入交叉保护代码:

        - 0

        不插入

        - 1

        插入默认的保护代码，参考 :ref:`对主脚本的特殊处理`

        - 文件名称

        使用文件指定的自定义模板

* runtime_path

    None 或者任何路径名称

    用来告诉加密脚本去哪里装载动态库 `_pytransform` 。

    默认值为 None ， 是指和模块 :file:`pytransform.py` 在相同的路径。

    主要用于使用打包工具（例如 py2exe）把加密脚本压缩到一个 `.zip` 文
    件的时候，无法正确定位动态库，这时候把 `runtime_path` 设置为空字符
    串可以解决这个问题。

.. include:: _common_definitions.txt
