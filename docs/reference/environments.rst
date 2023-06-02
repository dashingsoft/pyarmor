.. highlight:: none

=======================
 Building Environments
=======================

Command :command:`pyarmor` runs in :term:`build machine` to generate obfuscated scripts and all the other required files.

Here list everything related to :command:`pyarmor`.

Above all it only runs in the `supported platforms`_ by `supported Python versions`_.

Command line options, `configuration options`_, `plugins`_, `hooks`_ and a few environment variables control how to generate obfuscated scripts and runtime files.

All the command line options and environment variables are described in :doc:`man`

Supported Python versions
=========================

.. table:: Table-1. Supported Python Versions
   :widths: auto

   ===================  =====  =========  =========  ==========  ======  =======  ==============
   Python Version        2.7    3.0~3.4    3.5~3.6    3.7~3.10    3.11    3.12+   Remark
   ===================  =====  =========  =========  ==========  ======  =======  ==============
   pyarmor 8 RFT Mode    No       No         No          Y         Y       N/y      [#]_
   pyarmor 8 BCC Mode    No       No         No          Y         Y       N/y
   pyarmor 8 others      No       No         No          Y         Y       N/y
   pyarmor-7             Y        Y          Y           Y         No      No
   ===================  =====  =========  =========  ==========  ======  =======  ==============

Supported platforms
===================

.. table:: Table-2. Supported Platforms (1)
   :widths: auto

   ===================  ============  ========  =======  ============  =========  =======  =======
   OS                     Windows           Apple                    Linux [#]_
   -------------------  ------------  -----------------  -----------------------------------------
   Arch                  x86/x86_64    x86_64    arm64    x86/x86_64    aarch64    armv7    armv6
   ===================  ============  ========  =======  ============  =========  =======  =======
   Themida Protection        Y           No        No         No          No       No        No
   pyarmor 8 RFT Mode        Y           Y         Y          Y           Y        Y         No
   pyarmor 8 BCC Mode        Y           Y         Y          Y           Y        N/y       No
   pyarmor 8 others          Y           Y         Y          Y           Y        Y         No
   pyarmor-7 [#]_            Y           Y         Y          Y           Y        Y         Y
   ===================  ============  ========  =======  ============  =========  =======  =======

.. table:: Table-3. Supported Platforms (2) [#]_
   :widths: auto

   ===================  ============  =========  =========  ============  =========  =======  =======
   OS                     FreeBSD        Alpine Linux                      Android
   -------------------  ------------  --------------------  -----------------------------------------
   Arch                    x86_64      x86_64     aarch64    x86/x86_64    aarch64    armv7    armv6
   ===================  ============  =========  =========  ============  =========  =======  =======
   pyarmor 8 RFT Mode        Y            Y          Y           Y           Y          Y       No
   pyarmor 8 BCC Mode        Y            Y          Y           Y           Y          Y       No
   pyarmor 8 others          Y            Y          Y           Y           Y          Y       No
   pyarmor-7                 Y            Y          Y           Y           Y          Y       Y
   ===================  ============  =========  =========  ============  =========  =======  =======

.. rubric:: notes

.. [#] ``N/y`` means not yet now, but will be supported in future.
.. [#] This Linux is built with glibc
.. [#] pyarmor-7 also supports more linux arches, refer to `Pyarmor 7.x platforms`__.
.. [#] These platforms are introduced in Pyarmor 8.3

.. important::

   pyarmor-7 is bug fixed Pyarmor 7.x version, it's same as Pyarmor 7.x, and only works with old license. Do not use it with new license, it may report ``HTTP 401 error``.

__ https://pyarmor.readthedocs.io/en/v7.7/platforms.html

Configuration options
=====================

There are 3 kinds of configuration files

* global: an ini file :file:`~/.pyarmor/config/global`
* local: an ini file :file:`./.pyarmor/config`
* private: each module may has one ini file in :term:`Local Path`. For example, :file:`./.pyarmor/foo.rules` is private configuration of module ``foo``

Use command :ref:`pyarmor cfg` to change options in configuration files.

.. _plugins:

Plugins
=======

.. versionadded:: 8.2

.. program:: pyarmor gen

Plugin is a Python script used to do some post-build work when generating obfuscated scripts.

Plugin use cases:

- Additional processing in the output path
- Fix import statement in the obfuscated script for special cases
- Add comment to :term:`outer key` file
- Rename binary extension :mod:`pyarmor_runtime` suffix to avoid name conflicts
- In Darwin use `install_name_tool` to fix :term:`extension module` :mod:`pyarmor_runtime` couldn't be loaded if Python is not installed in the standard path
- In Darwin codesign pyarmor runtime extensions

Plugin script must define attribute ``__all__`` to export plugin name.

Plugin script could be any name.

Plugin script could define one or more plugin classes:

.. py:class:: PluginName

    .. py:staticmethod:: post_build(ctx, inputs, outputs, pack=None)

       This method is optional.

       This method is called when all the obfuscated scripts and runtime files have been generated by :ref:`pyarmor gen`

       :param Context ctx: building context
       :param list inputs: all the input paths
       :param list outputs: all the output paths
       :param str pack: if not None, it's an executable file specified by :option:`--pack`

    .. py:staticmethod:: post_key(ctx, keyfile, **keyinfo)

       This method is optional.

       This method is called when :term:`outer key` has been generated by :ref:`pyarmor gen key`

       :param Context ctx: building context
       :param str keyfile: path of generated key file
       :param dict keyinfo: runtime key information

       The possible items in the ``keyinfo``:

       :key expired: expired epoch or None
       :key devices: a list for binding device hardware information or None
       :key data: binding data (bytes) or None
       :key period: period in seconds or None

    .. py:staticmethod:: post_runtime(ctx, source, dest, platform)

       This method is optional.

       This method is called when the runtime extension module ``pyarmor_runtime.so`` in the :term:`runtime package` has been generated by :ref:`pyarmor gen`.

       It may be called many times if many platforms are specified in the command line.

       :param Context ctx: building context
       :param str source: source path of pyarmor extension
       :param str dest: output path of pyarmor extension
       :param str platform: standard :term:`platform` name

To make plugin script work, configure it with script name without extension ``.py`` by this way::

    $ pyarmor cfg plugins + "script name"

Pyarmor search plugin script in these paths in turn:

- Current path
- :term:`local path`, generally ``./.pyarmor/``
- :term:`global path`, generally ``~/.pyarmor/``

Here it's an example plugin script ``fooplugin.py``

.. code-block:: python

    __all__ = ['EchoPlugin']

    class EchoPlugin:

        @staticmethod
        def post_runtime(ctx, source, dest, platform):
            print('-------- test fooplugin ----------')
            print('ctx is', ctx)
            print('source is', source)
            print('dest is', dest)
            print('platform is', platform)

Store it to local path ``.pyarmor/fooplugin.py``, and enable it::

    $ pyarmor cfg plugins + "fooplugin"

Check it, this plugin information should be printed in the console::

    $ pyarmor gen foo.py

Disable this plugin::

    $ pyarmor cfg plugins - "fooplugin"

.. _hooks:

Hooks
=====

.. versionadded:: 8.2

Hook is a Python script which is embedded into the obfuscated script, and executed when the obfuscated script is running.

When obfuscating the scripts, Pyarmor searches path ``hooks`` in the :term:`local path` and :term:`global path` in turn. If there is any same name script exists, it's called module hook script.

For example, ``.pyarmor/hooks/foo.py`` is hook script of ``foo.py``, ``.pyarmor/hooks/joker.card.py`` is hook script of ``joker/card.py``.

When generating obfuscate script by this command::

    $ pyarmor gen foo.py

``.pyarmor/hooks/foo.py`` will be inserted into the beginning of ``foo.py``.

A hook script is a normal Python script, it could do everything Python could do. And it could use 2 special function :func:`__pyarmor__` and :func:`__assert_armored__` to do some interesting work.

Note that all the source lines in the hook script are inserted into module level of original script, be careful to avoid name conflicts.

.. seealso:: :func:`__pyarmor__`  :func:`__assert_armored__`

Special hook script
-------------------

.. versionadded:: 8.3

If want to do something before obfuscated scripts are executed, it need use a special hook script ``.pyarmor/hooks/pyarmor_runtime.py``, it will be called when initializing Python extension `pyarmor_runtime`.

First create script ``.pyarmor/hooks/pyarmor_runtime.py`` and define all in the hook function :func:`bootstrap`, only this function will be called.

.. function:: bootstrap(user_data)

   :param bytes user_data: user data in runtime key
   :return: False, quit and raise protection exception
   :raises SystemExit: quit without traceback
   :raises ohter Exception: quit with traceback

An example script:

.. code-block:: python

    def bootstrap(user_data):
        # Import everything in the function, not in the module level
        import sys
        import time
        from struct import calcsize

        print('user data is', user_data)

        # Check platform
        if sys.platform == 'win32' and calcsize('P'.encode()) * 8 == 32:
            raise SystemExit('no support for 32-bit windows')

        # Check debugger in Windows
        if sys.platform == 'win32':
            from ctypes import windll
            if windll.kernel32.IsDebuggerPresent():
                print('found debugger')
                return False

        # In this example, user_data is timestamp
        if time.time() > int(user_data.decode()):
            return False

Check it, first copy this script to ``.pyarmor/hooks/pyarmor_runtime.py``::

    $ pyarmor gen --bind-data 12345 foo.py
    $ python dist/foo.py

    user data is b'12345'
    Traceback (most recent call last):
      File "dist/foo.py", line 2, in <module>
      ...
    RuntimeError: unauthorized use of script (1:10325)

.. _target environments:

=====================
 Target Environments
=====================

Obfuscated scripts run in :term:`target device`.

Supported Python versions and platforms
=======================================

Supported platforms, arches and Python versions are same as `Building Environments`_

Environment variables
=====================

A few environment variables are used by obfuscated scripts.

.. envvar:: LANG

      OS environment variable, used to select runtime error language.

.. envvar:: PYARMOR_LANG

      It's used to set language runtime error language.

      If it's set, :envvar:`LANG` is ignored.

.. envvar:: PYARMOR_RKEY

      Set search path for :term:`outer key`

Supported Third-Party Interpreter
=================================

About third-party interpreter, for example Jython, and any embedded Python C/C++ code, only they could work with CPython :term:`extension module`, they could work with Pyarmor. Check third-party interpreter documentation to make sure this.

A few known issues

* On Linux, `RTLD_GLOBAL` must be set as loading `libpythonXY.so` by `dlopen`, otherwise obfuscated scripts couldn't work.

* Boost::python does not load `libpythonXY.so` with `RTLD_GLOBAL` by default, so it will raise error "No PyCode_Type found" as running obfuscated scripts. To solve this problem, try to call the method `sys.setdlopenflags(os.RTLD_GLOBAL)` as initializing.

* `PyPy` could not work with pyarmor, it's total different from `CPython`

* WASM is not supported.

Specialized builtin functions
=============================

.. versionadded:: 8.2

There are 2 specialized builtin functions, both of them could be used without import in the obfuscated scripts.

Generally they're used with inline marker or in the hook scripts.

.. function:: __pyarmor__(arg, kwarg, name, flag)

   :param bytes name: must be ``b'hdinfo'`` or ``b'keyinfo'``
   :param int flag: must be ``1``

   **get hdinfo**

   When ``name`` is ``b'hdinfo'``, call it to get hardware information.

   :param int arg: query which kind of device
   :param str kwarg: None or device name
   :return: arg == 0 return the serial number of first harddisk
   :return: arg == 1 return mac address of first network card
   :return: arg == 2 return ipv4 address of first network card
   :return: arg == 3 return device name
   :rtype: str
   :raises RuntimeError: when something is wrong

   For example,

   .. code-block:: python

         __pyarmor__(0, None, b'hdinfo', 1)
         __pyarmor__(1, None, b'hdinfo', 1)

   In Linux, ``kwarg`` is used to get named network card or named hard disk. For example:

   .. code-block:: python

         __pyarmor__(0, "/dev/vda2", b'hdinfo', 1)
         __pyarmor__(1, "eth2", b'hdinfo', 1)

   In Windows, ``kwarg`` is used to get all network cards and hard disks. For example:

   .. code-block:: python

         __pyarmor__(0, "/0", b'hdinfo', 1)    # First disk
         __pyarmor__(0, "/1", b'hdinfo', 1)    # Second disk

         __pyarmor__(1, "*", b'hdinfo', 1)
         __pyarmor__(1, "*", b'hdinfo', 1)


   **get keyinfo**

   When ``name`` is ``b'keyinfo'``, call it to query user data in the runtime key.

   :param int arg: what information to get from runtime key
   :param kwarg: always None
   :return: arg == 0 return bind data, no bind data return empty bytes
   :rtype: Bytes
   :return: arg == 1 return expired epoch, -1 if there is no expired date
   :rtype: Long
   :return: None if something is wrong

   For example:

   .. code-block:: python

         print('bind data is', __pyarmor__(0, None, b'keyinfo', 1))
         print('expired epoch is' __pyarmor__(1, None, b'keyinfo', 1))

.. function:: __assert_armored__(arg)

   :param object arg:  arg is a module or callable object
   :returns: return ``arg`` if ``arg`` is obfuscated, otherwise, raise protection error.

   For example

   .. code-block:: python

       m = __import__('abc')
       __assert_armored__(m)

       def hello(msg):
           print(msg)

       __assert_armored__(hello)
       hello('abc')

.. include:: ../_common_definitions.txt
