# -*- coding: utf-8 -*-

import logging
import os
import shutil
import unittest

from test.support import script_helper

from script_factory import script_generator


class BaseTestCase(unittest.TestCase):

    work_path = os.path.abspath(os.path.dirname(__file__))

    @classmethod
    def setUpClass(cls):
        cls.python_nogil = os.path.abspath(os.getenv('PYTHON_NOGIL'))
        cls.local_path = os.path.join(cls.work_path, '.pyarmor')
        cls.default_output = os.path.join(cls.work_path, 'dist')

    def setUp(self):
        shutil.rmtree(self.local_path, ignore_errors=True)

    def tearDown(self):
        pass

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

    def verify_script_nogil_pass(self, script, expected):
        from subprocess import check_output
        assert os.path.exists(self.python_nogil), self.python_nogil
        stdout = check_output([self.python_nogil, script])
        self.assertEqual(expected[1], stdout)

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

    def _test_target(self, target, catalog=None):
        for script in self.iter_scripts(catalog):
            with self.subTest(script=script):
                expected = self.assert_python_ok(script)
                obfscript = self.build_v9_script(script, target)
                self.verify_script_nogil_pass(obfscript, expected)

    def make_script(self, source, name='foo'):
        return script_helper.make_script(self.work_path, name, source)

    def iter_samples(self):
        path = os.path.join(self.work_path, 'samples')
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.endswith('.py') and entry.is_file():
                    yield entry.path

    def iter_scripts(self, catalog):
        if catalog:
            for name, source in script_generator(catalog):
                yield self.make_script(source, name=name)
        else:
            yield from self.iter_samples()


class UnitTestCases(BaseTestCase):

    def test_mini_mode(self):
        self._test_target('mini')
        self._test_target('mini', 'modules')
        self._test_target('mini', 'functions')
        self._test_target('mini', 'methods')

    def test_vmc_mode(self):
        self._test_target('vmc')
        self._test_target('vmc', 'modules')
        self._test_target('vmc', 'functions')
        self._test_target('vmc', 'methods')

    def test_ecc_mode(self):
        self._test_target('ecc-nogil')
        self._test_target('ecc-nogil', 'modules')
        self._test_target('ecc-nogil', 'functions')
        self._test_target('ecc-nogil', 'methods')

    def test_rft_mode(self):
        self._test_target('rft')
        self._test_target('rft', 'modules')
        self._test_target('rft', 'functions')
        self._test_target('rft', 'methods')

    def test_mini_rft_mode(self):
        self._test_target('mini-rft')
        self._test_target('mini-rft', 'modules')
        self._test_target('mini-rft', 'functions')
        self._test_target('mini-rft', 'methods')

    def test_vmc_rft_mode(self):
        self._test_target('vmc-rft')
        self._test_target('vmc-rft', 'modules')
        self._test_target('vmc-rft', 'functions')
        self._test_target('vmc-rft', 'methods')

    def test_ecc_rft_mode(self):
        self._test_target('ecc-nogil-rft')
        self._test_target('ecc-nogil-rft', 'modules')
        self._test_target('ecc-nogil-rft', 'functions')
        self._test_target('ecc-nogil-rft', 'methods')


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_nogil'
    suite = loader.loadTestsFromTestCase(UnitTestCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
