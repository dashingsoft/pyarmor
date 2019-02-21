.. _加密脚本和原脚本的区别:

加密脚本和原脚本的区别
======================

加密脚本和原来的脚本相比，存在下列一些的不同:

* 运行加密脚本的 Python 版本和加密脚本的 Python 版本必须要一致，因为加
  密的脚本实际上已经是 `.pyc` 文件，如果版本不一致，有些指令会出错。

* 执行加密角本的 Python 不能是调试版，准确的说，不能是设置了
  Py_TRACE_REFS 或者 Py_DEBUG 生成的 Python

* 使用 ``sys.settrace``, ``sys.setprofile``, ``threading.settrace`` 和
  ``threading.setprofile`` 设置的回调函数在加密脚本中将被忽略

* 代码块的属性 ``__file__`` 在加密脚本是 ``<frozen name>`` ，而不是文件
  名称，在异常信息中会看到文件名的显示是 ``<frozen name>``

  需要注意的是模块的属性 ``__file__`` 还和原来的一样，还是文件名称。加
  密下面的脚本并运行，就可以看到输出结果的不同::

      def hello(msg):
          print(msg)

      # The output will be 'foo.py'
      print(__file__)

      # The output will be '<frozen foo>'
      print(hello.__file__)


.. include:: _common_definitions.txt
