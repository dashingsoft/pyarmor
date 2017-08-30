# -*- coding: utf-8 -*-
#
import logging
import sys
import os
import shutil
import tarfile
import tempfile
from zipfile import ZipFile
from StringIO import StringIO

# Both python2/python3
try:
    import test.support as test_support
except ImportError:
    from test import test_support as test_support
# Fix python2.5 issue
if not hasattr(test_support, 'import_module'):
    setattr(test_support, 'import_module', lambda m: __import__(m) or sys.modules[m])
import unittest

srcpath = '../src'
namelist = ('pyshield.lic', 'pyshield.key', 'public.key', 'product.key',
            'config.py', 'pyarmor.py', 'pytransform.py', 'pyimcore.py')
workpath = '__runtime__'
ext_char = 'e'
logfile = os.path.join(workpath, '__pyarmor.log')

def setupModuleTest():
    if not os.path.exists(workpath):
        os.makedirs(workpath)

    tar = tarfile.open(os.path.join('data', 'pyarmor-data.tar.gz'))
    tar.extractall(path=workpath)
    tar.close()

    capsule = os.path.join('data', 'project.zip')
    path = os.path.join(workpath, 'project')
    os.makedirs(path)
    ZipFile(capsule).extractall(path=path)

    sys.rootdir = workpath
    sys.path.append(workpath)
    for name in namelist:
        shutil.copyfile(os.path.join(srcpath, name), os.path.join(workpath, name))

def cleanupModuleTest():
    sys.path.remove(workpath)

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        # self.stdout = open(os.path.join(workpath, 'stdout.log'), 'w')
        self.stdout = StringIO()
        sys.stdout = self.stdout
        self.pyarmor = test_support.import_module('pyarmor')
        self.pyarmor.__dict__['pytransform'] = test_support.import_module('pytransform')

        with open(logfile, 'w') as f:
            pass

    def tearDown(self):
        sys.stdout = sys.__stdout__
        self.stdout.close()

    def searchStdoutOutput(self, text):
        with open(logfile, 'r') as f:
            s = f.read()
            # sys.stderr.write('\n\n%s\n\n' % s)
            return not (s.decode().find(text) == -1)

class PyarmorTestCases(BaseTestCase):

    def test_get_registration_code(self):
        fm = self.pyarmor._get_registration_code
        self.assertEquals(fm(), 'Dashingsoft Pyshield Project')

    def test_show_version_info(self):
        fm = self.pyarmor.show_version_info
        fm()

    def test_show_hd_info(self):
        fm = self.pyarmor.show_hd_info
        fm()

    def test_usage(self):
        fm = self.pyarmor.usage
        fm()
        fm('capsule')
        fm('encrypt')
        fm('license')
        fm('not_command')

    def test_make_capsule(self):
        ft = self.pyarmor.make_capsule
        filename = os.path.join(workpath, 'project.zip')
        ft(rootdir=workpath, filename=filename)
        self.assertTrue(os.path.exists(filename))

    def test_encrypt_files(self):
        ft = self.pyarmor.encrypt_files
        names = 'main.py', 'foo.py'
        files = [os.path.join(workpath, x) for x in names]
        prokey = os.path.join(workpath, 'project', 'product.key')
        ft(files, prokey)
        self.assertTrue(os.path.exists(files[0] + ext_char))
        self.assertTrue(os.path.exists(files[1] + ext_char))

    def test_make_license(self):
        ft = self.pyarmor.make_license
        capsule = os.path.join('data', 'project.zip')
        filename = os.path.join(workpath, 'license.new_1.txt')
        code = 'test_make_license'
        ft(capsule, filename, code)
        self.assertTrue(os.path.exists(filename))

    def test_do_capsule(self):
        ft = self.pyarmor.do_capsule
        argv = ['--output', workpath]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(workpath, 'project.zip')))
        self.assertTrue(self.searchStdoutOutput('Generate capsule OK'))

        argv = ['--output', workpath, 'myproject']
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(workpath, 'myproject.zip')))

    def test_do_capsule_with_force(self):
        ft = self.pyarmor.do_capsule
        argv = ['--output', workpath]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('already exists'))

        argv.append('-f')
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Generate capsule OK'))

    # def test_encrypt_files_with_output(self):
    #     ft = self.pyarmor.encrypt_files
    #     files = [os.path.join(workpath, 'examples', 'hello1.py')]
    #     kv = self.key + self.iv
    #     output = os.path.join(workpath, 'build')
    #     ft(files, kv, output=output)
    #     self.assertTrue(os.path.exists(os.path.join(output, 'hello1.py' + ext_char)))

    # def test_do_encrypt(self):
    #     ft = self.pyarmor.do_encrypt

    #     output = os.path.join(workpath, 'build')
    #     argv = ['-O', output,
    #             os.path.join(workpath, 'examples/hello1.py'),
    #             os.path.join(workpath, 'examples/hello2.py'),
    #             os.path.join(workpath, 'examples/helloext.c'),
    #             os.path.join(workpath, 'examples/helloext.pyd'),
    #             ]
    #     ft(argv)
    #     self.assertTrue(os.path.exists(os.path.join(output, 'hello1.py' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'hello2.py' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'helloext.c' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'helloext.pyd' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.key')))

    # def test_do_encrypt_pattern_file(self):
    #     ft = self.pyarmor.do_encrypt

    #     output = os.path.join(workpath, 'build')
    #     argv = ['-O', output,
    #             os.path.join(workpath, 'examples/*.py'),
    #             ]
    #     ft(argv)

    #     self.assertTrue(os.path.exists(os.path.join(output, 'hello1.py' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'hello2.py' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'pyhello.py' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.key')))

    # def test_do_encrypt_with_path(self):
    #     ft = self.pyarmor.do_encrypt
    #     output = os.path.join(workpath, 'build')
    #     argv = ['-O', output, '--path',
    #             os.path.join(workpath, 'examples'),
    #             '*.pyd'
    #             ]
    #     ft(argv)
    #     self.assertTrue(os.path.exists(os.path.join(output, 'helloext.pyd' + ext_char)))

    # def test_do_encrypt_empty_file(self):
    #     ft = self.pyarmor.do_encrypt
    #     output = os.path.join(workpath, 'build')
    #     filename = os.path.join(workpath, 'examples', 'empty.py')
    #     f = open(filename, 'w')
    #     f.close()
    #     argv = ['-O', output, filename]
    #     ft(argv)
    #     self.assertTrue(os.path.exists(os.path.join(output, 'empty.py' + ext_char)))

    # def test_do_encrypt_with_path_at_file(self):
    #     ft = self.pyarmor.do_encrypt
    #     output = os.path.join(workpath, 'build')
    #     filename = os.path.join(workpath, 'filelist.txt')
    #     f = open(filename, 'w')
    #     f.write('register.py\n\ncore/pyshield.py')
    #     f.close()
    #     argv = ['-O', output, '--path',
    #             os.path.join(workpath, 'examples', 'pydist'),
    #             '@' + filename
    #             ]
    #     ft(argv)
    #     self.assertTrue(os.path.exists(os.path.join(output, 'register.py' + ext_char)))
    #     self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.py' + ext_char)))

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s %(message)s',
        filename=logfile,
        filemode='w',
        )
    setupModuleTest()
    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_do_capsule'
    suite = loader.loadTestsFromTestCase(PyarmorTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
    cleanupModuleTest()
