'''This is docstring'''


class BaseAnno:
    a: int = 3
    b: str = 'abc'


def foo(k: str):
    return k


a1 = BaseAnno.__annotations__
a2 = foo.__annotations__

if a1['a'] is int and a1['b'] is str and a2['k'] is str:
    print('All test passed')
