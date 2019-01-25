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

    MD5SUM_PYTRANSFORM_PY = '46995aee690c412c8e65da764b892562'
    MD5SUM_PYTRANSFORM_SO = 'ca202268bbd76ffe7df10c9ef1edcb6c'

    # Extra import to check expired date by NTP
    from ntplib import NTPClient
    from time import mktime, strptime

    NTP_SERVER = 'europe.pool.ntp.org'
    EXPIRED_DATE = '20190202'

    def check_md5sum(filename, expected):
        with open(filename, 'rb') as f:
            if not md5(f.read()).hexdigest() == expected:
                sys.exit(1)

    def protect_pytransform():
        # Be sure obfuscated script is not changed
        with open(__file__, 'r') as f:
            lines = f.readlines()
            if not ((len(lines[:4]) == 3) and
                    (lines[0].strip() == 'from pytransform import pyarmor_runtime') and
                    (lines[1].strip() == 'pyarmor_runtime()') and
                    (lines[2].startswith('__pyarmor__'))):
                sys.eixt(1)

        # Be sure 'pytransform.py' is not changed, maybe __file__ is 'pytransform.pyc'
        check_md5sum(pytransform.__file__, MD5SUM_PYTRANSFORM_PY)
        # Be sure '_pytransform.so' is not changed
        check_md5sum(pytransform._pytransform._name, MD5SUM_PYTRANSFORM_SO)

    if __name__ == '__main__':
        protect_pytransform()

If you want to hide the code more thoroughly, try to use any other
tool such as ASProtect_, VMProtect_ to protect dynamic library
`_pytransform` which is distributed with obfuscatd scripts.

.. include:: _common_definitions.txt
