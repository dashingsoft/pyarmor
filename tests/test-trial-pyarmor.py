# -*- coding: utf-8 -*-
#
import sys
import os
import shutil
import tarfile
import tempfile
from subprocess import Popen
from zipfile import ZipFile

try:
    from StringIO import StringIO
except Exception:
    from io import StringIO

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
namelist = ('pyshield.lic', 'pyshield.key', 'public.key', 'product.key', 'license.lic',
            'config.py', 'pyarmor.py', 'pytransform.py', 'pyimcore.py')
workpath = '__runtime__'
ext_char = 'e'

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

    def tearDown(self):
        sys.stdout = sys.__stdout__
        self.stdout.close()

class PyarmorTestCases(BaseTestCase):

    def test_get_registration_code(self):
        fm = self.pyarmor._get_registration_code
        self.assertEquals(fm(), '')

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
        '''Check all capsules generated are same.'''
        ft = self.pyarmor.make_capsule
        filename1 = os.path.join(workpath, 'project-t1.zip')
        ft(rootdir=workpath, filename=filename1)
        self.assertTrue(os.path.exists(filename1))

        filename2 = os.path.join(workpath, 'project-t2.zip')
        ft(rootdir=workpath, filename=filename2)
        self.assertTrue(os.path.exists(filename2))

        p = Popen(['diff', filename1, filename2])
        retcode = p.wait()
        self.assertEquals(retcode, 0)

    def test_encrypt_files(self):
        ft = self.pyarmor.encrypt_files
        names = 'main.py', 'foo.py'
        files = [os.path.join(workpath, x) for x in names]
        files = [(x, os.path.splitext(x)[0]) for x in files]
        prokey = os.path.join(workpath, 'project', 'product.key')
        ft(files, prokey)
        self.assertTrue(os.path.exists(files[0][0] + ext_char))
        self.assertTrue(os.path.exists(files[1][0] + ext_char))

    def test_make_license(self):
        ft = self.pyarmor.make_license
        capsule = os.path.join('data', 'project.zip')
        filename = os.path.join(workpath, 'license.new_1.txt')
        code = 'test_make_license'
        ft(capsule, filename, code)
        self.assertTrue(os.path.exists(filename))

if __name__ == '__main__':
    setupModuleTest()
    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_'
    suite = loader.loadTestsFromTestCase(PyarmorTestCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cleanupModuleTest()
    sys.exit(len(result.errors) + len(result.failures))
