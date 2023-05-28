.. highlight:: console
.. program:: pyarmor gen

============================
 Protecting system packages
============================

.. versionadded:: 8.2
.. versionchanged:: 8.2.2
                    Do not use :option:`--restrict` with :option:`--pack`, it doesn't work.

When packing the scripts, Pyarmor could also protect system packages in the bundle. The idea is to list all the dependent modules and packages and obfuscate them too.

Here it's an example to protect system packages for script ``foo.py``.

We need generate a file ``file.list`` list all the dependent modules and packages of ``foo.py`` by using PyInstaller features.

First generate ``foo.spec``::

    $ pyi-makespec foo.py

Then patch ``foo.spec``:

.. code-block:: python

    a = Analysis(
        ...
    )

    # Patched by Pyarmor to generate file.list
    _filelist = []
    _package = None
    for _src in sort([_src for _name, _src, _type in a.pure]):
        if _src.endswith('__init__.py'):
            _package = _src.replace('__init__.py', '')
            _filelist.append(_package)
        elif _package is None:
            _filelist.append(_src)
        elif not _src.startswith(_package):
            _package = None
            _filelist.append(_src)
    with open('file.list', 'w') as _file:
        _file.write('\n'.join(_filelist))
    # End of patch

Next pack ``foo.py`` by PyInstaller and generate :file:`file.list` at the same time::

    $ pyinstaller foo.py

Finally repack the script with the following options::

    $ pyarmor gen --assert-call --assert-import --pack dist/foo/foo foo.py @file.list

This example only guides how to do, please write your own patch script and use other necessary options to obfuscate scripts. For example, you could manually edit :file:`file.list` to meet needs.

====================
 Fix encoding error
====================

The default encoding is ``utf-8``, if encoding error occurs when obfuscating the scripts, set encoding to right one. For example, change default encoding to ``gbk``::

    $ pyarmor cfg encoding=gbk

When customizing runtime error message, it also could specify encoding for ``messages.cfg``. For example, set encoding to ``gbk`` by this command::

    $ pyarmor cfg messages=messages.cfg:gbk

====================
 Removing docstring
====================

It's easy to remove docstring from obfuscated scripts::

    $ pyarmor cfg optimize 2

The argument optimize specifies the optimization level of the compiler; the default value of -1 selects the optimization level of the interpreter as given by -O options. Explicit levels are 0 (no optimization; __debug__ is true), 1 (asserts are removed, __debug__ is false) or 2 (docstrings are removed too).

.. include:: ../_common_definitions.txt
