'''This is docstring'''

class BaseAnno:
    a: int = 3
    b: str = 'abc'


def anno_foo(k: str):
    return k

FlaskForm = object
class MyForm(FlaskForm): pass


print(__doc__)
print(BaseAnno.__annotations__)
print(anno_foo.__annotations__)
