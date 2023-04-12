# -*- coding: utf-8 -*-

import logging
import os
import shutil
import unittest

from test.support import script_helper


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.home = os.path.expanduser('~/.pyarmor')
        self.local_path = '.pyarmor'
        self.default_output = 'dist'

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

    def verify_script_pass(self, script, expected):
        rc, stdout, stderr = self.assert_python_ok(script)
        self.assertEqual(expected, stdout.splitlines())

    def verify_script_fail(self, script, errmsg):
        rc, stdout, stderr = self.assert_python_failure(script)
        self.assertIn(errmsg, stderr)


class UnitTestCases(BaseTestCase):

    def _update_dist_script(self, script):
        with open(script, 'a') as f:
            f.write('pi = 3.1415926')

    def test_simple(self):
        script = 'samples/pyfeatures/simple.py'
        args = ['g', script]
        self.pyarmor_gen(args)

        expected = [
            b"This is docstring",
            b"{'a': <class 'int'>, 'b': <class 'str'>}",
            b"{'k': <class 'str'>}"
        ]
        self.verify_script_pass(script, expected)


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_mix_str'
    suite = loader.loadTestsFromTestCase(UnitTestCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
