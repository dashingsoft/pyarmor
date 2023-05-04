=====================================
Localization and Internationalization
=====================================

.. highlight:: console

**When building obfuscated scripts**

For example::

    pyarmor gen foo.py

Pyarmor first searches file :file:`messages.cfg` in the :term:`local path`,
then searches in the :term:`global path`

If :file:`messages.cfg` exists, then read this file and save customized message to :term:`runtime key`

If this file is not encoded by ``utf-8``, set the right encoding ``XXX`` by this command::

    $ pyarmor cfg messages=messages.cfg:XXX

.. seealso:: :ref:`runtime errors`

**When launching obfuscated scripts**

For example::

    python dist/foo.py

When something is wrong, the obfuscated script need report error which has an error code:

First decide default language by checking the following items in turn

* :envvar:`PYARMOR_LANG`
* :attr:`sys._PARLANG`
* First part of :envvar:`LANG`. For example, ``en_US`` or ``zh_CN``

Then search error message table in the :term:`runtime key`, if there is an error message both of language code and error code are matched, then return it.

Otherwise return default error message.

.. include:: ../_common_definitions.txt
