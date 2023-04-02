========================
Insight Into Obfuscation
========================

.. highlight:: console

Filter scripts by finder::

  # Exclude "test" and all the path "test"
  pyarmor cfg finder:exludes="test */test lib/a.py"

  # Include special script, for example, ext is not .py
  pyarmor cfg finder:include="lib/extra.pyi"

  # Include data files, these data file will be copied to output
  # If don't want to obfuscate .py, but need copy it to output, list it here
  pyarmor cfg finder:data_files="a.py lib/readme.txt"

If follow :mod:`fnmatch` ruler, for windows, use lower case and
backward slash in pattern

.. include:: ../_common_definitions.txt
