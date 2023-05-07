.. highlight:: console

===========================
 Building obfuscated wheel
===========================

The test-project hierarchy is as follows::

    $ tree test-project

    test-project
    ├── MANIFEST.in
    ├── pyproject.toml
    ├── setup.cfg
    └── src
        └── parent
            ├── child
            │   └── __init__.py
            └── __init__.py

4 directories, 5 files

The content of ``MANIFEST.in`` is::

    recursive-include dist/parent/pyarmor_runtime_00xxxx *.so

The content of ``pyproject.toml`` is:

.. code-block:: ini

    [build-system]
        requires = [
            "setuptools>=66.1.1",
            "wheel"
        ]
        build-backend = "setuptools.build_meta"

The content of ``setup.cfg`` is:

.. code-block:: ini

    [metadata]
        name = parent.child
        version = attr: parent.child.VERSION

    [options]
        package_dir =
            =dist/

        packages =
            parent
            parent.child
            parent.pyarmor_runtime_00xxxx

        include_package_data = True

:file:`src/parent/__init__.py` and :file:`src/parent/child/__init__.py` are the same:

.. code-block:: python

    VERSION = '0.0.1'

First obfuscate the package::

    $ cd test-project
    $ pyarmor gen --recursive -i src/parent

After successful execution the output is the following directory::

    $ tree dist

    dist
    └── parent
        ├── child
        │   ├── __init__.py
        │   └── __pycache__
        │       └── __init__.cpython-311.pyc
        ├── __init__.py
        └── pyarmor_runtime_00xxxx
            ├── __init__.py
            └── pyarmor_runtime.so

Next, build the wheel package::

    $ python -m build --skip-dependency-check --no-isolation

Unfortunately it raises exception:

.. code-block:: python

    * Building sdist...
    Traceback (most recent call last):
      File "/usr/lib/python3/dist-packages/setuptools/config/expand.py", line 81, in __getattr__
        return next(
               ^^^^^
    StopIteration

    The above exception was the direct cause of the following exception:

    Traceback (most recent call last):
      File "/usr/lib/python3/dist-packages/setuptools/config/expand.py", line 191, in read_attr
        return getattr(StaticModule(module_name, spec), attr_name)

From traceback we found it uses ``StaticModule``, then check the source of ``setuptools`` by the filename and line no. to find ``StaticModule`` definition. From the source code we know it uses ``ast.parse`` to get locals from the script. It's impossible for obfuscated scripts, in order to fix this problem, we need insert a line in the ``dist/parent/child/__init__.py`` like this:

.. code-block:: python

    from pyarmor_runtime_00xxxx import __pyarmor__
    VERSION = '0.0.1'
    ...

But pyarmor doesn't allow to change obfuscated scripts by default, it need disable this restriction by this command::

    $ pyarmor cfg -p parent.child.__init__ restrict_module = 0
    $ pyarmor gen --recursive -i src/parent

The option :option:`pyarmor cfg -p` ``parent.child.__init__`` lets pyarmor disable this restriction for  ``parent/child/__init__.py``.

Now patch ``dist/parent/child/__init__.py`` and rebuild wheel::

    $ python -m build --skip-dependency-check --no-isolation

**Rename runtime package and store it in sub-package**

If you would rather to rename runtime package to ``libruntime`` and store it in the sub-package ``parent.child``, you need change the content of ``MANIFEST.in`` to::

    recursive-include dist/parent/child/libruntime *.so

and change the content of ``setup.cfg`` to::

    [options]
        ...
        packages =
            parent
            parent.child
            parent.child.libruntime
        ...

And obfuscate the scripts by these configurations::

    $ pyarmor cfg package_name_format "libruntime"
    $ pyarmor gen --recursive --prefix parent.child src/parent

Don't forget to patch ``dist/parent/child/__init__.py``, then build wheel::

    $ python -m build --skip-dependency-check --no-isolation

**Further more**

In order to patch ``dist/parent/child/__init__.py`` automatically, you can write a plugin script ``.pyarmor/myplugin.py``:

.. code-block:: python

    __all__ = ['VersionPlugin']

    class VersionPlugin:

        @staticmethod
        def post_build(ctx, inputs, outputs, pack):
            script = os.path.join(outputs[0], 'parent', 'child', '__init__.py')
            with open(script, 'a') as f:
                f.write("\nVERSION = '0.0.1'")

And enable this plugin::

    $ pyarmor cfg plugins + "myplugin"

After that, each build only run the following commands::

    $ pyarmor gen --recursive --prefix parent.child src/parent
    $ python -m build --skip-dependency-check --no-isolation

.. include:: ../_common_definitions.txt
