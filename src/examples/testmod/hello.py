import sys
import dis

from queens import main, Queens

main()

try:
  print(dis.dis(main.orig_func))
except Exception as e:
  print(e)

try:
  print(dis.dis(Queens.solve.orig_func))
except Exception as e:
  print(e)
