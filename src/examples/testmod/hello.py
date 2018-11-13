import dis
import os
import sys

# Import function and class from obfuscated module
from queens import main, Queens

# Call obfuscated function
main()

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
try:
  queens.test_exception()
except Exception:
  from traceback import print_exc
  print_exc()

# Check original func can not be got from exception frame
try:
  queens.test_exception()
except Exception:
  import inspect
  for exc_tb in inspect.trace():
    frame = exc_tb[0]
    print('Found frame of function %s' % exc_tb[3])
    if frame.f_locals.get('func') is None \
       and frame.f_locals.get('filename') is None \
       and frame.f_locals.get('n') is None:
      print('Can not get data from frame.f_locals')

# Check callback
def mycallback():
  frame = sys._getframe(1)
  if len(frame.f_locals) == 0:
    print('Got empty from callback')
queens.test_callback(mycallback)

# Check generator
a = list(queens.simple_generator(10))
if len(a) == 10:
  print('Generator works well')

# Check nested
func1 = queens.factory()
func2 = queens.factory()
func1(func2)
print('Shared code object works well')
  
# Access original func_code will crash: Segmentation fault
# print(dis.dis(main.orig_func))
# print(dis.dis(Queens.solve.orig_func))
