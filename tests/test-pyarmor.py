# -*- coding: utf-8 -*-
#
import logging
import sys
import os
import py_compile
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

    def test_do_encrypt(self):
        ft = self.pyarmor.do_encrypt
        capsule = os.path.join('data', 'project.zip')
        output = os.path.join(workpath, 'build')
        argv = ['-O', output,
                '-C', capsule,
                os.path.join(workpath, 'main.py'),
                os.path.join(workpath, 'foo.py'),
                ]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'main.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'foo.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.key')))

    def test_parse_file_args(self):
        fm = self.pyarmor._parse_file_args

        args = workpath + '/foo.?y', workpath + '/sky.*'
        filelist = fm(args)
        self.assertEquals(filelist, [os.path.join(workpath, 'foo.py'),
                                     os.path.join(workpath, 'sky.py')])

        filename = os.path.join(workpath, 'filelist.txt')
        with open(filename, 'w') as f:
            f.write(workpath + '/foo.?y\n')
            f.write(workpath + '/main.*y\n')
        args = ['@' + filename]
        filelist = fm(args)
        self.assertEquals(filelist, [os.path.join(workpath, 'foo.py'),
                                     os.path.join(workpath, 'main.py')])

        args = 'foo.py', 'main.py'
        filelist = fm(args, srcpath=workpath)
        self.assertEquals(filelist, [os.path.join(workpath, 'foo.py'),
                                     os.path.join(workpath, 'main.py')])

    def test_do_encrypt_empty_file(self):
        ft = self.pyarmor.do_encrypt
        filename = os.path.join(workpath, 'empty.py')
        f = open(filename, 'w')
        f.close()
        capsule = os.path.join('data', 'project.zip')
        output = os.path.join(workpath, 'build')
        argv = ['-O', output,
                '-C', capsule,
                filename]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Could not encrypt empty file'))
        self.assertFalse(os.path.exists(os.path.join(output, 'empty.py' + ext_char)))

    def test_do_encrypt_pyc(self):
        ft = self.pyarmor.do_encrypt
        filename = os.path.join(workpath, 'foo.pyc')
        py_compile.compile(filename[:-1])
        self.assertTrue(os.path.exists(filename))
        capsule = os.path.join('data', 'project.zip')
        output = os.path.join(workpath, 'compile')
        argv = ['-O', output,
                '-C', capsule,
                filename]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Encrypt all scripts OK'))
        self.assertTrue(os.path.exists(os.path.join(output, 'foo.pyc' + ext_char)))

    def test_do_encrypt_in_place(self):
        ft = self.pyarmor.do_encrypt
        filename = os.path.join(workpath, 'bootstrap.py')
        capsule = os.path.join('data', 'project.zip')
        output = os.path.join(workpath, 'build')
        argv = ['-O', output,
                '-C', capsule,
                '-i',
                filename]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Encrypt all scripts OK'))
        self.assertFalse(os.path.exists(os.path.join(output, 'bootstrap.py' + ext_char)))
        self.assertTrue(os.path.exists(os.path.join(workpath, 'bootstrap.py' + ext_char)))

    def test_do_encrypt_main(self):
        ft = self.pyarmor.do_encrypt
        filename = os.path.join(workpath, 'main.py')
        capsule = os.path.join('data', 'project.zip')
        output = os.path.join(workpath, 'scripts')
        argv = ['-O', output,
                '-C', capsule,
                '-m', 'main',
                filename]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Encrypt all scripts OK'))
        self.assertTrue(os.path.exists(os.path.join(output, 'main.py' + ext_char)))
        target = os.path.join(output, 'main.py')
        self.assertTrue(os.path.exists(target))
        with open(target, 'r') as f:
            s = f.read()
        self.assertTrue(s.find('main.pye') > 0)

    def test_do_encrypt_clean(self):
        ft = self.pyarmor.do_encrypt
        capsule = os.path.join('data', 'project.zip')
        output = os.path.join(workpath, 'build2')
        argv = ['-O', output,
                '-C', capsule,
                '-d',
                os.path.join(workpath, 'main.py'),
                os.path.join(workpath, 'foo.py'),
                ]
        ft(argv)
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Remove output path OK'))

    def test_do_encrypt_platname(self):
        ft = self.pyarmor.do_encrypt
        capsule = os.path.join('data', 'project.zip')
        output = os.path.join(workpath, 'build3')
        argv = ['-O', output,
                '-C', capsule,
                '--plat-name', 'unknow-plat',
                os.path.join(workpath, 'foo.py'),
                ]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Cross publish'))

    def test_do_license(self):
        ft = self.pyarmor.do_license
        capsule = os.path.join('data', 'project.zip')        
        argv = ['-O', workpath,
                '-C', capsule,
                ]
        ft(argv)
        self.assertTrue(os.path.exists(workpath + '/license.lic.txt'))
        self.assertTrue(self.searchStdoutOutput('Generate license file'))

        output = os.path.join(workpath, 'license.1.txt')
        argv = ['-O', output,
                '-C', capsule,
                'test-reg-code'
                ]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Generate license file'))
        self.assertTrue(os.path.exists(output))

        output = os.path.join(workpath, 'license.2.txt')
        argv = ['-O', output,
                '-C', capsule,
                '--bind-disk', 'abcdefh-hid'
                ]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Generate license file'))
        self.assertTrue(os.path.exists(output))

        output = os.path.join(workpath, 'license.3.txt')
        argv = ['-O', output,
                '-C', capsule,
                '--e', '2018-10-05',
                ]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Generate license file'))
        self.assertTrue(os.path.exists(output))

        output = os.path.join(workpath, 'license.4.txt')
        argv = ['-O', output,
                '-C', capsule,
                '--e', '2018-10-05',
                '--bind-disk', 'abcdefh-hid'
                ]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Generate license file'))
        self.assertTrue(os.path.exists(output))

        output = os.path.join(workpath, 'license.5.txt')
        argv = ['-O', output,
                '-C', capsule,
                '--bind-file', workpath + '/id_rsa',
                '~/.ssh/my_id_rsa'
                ]
        ft(argv)
        self.assertTrue(self.searchStdoutOutput('Generate license file'))
        self.assertTrue(os.path.exists(output))

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s %(message)s',
        filename=logfile,
        filemode='w',
        )
    setupModuleTest()
    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_do_license'
    suite = loader.loadTestsFromTestCase(PyarmorTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
    cleanupModuleTest()
