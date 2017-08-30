# -*- coding: utf-8 -*-
#
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
namelist = ('pyshield.lic', 'pyshield.key', 'public.key', 'product.key', 'license.lic',
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
        self.pyarmor = test_support.import_module('pyarmor')

    def tearDown(self):
        pass

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
        ft = self.pyarmor.make_capsule
        filename = os.path.join('data', 'project.zip')
        ft(rootdir=workpath, filename=filename)
        self.assertTrue(os.path.exists(filename))


if __name__ == '__main__':
    setupModuleTest()
    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test_usage'
    suite = loader.loadTestsFromTestCase(PyarmorTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
    cleanupModuleTest()
