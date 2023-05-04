================================
 Protecting Runtime Memory Data
================================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen

Pyarmor focus on protecting Python scripts, by several irreversible obfuscation methods, now Pyarmor make sure the obfuscated scripts can't be restored by any way.

But it isn't good at memory protection and anti-debug. If you care about runtime memory data, or runtime key verification, generally it need extra methods to prevent debugger from hacking dynamic libraries.

Pyarmor could make sure hacker can't get runtime data by valid Python C API and other Python ways, only if Python interpreter and extension module ``pyarmor_runtime`` are not hacked. This is what extra tools need to do, the common methods include

- Signing the binary file to make sure they're not changed by others
- Using third-party binary protection tools to protect Python interpreter and extension module ``pyarmor_runtime``
- Pyarmor provides some configuration item to check interps and debugger.
- Pyarmor provides runtime patch feature to let expert users to write C functions or python scripts to improve security.

..
  In Windows, using :option:`--enable-themida` could prevent from this attack, it could protect extension module ``pyarmor_runtime.pyd`` very well. But in the other platforms, it need extra tools to protect binary extension ``pyarmor_runtime.so``.

**Basic steps**

Above all, Python interpreter to run the obfuscated scripts can't be replaced, if the obfuscated scripts could be executed by patched Python interpreter, it's impossible to prevent others to read any Python runtime data.

At this time Pyarmor need combine :option:`--pack` and restrict mode options to implement this.

First pack the script by `PyInstaller`_::

    $ pyinstaller foo.py

Next configure and repack the bundle, the following options are necessary::

    $ pyarmor cfg check_debugger=1
    $ pyarmor gen --mix-str --assert-call --assert-import --restrict --pack dist/foo/foo foo.py

Then protect all the binary files in the output path :file:`dist/foo/` by other tools, make sure these binary files could not be replaced or modified in runtime.

Available external tools: codesign, VMProtect

.. rubric:: Note

If pack to one file by PyInstaller, it's not enough to protect this file alone. You must make sure all the binary files extracted from this file are protected too.

**Runtime Patch**

.. versionadded:: 8.x

                  It's not implemented.

Pyarmor provides runtime patch feature so that users could write one C or python script to do any anti-debug or other works. It will be embedded into :term:`runtime files`, and called on extension module ``pyarmor_runtime`` initialization.

The idea is to make a file  :file:`.pyarmor/hooks/pyarmor_runtime.py` or :file:`.pyarmor/hooks/pyarmor_runtime.c`, it will be inserted into runtime files when building obfuscated scripts.

.. include:: ../_common_definitions.txt
