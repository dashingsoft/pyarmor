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
#      Version: 1.7.0 - 3.3.0                               #
#                                                           #
#############################################################
#
#  DEPRECATED from v3.4. It will be replaced by pyarmor2.py
#  from v4.
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
from distutils.filelist import FileList
from distutils.text_file import TextFile
import fnmatch
import getopt
import glob
import imp
import logging
import os
import shutil
import sys
import tempfile
import time
from zipfile import ZipFile

try:
    unhexlify = bytes.fromhex
except Exception:
    from binascii import a2b_hex as unhexlify

from config import (version, version_info, trial_info, help_footer,
                    ext_char, plat_name, dll_ext, dll_name, wrap_runner)

def _import_pytransform():
    try:
        m = __import__('pytransform')
        m.pyarmor_init()
        return m
    except Exception:
        pass
    logging.info('Searching pytransform library ...')
    path = sys.rootdir
    pname = plat_name.replace('i586', 'i386').replace('i686', 'i386')
    src = os.path.join(path, 'platforms', pname, dll_name + dll_ext)
    if os.path.exists(src):
        logging.info('Find pytransform library "%s"', src)
        logging.info('Copy %s to %s', src, path)
        shutil.copy(src, path)
        m = __import__('pytransform')
        m.pyarmor_init()
        logging.info('Load pytransform OK.')
        return m
    logging.error('No library %s found', src)

def _get_registration_code():
    try:
        code = pytransform.get_registration_code()
    except Exception:
        code = ''
    return code

def checklicense(func):
    # Fix python25 no "as" keyword in statement "except"
    exc_msg = lambda : str(sys.exc_info()[1])
    def wrap(*arg, **kwargs):
        code = _get_registration_code()
        if code == '':
            sys.stderr.write('PyArmor Trial Version %s\n' % version)
            sys.stderr.write(trial_info)
        else:
            sys.stderr.write('PyArmor Version %s\n' % version)
        try:
            func(*arg, **kwargs)
        except RuntimeError:
            logging.error(exc_msg())
        except getopt.GetoptError:
            logging.error(exc_msg())
        except pytransform.PytransformError:
            logging.error(exc_msg())
    wrap.__doc__ = func.__doc__
    return wrap

def show_version_info(verbose=True):
    code = _get_registration_code()
    trial = ' Trial' if  code == '' else ''
    print('PyArmor%s Version %s' % (trial, version))
    if verbose:
        print(version_info)
        if code == '':
            print(trial_info)
        print(help_footer)

def show_hd_info():
    pytransform.show_hd_info()

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
    print(help_footer)

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
    logging.info('Rootdir is %s', rootdir)
    filelist = 'public.key', 'pyimcore.py', 'pytransform.py'
    for x in filelist:
        src = os.path.join(rootdir, x)
        if not os.path.exists(src):
            raise RuntimeError('No %s found in the rootdir' % src)

    licfile = os.path.join(rootdir, 'license.lic')
    if not os.path.exists(licfile):
        raise RuntimeError('Missing license file %s' % licfile)

    logging.info('Generating project key ...')
    pri, pubx, capkey, lic = pytransform.generate_project_capsule(licfile)
    logging.info('Generating project OK.')
    logging.info('Writing capsule to %s ...', filename)
    myzip = ZipFile(filename, 'w')
    try:
        myzip.write(os.path.join(rootdir, 'public.key'), 'pyshield.key')
        myzip.writestr('pyshield.lic', capkey)
        myzip.write(os.path.join(rootdir, 'pyimcore.py'), 'pyimcore.py')
        myzip.write(os.path.join(rootdir, 'pytransform.py'), 'pytransform.py')
        myzip.writestr('private.key', pri)
        myzip.writestr('product.key', pubx)
        myzip.writestr('license.lic', lic)
    finally:
        myzip.close()
    logging.info('Write project capsule OK.')

def encrypt_files(files, prokey, mode=8, output=None):
    '''Encrypt all the files, all the encrypted scripts will be plused with
    a suffix 'e', for example, hello.py -> hello.pye

    files          list all the scripts
    prokey         project key file used to encrypt scripts
    output         output directory. If None, the output file will be saved
                   in the same path as the original script

    Return None if sucess, otherwise raise exception
    '''
    ext = '.py' if mode in (7, 8, 9, 10, 11, 12, 13, 14) else \
          '.pyc' if mode in (1, 3, 4, 5, 6) else '.py' + ext_char
    if output is None:
        fn = lambda a, b: b[1] + ext
    else:
        # fn = lambda a, b : os.path.join(a, os.path.basename(b) + ch)
        # fn = lambda a, b: os.path.join(a, b[1] + ext)
        if not os.path.exists(output):
            os.makedirs(output)
        def _get_path(a, b):
            p = os.path.join(a, b[1] + ext)
            d = os.path.dirname(p)
            if not os.path.exists(d):
                os.makedirs(d)
            return p
        fn = _get_path
    flist = []
    for x in files:
        flist.append((x[0], fn(output, x)))
        logging.info('Encrypt %s to %s', *flist[-1])

    if len(flist[:1]) == 0:
        logging.info('No any script specified')
    else:
        if not os.path.exists(prokey):
            raise RuntimeError('Missing project key "%s"' % prokey)
        pytransform.encrypt_project_files(prokey, tuple(flist), mode)
        logging.info('Encrypt all scripts OK.')

def make_license(capsule, filename, code):
    myzip = ZipFile(capsule, 'r')
    myzip.extract('private.key', tempfile.gettempdir())
    prikey = os.path.join(tempfile.tempdir, 'private.key')
    try:
        pytransform.generate_license_file(filename, prikey, code)
    finally:
        os.remove(prikey)

@checklicense
def do_capsule(argv):
    '''Usage: pyarmor capsule [OPTIONS] [NAME]

Generate a capsule which used to encrypt/decrypt python scripts later,
it will generate random capsule when run this command again. Note that
the trial version of PyArmor will always generate same project capsule

Generately, one project, one capsule.

Available options:

  -O, --output=DIR        [option] The path used to save license file.

  -f, --force             [option] Overwrite output file even it exists.

For example,

 - Generate default capsule "project.zip":

   pyarmor capsule project

 - Generate a capsule "mycapsules/foo.zip":

   pyarmor capsule --output mycapsules foo

    '''
    opts, args = getopt.getopt(argv, 'fO:', ['force', 'output='])

    output = os.getcwd()
    overwrite = False
    for o, a in opts:
        if o in ('-O', '--output'):
            output = a
        elif o in ('-f', '--force'):
            overwrite = True

    if len(args) == 0:
        filename = os.path.join(output, 'project.zip')
    else:
        filename = os.path.join(output, '%s.zip' % args[0])

    if os.path.exists(filename) and not overwrite:
        logging.info("Specify -f to overwrite it if you really want to do")
        raise RuntimeError("Capsule %s already exists" % filename)

    if not os.path.exists(output):
        logging.info("Make output path %s", output)
        os.makedirs(output)

    logging.info('Output filename is %s', filename)
    make_capsule(sys.rootdir, filename)
    logging.info('Generate capsule OK.')

def _parse_template_file(filename, path=None):
    template = TextFile(filename,
                        strip_comments=1,
                        skip_blanks=1,
                        join_lines=1,
                        lstrip_ws=1,
                        rstrip_ws=1,
                        collapse_join=1)
    lines = template.readlines()

    filelist = FileList()
    try:
        if path is not None and not path == os.getcwd():
            oldpath = os.getcwd()
            os.chdir(path)
        else:
            oldpath = None

        for line in lines:
            filelist.process_template_line(line)
    finally:
        if oldpath is not None:
            os.chdir(oldpath)
    return filelist.files

def _parse_file_args(args, srcpath=None):
    filelist = []

    if srcpath is None:
        path, n = '', 0
    else:
        path, n = srcpath, len(srcpath) + 1

    if len(args) == 1 and args[0][0] == '@' and args[0].endswith('MANIFEST.in'):
        for x in _parse_template_file(args[0][1:], path=srcpath):
            filelist.append((os.path.join(path, x), os.path.splitext(x)[0]))
        return filelist

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
        for name in glob.glob(os.path.join(path, pat)):
            p = os.path.splitext(name)
            filelist.append((name, p[0][n:]))

    return filelist

@checklicense
def do_encrypt(argv):
    '''Usage: pyarmor encrypt [OPTIONS] [File Patterns or @Filename]

Encrpty the files list in the command line, you can use a specified
pattern according to the rules used by the Unix shell. No tilde
expansion is done, but *, ?, and character ranges expressed with []
will be correctly matched.

You can either list file patterns in one file, one pattern one line,
then add a prefix '@' to the filename.

All the files will be encrypted and saved as orginal file name plus
'e'. By default, the encrypted scripts and all the auxiliary files
used to run the encrypted scripts are save in the path "dist".

Available options:

  -O, --output=DIR            Output path for runtime files and encrypted
                              files (if no --in-place)

                              The default value is "build".

  -C, --with-capsule=FILENAME Specify the filename of capsule generated
                              before.

                              The default value is "project.zip".

  -i, --in-place              [option], the encrypted scripts will be
                              saved in the original path (same as source).
                              Otherwise, save to --output specified.

  -s, --src=DIR               [option], the source path of python scripts.
                              The default value is current path.

  -p, --plat-name             [option] platform name to run encrypted
                              scripts. Only used when encrypted scripts
                              will be run in different platform.

  -m, --main=NAME             Generate wrapper file to run encrypted script

  -e, --mode=MODE             Encrypt mode, available value:
                                0     Encrypt both source and bytecode
                                1     Encrypt bytecode only.
                                2     Encrypt source code only.
                                3     Obfuscate bytecodes.
                                5     Obfuscate code object of module.
                                6     Combine mode 3 and 4
                                7     Obfuscate code object of module,
                                      output wrapper scripts
                                8     Obfuscate both code object and bytecode,
                                      output wrapper scripts
                              Mode 0, 1, 2 is deprecated from v3.2.0, this
                              option can be ignored in general.

  -d, --clean                 Clean output path at start.

  --manifest FILENAME         Write file list to FILENAME

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

      pyarmor encrypt --plat-name=linux_x86_64 a.py b.py

Use MANIFEST.in to list files

      pyarmor encrypt --with-capsule=project.zip @myproject/MANIFEST.in

It's Following the Distutils’ own manifest template

    '''
    opts, args = getopt.getopt(
        argv, 'C:de:im:O:p:s:',
        ['in-place', 'output=', 'src=', 'with-capsule=', 'plat-name=',
         'main=', 'clean', 'mode=', 'manifest=']
    )

    output = 'build'
    srcpath = None
    capsule = 'project.zip'
    inplace = False
    pname = None
    extfile = None
    mainname = []
    clean = False
    mode = 8
    manifest = None

    for o, a in opts:
        if o in ('-O', '--output'):
            output = a
        elif o in ('-s', '--src'):
            srcpath = a
        elif o in ('-i', '--in-place'):
            inplace = True
        elif o in ('-C', '--with-capsule'):
            capsule = a
        elif o in ('-p', '--plat-name'):
            pname = a
        elif o in ('-d', '--clean'):
            clean = True
        elif o in ('-e', '--mode'):
            if a not in ('0', '1', '2', '3', '5', '6',
                         '7', '8', '9', '10', '11', '12',
                         '13', '14'):
                raise RuntimeError('Invalid mode "%s"' % a)
            mode = int(a)
        elif o in ('-m', '--main'):
            mainname.append(a)
        elif o in ('--manifest', ):
            manifest = a

    if srcpath is not None and not os.path.exists(srcpath):
        raise RuntimeError('No found specified source path "%s"' % srcpath)

    if capsule is None or not os.path.exists(capsule):
        raise RuntimeError('No found capsule file %s' % capsule)

    # Maybe user specify an empty path
    if output == '':
        output = 'build'

    logging.info('Output path is %s' % output)
    if os.path.exists(output) and clean:
        logging.info('Removing output path %s', output)
        shutil.rmtree(output)
        logging.info('Remove output path OK.')
    if not os.path.exists(output):
        logging.info('Make output path %s', output)
        os.makedirs(output)

    if pname is None:
        extfile = os.path.join(sys.rootdir, dll_name + dll_ext)
    else:
        logging.info("Cross publish, target platform is %s", pname)
        name = dll_name + ('.so' if pname.startswith('linux') else '.dll')
        extfile = os.path.join(sys.rootdir, 'platforms', pname, name)
        if not os.path.exists(extfile):
            # Need to download platforms/... from pyarmor homepage
            logging.info('You need download prebuilt library files '
                         'from pyarmor homepage first.')
            raise RuntimeError('Missing cross platform library %s' % extfile)
    logging.info('Copy %s to %s' % (extfile, output))
    shutil.copy(extfile, output)

    logging.info('Extract capsule %s ...', capsule)
    ZipFile(capsule).extractall(path=output)
    logging.info('Extract capsule to %s OK.', output)

    if mode >= 3:
        logging.info('Encrypt mode: %s', mode)
        with open(os.path.join(output, 'pyimcore.py'), 'w') as f:
            lines = 'from pytransform import old_init_runtime', \
                    'old_init_runtime(0, 0, 0, 0)', ''
            f.write('\n'.join(lines))
    elif mode:
        logging.info('Encrypt mode: %s', mode)
        with open(os.path.join(output, 'pyimcore.py'), 'r') as f:
            lines = f.read()
        with open(os.path.join(output, 'pyimcore.py'), 'w') as f:
            i = lines.rfind('\n\n')
            if i == -1:
                raise RuntimeError('Invalid pyimcore.py')
            f.write(lines[:i])
            if mode == 1:
                f.write('\n\nold_init_runtime()\n')
            elif mode == 2:
                f.write('\n\nsys.meta_path.append(PyshieldImporter())\n'
                        'old_init_runtime(0, 0, 0, 0)\n')

    prikey = os.path.join(output, 'private.key')
    if os.path.exists(prikey):
        logging.info('Remove private key %s in the output', prikey)
        os.remove(prikey)

    if mode not in (7, 8, 9, 10, 11, 12, 13, 14):
        for name in mainname:
            n = name.find(':')
            if n == -1:
                script = os.path.join(output, name + '.py')
            else:
                script = os.path.join(output, name[n+1:])
                name = name[:n]
            logging.info('Writing script wrapper %s ...', script)
            ch = 'c' if mode == 1 or mode == 3 else ext_char
            with open(script, 'w') as f:
                f.write(wrap_runner % (name + '.py' + ch))
            logging.info('Write script wrapper OK.')

    filelist = _parse_file_args(args, srcpath=srcpath)
    if manifest is not None:
        logging.info('Write filelist to %s', manifest)
        with open(manifest, 'w') as fp:
            fp.write('\n'.join([x[0] for x in filelist]))

    if len(filelist[:1]) == 0:
        logging.info('Generate extra files OK.')
    else:
        prokey = os.path.join(output, 'product.key')
        if not os.path.exists(prokey):
            raise RuntimeError('Missing project key %s' % prokey)
        logging.info('Encrypt files ...')
        encrypt_files(filelist, prokey, mode, None if inplace else output)
        if mode in (7, 8, 9, 10, 11, 12, 13, 14):
            for name in mainname:
                script = os.path.join(
                    output, name + ('' if name.endswith('.py') else '.py'))
                with open(script, 'r') as f:
                    source = f.read()
                logging.info('Patch entry script %s.', script)
                with open(script, 'w') as f:
                    f.write('import pyimcore\n')
                    f.write(source)
        logging.info('Encrypt files OK.')

@checklicense
def do_license(argv):
    '''
Usage: pyarmor license [Options] [CODE]

Generate a registration code for project capsule, save it to "license.txt"
by default.

Available options:

  -O, --output=DIR                Path used to save license file.

  -B, --bind-disk="XX"            [optional] Generate license file bind to
                                  harddisk of one machine.

      --bind-mac="XX:YY"          [optional] Generate license file bind to
                                  mac address of one machine.

      --bind-ip="a.b.c.d"         [optional] Generate license file bind to
                                  ipv4 of one machine.

      --bind-domain="domain"      [optional] Generate license file bind to
                                  domain of one machine.

  -F, --bind-file=FILENAME        [option] Generate license file bind to
                                  fixed file, for example, ssh private key.

  -e, --expired-date=YYYY-MM-NN   [option] Generate expired license file.
                                  It could be combined with "--bind"

  -C, --with-capsule=FILENAME     [required] Specify the filename of capsule
                                  generated before.

For example,

  - Generate a license file "license.lic" for project capsule "project.zip":

    pyarmor license --wth-capsule=project.zip MYPROJECT-0001

  - Generate a license file "license.lic" expired in 05/30/2015:

    pyarmor license --wth-capsule=project.zip -e 2015-05-30 MYPROJECT-0001

  - Generate a license file "license.lic" bind to machine whose harddisk's
    serial number is "PBN2081SF3NJ5T":

    pyarmor license --wth-capsule=project.zip --bind-disk PBN2081SF3NJ5T

  - Generate a license file "license.lic" bind to ssh key file id_rsa:

    pyarmor license --wth-capsule=project.zip \
            --bind-file src/id_rsa ~/.ssh/my_id_rsa

    File "src/id_rsa" is in the develop machine, pyarmor will read data
    from this file when generating license file.

    Argument "~/.ssh/id_rsa" means full path filename in target machine,
    pyarmor will find this file as key file when decrypting python scripts.

    You shuold copy "license.lic" to target machine, at the same time,
    copy "src/id_rsa" to target machine as "~/.ssh/my_id_rsa"

    '''
    opts, args = getopt.getopt(
        argv, 'B:C:e:F:O:',
        ['bind-disk=', 'bind-mac=', 'bind-ip=', 'bind-domain=',
         'expired-date=', 'bind-file=', 'with-capsule=', 'output=']
    )

    filename = 'license.lic.txt'
    bindfile = None
    capsule = 'project.zip'
    bindfileflag = False
    binddisk = None
    bindip = None
    bindmac = None
    binddomain = None
    expired = None
    for o, a in opts:
        if o in ('-C', '--with-capsule'):
            capsule = a
        elif o in ('-B', '--bind-disk'):
            binddisk = a
        elif o in ('-B', '--bind-mac'):
            bindmac = a
        elif o in ('-B', '--bind-ip'):
            bindip = a
        elif o in ('-B', '--bind-domain'):
            binddomain = a
        elif o in ('-F', '--bind-file'):
            bindfileflag = True
            bindfile = a
        elif o in ('-e', '--expired-date'):
            expired = a
        elif o in ('-O', '--output'):
            if os.path.exists(a) and os.path.isdir(a):
                filename = os.path.join(a, 'license.lic.txt')
            else:
                filename = a

    if len(args) == 0:
        key = 'POWERD-BY-PYARMOR'
    else:
        key = args[0]

    if expired is None:
        fmt = ''
    else:
        logging.info('License file expired at %s', expired)
        fmt = '*TIME:%.0f\n' % time.mktime(time.strptime(expired, '%Y-%m-%d'))

    if binddisk:
        logging.info('License file bind to harddisk "%s"', binddisk)
        fmt = '%s*HARDDISK:%s' % (fmt, binddisk)

    if bindmac:
        logging.info('License file bind to mac addr "%s"', key)
        fmt = '%s*IFMAC:%s' % (fmt, bindmac)

    if bindip:
        logging.info('License file bind to ip "%s"', key)
        fmt = '%s*IFIPV4:%s' % (fmt, bindip)

    if binddomain:
        logging.info('License file bind to domain "%s"', key)
        fmt = '%s*DOMAIN:%s' % (fmt, binddomain)

    if bindfileflag:
        if os.path.exists(bindfile):
            logging.info('You need copy %s to target machine as %s '
                         'with license file.', bindfile, key)
            f = open(bindfile, 'rb')
            s = f.read()
            f.close()
            if sys.version_info[0] == 3:
                fmt = '%s*FIXKEY:%s;%s' % (fmt, key, s.decode())
            else:
                fmt = '%s*FIXKEY:%s;%s' % (fmt, key, s)
        else:
            raise RuntimeError('Bind file %s not found' % bindfile)

    logging.info('Output filename is %s', filename)
    make_license(capsule, filename, fmt if fmt else key)
    logging.info('Generate license file "%s" OK.', filename)

if __name__ == '__main__':
    sys.rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
        # filename=os.path.join(sys.rootdir, 'pyarmor.log'),
        # filemode='w',
    )

    # if (len(sys.argv) == 1 or
    #     sys.argv[1] not in ('help', 'encrypt', 'capsule', 'license')):
    #     from pyarmor import main as main2
    #     main2(sys.argv[1:])
    #     sys.exit(0)

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    command = sys.argv[1]
    if len(sys.argv) >= 3 and sys.argv[2] == 'help':
        usage(command)
        sys.exit(0)

    pytransform = _import_pytransform()
    if pytransform is None:
        sys.exit(1)

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
