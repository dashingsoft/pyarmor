=============================
 Customization and Extension
=============================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor gen

Users could write any :term:`plugin script` or :term:`hook script` to extend Pyarmor features.

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

Using hook to check network time by other service
=================================================

.. versionadded:: 8.2

Create hook script in the ``.pyarmor/hooks/foo.py``

.. code-block:: python

    from http.client import HTTPSConnection
    expired = __pyarmor__(1, None, b'keyinfo', 1)
    host = 'worldtimeapi.org'
    path = '/api/timezone/Europe/Paris'
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

Then generate script with local expired date::

    $ pyarmor gen -e .30 foo.py

Because ``.pyarmor/hooks/foo.py`` will be inserted into ``foo.py``, in order to avoid name confilcts, refine it as this:

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

.. seealso:: :ref:`hooks` :func:`__pyarmor__`

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

.. seealso:: :ref:`hooks` :func:`__pyarmor__`

.. include:: ../_common_definitions.txt
