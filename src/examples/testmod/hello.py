import sys
import dis

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
