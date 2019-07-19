.. _examples:

Examples
========

Here are some examples.

Obfuscating and Packing PyQt Application
----------------------------------------

There is a tool `easy-han` based on PyQt. Here list the main files::

    config.json

    main.py
    ui_main.py
    readers/
        __init__.py
        msexcel.py

    tests/
    vnev/py36


Here the shell script used to pack this tool by PyArmor::

    cd /path/to/src
    pyarmor pack -e " --name easy-han --hidden-import comtypes --add-data 'config.json;.'" \
                 -x " --exclude vnev --exclude tests" -s "easy-han.spec" main.py

    cd dist/easy-han
    ./easy-han

By option `-e` passing extra options to run `PyInstaller`, to be sure these
options work with `PyInstaller`::

    cd /path/to/src
    pyinstaller --name easy-han --hidden-import comtypes --add-data 'config.json;.' main.py

    cd dist/easy-han
    ./easy-han

By option `-x` passing extra options to obfuscate the scripts, there are many
`.py` files in the path `tests` and `vnev`, but all of them need not to be
obfuscated. By passing option `--exclude` to exclude them, to be sure these
options work with command :ref:`obfuscate`::

    cd /path/to/src
    pyarmor obfuscate --exclude vnev --exclude tests main.py

By option `-s` to specify the `.spec` filename, because `PyInstaller` changes
the default filename of `.spec` by option `--name`, so it tell command `pack`
the right filename.

.. important::

   The command `pack` will obfuscate the scripts automatically, do not try to
   pack the obfuscated the scripts.

.. note::

   From PyArmor 5.5.0, it could improve the security by passing the obfuscated
   option `--advanced` to enable :ref:`Advanced Mode`. For example::

       pyarmor pack -x " --advanced --exclude tests" foo.py

.. include:: _common_definitions.txt
