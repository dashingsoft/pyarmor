# 大道归一，Python 源码保护之路

大约十年前开始用 Python 开发自己的应用的时候，就面临一个发布问题，如何
不让客户看到自己的源码呢？估计这也是大部分使用 Python 开发非服务器端的
应用时候会想到的问题。理由当然很多，有时候是保护代码，有时候是为了保护
数据，有时候甚至是自己的代码不够完美，不想让用户看到。也尝试过一些其他
工具，例如 `pyinstaller` 等等，最终决定开发一个自己的小工具。

最初的实现很简单，就是把源文件加密，然后定义自己的模块导入类，钩挂到
`sys.meta_path` 里面。这样运行的时候，如果发现导入的模块是加密的（扩展
名为 `.pye`)，那么使用的扩展模块 `pytransform.import_module` 接管这个模
块的导入：

* 首先进行解密   resore_encrypt_source
* 然后编译       Py_CompileString
* 最后导入该模块 PyImport_ExecCodeModule

```python
class PyshieldImporter(object):

    def __init__(self):
        self.filename = ""
        self.modtype = 0

    def find_module(self, fullname, path=None):
        try:
            _name = fullname.rsplit('.', 1)[-1]
        except AttributeError:
            # no rsplit in Python 2.3
            _name = fullname.split('.', 1)[-1]
        if path is None:
            path = sys.path
        for dirname in path:
            self.filename = os.path.join(dirname, _name + '.pye')
            if os.path.exists(self.filename):
                self.modtype = 0
                return self
        self.filename = ""

    def load_module(self, fullname):
        ispkg = 0
        try:
            mod = pytransform.import_module(
                fullname,
                self.filename,
                self.modtype
                )
            mod.__file__ = "<%s>" % self.__class__.__name__
            mod.__loader__ = self
        except Exception:
            raise ImportError("error occurred when import module")
        return mod

# Install the hook
sys.meta_path.append(PyshieldImporter())

```

关于 sys.meta_path 的工作原理，参考 http://www.python.org/dev/peps/pep-0302

在使用过程中，有用户发现这种方式其实并不能真正的打开加密的效果。因为一
旦模块导入之后，伪代码（byte code) 是可以被访问的，使用反编译模块
(dis)可以把代码显示出来。为了解决这个问题，当时想到的方法是钩挂
`sys.setprofile` 和 `threading.setprofile`，定义回调函数，在每一个函数
执行完成的时候，对函数的伪代码进行加密。如果不设置
`threading.setprofile` 的话，线程里面的函数是不会被跟踪的，所以也必须设
置每一个线程的跟踪函数。在扩展模块里面使用 `C` 实现的方式如下

``` c

// 定义 CFunction 类型的跟踪函数，作为 threading.setprofile 的输入参数

static PyMethodDef
trace_method = {"trace_trampoilne", do_trace_trampoline, METH_VARARGS, NULL};

static PyObject*
do_trace_trampoline(PyObject * self, PyObject * args)
{
  char * name;
  PyObject * frame, * arg;

  if (!PyArg_ParseTuple(args, "OsO", &frame, &name, &arg))
    return NULL;

  if (strncmp(name, whatnames[PyTrace_CALL], 4) == 0)
    _trace_trampoline(NULL, frame, PyTrace_CALL, arg);

  else if (strncmp(name, whatnames[PyTrace_RETURN], 6) == 0)
    _trace_trampoline(NULL, frame, PyTrace_RETURN, arg);

  Py_RETURN_NONE;
}

static void
set_trace_profile()
{
    // 设置其他线程的跟踪函数
    PyObject *mod = PyImport_ImportModule("threading");
    PyObject_SetAttrString(mod, "setprofile", PyCFunction_NewEx(&trace_method, NULL, NULL));

    // 设置主线程的跟踪函数
    PyEval_SetProfile(_trace_trampoline, 0);
}

static int
_trace_trampoline(PyObject *self, PyObject *frame, int what, PyObject *arg)
{
  // 函数调用的时候恢复加密的代码
  if (what == PyTrace_CALL) {
      PyObject *f_code = frame->f_code;
      restore_byte_code(f_code->co_code);
  }

  // 函数调用返回的时候加密代码
  else if (what == PyTrace_RETURN) {
    PyObject *f_code = frame->f_code;
    encrypt_byte_code(f_code->co_code);
  }
  return 0;
}

```

这种方式最大的问题就是对性能的影响太大，因为每一次函数调用都要调用跟踪
函数。即便是没有加密的系统库的调用，也要进去转一圈。很快通过用户的反馈
映证了这一点，没有加密之前 0.5 秒运行完的代码，加密之后要 4 秒多，这是
不可接受的，也迫使我重新思考加密的机制和方法。

有一天想到了`C`代码的加密保护方式，

* 首先编译成可执行文件或者动态链接库

* 然后替换二级制文件中的函数代码块，并在每一个函数入口处插入一条跳转指
  令，跳转到自己定义的包裹函数

* 在包裹函数里面，进行反编译侦测，没有问题的话恢复原来的函数代码，并调
  整到真正的函数入口执行

那么，在Python中是不是可以借鉴这种方式，不是在源代码层，而是在可执行文
件层，直接通过修改汇编指令来进行保护呢？在Python中，汇编指令对应的就是
伪代码（byte code）。这世界上的事情只有想不到的，没有做不到了。有了这样
的思路，一种全新的加密机制马上就出来了。模仿`C`代码保护方式的实现方式如
下：

1. 首先是编译Python源文件为代码对象（Code Object）

``` c
    char * filename = "xxx.py";
    char * source = read_file( filename );
    PyObject *co = Py_CompileString( source, filename, Py_file_input );
```

2. 然后遍历代码对象的所有子代码对象，并对每一个代码对象进行如下处理

    * 使用 `try...finally` 语句包裹代码对象的伪代码（co_code)，改造后的
      伪代码如下

    ```
        LOAD_GLOBALS    N (__armor_enter__)
        CALL_FUNCTION   0
        POP_TOP
        SETUP_FINALLY   X (jump to wrap footer)

        以上是额外增加的包裹头部，调用 __armor_enter__，然后开始一个 try...finally 块

        中间是处理过的原始伪代码，主要进行如下处理

            修改所有的绝对跳转指令（例如 JUMP_ABSOLUTE）的目标地址，增加包裹头部的大小
            加密原始伪代码

        以下是额外增加的包裹尾部，是 try...finally 块的执行代码，调用 __armor_exit__

        LOAD_GLOBALS    N + 1 (__armor_exit__)
        CALL_FUNCTION   0
        POP_TOP
        END_FINALLY

    ```

    * 在代码对象的常量列表（co_consts)的最后面增加两个函数名称（字符串）
        * `__armor_enter__`
        * `__armor_exit__`

    * 代码对象的堆栈（co_stacksize)大小增加2

        刚开始的时候没有增加堆栈，结果在64位机器上工作正常，在32位机器
        上出现各种崩溃问题。更令人头疼的是，使用 gdb 进行跟踪又不崩溃。
        足足花了我几乎半个月的时间，最终才发现是堆栈出了问题。我有时候
        就想，当你发现真正的原因的时候，总感觉为什么这么简单的解决方式，
        也就增加了两行代码，却花费了你如此多的时间。如何才能高效快速的
        定位原因所在呢，这个问题值得深思。

3. 把改造后的代码对象转换成为字符串，并进行加密，保护里面的常量和字符串

``` c
    char *original_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( original_code  );

```

4. 创建最终的加密脚本，生成一个和原来文件同名的 `.py` 文件

```
    sprintf( buf, "__pyarmor__(__name__, __file__, b'%s')", obfuscated_code );
    save_to_file( "/path/to/output/xxx.py", buf );

```

最终的加密脚本也是一个合法的Python源文件，长的就像这个样子

```
    __pyarmor__(__name__, __file__, b'\x01\x0a...')

```

这个加密的脚本可以像普通的Python脚本一样被使用，但是在使用之前，必须添
加三个自定义的函数到内置模块 `builtins` 里面

* `__pyarmor__`
* `__armro_enter__`
* `__armro_exit__`

这样，当加密脚本被Python解释器执行的时候

1. `__pyarmor__` 首先被调用，负责导入加密的模块，它的原型和实现如下

    ```c
    int __pyarmor__(char *modname, char *filename, unsigned char *obfuscated_code) {
    
        char *original_code = resotre_obfuscated_code( obfuscated_code );
        PyObject *co = marshal.loads( original_code );
        PyObject *m = PyImport_ExecCodeModule( modname, co );
    
        PyObject_SetAttrString(m, "__file__", PyString_FromString(filename));
        
    }
    ```

2. `__armor_enter__` 会在每一个代码块执行的时候被调用，它的原型和实现如下

    ``` c
    static PyObject*
    enter_armor(PyObject *self, PyObject *args)
    {
        // 得到对应的代码块
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;
    
        // 因为在递归调用或者多线程中，会出现同一个函数还没有退出之前，又被调
        // 用的情况，而同一个函数指向的伪代码是同一个对象。所以必须等到所有相
        // 同函数都退出之后，才能重新加密。如果函数只要执行完成就加密的话，其
        // 他正在执行的同名函数就会出错。
        //
        // 为了解决这个问题，需要对代码块的调用进行计数。当代码块被调用的时候，
        // 计数器增加一；当代码块执行完成的时候，计数器减去一。只有当计数器为
        // 一的时候，才重新加密代码块
        //
        // 这个计数器就借用 co_names 的 ob_refcnt 来实现
        //
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt ++;
    
        // 如果伪代码被加密，那么就恢复伪代码
        if (IS_OBFUSCATE(f_code->co_flags)) {
          restore_byte_code(f_code->co_code);
          clear_obfuscate_flag(f_code);
        }
    
        Py_RETURN_NONE;
    }
    
    ```

3. `__armor_exit__` 会在每一个代码块执行完成的时候被调用，它的原型和实现如下
    ``` c
    static PyObject*
    exit_armor(PyObject *self, PyObject *args)
    {
        // 得到对应的代码块
        PyFrameObject *frame = PyEval_GetFrame();
        PyCodeObject *f_code = frame->f_code;
    
        // 代码块调用计数器减去一
        PyObject *refcalls = f_code->co_names;
        refcalls->ob_refcnt --;
    
        // 仅当代码块调用计数器为 1 的时候，重新加密伪代码
        if (refcalls->ob_refcnt == 1) {
          obfuscate_byte_code(f_code->co_code);
          set_obfuscate_flag(f_code);    
        }
    
        // 清空局部变量
        clear_frame_locals(frame);

        Py_RETURN_NONE;
    }
    
    ```
    
这种Python仿真版的保护机制的性能和安全性都有了质的变化，Pyarmor 也终于
变得成熟。

从安全级别上来说，使用 Python 语言提供的任何机制是无法突破 Pyarmor 的保
护的。即便是使用调试器（例如 gdb），设置断点在 `PyEval_EvalFrameEx`，
Pyarmor 也可以在 `__armor_enter__` 中进行反侦测，一旦发现调试器存在，或
者Python解释器经过了改造，就拒绝工作。当然，这就是加密和破解两条阵线的
较量，也是性能和安全之间综合平衡的问题。不管怎么说，这种安全性已经到了
`C`语言的层面，是和如何保护二进制的可执行文件是相同的了。

回顾**Pyarmor**的发展历程，最终的实现方式和保护`C`代码如此类似，使我想
到了《老子》中“大道归一”这一句话，有感而发。

如果你有保护Python源码方面的需求，Pyarmor可能是你的一个选择： https://github.com/dashingsoft/pyarmor
