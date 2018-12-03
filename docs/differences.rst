.. _the differences of obfuscated scripts:

The Differences of Obfuscated Scripts
=====================================

There are something changed after Python scripts are obfuscated:

* Python Version in build machine must be same as in target
  machine. To be exact, the magic string value used to recognize
  byte-compiled code files (.pyc files) must be same.

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


.. include:: _common_definitions.txt
