.. _the security of pyarmor:

The Security of PyArmor
=======================

|PyArmor| will obfuscate python module in two levels. First obfucate
each function in module, then obfuscate the whole module file. For
example, there is a file `foo.py`::

  def hello():
      print('Hello world!')

  def sum(a, b):
      return a + b

  if __name == '__main__':
      hello()
      print('1 + 1 = %d' % sum(1, 1))

|PyArmor| first obfuscates the function `hello` and `sum`, then
obfuscates the whole moudle `foo`. In the runtime, only current called
function is restored and it will be obfuscated as soon as code object
completed execution. So even trace code in any ``c`` debugger, only a
piece of code object could be got one time.

.. _protect dynamic library _pytransform:

Cross Protection for `_pytransform`
-----------------------------------

The core functions of |PyArmor| are written by `c` in the dynamic
library `_pytransform`. `_pytransform` protects itself by JIT
technical, and the obfuscated scripts is protected by `_pytransform`.
on the other hand, the dynamic library `_pytransform` is checked in
the obfuscated script to be sure it's not changed. This is called
Cross Protection.

The dynamic library `_pytransform.so` uses JIT technical to achieve
two tasks:

* Keep the des key used to encrypt python scripts from tracing by any
  c debugger
* The code segment can't be changed any more. For example, change
  instruction `JZ` to `JNZ`, so that `_pytransform.so` can execute
  even if checking license failed

How JIT works?

First the instruction set based on GNU lightning are defined

Then write some core functions by this instruction set in c file, maybe like this::

    t_instruction protect_set_key_iv = {
        // function 1
        0x80001,
        0x50020,
        ...

        // function 2
        0x80001,
        0xA0F80,
        ...
    }

    t_instruction protect_decrypt_buffer = {
        // function 1
        0x80021,
        0x52029,
        ...

        // function 2
        0x80001,
        0xC0901,
        ...
    }

Build `_pytransform.so`, calculate the codesum of code segment of
`_pytransform.so`

Replace some instruction with real codesum got before, and obfuscate
all the instructions except "function 1" in c file

Finally build `_pytransform.so` with this changed c file.

When running obfuscated script, `_pytransform.so` loaded. Once a
proected function is called, it will

1. Generate code from `function 1`
2. Run `function 1`:
    * check codesum of code segment, if not expected, quit
    * check tickcount, if too long, quit
    * check there is any debugger, if found, quit
    * clear hardware breakpoints if possible
    * restore next function `function 2`
3. Generate code from `function 2`
4. Run `function 2`, do same thing as `function 1`

After repeat some times, the real code is called.

In order to protect `_pytransform` in Python script, some extra code
need to inserted into the script. Here is sample code::

    import pytransform
    from hashlib import md5

    MD5SUM_LIB_PYTRANSFORM = 'ca202268bbd76ffe7df10c9ef1edcb6c'

    CO_SELF_SIZES = 46, 36
    CO_DECORATOR_SIZES = 135, 122, 89, 86, 60
    CO_DLLMETHOD_SIZES = 22, 19, 16
    CO_LOAD_LIBRARY_SIZES = 662, 648, 646, 634, 628, 456
    CO_PYARMOR_INIT_SIZES = 58, 56, 40
    CO_PYARMOR_RUNTIME_SIZES = 146, 144, 138, 127, 121, 108
    CO_INIT_PYTRANSFORM_SIZES = 83, 80, 58
    CO_INIT_RUNTIME_SIZES = 74, 52

    CO_SELF_NAMES = ('pytransform', 'pyarmor_runtime', '__pyarmor__', '__name__', '__file__')
    CO_DECORATOR_NAMES = ('isinstance', 'str', 'encode', 'int', '_get_error_msg', 'PytransformError')
    CO_DLLMETHOD_NAMES = ()
    CO_LOAD_LIBRARY_NAMES = ('None', 'os', 'path', 'dirname', '__file__', 'normpath', 'platform', 'system',
                             'lower', 'abspath', 'join', 'PytransformError', 'exists', 'struct', 'calcsize',
                             'encode', 'format_platname', 'basename', 'cdll', 'LoadLibrary', 'Exception', 'set_option',
                             'sys', 'byteorder', 'c_char_p', '_debug_mode')
    CO_PYARMOR_INIT_NAMES = ('_pytransform', 'None', '_load_library', 'get_error_msg', '_get_error_msg', 'c_char_p', 'restype', 'init_pytransform')
    CO_PYARMOR_RUNTIME_NAMES = ('_pytransform', 'None', 'PytransformError', 'pyarmor_init', 'init_runtime', 'print', 'sys', 'exit')
    CO_INIT_PYTRANSFORM_NAMES = ('sys', 'version_info', 'PYFUNCTYPE', 'c_int', 'c_void_p', '_pytransform', 'pythonapi', '_handle')
    CO_INIT_RUNTIME_NAMES = ('pyarmor_init', 'PYFUNCTYPE', 'c_int', '_pytransform')

    def check_lib_pytransform(filename):
        expected = MD5SUM_LIB_PYTRANSFORM
        with open(filename, 'rb') as f:
            if not md5(f.read()).hexdigest() == expected:
                sys.exit(1)

    def check_code_object(f_code, sizes, names):
        return set(f_code.co_names) <= set(names) and len(f_code.co_code) in sizes

    def check_obfuscated_script():
        co = sys._getframe(3).f_code
        if not check_code_object(co, CO_SELF_SIZES, CO_SELF_NAMES):
            sys.exit(1)

    def check_mod_pytransform():
        code = '__code__' if sys.version_info[0] == 3 else 'func_code'
        closure = '__closure__' if sys.version_info[0] == 3 else 'func_closure'

        co = getattr(pytransform.dllmethod, code).co_consts[1]
        if not check_code_object(co, CO_DECORATOR_SIZES, CO_DECORATOR_NAMES):
            sys.exit(1)

        for item in [
                ('dllmethod', CO_DLLMETHOD_SIZES, CO_DLLMETHOD_NAMES),
                ('init_pytransform', CO_DECORATOR_SIZES, CO_DECORATOR_NAMES),
                ('init_runtime', CO_DECORATOR_SIZES, CO_DECORATOR_NAMES),
                ('_load_library', CO_LOAD_LIBRARY_SIZES, CO_LOAD_LIBRARY_NAMES),
                ('pyarmor_init', CO_PYARMOR_INIT_SIZES, CO_PYARMOR_INIT_NAMES),
                ('pyarmor_runtime', CO_PYARMOR_RUNTIME_SIZES, CO_PYARMOR_RUNTIME_NAMES)]:
            co = getattr(getattr(pytransform, item[0]), code)
            if not check_code_object(co, item[1], item[2]):
                sys.exit(1)

        for item in [
                ('init_pytransform', CO_INIT_PYTRANSFORM_SIZES, CO_INIT_PYTRANSFORM_NAMES),
                ('init_runtime', CO_INIT_RUNTIME_SIZES, CO_INIT_RUNTIME_NAMES)]:
            co_closures = getattr(getattr(pytransform, item[0]), closure)
            co = getattr(co_closures[0].cell_contents, code)
            if not check_code_object(co, item[1], item[2]):
                sys.exit(1)

    def protect_pytransform():
        try:
            # Be sure obfuscated script is not changed
            check_obfuscated_script()

            # Be sure 'pytransform.py' is not changed
            check_mod_pytransform()

            # Be sure '_pytransform.so' is not changed
            check_lib_pytransform(pytransform._pytransform._name)
        except Exception as e:
            print(e)
            sys.exit(1)

    if __name__ == '__main__':
        protect_pytransform()

If you want to hide the code more thoroughly, try to use any other
tool such as ASProtect_, VMProtect_ to protect dynamic library
`_pytransform` which is distributed with obfuscatd scripts.

.. include:: _common_definitions.txt
