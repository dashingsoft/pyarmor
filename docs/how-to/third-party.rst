=================================
 Work with Third-Party Libraries
=================================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen

There are countless big packages in Python world, many packages I never use and even don't know at all. It's also not easy for me to research a complex package to find which line conflicts with pyarmor, and it's difficult for me to run all of these complex packages in my local machine.

Pyarmor provides rich options to meet various needs, for complex application, please spend some time to check :doc:`../reference/man` to understand all of these options, one of them may be just for your problem. **I won't learn your application and tell you should use which options**

I'll improve pyamor make it works with other libraries as far as possible, but some
issues can't be fixed from Pyarmor side.

Generally most of problems for these third party libraries are

* they try to use low level object `frame` to get local variable or other runtime information of obfuscated scripts
* they try to visit code object directly to get something which is just pyarmor protected. The common case is using :mod:`inspect` to get source code.
* they pickle the obfuscated code object and pass it to other processes or threads.

Also check :ref:`the differences of obfuscated scripts`, if third party library use any feature changed by obfuscated scripts, it will not work with pyarmor. Especially for :term:`BCC mode`, it changes more.

The common solutions to fix third-party libraries issue

- Use RFT mode with ``--obf-code=0``

  RFT mode almost doesn't change internal structure of code object, it transforms the script in source level. :option:`--obf-code` is also required to disable code object obfuscation. The recommened options are like this::

    $ pyarmor gen --enable-rft --obf-code 0 /path/to/myapp

  First make sure it works, then try other options. For example::

    $ pyarmor gen --enable-rft --obf-code 0 --mix-str /path/to/myapp
    $ pyarmor gen --enable-rft --obf-code 0 --mix-str --assert-call /path/to/myapp

- Ignore problem scripts

  If only a few scripts are in trouble, try to obfuscate them with ``--obf-code 0``. For example, only module ``config.py`` has problem, all the other are fine, then::

    $ pyarmor cfg -p myapp.config obf_code=0
    $ pyarmor gen [other options] /path/to/myapp

  Another way is to copy plain script to overwrite the obfsucated one roughly::

    $ pyarmor gen [other options] /path/to/myapp
    $ cp /path/to/myapp/config.py dist/myapp/config.py

- Patch third-party library

  Here is an example

  .. code-block:: python

      @cherrypy.expose(alias='myapi')
         @cherrypy.tools.json_out()
         # pylint: disable=no-member
         @cherrypy.tools.authenticate()
         @cherrypy.tools.validateOptOut()
         @cherrypy.tools.validateHttpVerbs(allowedVerbs=['POST'])
         # pylint: enable=no-member
         def abc_xyz(self, arg1, arg2):
             """
             This is the doc string
             """

  If call this API with alias name "myapi" it throws me 404 Error and the API's which do not have any alias name works perfectly. Because ``cherrypy.expose`` decorator uses

  .. code-block:: python

      parents = sys._getframe(1).f_locals

  And ``sys._getframe(1)`` return unexpected frame in obfuscated scripts. But it could be fixed by patching this decorator to

  .. code-block:: python

      parents = sys._getframe(2).f_locals

  .. note::

      If :mod:`cheerypy` is also used by others, clone private one.

Third party libraries
=====================

Here are list problem libraries and possible solutions. Welcome create pull request to append new libraries sort alphabetically case insentensive.

.. list-table:: Table-1. Third party libraries
   :header-rows: 1

   * - Package
     - Status
     - Remark
   * - cherrypy
     - patch work [#patch]_
     - use sys._getframe
   * - `pandas`_
     - patch work [#patch]_
     - use sys._getframe
   * - playwright
     - patch should work [#RFT]_
     - Not verify yet
   * - `nuitka`_
     - Should work with restrict_module = 0
     - Not verify yet

.. rubric:: Footnotes

.. [#patch] the patched packge could work with Pyarmor
.. [#RFT] this package work with Pyarmor RFT mode
.. [#obfcode0] this package only work with ``--obf-code 0``
.. [#not] this package not work with Pyarmor any mode

pandas
------

Another similar example is :mod:`pandas`

.. code-block:: python

    import pandas as pd

    class Sample:
        def __init__(self):
            self.df = pd.DataFrame(
                data={'name': ['Alice', 'Bob', 'Dave'],
                'age': [11, 15, 8],
                'point': [0.9, 0.1, 0.4]}
            )

        def func(self, val: float = 0.5) -> None:
            print(self.df.query('point > @val'))

    sampler = Sample()
    sampler.func(0.3)

After obfuscated, it raises::

    pandas.core.computation.ops.UndefinedVariableError: local variable 'val' is not defined

It could be fixed by changing ``sys._getframe(self.level)`` to ``sys._getframe(self.level+1)``, ``sys._getframe(self.level+2)`` or ``sys._getframe(self.level+3)`` in ``scope.py`` of pandas.

nuitka
------

Because the obfuscated scripts could be taken as normal scripts with an extra runtime package, they also could be translated to C program by Nuitka.

I haven't tested it, but it's easy to verify it.

First disable restrict mode, and use default options to obfuscate the scripts::

    $ pyarmor cfg restrict_module=0
    $ pyarmor gen foo.py

Then nuitka the obfuscated scripts, check it works or not.

Try more options, but I think restrict options such as :option:`--private`, :option:`--restrict`, :option:`--assert-call`, :option:`--assert-import` may not work.

No disable restrict_module, run the nuitka script may raise error::

    RuntimeError: unauthorized use of script (1:871)

.. include:: ../_common_definitions.txt
