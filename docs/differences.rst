.. _the differences of obfuscated scripts:

The Differences of Obfuscated Scripts
=====================================

There are something changed after Python scripts are obfuscated:

* The major version of Python in build machine should be same as in
  target machine. Because the scripts will be compiled to byte-code
  before they're obfuscated, so the obfuscated scripts can't be run by
  all the Python versions as the original scripts could. Especially
  for Python 3.6, it introduces word size instructions, and it's
  totally different from Python 3.5 and before. It's recommeded to run
  the obfuscated scripts with same major version of Python.

* If Python interpreter is compiled with Py_TRACE_REFS or Py_DEBUG, it
  will crash to run obfuscated scripts.

* The callback function set by ``sys.settrace``, ``sys.setprofile``,
  ``threading.settrace`` and ``threading.setprofile`` will be ignored by
  obfuscated scripts.

* The attribute ``__file__`` of code object in the obfuscated scripts
  will be ``<frozen name>`` other than real filename. So in the
  traceback, the filename is shown as ``<frozen name>``.

  Note that ``__file__`` of moudle is still filename. For example,
  obfuscate the script ``foo.py`` and run it::

      def hello(msg):
          print(msg)

      # The output will be 'foo.py'
      print(__file__)

      # The output will be '<frozen foo>'
      print(hello.__file__)

About Third-Party Interpreter
-----------------------------

About third-party interperter, for example Jython, and any embeded
Python C/C++ code, they should satisfy the following conditions at
least to run the obfuscated scripts:

* They must be load offical Python dynamic library, which should be
  built from the soure https://github.com/python/cpython , and the
  core source code should not be modified.

* On Linux, `RTLD_GLOBAL` must be set as loading `libpythonXY.so` by
  `dlopen`, otherwise obfuscated scripts couldn't work.

.. note::  

   Boost::python does not load `libpythonXY.so` with `RTLD_GLOBAL` by
   default, so it will raise error "No PyCode_Type found" as running
   obfuscated scripts. To solve this problem, try to call the method
   `sys.setdlopenflags(os.RTLD_GLOBAL)` as initializing.

* The module `ctypes` must be exists and `ctypes.pythonapi._handle`
  must be set as the real handle of Python dynamic library, PyArmor
  will query some Python C APIs by this handle.

.. include:: _common_definitions.txt
