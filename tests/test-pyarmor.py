# -*- coding: utf-8 -*-
#
import logging
import sys
import os
import shutil
import tarfile
import tempfile

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

def setupModuleTest():
    if not os.path.exists(workpath):
        os.makedirs(workpath)

    tar = tarfile.open(os.path.join('data', 'pyarmor-data.tar.gz'))
    tar.extractall(path=workpath)
    tar.close()

    sys.rootdir = workpath
    sys.path.append(workpath)
    for name in namelist:
        shutil.copyfile(os.path.join(srcpath, name), os.path.join(workpath, name))
    
def cleanupModuleTest():
    sys.path.remove(workpath)

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.stdout = open(os.path.join(workpath, 'stdout.log'), 'w')
        sys.stdout = self.stdout
        self.pyarmor = test_support.import_module('pyarmor')

    def tearDown(self):
        sys.stdout = sys.__stdout__
        self.stdout.close()

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
        files = [os.path.join(workpath, 'examples', 'hello1.py')]
        kv = self.key + self.iv
        ft(files, kv)
        self.assertTrue(os.path.exists(files[0] + ext_char))

    def test_encrypt_files_with_output(self):
        ft = self.pyarmor.encrypt_files
        files = [os.path.join(workpath, 'examples', 'hello1.py')]
        kv = self.key + self.iv
        output = os.path.join(workpath, 'build')
        ft(files, kv, output=output)
        self.assertTrue(os.path.exists(os.path.join(output, 'hello1.py' + ext_char)))

    def test_do_encrypt(self):
        ft = self.pyarmor.do_encrypt

        output = os.path.join(workpath, 'build')
        argv = ['-O', output,
                os.path.join(workpath, 'examples/hello1.py'),
                os.path.join(workpath, 'examples/hello2.py'),
                os.path.join(workpath, 'examples/helloext.c'),
                os.path.join(workpath, 'examples/helloext.pyd'),
                ]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'hello1.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'hello2.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'helloext.c' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'helloext.pyd' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.key')))

    def test_do_encrypt_pattern_file(self):
        ft = self.pyarmor.do_encrypt

        output = os.path.join(workpath, 'build')
        argv = ['-O', output,
                os.path.join(workpath, 'examples/*.py'),
                ]
        ft(argv)

        self.assertTrue(os.path.exists(os.path.join(output, 'hello1.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'hello2.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyhello.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.key')))

    def test_do_encrypt_with_path(self):
        ft = self.pyarmor.do_encrypt
        output = os.path.join(workpath, 'build')
        argv = ['-O', output, '--path',
                os.path.join(workpath, 'examples'),
                '*.pyd'
                ]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'helloext.pyd' + ext_char)))

    def test_do_encrypt_empty_file(self):
        ft = self.pyarmor.do_encrypt
        output = os.path.join(workpath, 'build')
        filename = os.path.join(workpath, 'examples', 'empty.py')
        f = open(filename, 'w')
        f.close()
        argv = ['-O', output, filename]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'empty.py' + ext_char)))

    def test_do_encrypt_with_path_at_file(self):
        ft = self.pyarmor.do_encrypt
        output = os.path.join(workpath, 'build')
        filename = os.path.join(workpath, 'filelist.txt')
        f = open(filename, 'w')
        f.write('register.py\n\ncore/pyshield.py')
        f.close()
        argv = ['-O', output, '--path',
                os.path.join(workpath, 'examples', 'pydist'),
                '@' + filename
                ]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'register.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.py' + ext_char)))

if __name__ == '__main__':
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format='%(levelname)-8s %(message)s',
    #     filename=os.path.join(os.getcwd(), '__pyarmor.log'),
    #     filemode='w',
    #     )
    setupModuleTest()
    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test_make_capsule'
    suite = loader.loadTestsFromTestCase(PyarmorTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
    cleanupModuleTest()
