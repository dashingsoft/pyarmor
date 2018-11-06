# Pyarmor 加密和保护 Python 源代码的方法和机制

Pyarmor 是一个用于加密和保护 Python 源代码的小工具。它能够在运行时刻保护 Python
脚本的二进制代码不被泄露，设置加密后 Python 源代码的有效期限，绑定加密后的Python
源代码到硬盘、网卡等硬件设备。它的保障机制主要包括

* 加密编译后的代码块，保护模块中的字符串和常量
* 在脚本运行时候动态加密和解密代码块的二进制代码
* 代码块执行完成之后清空堆栈局部变量
* 通过授权文件限制加密后脚本的有效期和设备环境

让我们看看一个普通的 Python 脚本 `foo.py` 加密之后是什么样子。下面是加
密脚本所在的目录 `dist` 下的所有文件列表

```
    foo.py

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS

    pyshield.key
    pyshield.lic
    product.key
    license.lic
```

`dist/foo.py` 是加密后的脚本，它的内容如下

``` python
    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...')
```

所有其他文件叫做 `运行依赖文件`，它们是运行加密脚本所必须的。并且只要这里面的模块
`pytransform.py` 能被正常导入进来，加密脚本 `dist/foo.py` 就可以像正常脚本一样被
运行。这是 Pyarmor 的一个重要特征： **加密脚本无缝替换 Python 源代码**

## 加密 Python 源代码

Pyarmor 是怎么加密 Python 源代码呢？

首先把源代码编译成代码块 `Code Object`

``` c
    char *filename = "foo.py";
    char *source = read_file( filename );
    PyCodeObject *co = Py_CompileString( source, "<frozen foo>", Py_file_input );
```

接着对这个代码块进行如下处理

* 使用 `try...finally` 语句把代码块的代码段 `co_code` 包裹起来

```
    新添加一个头部，对应于 try 语句:

            LOAD_GLOBALS    N (__armor_enter__)     N = length of co_consts
            CALL_FUNCTION   0
            POP_TOP
            SETUP_FINALLY   X (jump to wrap footer) X = size of original byte code

    接着是处理过的原始代码段:

            对于所有的绝对跳转指令，操作数增加头部字节数

            加密修改过的所有指令代码

            ...

    追加一个尾部，对应于 finally 块:

            LOAD_GLOBALS    N + 1 (__armor_exit__)
            CALL_FUNCTION   0
            POP_TOP
            END_FINALLY
```

* 添加字符串名称 `__armor_enter`, `__armor_exit__` 到 `co_consts`

* 如果 `co_stacksize` 小于 4，那么设置为 4

* 在 `co_flags` 设置自定义的标志位 CO_OBFUSCAED (0x80000000)

* 按照上面的方式递归修改 `co_consts` 中的所有类型为代码块的常量

然后把改装后的代码块转换成为字符串，把字符串进行加密，保护其中的常量和字符串

``` c
    char *string_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( string_code  );
```

最后生成加密后的脚本，写入到磁盘文件

``` c
    sprintf( buf, "__pyarmor__(__name__, __file__, b'%s')", obfuscated_code );
    save_file( "dist/foo.py", buf );
```

单纯加密后的脚本就是一个正常的函数调用语句，长得就像这个样子

```
    __pyarmor__(__name__, __file__, b'\x01\x0a...')
```

## 运行加密脚本

那么，一个正常的 Python 解释器运行加密脚本 `dist/foo.py` 的过程是什么样呢？

上面我们看到 `dist/foo.py` 的前两行是这个样子

``` python
    from pytransfrom import pyarmor_runtime
    pyarmor_runtime()
```

这两行叫做 `引导代码`，在运行任何加密脚本之前，它们必须先要被执行。它们
有着重要的使命

* 使用 `ctypes` 来装载动态库 `_pytransform`
* 检查授权文件 `dist/license.lic` 是否合法
* 添加三个内置函数到模块 `builtins`
  * `__pyarmor__`
  * `__armor_enter__`
  * `__armor_exit__`

最主要的是添加了三个内置函数，这样 `dist/foo.py` 的下一行代码才不会出错，
因为它马上要调用函数 `__pyarmor__`

```
    __pyarmor__(__name__, __file__, b'\x01\x0a...')

```

`__pyarmor__` 主要负责导入加密的模块，实现的原理如下

```c
    static PyObject *
    __pyarmor__(char *name, char *pathname, unsigned char *obfuscated_code)
    {
        char *string_code = restore_obfuscated_code( obfuscated_code );
        PyCodeObject *co = marshal.loads( string_code );
        return PyImport_ExecCodeModuleEx( name, co, pathname );
    }
```

第一个导入的模块是 `__main__`, 从现在开始，在整个 Python 解释器的生命周期中

* 每一个函数（代码块）一旦被调用，首先就会执行函数 `__armor_enter__`，
  它负责恢复代码块。其实现原理如下所示

``` c
    static PyObject *
    __armor_enter__(PyObject *self, PyObject *args)
    {
        // 通过当前执行堆栈得到当前代码块指针
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // 借用 co_names->ob_refcnt 来记录当前代码块
        // 的调用次数
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt ++;

        // 恢复被加密的代码块
        if (IS_OBFUSCATED(f_code->co_flags)) {
            restore_byte_code(f_code->co_code);
            clear_obfuscated_flag(f_code);
        }

        Py_RETURN_NONE;
    }
```

* 因为每一个代码块都被人为的使用 `try...finally` 块包裹了一下，所以代码
  块执行完之后，在返回上一级之前，就会调用 `__armor_exit__`。它会重新加
  密代码块，同时清空堆栈内的局部变量

``` c
    static PyObject *
    __armor_exit__(PyObject *self, PyObject *args)
    {
        // 得到当前代码块指针
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // 调用计数器递减
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt --;

        // 仅当调用计数器为 0 的时候重新加密代码块的代码段 co_code
        // 在多线程、递归等很多种情况下，都会出现一个代码段 co_code
        // 被多个代码块 Code Object 同时使用的情况
        if (refcalls->ob_refcnt == 1) {
            obfuscate_byte_code(f_code->co_code);
            set_obfuscated_flag(f_code);
        }

        // 清空当前堆栈的局部变量
        clear_frame_locals(frame);

        Py_RETURN_NONE;
    }
```

## 加密脚本的授权

当 `引导代码` `pyarmor_runtime()` 被调用时候，它会检查授权文件`dist/license.lic`。
如果存在非授权的使用，就会报错退出。在加密脚本的时候同时会生成一个默认的授权文件，
它允许加密脚本运行在任何机器上，并且永不过期。

我们可以在授权文件里面包含一个有效的日期，或者硬盘序列号，网卡的Mac地址等，这样
`pyarmor_runtime()` 就可以检查时间，比对硬件设备，从而确定当前运行环境是否满足条
件，选择继续运行或者报错退出。

Pyarmor 使用命令 `hdinfo` 来获取目标机器的硬件信息

```bash
    python pyarmor.py hdinfo
```

然后使用命令 `licenses` 来生成新的授权文件

``` bash
    python pyarmor.py licenses
                      --expired 2018-12-31
                      --bind-disk "100304PBN2081SF3NJ5T"
                      --bind-mac "70:f1:a1:23:f0:94"
                      --bind-ipv4 "202.10.2.52"
                      Customer-Jondy
```

更多详细信息，请访问 [Pyarmor 网站主页](http://pyarmor.dashingsoft.com/index-zh.html)
