import dis
import os
import sys

# Import function and class from obfuscated module
from queens import main, Queens

# Call obfuscated function
main()

# Check func_code is obfuscated
try:
  print(dis.dis(main.orig_func))
except Exception as e:
  print(e)

# Check class method is obfuscated
try:
  print(dis.dis(Queens.solve.orig_func))
except Exception as e:
  print(e)

# Check __file__ of obfuscated module "queens" is filename in target machine
import queens
if os.path.abspath(queens.__file__) == os.path.abspath(os.path.join(os.path.dirname(__file__), "queens.py")):
  print("The value of __file__ is OK")
  
# Check __wraparmor__ can't be called out of decorator
try:
    from builtins import __wraparmor__
except Exception:
    from __builtin__ import __wraparmor__
try:
  __wraparmor__(main)
except Exception as e:
  print('__wraparmor__ can not be called out of decorator')

# Check filename in trackback
queens.test_exception()
