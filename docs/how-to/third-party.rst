=================================
 Work with Third-Party Libraries
=================================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen

There are countless big packages in the Python world, many packages I never use and which I don't know at all. It's also not easy for me to research a complex package to find which line conflicts with pyarmor, and it's difficult for me to run all of these complex packages on my local machine.

Pyarmor provides rich options to meet various needs, for complex applications, please spend some time checking :doc:`../reference/man` to understand all of these options, one of them may be just for your problem. **I won't learn your application and tell you should use which options**

I'll improve pyarmor and make it work with other libraries as far as possible, but some issues can't be fixed from Pyarmor side.

Generally most of problems for these third party libraries are

* they try to use low level object `frame` to get local variable or other runtime information of obfuscated scripts
* they try to visit code object directly to get something which is just pyarmor protected. The common case is using :mod:`inspect` to get source code.
* they pickle the obfuscated code object and pass it to other processes or threads.

Also check :ref:`the differences of obfuscated scripts`, if third party library uses any feature changed by obfuscated scripts, it will not work with pyarmor. Especially for :term:`BCC mode`, it changes more.

The common solutions to fix third-party libraries issue

- Use RFT mode with ``--obf-code=0``

  RFT mode almost doesn't change internal structure of code object, it transforms the script in source level. :option:`--obf-code` is also required to disable code object obfuscation. The recommended options are like this::

    $ pyarmor gen --enable-rft --obf-code 0 /path/to/myapp

  First make sure it works, then try other options. For example::

    $ pyarmor gen --enable-rft --obf-code 0 --mix-str /path/to/myapp
    $ pyarmor gen --enable-rft --obf-code 0 --mix-str --assert-call /path/to/myapp

- Ignore problem scripts

  If only a few scripts are in trouble, try to obfuscate them with ``--obf-code 0``. For example, if only module ``config.py`` has problem, all the other are fine, then::

    $ pyarmor cfg -p myapp.config obf_code=0
    $ pyarmor gen [other options] /path/to/myapp

  Another way is to copy plain script to overwrite the obfuscated one roughly::

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

Here are the list of problem libraries and possible solutions. You are welcome to create a pull request to append new libraries (sort alphabetically case insensitivity).

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

.. [#patch] the patched package could work with Pyarmor
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

First disable restrict mode::

    $ pyarmor cfg restrict_module=0

Next use default options to obfuscate the scripts::

    $ pyarmor gen foo.py

Finally nuitka the obfuscated script ``dist/foo.py``, check whether it works or not.

Try more options, but I think restrict options such as :option:`--private`, :option:`--restrict`, :option:`--assert-call`, :option:`--assert-import` may not work.

.. note::

   It may requires v9.0.8+ and non-trial version. Because Nuitka will convert package `pyarmor_runtime_000000/__init__.py` to `pyarmor_runtime_000000_init_.py`, it also results in ``RuntimeError: unauthorized use of script``, this is fixed in v9.0.8

streamlit
---------

It need change default configurations. At least::

    $ pyarmor cfg restrict_module=0
    $ pyarmor cfg clear_module_co=0

This first one solves issue `RuntimeError: unauthorized use of script (1:1102)`

Then second one solves issue `RuntimeError: the format of obfuscated script is incorrect (1:1082)`

Now obfuscate the scripts::

    $ pyarmor gen foo.py

**It may still not work because of Streamlit may patch code object by itself**

.. include:: ../_common_definitions.txt
