# -*- coding: utf-8 -*-

import glob
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

    def pyarmor_cmd(self, options):
        args = ['-m', 'pyarmor.cli'] + options
        rc, stdout, stderr = self.assert_python_ok(*args)
        self.assertIn(b'obfuscate scripts OK', stderr)

    def pyarmor_cfg(self, options):
        args = ['-m', 'pyarmor.cli'] + options
        rc, stdout, stderr = self.assert_python_ok(*args)

    def verify_script_pass(self, script, expected=None):
        rc, stdout, stderr = self.assert_python_ok(script)
        if expected:
            self.assertIn(expected, stdout)

    def verify_script_fail(self, script, errmsg=None):
        rc, stdout, stderr = self.assert_python_failure(script)
        if errmsg:
            self.assertIn(errmsg, stderr)


class UnitTestCases(BaseTestCase):

    def _update_dist_script(self, script):
        with open(script, 'a') as f:
            f.write('pi = 3.1415926')

    def test_simple_issues(self):
        prefix = 'samples/pyfeatures/is_'
        scripts = glob.glob(prefix + '*.py')
        expected = b'All test passed'
        for script in scripts:
            args = ['g', script]
            self.pyarmor_cmd(args)
            with self.subTest(issue=script[len(prefix):-3]):
                self.verify_script_pass(script, expected)

    def test_wrapmode_2(self):
        script = 'samples/pyfeatures/wrap2.py'
        expected = b'All test passed'
        self.pyarmor_cfg(['cfg', 'wrap_mode', '2'])
        self.pyarmor_cmd(['g', script])
        self.pyarmor_cfg(['cfg', 'wrap_mode', '1'])
        self.verify_script_pass(script, expected)

    def test_rft_issues(self):
        prefix = 'samples/pyfeatures/rft_'
        scripts = glob.glob(prefix + '*.py')

        for script in scripts:
            args = ['g', '--enable-rft', script]
            self.pyarmor_cmd(args)
            with self.subTest(issue=script[len(prefix):-3]):
                self.verify_script_pass(script)


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())

    verbosity = 1

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_mix_str'
    suite = loader.loadTestsFromTestCase(UnitTestCases)
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
