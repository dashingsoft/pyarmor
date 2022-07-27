.. _the modes of obfuscated scripts:

The Modes of Obfuscated Scripts
===============================

PyArmor could obfuscate the scripts in many modes in order to balance the
security and performance. In most of cases, the default mode works fine. But if
the performace is to be bottle-block or in some special cases, maybe you need
understand what the differents of these modes and obfuscate the scripts in
different mode so that they could work as desired.

.. _super mode:

Super Mode
----------

This feature **Super Mode** is introduced from PyArmor 6.2.0. In this mode the
structure of PyCode_Type is changed, and byte code or word code is mapped, it's
the highest security level in PyArmor. There is only one runtime file required,
that is extension ``pytransform``, and the form of obfuscated scripts is unique,
no so called :ref:`bootstrap code` which may make some users confused. All the
obfuscated scripts would be like this::

    from pytransform import pyarmor
    pyarmor(__name__, __file__, b'\x0a\x02...', 1)

It's recommended to enable this mode in suitable cases. Now only the latest
Python versions are supported:

* Python 2.7
* Python 3.7
* Python 3.8
* Python 3.9

In order to enable it, set option ``--advanced 2`` to :ref:`obfuscate`::

    pyarmor obfuscate --advanced 2 foo.py

More usage refer to :ref:`using super mode`

.. note::

   It doesn't work to mix super mode obfuscated scripts and non-super mode ones.

.. _super plus mode:

Super Plus Mode
---------------

This is an enhancement of super mode, it will convert some functions to binary
code. It's introduced in PyArmor 7.0.1, and now only works for arch X86_64 and
Python 3.7, 3.8, 3.9. From PyArmor 7.5.0, Python 3.10 with arch X86_64 works,
and Python 3.7~3.10 for arch AARCH64 in Darwin and Linux works.

It requires ``c`` compiler. In Linux and Darwin, ``gcc`` and ``clang`` is OK. In
Windows, only ``clang.exe`` works. It could be configured by one of these ways:

* If there is any ``clang.exe``, it's OK if it could be run in any path.
* Download and install Windows version of `LLVM <https://releases.llvm.org>`_
* Download `https://pyarmor.dashingsoft.com/downloads/tools/clang-9.0.zip`, it's
  about 26M bytes, there is only one file in it. Unzip it and save ``clang.exe``
  to ``$HOME/.pyarmor/``. ``$HOME`` is home path of current logon user, check the
  environment variable ``HOME`` to get the real path.

After ``c`` compiler works, enable super plus mode by ``--advanced 5``::

  pyarmor obfuscate --advanced 5 foo.py

Only partial functions in the module will be obfuscated by spp mode, all the
others are still obfuscated by super mode. The functions using any feature not
supported by spp mode will be ignored automatically, if something is wrong with
this module in super plus mode, insert one line at the beginning of the module
to ignore the module manually::

  # pyarmor options: no-spp-mode

Super plus mode will scan from the first line, ignore blank lines, parse the
line starts with ``#``, and stop scanning for any other line. If it finds one
line begins with ``pyarmor options``, it will read the options after that. It
also works in the docstring to ignore ``function`` or ``class``, for example:

.. code-block:: python

    def foo(a, b):
        '''pyarmor options: no-spp-mode'''
        pass

There are a few differences in the spp mode:

* Calling `raise` without argument not in the exception handler will raise
  different exception.

.. code-block:: python

    >>> raise
    RuntimeError: No active exception to reraise

    # In spp mode
    >>> raise
    UnboundlocalError: local variable referenced before assignment

* Some exception messages may different from the plain script.

* Most of function attributes which starts with `__` doesn't exists,
  or the value is different from the original.

Unsupport features for spp mode:

.. code-block:: python

    unsupport_nodes = (
        ast.ExtSlice,

        ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith,
        ast.Await, ast.Yield, ast.YieldFrom, ast.GeneratorExp,

        ast.NamedExpr,

        ast.MatchValue, ast.MatchSingleton, ast.MatchSequence,
        ast.MatchMapping, ast.MatchClass, ast.MatchStar,
        ast.MatchAs, ast.MatchOr
    )

And unsupport functions:

* exec,
* eval
* super
* locals
* sys._getframe
* sys.exc_info

For example, the following functions are not obfuscated by super plus
mode, because they use unsupported features or unsupported functions:

.. code-block:: python

   async def nested():
       return 42

   def foo1():
       for n range(10):
           yield n

   def foo2():
      frame = sys._getframe(2)
      print('parent frame is', frame)

.. note::

   Super plus mode is not available in the trial version.

.. _advanced mode:

Advanced Mode
-------------

This feature **Advanced Mode** is introduced from PyArmor 5.5.0. In this mode
the structure of PyCode_Type is changed a little to improve the security. And a
hook also is injected into Python interpreter so that the modified code objects
could run normally. Besides if some core Python C APIs are changed unexpectedly,
the obfuscated scripts in advanced mode won't work. Because this feature is
highly depended on the machine instruction set, it's only available for x86/x64
arch now. And pyarmor maybe makes mistake if Python interpreter is compiled by
old gcc or some other `C` compiles. It's welcome to report the issue if Python
interpreter doesn't work in advanced mode.

Take this into account, the advanced mode is disabled by default. In order to
enable it, pass option ``--advanced`` to command :ref:`obfuscate`::

    pyarmor obfuscate --advanced 1 foo.py

**Upgrade Notes**:

Before upgrading, please estimate Python interpreter in product environments to
be sure it works in advanced mode. Here is the guide

https://github.com/dashingsoft/pyarmor-core/tree/v5.3.0/tests/advanced_mode/README.md

It is recommended to upgrade in the next minor version.

.. note::

   In trial version the module could not be obfuscated by advanced
   mode if there are more than about 30 functions in this module, (It
   still could be obfuscated by non-advanced mode).

.. important::

   For Python3.9 advanced mode isn't supported. It's recommended to use super
   mode for any Python version which works with super mode.

.. _vm mode:

VM Mode
--------

VM mode is introduced since 6.3.3. VM mode is based on code virtualization, it
uses a strong vm tool to protect the core algorithm of dynamic library. This
mode is an enhancement of advanced mode and super mode.

Enable vm mode with advanced mode by this way::

    pyarmor obfuscate --advanced 3 foo.py

Enable vm mode with super mode by this way::

    pyarmor obfuscate --advanced 4 foo.py

Though vm mode improves the security remarkably, but the size of dynamic library
is increased, and the performance is reduced. The original size is about
600K~800K, but in vm mode the size is about 4M. About the performances, refer to
:ref:`the Performance of Obfuscated Scripts` to test it.

.. _obfuscating code mode:

Obfuscating Code Mode
---------------------

In a python module file, generally there are many functions, each
function has its code object.

* obf_code == 0

The code object of each function will keep it as it is.

* obf_code == 1 (Default)

In this case, the code object of each function will be obfuscated in
different ways depending on wrap mode.

* obf_code == 2

Almost same as obf_mode 1, but obfuscating bytecode by more complex
algorithm, and so slower than the former.

.. _wrap mode:

Wrap Mode
---------

.. note::

    For super mode, wrap mode is always enabled, it can't be disabled
    in super mode.

* wrap_mode == 0

When wrap mode is off, the code object of each function will be
obfuscated as this form::

    0   JUMP_ABSOLUTE            n = 3 + len(bytecode)

    3    ...
         ... Here it's obfuscated bytecode of original function
         ...

    n   LOAD_GLOBAL              ? (__armor__)
    n+3 CALL_FUNCTION            0
    n+6 POP_TOP
    n+7 JUMP_ABSOLUTE            0

When this code object is called first time

1. First op is JUMP_ABSOLUTE, it will jump to offset n

2. At offset n, the instruction is to call PyCFunction
   `__armor__`. This function will restore those obfuscated bytecode
   between offset 3 and n, and move the original bytecode at offset 0

3. After function call, the last instruction is to jump to
   offset 0. The really bytecode now is executed.

After the first call, this function is same as the original one.

* wrap_mode == 1 (Default)

When wrap mode is on, the code object of each function will be wrapped
with `try...finally` block::

    LOAD_GLOBALS    N (__armor_enter__)     N = length of co_consts
    CALL_FUNCTION   0
    POP_TOP
    SETUP_FINALLY   X (jump to wrap footer) X = size of original byte code

    Here it's obfuscated bytecode of original function

    LOAD_GLOBALS    N + 1 (__armor_exit__)
    CALL_FUNCTION   0
    POP_TOP
    END_FINALLY

When this code object is called each time

1. `__armor_enter__` will restore the obfuscated bytecode

2. Execute the real function code

3. In the final block, `__armor_exit__` will obfuscate bytecode again.

.. _obfuscating module mode:

Obfuscating module Mode
-----------------------

* obf_mod == 1

The final obfuscated scripts would like this::

    __pyarmor__(__name__, __file__, b'\x02\x0a...', 1)

The third parameter is serialized code object of the Python
script. It's generated by this way::

    PyObject *co = Py_CompileString( source, filename, Py_file_input );
    obfuscate_each_function_in_module( co, obf_mode );
    char *original_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_whole_module( original_code  );
    sprintf( buffer, "__pyarmor__(__name__, __file__, b'%s', 1)", obfuscated_code );

* obf_mod == 2 (Default)

Use different cipher algorithm, more security and faster, new since v6.3.0

* obf_mod == 0

In this mode, the last statement would be like this to keep the serialized module as it is::

    sprintf( buffer, "__pyarmor__(__name__, __file__, b'%s', 0)", original_code );

And the final obfuscated scripts would be::

    __pyarmor__(__name__, __file__, b'\x02\x0a...', 0)

All of these modes only could be changed in the project for now, refer to
:ref:`Obfuscating Scripts With Different Modes`

.. _restrict mode:

Restrict Mode
-------------

Each obfuscated script has its own restrict mode used to limit the usage of this
script. When importing an obfuscated module and using any function or attribute,
the restrict mode will be checked at first, raises protection exception if the
restrict mode is violated.

There are 5 restrict mode, mode 2 and 3 are only for standalone scripts, mode 4
is mainly for obfuscated packages, mode 5 for both.

* Mode 1

In this mode, the obfuscated scripts can't be changed at all. For example,
append one `print` statement at the end of the obfuscated script `foo.py`::

    __pyarmor__(__name__, __file__, b'...', 1)
    print('This is obfuscated module')

This script will raise restrict exception when it's imported.

* Mode 2

In this mode, the obfuscated scripts can't be imported from plain script, and
the main script must be obfuscated as :ref:`entry script`. It could be run by
Python interpreter directly, or imported by other obfuscated scripts. When it's
imported, it will check the caller and the main script, and make sure both of
them are obfuscated.

For example, `foo2.py` is obfuscated by mode 2. It can be run like this::

    python foo2.py

But try to import it from any plain script. For example::

    python -c'import foo2'

It will raise protection exception.

* Mode 3

It's an enhancement of mode 2, it also protects module attributes. When visiting
any module attribute or calling any module function, the caller will be checked
and raise protection exception if the caller is not obfuscated.

* Mode 4

It's almost same as mode 3, the only difference is that it doesn't check the
main script is obfuscated or not when it's imported.

It's mainly used to obfuscate the Python package. The common way is that the
`__init__.py` is obfuscated by restrict mode 1, all the other modules in this
package are obfuscated by restrict mode 4.

For example, there is package `mypkg`::

    mypkg/
        __init__.py
        private_a.py
        private_b.py

In the ``__init__.py``, define public functions and attributes which are used by
plain scripts:

.. code:: python

    from . import private_a as ma
    from . import private_b as mb

    public_data = 'welcome'

    def proxy_hello():
        print('Call private hello')
        ma.hello()

    def public_hello():
        print('This is public hello')

In the ``private_a.py``, define private functions and attributes:

.. code:: python

    import sys

    password = 'xxxxxx'

    def hello():
        print('password is: %s' % password)

Then obfuscate ``__init__.py`` by mode 1 and others by mode 4 in the `dist`::

    dist/
        __init__.py
        private_a.py
        private_b.py

Now do some tests from Python interpreter:

.. code:: python

    import dist as mypkg

    # It works
    mypkg.public_hello()
    mypkg.proxy_hello()
    print(mypkg.public_data)
    print(mypkg.ma)

    # It doesn't work
    mypkg.ma.hello()
    print(mypkg.ma.password)

* Mode 5 (New in v6.4.0)

Mode 5 is an enhancement of mode 4, it also protects the globals in the
frame. When running any function in the mode 5, the outer plain script could get
nothing from the globals of this function. It's highest security, works for both
of standalone scripts and packages. But it will check each global variable in
runtime, this may reduce the performance.

* Mode 100+ (New in v6.7.4)

This mode is an enhancement for mode 1-5 to enable an extra feature: module
attribute ``__dict__`` restriction. So mode 101 equals mode 1 plus this
feature, and mode 102 equals mode 2 plus this feature, and so on.

If this feature is enabled, the module attribute ``__dict__`` looks like an
empty dictionary. And there are something changed for this module:

* All the objects in the `module.__dict__` will not be clean when cleanuping
  this module
* After this module has been imported, `module.__dict__` can't be inserted or
  deleted an item both implicitly and explicitly
* The function of `dirs`, `vars` will also return empty

For example,

.. code:: python

    # This is foo6.py, obfuscated with mode 105

    # It's OK
    global var_a
    var_a = 'This is global variable a'
    var_b = 'This is global variable b'
    del var_a

    def fabico():
        global var_b

        # Wrong, remove item from module.__dict__ not in modul level
        del var_b

    # This is foo.py, obfuscated with mode 101

    import foo6

    # The result is {}
    foo6.__dict__

    # The output is {}
    vars(foo6)

    # The output is []
    dirs(foo6)

    # OK
    foo6.var_a = 'Changed by foo'

    # Wrong, add new item to __dict__
    foo6.__dict__['var_c'] = 1
    foo6.var_d = 2

This feature only works for Python 3.7 and later, it takes no effect for
previous Python version.

.. important::

   The protection of module attributes for mode 3 and 4 is introduced in
   v6.3.7. Before that, only function calling is protected.

   Do not import any function or class from private module in the public
   ``__init__.py``, because only module attributes are protected::

       # Right, import module only
       from . import private_a as ma

       # Wrong, function `hello` is opened for plain script
       from .private_a import hello

.. note::

   Mode 2 and 3 could not be used to obfuscate the Python package, because the
   main script must be obfuscated either, otherwise it can't not be imported.

.. note::

   Restrict mode is applied to one single script, different scripts could be
   obfuscated by different restrict mode.

.. note::

   If the scripts are obfuscated by ``--obf-code=0``, it will be taken as plain
   script.

   Let's say there're three scripts in a package

   1. ``__init__.py`` : [ restrict_mode : 1, obf-code 2]
   2. ``foo.py`` : [restrict_mode : 4, obf-code 2]
   3. ``bar.py`` : [restrict_mode : 1, obf-code 0]

   Here ``bar.py`` would appear as plain script at runtime due to obf-code=0.

   So ``foo.py`` cannot be imported inside ``bar.py`` since it would appear like
   a plain script and hence cannot import ``foo.py``. But ``foo.py`` can be
   imported inside ``__init__.py`` since it has obf-code=2 and hence would work.

From PyArmor 5.2, Restrict Mode 1 is default.

Obfuscating the scripts by other restrict mode::

    pyarmor obfuscate --restrict=2 foo.py
    pyarmor obfuscate --restrict=4 foo.py

    # For project
    pyarmor config --restrict=2
    pyarmor build -B

All the above restricts could be disabled by this way if required::

    pyarmor obfuscate --restrict=0 foo.py

    # For project
    pyarmor config --restrict=0
    pyarmor build -B

If the obfuscates scripts uses the license generated by :ref:`licenses`, in
order to disable all the restricts, pass option ``--disable-restrict-mode`` to
command :ref:`licenses`. For example::

    pyarmor licenses --disable-restrict-mode r001

    pyarmor obfuscate --with-license=licenses/r001/license.lic foo.py

    # For project
    pyarmor config --with-license=licenses/r001/license.lic
    pyarmor build -B

For more examples, refer to :ref:`Improving the security by restrict mode`

From PyArmor 5.7.0, there is another implicit restrict for obfuscate scripts:
the :ref:`bootstrap code` must be in the obfuscated scripts and must be
specified as entry script. For example, there are 2 scripts `foo.py` and
`test.py` in the same folder, obfuscated by this command::

    pyarmor obfuscate foo.py

Inserting the `bootstrap code` into obfuscated script `dist/test.py` by manual
doesn't work, because it's not specified as entry script. It must be run this
command to insert the :ref:`bootstrap code`::

    pyarmor obfuscate --no-runtime --exact test.py

If you need insert the :ref:`bootstrap code` into plain script, first obfuscate
an empty script like this::

    echo "" > pytransform_bootstrap.py
    pyarmor obfuscate --no-runtime --exact pytransform_bootstrap.py

Then import `pytransform_bootstrap` in the plain script.

.. include:: _common_definitions.txt
