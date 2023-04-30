=============================
 Customization and Extension
=============================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen

Pyarmor provides the following ways to extend:

- Using :ref:`pyarmor cfg` to change default configurations
- Using :term:`plugin script` to customize all generated files
- Using :term:`hook script` to extend features in obfuscated scripts

Changing runtime package name
=============================

.. versionadded:: 8.2 [#]_

By default the runtime package name is ``pyarmor_runtime_xxxxxx``

This name is variable with any valid package name. For example, set it to ``my_runtime``::

    pyarmor cfg package_name_format "my_runtime"

.. [#] Pyarmor trial version could not change runtime package name

Using plugin to fix loading issue in darwin
===========================================

.. versionadded:: 8.2

In darwin, if Python is not installed in the standard path, the obfuscated scripts may not work because :term:`extension module` ``pyarmor_runtime`` in the :term:`runtime package` could not be loaded.

Let's check the dependencies of ``pyarmor_runtime.so``::

    $ otool -L dist/pyarmor_runtime_000000/pyarmor_runtime.so

    dist/pyarmor_runtime_000000/pyarmor_runtime.so:

	pyarmor_runtime.so (compatibility version 0.0.0, current version 1.0.0)
        ...
	@rpath/lib/libpython3.9.dylib (compatibility version 3.9.0, current version 3.9.0)
        ...

Suppose :term:`target device` has no ``@rpath/lib/libpython3.9.dylib``, but ``@rpath/lib/libpython3.9.so``, in this case ``pyarmor_runtime.so`` could not be loaded.

We can create a plugin script :file:`.pyarmor/conda.py` to fix this problem

.. code-block:: python

    __all__ = ['CondaPlugin']

    class CondaPlugin:

        def _fixup(self, target):
            from subprocess import check_call
            check_call('install_name_tool -change @rpath/lib/libpython3.9.dylib @rpath/lib/libpython3.9.so %s' % target)
            check_call('codesign -f -s - %s' % target)

        @staticmethod
        def post_runtime(ctx, source, target, platform):
            if platform.startswith('darwin.'):
                print('using install_name_tool to fix %s' % target)
                self._fixup(target)

Enable this plugin and generate the obfusated script again::

    $ pyarmor cfg plugins + "conda"
    $ pyarmor gen foo.py

.. seealso:: :ref:`plugins`

Using hook to bind script to docker id
======================================

.. versionadded:: 8.2

Suppose we need bind script ``app.py`` to 2 dockers which id are ``docker-a1`` and ``docker-b2``

First create hook script ``.pyarmor/hooks/app.py``

.. code-block:: python

    def _pyarmor_check_docker():
        cid = None
        with open("/proc/self/cgroup") as f:
            for line in f:
                if line.split(':', 2)[1] == 'name=systemd':
                    cid = line.strip().split('/')[-1]
                    break

        docker_ids = __pyarmor__(0, None, b'keyinfo', 1).decode('utf-8')
        if cid is None or cid not in docker_ids.split(','):
            raise RuntimeError('license is not for this machine')

    _pyarmor_check_docker()

Then generate the obfuscated script, store docker ids to :term:`runtime key` as private data at the same time::

    $ pyarmor gen --bind-data "docker-a1,docker-b2" app.py

Run the obfuscated script to check it, please add print statements in the hook script to debug it.

.. seealso:: :ref:`hooks` :func:`__pyarmor__`

Using hook to check network time by other service
=================================================

.. versionadded:: 8.2

If NTP is not available in the :term:`target device` and the obfuscated scripts has expired date, it may raise ``RuntimeError: Resource temporarily unavailable``.

In this case, using hook script to verify expired data by other time service.

First create hook script in the ``.pyarmor/hooks/foo.py``:

.. code-block:: python

    def _pyarmor_check_worldtime(host, path):
        from http.client import HTTPSConnection
        expired = __pyarmor__(1, None, b'keyinfo', 1)
        conn = HTTPSConnection(host)
        conn.request("GET", path)
        res = conn.getresponse()
        if res.code == 200:
            data = res.read()
            s = data.find(b'"unixtime":')
            n = data.find(b',', s)
            current = int(data[s+11:n])
            if current > expire:
                raise RuntimeError('license is expired')
         else:
             raise RuntimeError('got network time failed')
    _pyarmor_check_worldtime('worldtimeapi.org', '/api/timezone/Europe/Paris')

Then generate script with local expired date::

    $ pyarmor gen -e .30 foo.py

Thus the obfuscated script could verify network time by itself.

.. seealso:: :ref:`hooks` :func:`__pyarmor__`

.. include:: ../_common_definitions.txt
