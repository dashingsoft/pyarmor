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

By option ``-e`` passing extra options to run `PyInstaller`_, to be sure these
options work with `PyInstaller`_::

    cd /path/to/src
    pyinstaller --name easy-han --hidden-import comtypes --add-data 'config.json;.' main.py

    cd dist/easy-han
    ./easy-han

By option ``-x`` passing extra options to obfuscate the scripts, there are many
`.py` files in the path `tests` and `vnev`, but all of them need not to be
obfuscated. By passing option ``--exclude`` to exclude them, to be sure these
options work with command :ref:`obfuscate`::

    cd /path/to/src
    pyarmor obfuscate --exclude vnev --exclude tests main.py

By option ``-s`` to specify the `.spec` filename, because `PyInstaller`_ changes
the default filename of `.spec` by option ``--name``, so it tell command
:ref:`pack` the right filename.

.. important::

   The command :ref:`pack` will obfuscate the scripts automatically, do not try
   to pack the obfuscated the scripts.

.. note::

   From PyArmor 5.5.0, it could improve the security by passing the obfuscated
   option ``--advanced`` to enable :ref:`Advanced Mode`. For example::

       pyarmor pack -x " --advanced 1 --exclude tests" foo.py

Running obfuscated Django site with Apache and mod_wsgi
-------------------------------------------------------

Here is a simple site of Django::

    /path/to/mysite/
        db.sqlite3
        manage.py
        mysite/
            __init__.py
            settings.py
            urls.py
            wsgi.py
        polls/
            __init__.py
            admin.py
            apps.py
            migrations/
                __init__.py
            models.py
            tests.py
            urls.py
            views.py

First obfuscating all the scripts::

    # Create target path
    mkdir -p /var/www/obf_site

    # Copy all files to target path, because pyarmor don't deal with any data files
    cp -a /path/to/mysite/* /var/www/obf_site/

    cd /path/to/mysite

    # Obfuscating all the scripts in the current path recursively, specify the entry script "wsgi.py"
    # The obfuscate scripts will be save to "/var/www/obf_site"
    pyarmor obfuscate --src="." -r --output=/var/www/obf_site mysite/wsgi.py

Then edit the server configuration file of Apache::

    WSGIScriptAlias / /var/www/obf_site/mysite/wsgi.py
    WSGIPythonHome /path/to/venv

    # The runtime files required by pyarmor are generated in this path
    WSGIPythonPath /var/www/obf_site

    <Directory /var/www/obf_site/mysite>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

Finally restart Apache::

    apachectl restart

.. include:: _common_definitions.txt
