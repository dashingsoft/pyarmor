def foo(arg=None):
    if arg is not None:
        if arg is True:
            return arg
        elif arg is False:
            return False
        else:
            return
    bar = 1
    raise RuntimeError('some error %s' % bar)


def foo2(arg):
    return arg


def foo3(arg):
    return 1


if not foo(True):
    print('return non-const failed')

if foo(False):
    print('return const failed')

if foo(0) is not None:
    print('return None failed')

try:
    foo()
except RuntimeError:
    print('All test passed')
