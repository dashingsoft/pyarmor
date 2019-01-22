.. _the security and anti-debug:

The Security and Anti-Debug
===========================

|PyArmor| will obfuscate not only the whole module file, but also each
function. For example, there is a file `foo.py`::

  def hello():
      print('Hello world!')

  def sum(a, b):
      return a + b

|PyArmor| first obfuscates the function `hello` and `sum`, then
obfuscates the whole moudle `foo`. In the runtime, each function is
restored only as it's called and will be obfuscated as soon as code
object completed execution. So even trace code in any ``c`` debugger,
only a piece of code object could be got one time.

.. _protect dynamic library _pytransform:

Protect Dynamic Library `_pytransform`
--------------------------------------

The core functions of |PyArmor| are in the `_pytransform`, and it's
plain. |PyArmor| use JIT technical to keep code segment from
hacking. The protect code is generated in runtime, they don't exists
in the static file. When running obfuscated scripts, `_pytransform`
loaded, then part of protect code are generated and start to run. It
will check the codesum of the whole code segment, once any code
changed, stop executiion and quit. If no code changed and no debugger
found, the next protect code is generated and continue to run. This
process is repeated several times.

If you want to hide the code more thoroughly, try to use any other
tool such as ASProtect_, VMProtect_ to protect dynamic library
`_pytransform` which is distributed with obfuscatd scripts.

Besides, it's possible to check the dynalic library in the main
script.

First get checksum of `_pytransform`, then add code to verify the
checksum of this file in the obfusated script. Assume `md5sum` is
`26d6de59a7717690363c430d6f460218`, here it's example code::

    import os
    from hashlib import md5
    from pytransform import _pytransform

    def check_pytransform(filename):
        with open(filename, 'rb') as f:
            return md5(f.read()).hexdigest() == '26d6de59a7717690363c430d6f460218'

    if not check_pytransform(_pytransform._name):
        print('%s is modified' % _pytransform._name)
        sys.exit(1)

The end user can't change this obfuscated script any more, so these
code can keep the dynamic library from hacking.

You can even add any other authentication code in obfuscated scripts
to double check there is no unauthorized use. For example::

    from datetime import datetime
    if datetime.now() > datetime(2019, 2, 2):  # expired on 2019-2-2
        sys.exit(1)

.. include:: _common_definitions.txt
