# -*- coding: utf-8 -*-
#
# 生成脚本实例
#
# 使用方法:
#
#    from test.support import script_helper
#    from driver import generator
#
#    for name, source in generator.iter_scripts(''):
#       script_helper.make_script(source, name=name)
#

import itertools

from string import Template
from textwrap import dedent, indent


INDENT = 4
"""int: Python 脚本的缩进宽度"""


module_tpl = Template('''\
$body
''')

function_tpl = Template('''\
def foo():
    $body
foo()
''')

class_tpl = Template('''\
class Foo():
    $body
Foo()
''')

method_tpl = Template('''\
class Foo():
    def run(self):
        $body
Foo().run()
''')

nest_function_tpl = Template('''\
def foo():
    def nest():
        $body
    nest()
foo()
''')

nest_class_tpl = Template('''\
$body
''')

nest_class_method_tpl = Template('''\
$body
''')


tpl_catalog = {
    'modules': (module_tpl, 0),
    'functions': (function_tpl, 1),
    'classes': (class_tpl, 1),
    'methods': (method_tpl, 2),
    'nest_functions': (nest_function_tpl, 2),
}


expr_call_materials = [
    ('call_1', dedent('''\
    print('ok')
    ''')),
    ('call_2', dedent('''\
    print('ok', end='$')
    ''')),
    ('call_3', dedent('''\
    print(*('ok', 'yes'))
    ''')),
    ('call_3_1', dedent('''\
    print(*['ok2', 'yes2'])
    ''')),
    ('call_4', dedent('''\
    print(*('ok', 'yes'), end='$')
    ''')),
    ('call_5', dedent('''\
    args = ('ok', 'yes')
    kwargs = {'end': '$'}
    print(*args, **kwargs)
    ''')),
    ('call_6', dedent('''\
    args = ('ok', 'yes')
    kwargs = {'end': '$'}
    print('abc', *args, '123', sep='\t', **kwargs)
    ''')),
]

assign_materials = [
    ('assign_1', dedent('''\
    a = 1
    print(a)
    ''')),
    ('assign_2', dedent('''\
    x = [0, 1]
    x[1] = 2
    print(x)
    ''')),
    ('assign_3', dedent('''\
    x = [0, 1]
    x[1:1] = 4, 5, 6
    print(x)
    ''')),
    ('assign_3_1', dedent('''\
    x = [0, 1]
    x[:] = 4, 5, 6
    print(x)
    ''')),
    ('assign_3_2', dedent('''\
    x = [0, 1]
    x[:1] = 4, 5, 6
    print(x)
    ''')),
    ('assign_3_3', dedent('''\
    x = [0, 1]
    x[1:] = 4, 5, 6
    print(x)
    ''')),
    ('assign_4', dedent('''\
    x = {}
    x['k'] = 2
    print(x)
    ''')),
    ('assign_5', dedent('''\
    class C: pass
    a = C()
    a.x = 1
    print(a.x)
    ''')),
    ('assign_6', dedent('''\
    a, b, c = 1, 2, 3
    print(a, b, c)
    ''')),
    ('assign_7', dedent('''\
    a, (b, c), d = 1, (2, 3), 5
    print(a, b, c, d)
    ''')),
    ('assign_7_1', dedent('''\
    a, [b, c], d = 1, (2, 3), 5
    print(a, b, c, d)
    ''')),
    ('assign_7_2', dedent('''\
    [b, c], = (2, 3),
    print(b, c)
    ''')),
    ('assign_8', dedent('''\
    a, b, *c = 1, (2, 3), 5
    print(a, b, c)
    ''')),
    ('assign_8_1', dedent('''\
    a, *b, c, d = 1, 2, 3, 5, 6, 7
    print(a, b, c, d)
    ''')),
    ('assign_8_2', dedent('''\
    *a, (b, c), d = 1, (2, 3), 5
    print(a, b, c, d)
    ''')),
    ('assign_8_3', dedent('''\
    *a, = 1, (2, 3), 5, 6, 7
    print(a)
    ''')),
    ('assign_9', dedent('''\
    a, (b, c), *d = 1, (2, 3), 5, 6, 7
    print(a, b, c, d)
    ''')),
    ('assign_10', dedent('''\
    x = [0, 1]
    i = 0
    i, x[i] = 1, 2
    print(i, x)
    '''))
]

augassign_materials = [
    ('augassign_1', dedent('''\
    a = 1
    a += 2
    a -= 1
    a *= 3
    print(a)
    ''')),
    ('augassign_2', dedent('''\
    x = [0, 1]
    x[1] += 2
    x[1] /= 3
    print(x)
    ''')),
    ('augassign_3', dedent('''\
    x = {}
    x['k'] = 2
    x['k'] += 2
    print(x)
    ''')),
    ('augassign_4', dedent('''\
    class C: pass
    a = C()
    a.x = 1
    a.x += 1
    print(a.x)
    ''')),
]

annassign_materials = [
    ('annassign_1', dedent('''\
    a: int = 1
    print(a)
    ''')),
    ('annassign_2', dedent('''\
    (a): int = 1
    print(a)
    ''')),
    ('annassign_3', dedent('''\
    c:int
    ''')),
    ('annassign_4', dedent('''\
    x = [0, 1]
    x[1]:int
    print(x)
    ''')),
    ('annassign_5', dedent('''\
    class C: pass
    a = C()
    a.x:int = 2
    print(a.x)
    ''')),
]

delete_materials = [
    ('delete_1', dedent('''\
    a = 1
    del a
    print('a: ', 'a' in locals())
    ''')),
    ('delete_2', dedent('''\
    x = [0, 1, 2]
    del x[1]
    print(x)
    ''')),
    ('delete_2_1', dedent('''\
    x = [0, 1, 2]
    del x[:]
    print(x)
    ''')),
    ('delete_3', dedent('''\
    class C: pass
    a = C()
    a.x = 1
    print(a.x)
    ''')),
]

for_materials = [
    ('for_1', dedent('''\
    for i in (1, 2, 3):
        print(i)
    ''')),
    ('for_2', dedent('''\
    for i, j in zip((1, 2, 3), (4, 5, 6)):
        print(i + j)
    ''')),
    ('for_3', dedent('''\
    for i in (1, 2, 3):
        print(i)
        if i > 2:
            break
    ''')),
    ('for_4', dedent('''\
    for i in (1, 2, 3):
        if i > 2:
            continue
        print(i)
    ''')),
    ('for_5', dedent('''\
    for i in (1, 2, 3):
        print(i)
    else:
        print('else ok')
    ''')),
    ('for_6', dedent('''\
    for i in (1, 2, 3):
        print(i)
        break
    else:
        print('else ok')
    ''')),
    ('for_7', dedent('''\
    for i in (1, 2, 3):
        print(i)
        break
    else:
        print('else ok')
    ''')),
]

while_materials = [
    ('while_1', dedent('''\
    i = 0
    while i < 3:
        print(i)
        i += 1
    ''')),
    ('while_2', dedent('''\
    i = 0
    while i < 3:
        print(i)
        i += 1
    else:
        print('else', i)
    ''')),
    ('while_3', dedent('''\
    i = 0
    while i < 5:
        print(i)
        if i > 3:
            break
        i += 1
    ''')),
    ('while_4', dedent('''\
    i = 0
    while i < 5:
        i += 1
        if i > 3:
            continue
        print(i)
    ''')),
    ('while_5', dedent('''\
    i = 0
    while i < 5:
        i += 1
        if i > 3:
            continue
        print(i)
    else:
        print('else ok')
    ''')),
    ('while_6', dedent('''\
    i = 0
    while i < 5:
        i += 1
        if i > 3:
            break
        print(i)
    else:
        print('else ok', i)
    ''')),
]

if_materials = [
    ('if_1', dedent('''\
    if 1:
        print('if ok')
    ''')),
    ('if_2', dedent('''\
    if 0:
        print('if ok')
    else:
        print('else ok')
    ''')),
]

listcomp_materials = [
    ('listcomp_1', dedent('''\
    a = [x for x in range(10)]
    print(a)
    ''')),
    ('listcomp_2', dedent('''\
    a = [x for x in range(10) if x > 2]
    print(a)
    ''')),
    ('listcomp_2_1', dedent('''\
    a = [x for x in range(10) if x < 6]
    print(a)
    ''')),
    ('listcomp_3', dedent('''\
    a = [x for x in range(10) if x > 2 if x % 3 == 0]
    print(a)
    ''')),
    ('listcomp_4', dedent('''\
    a = [(x, y) for x in range(3) for y in range(3)]
    print(a)
    ''')),
    ('listcomp_5', dedent('''\
    a = [(x, y) for x in range(10) if x > 2 for y in range(10)]
    print(a)
    ''')),
    ('listcomp_6', dedent('''\
    a = [(x, y) for x in range(10) for y in range(10) if y > x]
    print(a)
    ''')),
    ('listcomp_7', dedent('''\
    a = [(x, y) for x in range(10) if x > 2 for y in range(10) if y > x]
    print(a)
    ''')),
]

setcomp_materials = [
    ('setcomp_1', dedent('''\
    a = {x for x in range(10)}
    print(a)
    ''')),
    ('setcomp_2', dedent('''\
    a = {x for x in range(10) if x > 2}
    print(a)
    ''')),
    ('setcomp_2_1', dedent('''\
    a = {x for x in range(10) if x < 6}
    print(a)
    ''')),
    ('setcomp_3', dedent('''\
    a = {x for x in range(10) if x > 2 if x % 3 == 0}
    print(a)
    ''')),
    ('setcomp_4', dedent('''\
    a = {(x, y) for x in range(3) for y in range(3)}
    print(a)
    ''')),
    ('setcomp_5', dedent('''\
    a = {(x, y) for x in range(10) if x > 2 for y in range(10)}
    print(a)
    ''')),
    ('setcomp_6', dedent('''\
    a = {(x, y) for x in range(10) for y in range(10) if y > x}
    print(a)
    ''')),
    ('setcomp_7', dedent('''\
    a = {(x, y) for x in range(10) if x > 2 for y in range(10) if y > x}
    print(a)
    ''')),
]

gencomp_materials = [
    ('gencomp_1', dedent('''\
    a = (x for x in range(10))
    print(list(a))
    ''')),
    ('gencomp_2', dedent('''\
    a = (x for x in range(10) if x > 2)
    print(list(a))
    ''')),
    ('gencomp_2_1', dedent('''\
    a = (x for x in range(10) if x < 6)
    print(list(a))
    ''')),
    ('gencomp_3', dedent('''\
    a = (x for x in range(10) if x > 2 if x % 3 == 0)
    print(list(a))
    ''')),
    ('gencomp_4', dedent('''\
    a = ((x, y) for x in range(3) for y in range(3))
    print(list(a))
    ''')),
    ('gencomp_5', dedent('''\
    a = ((x, y) for x in range(10) if x > 2 for y in range(10))
    print(list(a))
    ''')),
    ('gencomp_6', dedent('''\
    a = ((x, y) for x in range(10) for y in range(10) if y > x)
    print(list(a))
    ''')),
    ('gencomp_7', dedent('''\
    a = ((x, y) for x in range(10) if x > 2 for y in range(10) if y > x)
    print(list(a))
    ''')),
]

dictcomp_materials = [
    ('dictcomp_1', dedent('''\
    a = {x: x for x in range(10)}
    print(a)
    ''')),
    ('dictcomp_2', dedent('''\
    a = {x: x for x in range(10) if x > 2}
    print(a)
    ''')),
    ('dictcomp_2_1', dedent('''\
    a = {x: x for x in range(10) if x < 6}
    print(a)
    ''')),
    ('dictcomp_3', dedent('''\
    a = {x: x for x in range(10) if x > 2 if x % 3 == 0}
    print(a)
    ''')),
    ('dictcomp_4', dedent('''\
    a = {x: y for x in range(3) for y in range(3)}
    print(a)
    ''')),
    ('dictcomp_5', dedent('''\
    a = {x: y for x in range(10) if x > 2 for y in range(10)}
    print(a)
    ''')),
    ('dictcomp_6', dedent('''\
    a = {x: y for x in range(10) for y in range(10) if y > x}
    print(a)
    ''')),
    ('dictcomp_7', dedent('''\
    a = {x: y for x in range(10) if x > 2 for y in range(10) if y > x}
    print(a)
    ''')),
]

namedexpr_materials = [
    ('namedexpr_1', dedent('''\
    (a := 2)
    print(a)
    ''')),
    ('namedexpr_2', dedent('''\
    x = (a := 2)
    print(a, x)
    ''')),
]

boolop_materials = [
    ('boolop_1', dedent('''\
    a = 0 or 1
    print(a)
    ''')),
    ('boolop_2', dedent('''\
    a = 0 and 1
    print(a)
    ''')),
    ('boolop_3', dedent('''\
    a = 0 or False or True
    print(a)
    ''')),
    ('boolop_4', dedent('''\
    a = 1 and True and 'abc'
    print(a)
    ''')),
]

binop_materials = [
    ('binop_1', dedent('''\
    a = 1
    b = 2
    x = a + b + 5 + int('2')
    print(x)
    print(a * b)
    print( b / a)
    print(a * b * 5)
    print(10 / a / b)
    print(17 % 5)
    print(7 >> 2)
    print(7 << 2)
    print(2 ** 5)
    print(2 ^ 10)
    print(2 | 9)
    print(2 & 9)
    ''')),
]

unaryop_materials = [
    ('unaryop_1', dedent('''\
    a = 1
    print(not a)
    print(-a)
    print(+a)
    print(~a)
    ''')),
]

lambda_materials = [
    ('lambda_1', dedent('''\
    a = lambda x: (x + 2) * 3
    print(a(3))
    ''')),
]

ifexp_materials = [
    ('ifexp_1', dedent('''\
    x = 1
    a = 'ok' if x > 0 else 'yes, else'
    print(a)
    ''')),
    ('ifexp_2', dedent('''\
    x = 1
    a = 'ok' if x < 0  else 'yes else'
    print(a)
    ''')),
]

dict_materials = [
    ('dict_1', dedent('''\
    x = {'a': 1, 'b': 2}
    print(x)
    ''')),
    ('dict_2', dedent('''\
    f = {'c': 3}
    x = {'a': 1, **f, 'b': 2}
    print(x)
    ''')),
    ('dict_2', dedent('''\
    f = {'c': 3}
    g = {'d': 3}
    x = {'a': 1, **f, 'b': 2, **g}
    print(x)
    ''')),
]

list_materials = [
    ('list_1', dedent('''\
    c = 5
    a = [1, 2, c]
    print(a)
    ''')),
    ('list_2', dedent('''\
    a = [1, 2]
    x = [3, 4, *a]
    print(x)
    ''')),
    ('list_3', dedent('''\
    a = [1, 2]
    x = [*a, 3, 4, *a, 5, 6]
    print(x)
    ''')),
]

tuple_materials = [
    ('tuple_1', dedent('''\
    c = 5
    a = 1, 2, c
    print(a)
    ''')),
    ('tuple_2', dedent('''\
    a = [1, 2]
    x = 3, 4, *a
    print(x)
    ''')),
    ('tuple_2_1', dedent('''\
    a = 1, 2
    x = 3, 4, *a
    print(x)
    ''')),
    ('tuple_3', dedent('''\
    a = 1, 2
    x = *a, 3, 4, *a, 5, 6
    print(x)
    ''')),
]

set_materials = [
    ('set_1', dedent('''\
    c = {5}
    a = {1, 2}
    print(a, c)
    ''')),
    ('set_2', dedent('''\
    a = [1, 2]
    x = {1, 3, 4, *a}
    print(x)
    ''')),
    ('set_2_1', dedent('''\
    a = 1, 2
    x = {3, 4, *a}
    print(x)
    ''')),
    ('set_2_2', dedent('''\
    a = {1, 2}
    x = {3, 4, *a}
    print(x)
    ''')),
    ('set_3', dedent('''\
    a = 1, 2
    x = {*a, 3, 4, *a, 5, 6}
    print(x)
    ''')),
]

compare_materials = [
    ('compare_1', dedent('''\
    x = 1 > 2
    print(x)
    ''')),
    ('compare_1_1', dedent('''\
    x = 2 >= 1
    print(x)
    ''')),
    ('compare_1_2', dedent('''\
    x = 1 < 2
    print(x)
    ''')),
    ('compare_1_3', dedent('''\
    x = 1 <= 2
    print(x)
    ''')),
    ('compare_1_4', dedent('''\
    x = (1 < 2) is True
    print(x)
    ''')),
    ('compare_1_5', dedent('''\
    x = (1 < 2) is not True
    print(x)
    ''')),
    ('compare_1_6', dedent('''\
    x = 2 in (1, 2, 3)
    print(x)
    ''')),
    ('compare_1_7', dedent('''\
    x = 2 not in (1, 2, 3)
    print(x)
    ''')),
    ('compare_2', dedent('''\
    x = 5 > 4 > 3
    print(x)
    ''')),
    ('compare_3', dedent('''\
    x = (5 > 4) > 3
    print(x)
    ''')),
]

joinedstr_materials = [
    ('joinedstr_1', dedent('''\
    x = f""
    print(x)
    ''')),
    ('joinedstr_1_1', dedent('''\
    x = f"ok"
    print(x)
    ''')),
    ('joinedstr_1_2', dedent('''\
    a = "ok"
    x = f"{a}"
    print(x)
    ''')),
    ('joinedstr_2', dedent('''\
    a = 5.82892
    x = f"sin({a}) is {float(a):.3}"
    print(x)
    ''')),
    ('joinedstr_3', dedent('''\
    a = 60.8999
    b = 'ok'
    x = f"{a}{b}sin({a}) is {a:.3}"
    print(x)
    ''')),
]

try_materials = [
    ('try_1', dedent('''\
    try:
        1 / 0
    except Exception:
        print('try ok')
    ''')),
    ('try_2', dedent('''\
    try:
        1 / 0
    except Exception as e:
        print('try ok', e)
    ''')),
]

with_materials = [
    ('with_1', dedent('''\
    class cm (object):
        def __enter__(self):
            pass
        def __exit__(self, type, value, traceback):
            pass
    with cm():
        print('with ok')
    ''')),
]

yield_materials = [
    ('yield_1', dedent('''\
    def gen():
        for i in range(10):
            yield i
    print(list(gen()))
    ''')),
    ('yield_2', dedent('''\
    def gen():
        a = 3
        b = 4
        c = 5
        yield from (a, b, c)
    print(list(gen()))
    ''')),
]

match_materials = [
    ('match_1', dedent('''\
    flag = False
    match (100, 200):
        case (100, 300):  # Mismatch: 200 != 300
            print('Case 1')
        case (100, 200) if flag:  # Successful match, but guard fails
            print('Case 2')
        case (100, y):  # Matches and binds y to 200
            print(f'Case 3, y: {y}')
        case _:  # Pattern not attempted
            print('Case 4, I match anything!')
    ''')),
]

cell_materials = [
    ('cell_1', dedent('''\
    def test_cell_main():
        a = 12
        def test_cell(b):
            print('cell is', a)
            print('arg is', b)
        test_cell('9')
    test_cell_main()
    ''')),
]


script_materials = itertools.chain(
    expr_call_materials,
    assign_materials,
    augassign_materials,
    annassign_materials,
    delete_materials,
    for_materials,
    while_materials,
    if_materials,
    listcomp_materials,
    setcomp_materials,
    gencomp_materials,
    dictcomp_materials,
    namedexpr_materials,
    boolop_materials,
    binop_materials,
    unaryop_materials,
    lambda_materials,
    ifexp_materials,
    dict_materials,
    list_materials,
    tuple_materials,
    set_materials,
    compare_materials,
    joinedstr_materials,
    try_materials,
    with_materials,
    yield_materials,
    match_materials,
    cell_materials,
)
# script_materials = cell_materials


locals_materials = [
]

super_materials = [
]

samename_materials = [
    ('samename_1', dedent('''\
    def gen():
        a = 3
        b = 4
        c = 5
        return a, b, c
    print(gen())

    def gen():
        i = 1
        return i
    print(gen())
    ''')),
]

immortal_refcnt_materials = [
]

async_materials = [
]

script_catalog = {
    'locals': locals_materials,
    'super': super_materials,
    'samename': samename_materials,
    'async': async_materials,
    'immortal_refcnt': immortal_refcnt_materials,
}


def iter_scripts(catalog=None):
    """生成用于测试各种 Python 功能的脚本

    参数:
        catalog (str): tpl_catalog 或者 script_catalog 中的分类名称

    生成: (name, source)

        name 是脚本名称，没有后缀 `.py`
        source 是脚本内容

    """
    tplinfo = tpl_catalog.get(catalog)
    if tplinfo:
        tpl, level = tplinfo
        if level:
            col = level * INDENT
            prefix = ' ' * col
        for name, source in script_materials:
            yield name, tpl.substitute(
                body=indent(source, prefix)[col:] if level else source)
    else:
        materials = script_catalog.get(catalog, [])
        yield from materials
