# -*- coding: utf-8 -*-

import logging
import os
import shutil
import unittest

from subprocess import check_output, STDOUT
from test.support import script_helper


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.home = os.path.expanduser('~/.pyarmor')
        self.local_path = '.pyarmor'
        self.default_output = 'dist'
        self.more_pyi_options = '-i {0} --add-data "{1}{2}mypkg"'.format(
            'samples/pack/mypkg/logo.ico',
            'samples/pack/mypkg/data.json',
            os.pathsep
        )

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

    def pyispec_cmd(self, options):
        args = ['-m', 'PyInstaller.utils.cliutils.makespec'] + options
        self.assert_python_ok(*args)

    def verify_bundle(self, myapp):
        expected = ['this is fib:  __pyarmor__',
                    'hello world',
                    'pass: abcxyz',
                    '2 + 6 = 8',
                    '0 1 1 2 3 5 ',
                    'this is foo:  __pyarmor__']
        stdout = check_output(myapp, stderr=STDOUT)
        self.assertEqual(stdout.decode().strip().split(os.linesep), expected)


class UnitTestCases(BaseTestCase):

    def test_onefile(self):
        args = ['gen', '--pack', 'onefile', 'samples/pack/myapp.py']
        self.pyarmor_cmd(args)
        self.verify_bundle('dist/myapp')

    def test_onedir(self):
        args = ['gen', '--pack', 'onedir', 'samples/pack/myapp.py']
        self.pyarmor_cmd(args)
        self.verify_bundle('dist/myapp/myapp')

    def test_specfile(self):
        self.pyispec_cmd(['-F', 'samples/pack/myapp.py'])
        args = ['gen', '--pack', 'myapp.spec', '-r',
                'samples/pack/myapp.py', 'samples/pack/mypkg/']
        self.pyarmor_cmd(args)
        self.verify_bundle('dist/myapp')

    def test_onefile_with_name(self):
        args = ['cfg', 'pack:pyi_options', '=', '-n myapp2']
        self.pyarmor_cmd(args)

        args = ['gen', '--pack', 'onefile', 'samples/pack/myapp.py']
        self.pyarmor_cmd(args)
        self.verify_bundle('dist/myapp2')

    def test_onedir_with_name(self):
        args = ['cfg', 'pack:pyi_options', '=', '-n myapp2']
        self.pyarmor_cmd(args)

        args = ['gen', '--pack', 'onedir', 'samples/pack/myapp.py']
        self.pyarmor_cmd(args)
        self.verify_bundle('dist/myapp2/myapp2')

    def test_onefile_with_options(self):
        args = ['cfg', 'pack:pyi_options', '=', self.more_pyi_options]
        self.pyarmor_cmd(args)

        args = ['gen', '--pack', 'onefile', 'samples/pack/myapp.py']
        self.pyarmor_cmd(args)
        self.verify_bundle('dist/myapp')

    def test_onedir_with_options(self):
        args = ['cfg', 'pack:pyi_options', '=', self.more_pyi_options]
        self.pyarmor_cmd(args)

        args = ['gen', '--pack', 'onedir', 'samples/pack/myapp.py']
        self.pyarmor_cmd(args)
        self.verify_bundle('dist/myapp/myapp')


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_exclude_'
    suite = loader.loadTestsFromTestCase(UnitTestCases)
    result = unittest.TextTestRunner().run(suite)
