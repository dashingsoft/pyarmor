from __future__ import print_function
print('__future__ ok')

def foo():
  return 'woo'

def foo2():
  try:
    return 'finally woo'
  finally:
    pass

def foo3(a):
    return a

def foo4():
    return 1

def foo5():
    raise Exception('auto wrap mode exception')

class C:
    name = 'Class Sky'

    @classmethod
    def test(cls):
        return 'static classmethod'

def solve(n):
  if n < 1:
    return 'solved'
  return solve(n - 1)

def wraparmor(func):
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  return wrapper

@wraparmor
def test_wrapper():
  return 'OK'

print('hello')
print(foo())
print(foo2())
print(foo3('only a'))
print('only const %s' % foo4())
print(C.name)
print(C.test())
print('recursive call return %s' % solve(5))
print('first test decorator return %s' % test_wrapper())
print('second test decorator return %s' % test_wrapper())
# foo5()
try:
  foo5()
except Exception as e:
  print(e)
