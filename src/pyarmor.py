#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2013 - 2017 Dashingsoft corp.            #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 1.7.0 - 3.0.1                               #
#                                                           #
#############################################################
#
#
#  @File: pyarmor.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2013/07/24
#
#  @Description:
#
#   A tool used to import or un encrypted python scripts.
#
import fnmatch
import getopt
import glob
import logging
import os
import platform
import shutil
import sys
import tempfile
import time
from zipfile import ZipFile

# The last three components of the filename before the extension are
# called "compatibility tags." The compatibility tags express the
# package's basic interpreter requirements and are detailed in PEP
# 425(https://www.python.org/dev/peps/pep-0425).
from distutils.util import get_platform

try:
    unhexlify = bytes.fromhex
except Exception:
    from binascii import a2b_hex as unhexlify

__version__ = '3.0.1'

__version_info__ = '''
Pyarmor is a tool used to import or run the encrypted python
scripts. Only by a few extra files, pyarmor can run and imported
encrypted files in the normal python environments. Here are the basic
steps:

- Generate project capsule
- Encrypt python scripts with project capsule
- Copy project capsule and encrypted scripts to runtime environments.

Pyarmor just likes an enhancement which let python could run or import
encrypted files.

'''

__trial_info__ = '''
You're using trail version. Free trial version that never expires,
but project capsule generated is fixed by hardcode, so all the
encrypted files are encrypted by same key.

A registration code is required to generate random project
capsule. Visit
https://shopper.mycommerce.com/checkout/cart/add/55259-1 to purchase
one.

If you have received a registration code, just replace the content of
"license.lic" with registration code only (no newline).

'''

__footer__ = '''
For more information, refer to https://github.com/dashingsoft/pyarmor
'''

# Extra suffix char for encrypted python scripts
ext_char = os.getenv('PYARMOR_EXTRA_CHAR', 'e')

def _get_kv(value):
    if os.path.exists(value):
        f = open(value, 'r')
        value = f.read()
        f.close()
    return value.replace('\n', ' ').replace('\r', '')

def _get_registration_code():
    try:
        code = pytransform.get_registration_code()
    except Exception:
        code = ''
    return code

def _format_platform():
    platform = get_platform().replace('-', '_').replace('.', '_').lower()
    return platform

def _import_pytransform():
    try:
        m = __import__('pytransform')
        return m
    except ImportError:
        pass
    path = sys.rootdir
    platform = _format_platform()
    name = '_pytransform.' + ('so' if platform.startswith('linux') else 'dll')
    src = os.path.join(path, 'platforms', platform, name)
    if not os.path.exists(src):
        raise RuntimeError('no library %s found' % src)
    logging.info('find pytransform library "%s"' % src)
    logging.info('copy %s to %s' % (src, path))
    shutil.copyfile(src, path)

    m = __import__('pytransform')
    logging.info('Load pytransform OK.')
    return m

def checklicense(func):
    def wrap(*arg, **kwargs):
        code = _get_registration_code()
        if code == '':
            print(__trial_info__)
        func(*arg, **kwargs)
    return wrap

def show_version_info(verbose=True):
    code = _get_registration_code()
    trial = ' Trial' if  code == '' else ''
    print('Pyarmor%s Version %s' % (trial, __version__))
    if verbose:
        print(__version_info__)
        if code == '':
            print(__trial_info__)
        print(__footer__)

def show_hd_info():
    sn = pytransform.get_hd_sn()
    if sn == '':
        print("Could not get harddisk's serial number")
    else:
        print("Harddisk's serial number is '%s'" % sn)

def usage(command=None):
    '''
Usage: pyarmor [command name] [options]

Command name can be one of the following list

  help                Show this usage
  version             Show version information
  capsule             Generate project capsule used to encrypted files
  encrypt             Encrypt the scripts
  license             Generate registration code

If you want to know the usage of each command, type the
following command:

  pyarmor help [command name]

and you can type the left match command, such as

   pyarmor c
or pyarmor cap
or pyarmor capsule

    '''
    show_version_info(verbose=False)

    if command is None:
        print(usage.__doc__)
    else:
        funcname = 'do_' + command
        func = globals().get(funcname, usage)
        print(func.__doc__)
    print(__footer__)

def make_capsule(rootdir=None, filename='project.zip'):
    '''Generate all the files used by running encrypted scripts, pack all
    of them to a zip file.

    rootdir        pyarmor root dir, where you can find license files,
                   auxiliary library and pyshield extension module.

    filename       output filename, the default value is project.zip

    Return True if sucess, otherwise False or raise exception
    '''
    try:
        if rootdir is None:
            rootdir = sys.rootdir
    except AttributeError:
        rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    logging.info('rootdir is %s' % rootdir)
    filelist = 'public.key', 'pyimcore.py'
    for x in filelist:
        src = os.path.join(rootdir, x)
        if not os.path.exists(src):
            logging.error('missing %s' % src)
            return False

    licfile = os.path.join(rootdir, 'license.lic')
    if not os.path.exists(licfile):
        logging.error('missing license file %s' % licfile)
        return False

    logging.info(_('generate product key'))
    pri, pubx, capkey, lic = pytransform.generate_project_capsule()

    logging.info('generating capsule %s ...' % filename)
    myzip = ZipFile(filename, 'w')
    try:
        myzip.write(os.path.join(rootdir, 'public.key'), 'pyshield.key')
        myzip.writestr('pyshield.lic', capkey)
        myzip.write(os.path.join(rootdir, 'pyimcore.py'), 'pyimcore.py')
        myzip.writestr('private.key', pri)
        myzip.writestr('product.key', pubx)
        myzip.writestr('license.lic', lic)
    finally:
        myzip.close()
    logging.info('generate capsule %s OK.' % os.path.abspath(filename))
    return True

def encrypt_files(files, kv, output=None):
    '''Encrypt all the files, all the encrypted scripts will be plused with
    a suffix 'e', for example, hello.py -> hello.pye

    files          list all the scripts
    kv             32 bytes used to encrypt scripts
    output         output directory. If None, the output file will be saved
                   in the same path as the original script

    Return None if sucess, otherwise raise exception
    '''
    if output is None:
        fn = lambda a, b : b + ext_char
    else:
        fn = lambda a, b : os.path.join(a, os.path.basename(b) + ext_char)
        if not os.path.exists(output):
            os.makedirs(output)

    flist = []
    for x in files:
        flist.append((x, fn(output, x)))
        logging.info(_('encrypt %s to %s') % flist[-1])

    if flist[:1]:
        if isinstance(kv, str) and kv.endswith('product.key'):
            if not os.path.exists(kv):
                raise RuntimeError('missing product.key')
            pytransform.encrypt_project_files(kv, tuple(flist))
        else:
            pytransform.encrypt_files(kv, tuple(flist))
        logging.info(_('encrypt all scripts OK.'))
    else:
        logging.info(_('No script found.'))

def make_license(capsule, filename, fmt):
    myzip = ZipFile(capsule, 'r')
    myzip.extract('private.key', tempfile.gettempdir())
    prikey = os.path.join(tempfile.tempdir, 'private.key')
    start = -1
    count = 1
    pytransform.generate_serial_number(filename, prikey, fmt, start, count)
    os.remove(prikey)

@checklicense
def do_encrypt(argv):
    '''
Usage: pyarmor encrypt [OPTIONS] [File Patterns or @Filename]

  Encrpty the files list in the command line, you can use a
  specified pattern according to the rules used by the Unix
  shell. No tilde expansion is done, but *, ?, and character
  ranges expressed with [] will be correctly matched.

  You can either list file patterns in one file, one pattern one line,
  then add a prefix '@' to the filename.

  All the files will be encrypted and saved as orginal file
  name plus 'e'. By default, the encrypted scripts and all the
  auxiliary files used to run the encrypted scripts are save in
  the path "dist".

  Available options:

  -O, --output=DIR                [option], all the encrypted files will
                                  be saved here.
                                  The default value is "dist".

  -C, --with-capsule=FILENAME     [option] Specify the filename of capsule
                                  generated before. If this option isn't
                                  specified, pyarmor will generate a
                                  temporary capsule to encrypt the scripts.

  -i                              [option], the encrypted scripts will be saved
                                  in the original path (same as source).

  -P, --path=DIR                  [option], the source path of python scripts.
                                  The default value is current path.

                                  The default value is "dist".
  -S, --with-extension=FILENAME   [option] Specify the filename of python
                                  module "pytransform", only used for cross
                                  publish. By default, it will be the value
                                  of pytransform.__file__ imported by pyarmor.

  For examples:

    - Encrypt a.py and b.py as a.pyx and b.pyx, saved in the path "dist":

      pyarmor encrypt a.py b.py

    - Use file pattern to specify files:

      pyarmor encrypt a.py *.py src/*.py lib/*.pyc

    - Save encrypted files in the directory "/tmp/build" other than "dist":

      pyarmor encrypt --output=/tmp/build a.py

    - Encrypt python scripts by project capsule "project.zip" in the
      current directory:

      pyarmor encrypt --with-capsule=project.zip src/*.py

    - Encrypt python scripts to run in different platform:

      pyarmor encrypt \
        --with-extension=extensions/pytransform-1.7.2.linux-armv7.so \
        a.py b.py

    '''

    try:
        opts, args = getopt.getopt(
            argv,
            'C:O:iP:S:',
            ['in-place', 'output=', 'path=', 'with-capsule=', 'with-extension=']
            )
    except getopt.GetoptError:
        logging.exception('option error')
        usage('encrypt')
        sys.exit(1)

    if len(args) == 0:
        logging.error(_('missing the script names'))
        usage('encrypt')
        sys.exit(2)

    output = 'dist'
    srcpath = None
    kv = None
    capsule = None
    extfile = None
    sameplace = False

    for o, a in opts:
        if o in ('-O', '--output'):
            output = a
        elif o in ('-P', '--path'):
            srcpath = a
        elif o in ('-i', '--in-place'):
            sameplace = True
        elif o in ('-C', '--with-capsule'):
            capsule = a
        elif o in ('-S', '--with-extension'):
            extfile = a

    if srcpath is not None and not os.path.exists(srcpath):
        logging.error(_('missing base path "%s"') % srcpath)
        return False

    if capsule is not None and not os.path.exists(capsule):
        logging.error(_('missing capsule file'))
        return False

    if output == '':
        output = os.getcwd()

    logging.info(_('output path is %s') % output)
    if not os.path.exists(output):
        logging.info(_('make output path: %s') % output)
        os.makedirs(output)

    if extfile is None:
        extfile = pytransform.__file__
        relfiles = get_related_files()
    elif os.path.exists(extfile):
        relfiles = get_related_files(extfile)
    else:
        logging.error(_('missing pytransform extension file %s') % extfile)
        return False

    if extfile.endswith('.pyd'):
        target = os.path.join(output, 'pytransform.pyd')
    elif extfile.endswith('.so'):
        target = os.path.join(output, 'pytransform.so')
    else:
        raise RuntimeError(_('Unsupport extension format'))

    logging.info(_('copy %s as %s') % (extfile, target))
    shutil.copy(extfile, target)

    for filename in relfiles:
        if not os.path.exists(filename):
            logging.error(_('missing file %s') % filename)
            return False
        logging.info(_('copy %s to %s') % (filename, output))
        target = os.path.join(output, os.path.basename(filename))
        shutil.copy(filename, target)

    if kv is not None:
        logging.info(_('key is %s') % kv)

    filelist = []
    patterns = []
    for arg in args:
        if arg[0] == '@':
            f = open(arg[1:], 'r')
            for pattern in f.read().splitlines():
                if not pattern.strip() == '':
                    patterns.append(pattern.strip())
            f.close()
        else:
            patterns.append(arg)
    for pat in patterns:
        if os.path.isabs(pat) or srcpath is None:
            for name in glob.glob(pat):
                filelist.append(name)
        else:
            for name in glob.glob(os.path.join(srcpath, pat)):
                filelist.append(name)

    if capsule is None:
        logging.info(_('make anonymous capsule'))
        filename = os.path.join(output, 'tmp_project.zip')
        make_capsule(sys.rootdir, None, filename)
        logging.info(_('extract anonymous capsule'))
        ZipFile(filename).extractall(path=output)
        os.remove(filename)
    else:
        logging.info(_('extract capsule %s') % capsule)
        ZipFile(capsule).extractall(path=output)
    prikey = os.path.join(output, 'private.key')
    if os.path.exists(prikey):
        logging.info(_('remove private key %s') % capsule)
        os.remove(prikey)
    kvfile = os.path.join(output, 'key.txt')
    if os.path.exists(kvfile):
        logging.info(_('use capsule key in %s') % kvfile)
        kv = unhexlify(_get_kv(kvfile).replace(' ', ''))
        logging.info(_('remove key file %s') % kvfile)
        os.remove(kvfile)

    if kv is None:
        kv = os.path.join(output, 'product.key')
    elif not os.path.exists(os.path.join(output, 'module.key')):
        raise RuntimeError(_('missing module key'))
    logging.info(_('encrypt files ...'))
    encrypt_files(filelist, kv, None if sameplace else output)

    logging.info(_('Encrypt files OK.'))

@checklicense
def do_capsule(argv):
    '''
Usage: pyarmor capsule [Options] [name]

  Generate a capsule which used to encrypt/decrypt python scripts later, it
  will generate different capsule when run this command again. Generately,
  one project, one capsule.

  Available options:

  -O, --output=DIR            [option] The path used to save capsule file.

  For example,

     - Generate default capsule "project.zip":

       pyarmor capsule

     - Generate a capsule "dist/foo.zip":

       pyarmor capsule --output=dist foo
    '''

    try:
        opts, args = getopt.getopt(argv, 'K:O:', ['key=', 'output='])
    except getopt.GetoptError:
        logging.exception('option error')
        usage('capsule')
        sys.exit(2)

    output = ''
    keystr = None
    for o, a in opts:
        if o in ('-K', '--key'):
            keystr = _get_kv(a)
        elif o in ('-O', '--output'):
            output = a

    if output == '':
        output = os.getcwd()

    if not os.path.exists(output):
        logging.info(_('make output path: %s') % output)
        os.makedirs(output)

    if len(args) == 0:
        filename = os.path.join(output, 'project.zip')
    else:
        filename = os.path.join(output, '%s.zip' % args[0])

    if keystr is not None:
        logging.info(_('key is %s') % keystr)
    logging.info(_('output filename is %s') % filename)
    make_capsule(sys.rootdir, keystr, filename)
    logging.info(_('Generate capsule OK.'))

@checklicense
def do_license(argv):
    '''Usage: pyarmor license [Options] [CODE]

  Generate a registration code for project capsule, save it to "license.lic"
  by default.

  Available options:

  -O, --output=DIR                [option] The path used to save license file.

  -B, --bind                      [option] Generate license file bind to fixed machine.

  -F, --bind-file=FILENAME        [option] Generate license file bind to fixed file, for example, ssh private key.

  -e, --expired-date=YYYY-MM-NN   [option] Generate license file expired in certain day.
                                           This option could be combined with "--bind"

  -C, --with-capsule=FILENAME     [required] Specify the filename of capsule
                                  generated before.

  For example,

     - Generate a license file "license.lic" for project capsule "project.zip":

       pyarmor license --wth-capsule=project.zip MYPROJECT-0001

     - Generate a license file "license.lic" expired in 05/30/2015:

       pyarmor license --wth-capsule=project.zip -e 2015-05-30 MYPROJECT-0001

     - Generate a license file "license.lic" bind to machine whose harddisk's
       serial number is "PBN2081SF3NJ5T":

       pyarmor license --wth-capsule=project.zip --bind PBN2081SF3NJ5T

     - Generate a license file "license.lic" bind to ssh private key file id_rsa:

       pyarmor license --wth-capsule=project.zip --bind-file src/id_rsa ~/.ssh/my_id_rsa

       File "src/id_rsa" is in the develop machine, pyarmor will read data from this file
       when generating license file.

       Argument "~/.ssh/id_rsa" means full path filename in target machine, pyarmor will
       find this file as key file when decrypting python scripts.

       You shuold copy "license.lic" to target machine, at the same time, copy "src/id_rsa"
       to target machine as "~/.ssh/my_id_rsa"

    '''
    try:
        opts, args = getopt.getopt(
            argv,
            'BC:e:F:O:',
            ['bind', 'expired-date=', 'bind-file=', 'with-capsule=', 'output=']
            )
    except getopt.GetoptError:
        logging.exception('option error')
        usage('license')
        sys.exit(2)

    filename = 'license.lic.txt'
    bindfile = None
    capsule = 'project.zip'
    bindflag = False
    bindfileflag = False
    expired = None
    for o, a in opts:
        if o in ('-C', '--with-capsule'):
            capsule = a
        elif o in ('-B', '--bind'):
            bindflag = True
        elif o in ('-F', '--bind-file'):
            bindfileflag = True
            bindfile = a
        elif o in ('-e', '--expired-date'):
            expired = a
        elif o in ('-O', '--output'):
            if os.path.exists(a) and os.path.isdir(a):
                filename = os.path.join(a, 'license.lic')
            else:
                filename = a

    if len(args) == 0:
        key = 'PROJECT-CODE'
    else:
        key = args[0]

    if expired is None:
        fmt = ''
    else:
        logging.info('license file expired at %s', expired)
        fmt = '*TIME:%.0f\n' % time.mktime(time.strptime(expired, '%Y-%m-%d'))

    if bindflag:
        logging.info('license file bind to harddisk %s', key)
        fmt = '%s*HARDDISK:%s' % (fmt, key)

    elif bindfileflag:
        if os.path.exists(bindfile):
            logging.info('you need copy %s to target machine as %s with license file.', bindfile, key)
            f = open(bindfile, 'rb')
            s = f.read()
            f.close()
            if sys.version_info[0] == 3:
                fmt = '%s*FIXKEY:%s;%s' % (fmt, key, s.decode())
            else:
                fmt = '%s*FIXKEY:%s;%s' % (fmt, key, s)
        else:
            logging.error('bind file %s not found', bindfile)
            return

    logging.info(_('output filename is %s'), filename)
    make_license(capsule, filename, fmt if fmt else key)
    logging.info(_('Generate license file "%s" OK.'), filename)

if __name__ == '__main__':
    sys.rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
        # filename=os.path.join(sys.rootdir, 'pyarmor.log'),
        # filemode='w',
    )

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    pytransform = _import_pytransform()
    command = sys.argv[1]
    if len(sys.argv) >= 3 and sys.argv[2] == 'help':
        usage(command)
        sys.exit(0)

    if 'help'.startswith(command) or sys.argv[1].startswith('-h'):
        try:
            usage(sys.argv[2])
        except IndexError:
            usage()

    elif 'version'.startswith(command) or sys.argv[1].startswith('-v'):
          show_version_info()

    elif 'capsule'.startswith(command):
          do_capsule(sys.argv[2:])

    elif 'encrypt'.startswith(command):
          do_encrypt(sys.argv[2:])

    elif 'license'.startswith(command):
          do_license(sys.argv[2:])

    elif 'hdinfo'.startswith(command):
          show_hd_info()

    else:
          usage(command)
