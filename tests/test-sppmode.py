# -*- coding: utf-8 -*-
# {No PyArmor Protection Code}

import gc
import sys
import unittest
import weakref

from decimal import localcontext, Decimal

# Lib/test/
#     test_unary.py
#     test_binop.py


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


class BlockTestCases(BaseTestCase):

    def test_while_try_else(self):
        while 1:
            try:
                a = 1
            except RuntimeError:
                pass
            else:
                break
            finally:
                a = 2

        self.assertEqual(a, 2)

    def test_while_while_else(self):
        a = 1
        while a < 2:
            try:
                while a == 1:
                    a = 2
                else:
                    continue
            finally:
                a = 10

        self.assertEqual(a, 10)

    def test_raise_1(self):
        # In Python, it raises RuntimeError
        with self.assertRaises(UnboundLocalError):
            raise

    def test_raise_2(self):
        with self.assertRaises(ZeroDivisionError):
            raise ZeroDivisionError

        with self.assertRaisesRegex(ZeroDivisionError, 'abc'):
            raise ZeroDivisionError('abc')

    def test_raise_3(self):
        with self.assertRaises(ZeroDivisionError):
            try:
                1 / 0
            except Exception:
                raise

    def test_raise_in_while(self):
        with self.assertRaises(ZeroDivisionError):
            a = b = 1
            while True:
                try:
                    raise ZeroDivisionError
                except RuntimeError:
                    b = 5
                else:
                    b = 2
                finally:
                    a = 2
            self.assertEqual(a, 2)
            self.assertEqual(b, 1)

        with self.assertRaises(ZeroDivisionError):
            a = b = 1
            while True:
                try:
                    b = 5
                except RuntimeError:
                    b = 2
                else:
                    raise ZeroDivisionError
                finally:
                    a = 2
            self.assertEqual(a, 2)
            self.assertEqual(b, 5)

        with self.assertRaises(ZeroDivisionError):
            a = b = 1
            while True:
                try:
                    raise RuntimeError
                except RuntimeError:
                    b = 2
                    raise ZeroDivisionError
                else:
                    b = 3
                finally:
                    a = 2
            self.assertEqual(a, 2)
            self.assertEqual(b, 2)

    def test_continue_in_try_try(self):
        a = 1
        while True:
            if a > 10:
                break
            try:
                a += 1
                try:
                    continue
                finally:
                    a += 10
            finally:
                a += 100
        self.assertEqual(a, 112)

    def test_import(self):
        import tempfile
        import os.path
        import os.path as os_path

        self.assertTrue(tempfile)
        self.assertTrue(os.path)
        self.assertTrue(os_path)

    def test_import_from(self):
        from os.path import join as join_path
        from os import sep
        self.assertEqual(join_path('a', 'b'), 'a' + sep + 'b')

    def test_assert(self):
        with self.assertRaises(AssertionError):
            assert False

        with self.assertRaisesRegex(AssertionError, 'abc'):
            assert False, 'abc'

        assert True

        a = 6
        while True:
            try:
                a += 1
                assert False
            except AssertionError:
                a += 1
                break
            else:
                a = 100
            finally:
                a += 1
        self.assertEqual(a, 9)

        a = 6
        with self.assertRaises(AssertionError):
            while True:
                try:
                    assert False
                except RuntimeError:
                    pass
                else:
                    a = 100
                finally:
                    a += 1
        self.assertEqual(a, 7)

    def test_ellipsis(self):
        x = ...
        self.assertTrue(x is Ellipsis)

    def test_fstring(self):
        self.assertEqual(f'', '')
        self.assertEqual(f'a', 'a')
        self.assertEqual(f' ', ' ')

        width = 10
        precision = 4
        value = Decimal('12.34567')
        self.assertEqual(f'result: {value:{width}.{precision}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{width!r}.{precision}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{width:0}.{precision:1}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{1}{0:0}.{precision:1}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{ 1}{ 0:0}.{ precision:1}}', 'result:      12.35')
        self.assertEqual(f'{10:#{1}0x}', '       0xa')
        self.assertEqual(f'{10:{"#"}1{0}{"x"}}', '       0xa')
        self.assertEqual(f'{-10:-{"#"}1{0}x}', '      -0xa')
        self.assertEqual(f'{-10:{"-"}#{1}0{"x"}}', '      -0xa')
        self.assertEqual(f'{10:#{3 != {4:5} and width}x}', '       0xa')

    def test_boolop(self):
        self.assertIs(None and True, None)
        self.assertIs(10 and True, True)
        self.assertEqual(True and 10, 10)
        self.assertIs(True and None, None)
        self.assertEqual(0 and 10, 0)
        self.assertIs(False and 10, False)

        self.assertEqual(10 or True, 10)
        self.assertIs(0 or None, None)
        self.assertEqual(None or 0, 0)
        self.assertIs(True or 10, True)
        self.assertEqual(0 or 10, 10)
        self.assertEqual(False or 10, 10)

    def test_recursion_limit(self):
        '''sppmode will ignore function by RecursionError'''
        def f():
            try:
                f()
            except RecursionError:
                pass
        self.assertEqual(f(), None)

    def test_starlist(self):
        a = {1, 2, 3}
        self.assertEqual({*a, 4}, {1, 2, 3, 4})

        a = 1, 2, 3
        self.assertEqual((*a, 4), (1, 2, 3, 4))
        self.assertEqual((a, 4), ((1, 2, 3), 4))

        a = (1, 2), 3
        b = 4, (5, 6)
        self.assertEqual((*a, *b, 7), ((1, 2), 3, 4, (5, 6), 7))

        a = [1, 2, 3]
        self.assertEqual([a, 4], [[1, 2, 3], 4])
        self.assertEqual([*a, 4], [1, 2, 3, 4])

        a = [(1, 2), 3]
        b = [4, (5, 6)]
        self.assertEqual([*a, *b, 7], [(1, 2), 3, 4, (5, 6), 7])

        a = {1: 1, 2: 2}
        b = {3: 3}
        self.assertEqual({**a, **b, 4: 4}, {1: 1, 2: 2, 3: 3, 4: 4})

        a, *b = 1, 2, 3, 4
        self.assertEqual(a, 1)
        self.assertEqual(b, [2, 3, 4])

        *a, b = 1, 2, 3, 4
        self.assertEqual(a, [1, 2, 3])
        self.assertEqual(b, 4)

    def test_refcnt_expr(self):
        a = 'this is a test'
        n = sys.getrefcount(a)
        a
        a
        self.assertEqual(sys.getrefcount(a), n)

    def test_exception_with_local_var(self):
        e = 1
        try:
            1 / 0
        except ZeroDivisionError as e:
            def handler(e):
                self.assertEqual(ZeroDivisionError, type(e))
            with self.assertRaises(TypeError):
                handler()

    def test_exception_with_local_cellvar(self):
        e = 1
        try:
            1 / 0
        except ZeroDivisionError as e:
            def handler():
                self.assertEqual(ZeroDivisionError, type(e))
            handler()

    def test_exception_catch_not_exception(self):
        object_ = 'abc'
        try:
            try:
                raise Exception
            except object_:
                pass
        except TypeError:
            pass
        except Exception:
            self.fail("TypeError expected when catching %s" % type(object_))

    def test_extra_kwargs(self):
        class subclass(bytearray):
            def __init__(me, newarg=1, *args, **kwargs):
                bytearray.__init__(me, *args, **kwargs)
        x = subclass(newarg=4, source=b"abcd")
        self.assertEqual(x, b"abcd")

    def test_multiplicative_ops(self):
        x = {'one' or 'two': 1 or 2}
        self.assertEqual(x, dict(one=1))

    def test_closures(self):

        def foo(a):
            self.assertEqual(xc, a)

        xc = 2
        foo(2)

        xc = 3
        foo(3)

    def test_multiple_starargs(self):

        def foo(a, b, c, d, e):
            self.assertEqual((a, b, c, d, e), (1, 2, 3, 4, 5))

        arg1 = 2, 3
        arg2 = 4, 5
        foo(1, *arg1, *arg2)

    def test_break_continue_loop(self):
        # This test warrants an explanation. It is a test specifically for SF bugs
        # #463359 and #462937. The bug is that a 'break' statement executed or
        # exception raised inside a try/except inside a loop, *after* a continue
        # statement has been executed in that loop, will cause the wrong number of
        # arguments to be popped off the stack and the instruction pointer reset to
        # a very small number (usually 0.) Because of this, the following test
        # *must* written as a function, and the tracking vars *must* be function
        # arguments with default values. Otherwise, the test will loop and loop.

        def test_inner(extra_burning_oil=1, count=0):
            big_hippo = 2
            while big_hippo:
                count += 1
                try:
                    if extra_burning_oil and big_hippo == 1:
                        extra_burning_oil -= 1
                        break
                    big_hippo -= 1
                    continue
                except:
                    raise
            if count > 2 or big_hippo != 1:
                self.fail("continue then break in try/except in loop broken!")
        test_inner()

    def test_child_function_when_parent_failed(self):
        # Child function "one" should be mapped to c. After "one" has
        # been converted to c, parent failed because of unsupport
        # features. In this case, "one" should be mapped to c as top
        # function.
        var1: int = 5
        var2: [int, str]
        my_lst = [42]
        def one():
            return 1
        int.new_attr: int
        [list][0]: type
        my_lst[one()-1]: int = 5
        self.assertEqual(my_lst, [5])

    def test_mangling(self):
        class X:
            # __a will be "_X__a" in f.__kwdefaults__
            def f(self, *, __a=42):
                return __a
        self.assertEqual(X().f(), 42)

    def test_in_and_not_in(self):
        self.assertRaises(TypeError, lambda: 3 in 12)

    def test_arg_after_stararg(self):
        def foo(a, b, c, d):
            self.assertEqual(d, 4)
        arg = 2, 3
        foo(1, *arg, 4)

    def testNestedNonLocal(self):

        def f(x):
            def g():
                nonlocal x
                x -= 2
                def h():
                    nonlocal x
                    x += 4
                    return x
                return h
            return g

        g = f(1)
        h = g()
        self.assertEqual(h(), 3)

    def testLocalsFunction(self):

        def f(x):
            def g(y):
                def h(z):
                    return y + z
                w = x + y
                y += 3
                return w, y, h(w)
            return g

        d = f(2)(4)
        self.assertEqual((6, 7, 13), d)

    def testUnboundLocal_AfterDel(self):
        # #4617: It is now legal to delete a cell variable.
        # The following functions must obviously compile,
        # and give the correct error when accessing the deleted name.
        def errorInOuter():
            y = 1
            del y
            print(y)
            def inner():
                return y

        def errorInInner():
            def inner():
                return y
            y = 1
            del y
            inner()

        self.assertRaises(UnboundLocalError, errorInOuter)
        self.assertRaises(NameError, errorInInner)

    def testMixedFreevarsAndCellvars(self):

        def identity(x):
            return x

        def f(x, y, z):
            def g(a, b, c):
                a = a + x # 3
                def h():
                    # z * (4 + 9)
                    # 3 * 13
                    return identity(z * (b + y))
                y = c + z # 9
                return h
            return g

        g = f(1, 2, 3)
        h = g(2, 4, 6)
        self.assertEqual(h(), 39)

    def test_set_literal_insertion_order(self):
        # SF Issue #26020 -- Expect left to right insertion
        s = {1, 1.0, True}
        self.assertEqual(len(s), 1)
        stored_value = s.pop()
        self.assertEqual(type(stored_value), int)

    def test_same_constans_used_by_many_times(self):

        def foo():
            alist = [1, 2, 3]
            atuple = (1, 2, 3)
            atuple2 = (1, [], 3)
            adict = {'a': 1}
            aset = {1, 2, 3}

            blist = [1, 2, 3]
            btuple = (1, 2, 3)
            btuple2 = (1, [], 3)
            bdict = {'a': 1}
            bset = {1, 2, 3}

            alist.pop(1)
            self.assertEqual(len(alist), 2)
            self.assertEqual(len(blist), 3)

            self.assertEqual(atuple, btuple)

            atuple2[1].append('a')
            self.assertEqual(len(atuple2[1]), 1)
            self.assertEqual(len(btuple2[1]), 0)

            adict.pop('a')
            self.assertEqual(len(adict), 0)
            self.assertEqual(len(bdict), 1)

            aset.pop()
            self.assertEqual(len(aset), 2)
            self.assertEqual(len(bset), 3)

        for i in range(5):
            foo()

    def test_raise_from_cause(self):
        def foo():
            try:
                print(1 / 0)
            except Exception as exc:
                raise RuntimeError("Something bad happened") from exc
        self.assertRaises(RuntimeError, foo)

    def test_with_statement(self):
        class Ctx(object):
            def __enter__(self):
                return self

            def __exit__(self, exc, val, tb):
                return True

        def foo():
            with localcontext() as ctx:
                ctx.prec = 42
                return 1
            return 2

        self.assertEqual(1, foo())

        def foo2():
            for i in range(5, 10):
                with localcontext() as ctx:
                    ctx.prec = 42
                    return i
            return 'a'

        self.assertEqual(5, foo2())

        def foo_with_break_loop():
            k = 0
            for i in range(5, 10):
                with localcontext() as ctx:
                    ctx.prec = 42
                    break
                k += 1
            return k

        self.assertEqual(0, foo_with_break_loop())

        def foo_with_continue_loop():
            k = 0
            for i in range(5, 10):
                k += 1
                with localcontext() as ctx:
                    ctx.prec = 42
                    continue
                k += 1
            return k

        self.assertEqual(5, foo_with_continue_loop())

        class C(object):
            def __enter__(self):
                return self

            def __exit__(self, exc, val, tb):
                c_exit.append('C')
                return True

        def foo_with_break_loop2(C):
            k, j = 0, 2
            for i in range(5, 10):
                k += 1
                with localcontext() as ctx, C() as c:
                    ctx.prec = 42
                    break
                j += 1
            return k, j

        c_exit = []
        self.assertEqual((1, 2), foo_with_break_loop2(C))
        self.assertEqual(['C'], c_exit)

        def foo_with_continue_loop2(C):
            j, k = 0, 2
            for i in range(5, 10):
                j += 1
                with localcontext() as ctx, C() as c:
                    ctx.prec = 42
                    continue
                k += 1
            return j, k

        c_exit = ['a']
        self.assertEqual((5, 2), foo_with_continue_loop2(C))
        self.assertEqual(['a', 'C', 'C', 'C', 'C', 'C'], c_exit)

    def test_list_comp(self):
        self.assertEqual([0, 1, 2], [i for i in range(3)])
        self.assertEqual([1, 2, 3], [i for i in range(4) if i])

        self.assertEqual([(2, 3), (3, 4)],
                         [(i, i+1) for i in range(4) if i > 1])
        self.assertEqual([0, 1, 1, 2], [i + j
                                        for i in range(2)
                                        for j in range(2)])
        self.assertEqual([1, 2, 3], [a + b
                                     for a in range(3) if a > 0
                                     for b in range(2) if b < a])
        self.assertEqual([[0, 1, 2, 3]],
                         [[i for i in range(n)] for n in range(6) if n == 4])

    def test_set_comp(self):
        self.assertEqual({0, 1, 2}, {i for i in range(3)})
        self.assertEqual({1, 2, 3}, {i for i in range(4) if i})

        self.assertEqual({(2, 3), (3, 4)},
                         {(i, i+1) for i in range(4) if i > 1})
        self.assertEqual({0, 1, 1, 2}, {i + j
                                        for i in range(2)
                                        for j in range(2)})
        self.assertEqual({1, 2, 3}, {a + b
                                     for a in range(3) if a > 0
                                     for b in range(2) if b < a})
        self.assertEqual({6},
                         {sum({i for i in range(n)}) for n in range(6) if n == 4})

    def test_dict_comp(self):
        self.assertEqual({0:0, 1:1, 2:2}, {i:i for i in range(3)})
        self.assertEqual({1:1, 2:2, 3:3}, {i:i for i in range(4) if i})

        self.assertEqual({0:1, 1:2}, {i:i + j
                                      for i in range(2)
                                      for j in range(2)})
        self.assertEqual({1:1, 2:3}, {a: a + b
                                      for a in range(3) if a > 0
                                      for b in range(2) if b < a})
        self.assertEqual({4: 6},
                         {n: sum({i for i in range(n)}) for n in range(6) if n == 4})


class MethodTestCases(BaseTestCase):

    def test_bound_method(self):
        class E(object):
            def f(obj, x):
                return obj, x
        a, b = E().f(3)
        self.assertTrue(isinstance(a, E))
        self.assertEqual(3, b)

    def test_static_function(self):
        class E(object):
            def f(x):
                return 2
            f = staticmethod(f)

        class E2(object):
            @staticmethod
            def f(x):
                return x
        self.assertEqual(2, E.f(2))
        self.assertEqual(2, E().f(2))
        self.assertEqual(5, E2.f(5))
        self.assertEqual(5, E2().f(5))

    def test_class_function(self):
        class Dict(dict):
            def fromkeys(klass, iterable, value=None):
                d = klass()
                for key in iterable:
                    d[key] = value
                return d
            fromkeys = classmethod(fromkeys)

        expected = {'a': None, 'b': None}
        self.assertEqual(Dict.fromkeys('ab'), expected)

    def test_method_with_double_underline_arg(self):
        class X:
            def f(obj, __b, *, __a=42):
                self.assertEqual((__a, __b), (42, 9))

        X().f(9)


class C1055820(object):
    def __init__(self, i):
        self.i = i
        self.loop = self


class MiscTestCases(BaseTestCase):

    def test_property_with_double_underline(self):
        class X:
            # __a will be "_X__a" in the co.co_names
            def k(self):
                self.__a = 1

            def get_a(self):
                return self.__a

        a = X()
        a.k()
        self.assertEqual(1, a.get_a())

    def test_bug1055820b(self):
        # Corresponds to temp2b.py in the bug report.

        ouch = []
        def callback(ignored):
            ouch[:] = [wr() for wr in WRs]

        Cs = [C1055820(i) for i in range(2)]
        WRs = [weakref.ref(c, callback) for c in Cs]
        c = None

        gc.collect()
        self.assertEqual(len(ouch), 0)
        # Make the two instances trash, and collect again.  The bug was that
        # the callback materialized a strong reference to an instance, but gc
        # cleared the instance's dict anyway.
        Cs = None
        gc.collect()
        self.assertEqual(len(ouch), 2)  # else the callbacks didn't run
        for x in ouch:
            # If the callback resurrected one of these guys, the instance
            # would be damaged, with an empty __dict__.
            self.assertEqual(x, None)

    def test_missing_variable(self):
        with self.assertRaises(NameError):
            f'v:{value}'


if __name__ == '__main__':
    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_set_literal_insertion_order'
    suite1 = loader.loadTestsFromTestCase(BlockTestCases)
    suite2 = loader.loadTestsFromTestCase(MethodTestCases)
    suite3 = loader.loadTestsFromTestCase(MiscTestCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite1)
    result = unittest.TextTestRunner(verbosity=2).run(suite2)
    result = unittest.TextTestRunner(verbosity=2).run(suite3)
