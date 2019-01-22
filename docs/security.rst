.. _the security and anti-debug:

The Security and Anti-Debug
===========================

|PyArmor| will obfuscate not only the whole module file, but also each
function. For example, there is a file ``foo.py``::

  def hello():
      print('Hello world!')

  def sum(a, b):
      return a + b

|PyArmor| first obfuscates the function ``hello`` and ``sum``, then
obfuscates the whole moudle ``foo``. In the runtime, each function is
restored only as it's called and will be obfuscated as soon as code
object completed execution. So even trace code in any ``c`` debugger,
only a piece of code object could be got one time.

Protect Dynamic Library ``_pytransform``
----------------------------------------

The core functions of |PyArmor| are in the ``_pytransform``. In order
to protect it, add code to verify md5sum of this file in the obfusated
script. For example::

    import os
    from hashlib import md5
    from pytransform import lib_filename

    def check_pytransform(filename):
        with open(filename, 'rb') as f:
            return md5(f.read()).hexdigest() == 'xxxxxxxxxxxxxxxxxx'

    if not check_pytransform(libfile):
        print('%s is modified' % libfile)
        sys.exit(1)

The end user can't change this obfuscated script any more, so these
code can keep the dynamic library from hacking.

Besides, you can add any other authentication code in obfuscated
scripts to double check there is no unauthorized use. For example::

    from datetime import datetime
    if datetime.now() > datetime(2019, 2, 2):  # expired on 2019-2-2
        sys.exit(1)

If you want to hide the code more thoroughly, try to use any other
tool such as ASProtect_, VMProtect_ to protect dynamic library
``_pytransform`` which is distributed with obfuscatd scripts.

.. include:: _common_definitions.txt
