# -*- coding: utf-8 -*-

import logging
import os
import shutil
import time
import unittest

from struct import calcsize
from test.support import script_helper


def metricmethod(func):
    if not hasattr(time, 'process_time'):
        time.process_time = time.clock

    def wrap(*args, **kwargs):
        t1 = time.process_time()
        result = func(*args, **kwargs)
        t2 = time.process_time()
        print('%10.6f ms' % ((t2 - t1) * 1000))
        return result
    return wrap


def is_x86():
    return calcsize('P'.encode()) * 8 == 32


def skip_protest(func):

    def wrap(self, *args, **kwargs):
        if self.is_trial():
            self.skipTest('pro case')
        func(self, *args, **kwargs)

    return wrap


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.home = os.path.expanduser('~/.pyarmor')
        self.local_path = '.pyarmor'
        self.default_output = 'dist'

    def is_trial(self):
        return not os.path.exists(os.path.join(self.home, 'license.lic'))

    def tearDown(self):
        shutil.rmtree(self.local_path, ignore_errors=True)
        shutil.rmtree(self.default_output, ignore_errors=True)

    def assert_python_ok(self, *args):
        kwargs = {
            '__isolated': False
        }
        return script_helper.assert_python_ok(*args, **kwargs)

    def assert_python_failure(self, *args):
        kwargs = {
            '__isolated': False
        }
        return script_helper.assert_python_failure(*args, **kwargs)

    def pyarmor_gen(self, options):
        args = ['-m', 'pyarmor.cli'] + options
        rc, stdout, stderr = self.assert_python_ok(*args)
        self.assertIn(b'obfuscate scripts OK', stderr)

    def verify_dist_foo(self, script=None):
        if script is None:
            script = 'dist/foo.py'
        assert_python_ok = metricmethod(self.assert_python_ok)
        rc, stdout, stderr = assert_python_ok(script)
        self.assertEqual(stdout.replace(b'\r\n', b'\n'),
                         b'hello world\npass: abcxyz\n2 + 6 = 8\n')

    def verify_dist_foo_fail(self, script=None, errmsg=None):
        if script is None:
            script = 'dist/foo.py'
        rc, stdout, stderr = self.assert_python_failure(script)
        if errmsg is None:
            errmsg = b'RuntimeError: unauthorized use of script'
        self.assertIn(errmsg, stderr)

    def verify_dist_joker(self, script=None):
        if script is None:
            script = 'dist/a.py'
            with open(script, 'w') as f:
                lines = (
                    'from joker import fib',
                    'fib(2)'
                )
                f.write('\n'.join(lines))
        rc, stdout, stderr = self.assert_python_ok(script)
        self.assertEqual(stdout.strip(), b'0 1 1')

    def verify_dist_joker_fail(self, script=None):
        if script is None:
            script = 'dist/a.py'
            with open(script, 'w') as f:
                lines = (
                    'from joker import fib',
                    'fib(2)'
                )
                f.write('\n'.join(lines))
        rc, stdout, stderr = self.assert_python_failure(script)
        errmsg = b'RuntimeError: protection exception'
        self.assertIn(errmsg, stderr)


class UnitTestCases(BaseTestCase):

    def _update_dist_foo(self, script='dist/foo.py'):
        with open(script, 'a') as f:
            f.write('pi = 3.1415926')

    @unittest.skip("too slow")
    def test_custome_type(self):
        args = ['g', 'samples/foo.py']
        self.pyarmor_gen(args)
        for i in range(100):
            self.verify_dist_foo()

    def test_sciprt(self):
        args = ['g', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    def test_package(self):
        args = ['g', 'samples/joker']
        self.pyarmor_gen(args)
        self.verify_dist_joker()

    def test_enable_jit(self):
        args = ['g', '--enable-jit', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    @skip_protest
    def test_mix_str(self):
        args = ['g', '--mix-str', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    @skip_protest
    def test_enable_bcc(self):
        args = ['g', '--enable-bcc', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    @skip_protest
    def test_enable_rft(self):
        args = ['g', '--enable-rft', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    @skip_protest
    def test_enable_rft_bcc(self):
        args = ['g', '--enable-rft', '--enable-bcc', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    def test_default_restrict(self):
        args = ['g', 'samples/foo.py']
        self.pyarmor_gen(args)
        self._update_dist_foo()
        self.verify_dist_foo_fail()

    def test_private_script(self):
        args = ['g', '--private', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    def test_restrict_script(self):
        args = ['g', '--restrict', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo_fail()

    def test_restrict_pkg(self):
        args = ['g', '--restrict', 'samples/joker']
        self.pyarmor_gen(args)
        self.verify_dist_joker()

    def test_assert_import(self):
        args = ['g', '--assert-import', 'samples/joker']
        self.pyarmor_gen(args)
        self.verify_dist_joker()

        shutil.copy2('samples/joker/card.py', 'dist/joker/card.py')
        self.verify_dist_joker_fail()

    def test_assert_call(self):
        args = ['g', '--assert-call', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    def test_expired_local_days(self):
        args = ['g', '-e', '.30', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    def test_expired_nts_days(self):
        args = ['g', '-e', '30', 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()

    def test_expired_local_iso_date(self):
        args = ['g', '-e', '.2020-01-01', 'samples/foo.py']
        self.pyarmor_gen(args)
        errmsg = b'RuntimeError: this license key is expired'
        self.verify_dist_foo_fail(errmsg=errmsg)

    @unittest.skip("other machine")
    def test_bind_device(self):
        hdinfo = 'FV994730S6LLF07AY', 'f8:ff:c2:27:00:7f', '192.168.121.100'
        args = ['g', '-b', ' '.join(hdinfo), 'samples/foo.py']
        self.pyarmor_gen(args)
        self.verify_dist_foo()


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_mix_str'
    suite = loader.loadTestsFromTestCase(UnitTestCases)
    result = unittest.TextTestRunner().run(suite)
