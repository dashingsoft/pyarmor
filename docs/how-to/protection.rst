================================
 Protecting Runtime Memory Data
================================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen

Pyarmor focus on protecting Python scripts, by several irreversible obfuscation methods, now Pyarmor makes sure the obfuscated scripts can't be restored by any way.

But it isn't good at memory protection and anti-debug. If you care about runtime memory data, or runtime key verification, generally it need extra methods to prevent debugger from hacking dynamic libraries.

Pyarmor could prevent hacker from querying runtime data by valid Python C API and other Python ways, only if Python interpreter and extension module ``pyarmor_runtime`` are not hacked. This is what extra tools need to protect, the common methods include

- Signing the binary file to make sure they're not changed by others
- Using third-party binary protection tools to protect Python interpreter and extension module ``pyarmor_runtime``
- Pyarmor provides some configuration options to check interps and debuggers.
- Pyarmor provides runtime patch feature to let expert users to write C functions or python scripts to improve security.

..
  In Windows, using :option:`--enable-themida` could prevent from this attack, it could protect extension module ``pyarmor_runtime.pyd`` very well. But in the other platforms, it need extra tools to protect binary extension ``pyarmor_runtime.so``.

**Basic steps**

Above all, Python interpreter to run the obfuscated scripts can't be replaced, if the obfuscated scripts could be executed by patched Python interpreter, it's impossible to prevent others to read any Python runtime data.

At this time Pyarmor need combine :option:`--pack` and restrict mode options to implement this.

First pack the script by `PyInstaller`_ [#]_::

    $ pyinstaller foo.py

Next configure and repack the bundle, the following options are necessary [#]_::

    $ pyarmor cfg check_debugger=1 check_interp=1
    $ pyarmor gen --mix-str --assert-call --assert-import --pack dist/foo/foo foo.py

Then protect all the binary files in the output path :file:`dist/foo/` by external tools, make sure these binary files could not be replaced or modified in runtime.

Available external tools: codesign, VMProtect

.. rubric:: Note

.. [#] If pack to one file by PyInstaller, it's not enough to protect this file alone. You must make sure all the binary files extracted from this file are protected too.

.. [#] Do not use ``check_interp`` in 32-bit x86 platforms, it doesn't work

**Hook Scripts**

Expert users could write :term:`hook script` to check PyInstaller bootstrap modules to improve security.

Here it's an example to show how to do, note that it may not work in different PyInstaller version, do not use it directly.

.. code-block:: python
    :linenos:
    :emphasize-lines: 12-14

    # Hook script ".pyarmor/hooks/foo.py"

    def protect_self():
        from sys import modules

        def check_module(name, checklist):
            m = modules[name]
            for attr, value in checklist.items():
                if value != sum(getattr(m, attr).__code__.co_code):
                    raise RuntimeError('unexpected %s' % m)

        checklist__frozen_importlib = {}
        checklist__frozen_importlib_external = {}
        checklist_pyimod03_importers = {}

        check_module('_frozen_importlib', checklist__frozen_importlib)
        check_module('_frozen_importlib_external', checklist__frozen_importlib_external)
        check_module('pyimod03_importers', checklist_pyimod03_importers)

    protect_self()

The highlight lines need to be replaced with real check list. In order to get baseline, first replace function ``check_module`` with this fake function

.. code-block:: python

        def check_module(name, checklist):
            m = modules[name]
            refs = {}
            for attr in dir(m):
                value = getattr(m, attr)
                if hasattr(value, '__code__'):
                    refs[attr] = sum(value.__code__.co_code)
            print('    checklist_%s = %s' % (name, refs))


Run the following command to get baseline::

    $ pyinstaller foo.py
    $ pyarmor gen --pack dist/foo/foo foo.py

    ...
    checklist__frozen_importlib = {'__import__': 9800, ...}
    checklist__frozen_importlib_external = {'_calc_mode': 2511, ...}
    checklist_pyimod03_importers = {'imp_lock': 183, 'imp_unlock': 183, ...}

Edit hook script to restore ``check_module`` and replace empty check lists with real ones.

Using this real hook script to generate the final bundle::

    $ pyinstaller foo.py
    $ pyarmor gen --pack dist/foo/foo foo.py

**Runtime Patch**

.. versionadded:: 8.x

                  It's not implemented.

Pyarmor provides runtime patch feature so that users could write one C or python script to do any anti-debug or other checks. It will be embedded into :term:`runtime files`, and called on extension module ``pyarmor_runtime`` initialization.

The idea is to make a file  :file:`.pyarmor/hooks/pyarmor_runtime.py` or :file:`.pyarmor/hooks/pyarmor_runtime.c`, it will be inserted into runtime files when building obfuscated scripts.

.. include:: ../_common_definitions.txt
