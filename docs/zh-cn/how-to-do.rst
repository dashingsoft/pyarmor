PyArmor 的工作原理
==================

让我们看看一个普通的 Python 脚本 `foo.py` 加密之后是什么样子。下面是加
密脚本所在的目录 `dist` 下的所有文件列表::

    foo.py

    pytransform.py
    _pytransform.so, or _pytransform.dll in Windows, _pytransform.dylib in MacOS
    pytransform.key
    license.lic

`dist/foo.py` 是加密后的脚本，它的内容如下::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

    __pyarmor__(__name__, __file__, b'\x06\x0f...')

所有其他文件叫做 :ref:`运行辅助文件` ，它们是运行加密脚本所必须的。并
且只要这里面的模块 `pytransform.py` 能被正常导入进来，加密脚本
`dist/foo.py` 就可以像正常脚本一样被运行。

这是 PyArmor 的一个重要特征： **加密脚本无缝替换 Python 源代码**

.. _如何加密脚本:

如何加密脚本
------------

PyArmor 是怎么加密 Python 源代码呢？

首先把源代码编译成代码块::

    char *filename = "foo.py";
    char *source = read_file( filename );
    PyCodeObject *co = Py_CompileString( source, "<frozen foo>", Py_file_input );


接着对这个代码块进行如下处理

* 使用 `try...finally` 语句把代码块的代码段 `co_code` 包裹起来::

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

* 添加字符串名称 `__armor_enter`, `__armor_exit__` 到 `co_consts`

* 如果 `co_stacksize` 小于 4，那么设置为 4

* 在 `co_flags` 设置自定义的标志位 CO_OBFUSCAED (0x80000000)

* 按照上面的方式递归修改 `co_consts` 中的所有类型为代码块的常量

然后把改装后的代码块转换成为字符串，把字符串进行加密，保护其中的常量和字符串::

    char *string_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( string_code  );

最后生成加密后的脚本，写入到磁盘文件::

    sprintf( buf, "__pyarmor__(__name__, __file__, b'%s')", obfuscated_code );
    save_file( "dist/foo.py", buf );

单纯加密后的脚本就是一个正常的函数调用语句，长得就像这个样子::

    __pyarmor__(__name__, __file__, b'\x01\x0a...')


.. _如何运行加密脚本:

如何运行加密脚本
----------------

那么，一个普通的 Python 解释器运行加密脚本 `dist/foo.py` 的过程是什么样呢？

上面我们看到 `dist/foo.py` 的前两行是这个样子::

    from pytransform import pyarmor_runtime
    pyarmor_runtime()

这两行叫做 :ref:`引导代码` ，在运行任何加密脚本之前，它们必须先要被执行。
它们有着重要的使命

* 使用 `ctypes` 来装载动态库 `_pytransform`
* 检查授权文件 `dist/license.lic` 是否合法
* 添加三个内置函数到模块 `builtins`
  * `__pyarmor__`
  * `__armor_enter__`
  * `__armor_exit__`

最主要的是添加了三个内置函数，这样 `dist/foo.py` 的下一行代码才不会出错，
因为它马上要调用函数 `__pyarmor__`::

    __pyarmor__(__name__, __file__, b'\x01\x0a...')

`__pyarmor__` 被调用，它的主要功能是导入加密的模块，实现的伪代码如下::

    static PyObject *
    __pyarmor__(char *name, char *pathname, unsigned char *obfuscated_code)
    {
        char *string_code = restore_obfuscated_code( obfuscated_code );
        PyCodeObject *co = marshal.loads( string_code );
        return PyImport_ExecCodeModuleEx( name, co, pathname );
    }

从现在开始，在整个 Python 解释器的生命周期中

* 每一个函数（代码块）一旦被调用，首先就会执行函数 `__armor_enter__` ，
  它负责恢复代码块。其实现原理如下所示::

    static PyObject *
    __armor_enter__(PyObject *self, PyObject *args)
    {
        // Got code object
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // Increase refcalls of this code object
        // Borrow co_names->ob_refcnt as call counter
        // Generally it will not increased  by Python Interpreter
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt ++;

        // Restore byte code if it's obfuscated
        if (IS_OBFUSCATED(f_code->co_flags)) {
            restore_byte_code(f_code->co_code);
            clear_obfuscated_flag(f_code);
        }

        Py_RETURN_NONE;
    }

* 因为每一个代码块都被人为的使用 `try...finally` 块包裹了一下，所以代码
  块执行完之后，在返回上一级之前，就会调用 `__armor_exit__` 。它会重新加
  密代码块，同时清空堆栈内的局部变量::

    static PyObject *
    __armor_exit__(PyObject *self, PyObject *args)
    {
        // Got code object
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;

        // Decrease refcalls of this code object
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt --;

        // Obfuscate byte code only if this code object isn't used by any function
        // In multi-threads or recursive call, one code object may be referenced
        // by many functions at the same time
        if (refcalls->ob_refcnt == 1) {
            obfuscate_byte_code(f_code->co_code);
            set_obfuscated_flag(f_code);
        }

        // Clear f_locals in this frame
        clear_frame_locals(frame);

        Py_RETURN_NONE;
    }

.. _对主脚本的特殊处理:

对主脚本的特殊处理
------------------

和其他模块不一样，PyArmor 对主脚本有额外的处理:

* 在加密之前，修改主脚本，插入保护代码
* 在加密之后，修改加密脚本，插入引导代码

在加密主脚本之前，PyArmor 会逐行扫描源代码。如果发现下面的一行::

    # {PyArmor Protection Code}

PyArmor 就会把这一行替换成为保护代码。

如果发现了下面这一行::

    # No PyArmor Protection Code

PyArmor 就不会在主脚本中插入保护代码。

如果上面两个特征行都没有，那么在看看有没有这样的行::

    if __name__ == '__main__'

如果有，插入保护代码到这条语句的前面。如果没有，那么不添加保护代码。

默认的保护代码的模板如下::

    def protect_pytransform():

        import pytransform

        def check_obfuscated_script():
            CO_SIZES = 49, 46, 38, 36
            CO_NAMES = set(['pytransform', 'pyarmor_runtime', '__pyarmor__',
                            '__name__', '__file__'])
            co = pytransform.sys._getframe(3).f_code
            if not ((set(co.co_names) <= CO_NAMES)
                    and (len(co.co_code) in CO_SIZES)):
                raise RuntimeError('Unexpected obfuscated script')

        def check_mod_pytransform():
            CO_NAMES = set(['Exception', 'LoadLibrary', 'None', 'PYFUNCTYPE',
                            'PytransformError', '__file__', '_debug_mode',
                            '_get_error_msg', '_handle', '_load_library',
                            '_pytransform', 'abspath', 'basename', 'byteorder',
                            'c_char_p', 'c_int', 'c_void_p', 'calcsize', 'cdll',
                            'dirname', 'encode', 'exists', 'exit',
                            'format_platname', 'get_error_msg', 'init_pytransform',
                            'init_runtime', 'int', 'isinstance', 'join', 'lower',
                            'normpath', 'os', 'path', 'platform', 'print',
                            'pyarmor_init', 'pythonapi', 'restype', 'set_option',
                            'str', 'struct', 'sys', 'system', 'version_info'])

            colist = []

            for name in ('dllmethod', 'init_pytransform', 'init_runtime',
                         '_load_library', 'pyarmor_init', 'pyarmor_runtime'):
                colist.append(getattr(pytransform, name).{code})

            for name in ('init_pytransform', 'init_runtime'):
                colist.append(getattr(pytransform, name).{closure}[0].cell_contents.{code})
            colist.append(pytransform.dllmethod.{code}.co_consts[1])

            for co in colist:
                if not (set(co.co_names) < CO_NAMES):
                    raise RuntimeError('Unexpected pytransform.py')

        def check_lib_pytransform():
            filename = pytransform.os.path.join({rpath}, {filename})
            size = {size}
            n = size >> 2
            with open(filename, 'rb') as f:
                buf = f.read(size)
            fmt = 'I' * n
            checksum = sum(pytransform.struct.unpack(fmt, buf)) & 0xFFFFFFFF
            if not checksum == {checksum}:
                raise RuntimeError("Unexpected %s" % filename)
        try:
            check_obfuscated_script()
            check_mod_pytransform()
            check_lib_pytransform()
        except Exception as e:
            print("Protection Fault: %s" % e)
            pytransform.sys.exit(1)

    protect_pytransform()

在加密脚本的时候， PyArmor 会使用真实的值来替换其中的字符串模板 `{xxx}`

如果不想让 PyArmor 添加保护代码，除了在脚本中添加上面所示的标志行之外，
也可以使用命令行选项 `--cross-protection=0` ，例如::

    pyarmor obfuscate --cross-protection=0 foo.py

主脚本被加密之后， PyArmor 会在最前面插入 :ref:`引导代码` 。

.. include:: _common_definitions.txt
