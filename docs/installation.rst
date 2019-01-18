Installation
============

|PyArmor| is a normal Python package.  You can download the archive
from PyPi_, but it is easier to install using pip_ where is is
available, for example::

    pip install pyarmor

or upgrade to a newer version::

    pip install --upgrade pyarmor

Verifying the installation
--------------------------

On all platforms, the command ``pyarmor`` should now exist on the
execution path. To verify this, enter the command::

    pyarmor --version

The result should show ``PyArmor Version X.Y.Z`` or ``PyArmor Trial Version X.Y.Z``.

If the command is not found, make sure the execution path includes the
proper directory.

Installed commands
------------------

The complete installation places these commands on the execution path:

* ``pyarmor`` is the main command. See :ref:`Using PyArmor`.

* ``pyarmor-webui`` is used to open a simple web ui of PyArmor.

If you do not perform a complete installation (installing via
``pip``), these commands will not be installed as commands.  However,
you can still execute all the functions documented below by running
Python scripts found in the distribution folder.  The equivalent of
the ``pyarmor`` command is :file:`{pyarmor-folder}/pyarmor.py`, and of
``pyarmor-webui`` is :file:`{pyarmor-folder}/pyarmor-webui.py`.

.. include:: _common_definitions.txt
