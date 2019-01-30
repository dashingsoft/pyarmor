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
On the other hand, the dynamic library `_pytransform` is checked in
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

First PyArmor defines an instruction set based on GNU lightning.

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

Replace the related instructions with real codesum got before, and
obfuscate all the instructions except "function 1" in c file. The
updated file maybe likes this::

    t_instruction protect_set_key_iv = {
        // plain function 1
        0x80001,
        0x50020,
        ...

        // obfuscated function 2
        0xXXXXX,
        0xXXXXX,
        ...
    }

    t_instruction protect_decrypt_buffer = {
        // plain function 1
        0x80021,
        0x52029,
        ...

        // obfuscated function 2
        0xXXXXX,
        0xXXXXX,
        ...
    }

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

After repeat some times, the real code is called. All of that is to be
sure there is no breakpoint in protection code.

In order to protect `_pytransform` in Python script, some extra code
will be inserted into the entry script before the line ``if __name__
== '__main__'`` when obfuscating scripts::

    def protect_pytransform():

        import pytransform

        #
        # Be sure the obfuscated script self is not hacked
        #
        def check_obfuscated_script():
            CO_SIZES = 46, 36
            CO_NAMES = set(['pytransform', 'pyarmor_runtime', '__pyarmor__',
                            '__name__', '__file__'])
            co = pytransform.sys._getframe(3).f_code
            if not ((set(co.co_names) <= CO_NAMES)
                    and (len(co.co_code) in CO_SIZES)):
                raise RuntimeError('Unexpected obfuscated script')

        #
        # Be sure pytransform._pytransform._name isn't hacked here
        #
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

        #
        # Be sure dynamic library file isn't hacked
        #
        def check_lib_pytransform(filename):
            size = 0x{size:X}
            n = size >> 2
            with open(filename, 'rb') as f:
                buf = f.read(size)
            fmt = 'I' * n
            checksum = sum(pytransform.struct.unpack(fmt, buf)) & 0xFFFFFFFF
            if not checksum == 0x{checksum:X}:
                raise RuntimeError("Unexpected %s" % filename)

        try:
            check_obfuscated_script()
            check_mod_pytransform()
            check_lib_pytransform(pytransform._pytransform._name)
        except Exception as e:
            print("Protection Fault: %s" % e)
            pytransform.sys.exit(1)

    protect_pytransform()

    if __name__ == '__main__':
        ...

If you want to hide the code more thoroughly, try to use any other
tool such as ASProtect_, VMProtect_ to protect dynamic library
`_pytransform` which is distributed with obfuscatd scripts.

.. include:: _common_definitions.txt
