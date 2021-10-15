# -*- coding: utf-8 -*-
# {No PyArmor Protection Code}

import sys
import unittest

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
        from decimal import Decimal
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
        self.assertEqual(10 and True, True)
        self.assertEqual(True and 10, 10)
        self.assertEqual(0 and 10, 0)
        self.assertEqual(False and 10, 0)

        self.assertEqual(10 or True, 10)
        self.assertEqual(True or 10, True)
        self.assertEqual(0 or 10, 10)
        self.assertEqual(False or 10, 10)

    @unittest.skipIf(sys.platform == 'win32', 'due to super mode crash')
    def test_recursion_limit(self):
        '''sppmode will ignore function by RecursionError'''
        def f():
            try:
                f()
            except RecursionError:
                pass
        self.assertEqual(f(), None)

    def test_starlist(self):
        a = 1, 2, 3
        self.assertEqual((*a, 4), (1, 2, 3, 4))

        a = (1, 2), 3
        b = 4, (5, 6)
        self.assertEqual((*a, *b, 7), ((1, 2), 3, 4, (5, 6), 7))

        a = {1: 1, 2: 2}
        b = {3: 3}
        self.assertEqual({**a, **b, 4: 4}, {1: 1, 2: 2, 3: 3, 4: 4})

        # a, *b = 1, 2, 3, 4
        # self.assertEqual(a, 1)
        # self.assertEqual(b, [2, 3, 4])

        # *a, b = 1, 2, 3, 4
        # self.assertEqual(a, [1, 2, 3])
        # self.assertEqual(b, 4)

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
            def handler():
                self.assertEqual(ZeroDivisionError, type(e))
            handler()


if __name__ == '__main__':
    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_op_inplace'
    suite = loader.loadTestsFromTestCase(BlockTestCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
