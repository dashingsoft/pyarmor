========================
Insight Into Obfuscation
========================

.. highlight:: bash

TODO:

..
  Filter scripts by finder

  # Script ext is not .py, list it in command line
  pyarmor gen main.py my.config

  # Exclude "test" and all the path "test"
  pyarmor cfg finder:excludes="test */test lib/a.py"

  # Include special script in package, for example, ext is not .py
  pyarmor cfg finder:includes="lib/extra.pyi"

  # Include data files, these data file will be copied to output
  # If don't want to obfuscate .py, but need copy it to output, list it here
  pyarmor cfg finder:data_files="a.py lib/readme.txt"

  It following :mod:`fnmatch` ruler to match pattern.

.. include:: ../_common_definitions.txt
