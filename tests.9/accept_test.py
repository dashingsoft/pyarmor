# -*- coding: utf-8 -*-

import logging
import os
import shutil
import unittest

from test.support import script_helper

import genscript as script_generator


class BaseTestCase(unittest.TestCase):

    work_path = os.path.abspath(os.path.dirname(__file__))

    @classmethod
    def setUpClass(cls):
        cls.local_path = os.path.join(cls.work_path, '.pyarmor')
        cls.default_output = os.path.join(cls.work_path, 'dist')

    def setUp(self):
        shutil.rmtree(self.local_path, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.local_path, ignore_errors=True)

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

    def verify_script_pass(self, script, expected):
        rc, stdout, stderr = self.assert_python_ok(script)
        self.assertEqual(expected, (rc, stdout, stderr))

    def build_v9_script(self, script, target):
        kwargs = {
            '__isolated': False,
            '__cwd': self.work_path,
        }
        args = ['-m', 'pyarmor.cli', 'init', '-e', os.path.abspath(script)]
        script_helper.assert_python_ok(*args, **kwargs)

        args = ['-m', 'pyarmor.cli', 'build', '--' + target]
        script_helper.assert_python_ok(*args, **kwargs)
        return os.path.join(self.default_output, os.path.basename(script))

    def make_script(self, source, name='foo'):
        return script_helper.make_script(self.work_path, name, source)

    def iter_scripts(self, catalog=''):
        path = os.path.join('samples', catalog)
        if os.path.exists(path):
            with os.scandir(path) as it:
                for entry in it:
                    if entry.name.endswith('.py') and entry.is_file():
                        yield entry.path

        for name, source in script_generator.iter_scripts(catalog):
            yield self.make_script(source, name=name)


class UnitTestCases(BaseTestCase):

    def test_vmc_mode(self):
        for script in self.iter_scripts('modules'):
            with self.subTest(script=script):
                expected = self.assert_python_ok(script)
                vmcscript = self.build_v9_script(script, 'vmc')
                self.verify_script_pass(vmcscript, expected)


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_exclude_'
    suite = loader.loadTestsFromTestCase(UnitTestCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
