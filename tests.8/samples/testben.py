import benchmark
import sys
import time


def metric(func):
    if not hasattr(time, 'process_time'):
        time.process_time = time.clock

    def wrap(*args, **kwargs):
        t1 = time.process_time()
        result = func(*args, **kwargs)
        t2 = time.process_time()
        print('%-16s: %10.3f ms' % (func.__name__, ((t2 - t1) * 1000)))
        return result
    return wrap


@metric
def test_import():
    import benchmark2 as m2
    return m2


@metric
def test_foo():
    benchmark.foo()


if __name__ == '__main__':
    print('Python %s.%s' % sys.version_info[:2])
    test_import()
    test_foo()
