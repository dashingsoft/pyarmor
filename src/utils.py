#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2018 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 3.4.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: utils.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2018/01/17
#
#  @Description:
#
#  All the routines of pytransform.
#
import logging
import os
import shutil
import sys
import tempfile
import time
from zipfile import ZipFile

from config import plat_name, dll_ext, dll_name, entry_code

PYARMOR_PATH = os.getenv('PYARMOR_PATH', os.path.dirname(__file__))
#
# Bootstrap
#
def search_pytransform(path):
    logging.info('Searching %s%s for %s ...', dll_name, dll_ext, plat_name)
    name = plat_name.replace('i586', 'i386').replace('i686', 'i386')
    src = os.path.join(path, 'platforms', name, dll_name + dll_ext)
    if os.path.exists(src):
        logging.info('Find _pytransform library "%s"', src)
        logging.info('Copy %s to %s', src, path)
        shutil.copy(src, path)
    else:
        raise RuntimeError('No library %s found', src)

import pytransform
try:
    pytransform.pyarmor_init()
except Exception:
    search_pytransform(PYARMOR_PATH)
    pytransform.pyarmor_init()

def make_capsule(filename):
    path = PYARMOR_PATH
    logging.info('Pyarmor install path: %s', path)

    for a in 'public.key', 'license.lic':
        x = os.path.join(path, a)
        if not os.path.exists(x):
            raise RuntimeError('No %s found in pyarmor' % x)
    licfile = os.path.join(path, 'license.lic')

    logging.info('Generating project key ...')
    pri, pubx, capkey, lic = pytransform.generate_project_capsule(licfile)
    logging.info('Generate project key OK.')

    logging.info('Writing capsule to %s ...', filename)
    myzip = ZipFile(filename, 'w')
    try:
        myzip.write(os.path.join(path, 'public.key'), 'pyshield.key')
        myzip.writestr('pyshield.lic', capkey)
        # myzip.write(os.path.join(path, 'pytransform.py'), 'pytransform.py')
        myzip.writestr('private.key', pri)
        myzip.writestr('product.key', pubx)
        myzip.writestr('license.lic', lic)
    finally:
        myzip.close()
    logging.info('Write capsule OK.')

def _make_entry(filename, rpath=None):
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Fix empty file issue
    n = 0
    for n in range(len(lines)):
        if not lines[n][0] == '#':
            break
    for line in lines[n:]:
        if line.strip() == 'from pytransform import pyarmor_runtime':
            return
    with open(filename, 'w') as f:
        f.write(''.join(lines[:n]))
        f.write(entry_code % ('' if rpath is None else repr(rpath)))
        f.write(''.join(lines[n:]))

def make_entry(entris, path, output, rpath=None, ispackage=False):
    for entry in entris.split(','):
        entry = entry.strip()
        src = build_path(entry, path)
        if (ispackage
            and (not os.path.isabs(entry)) and (not entry.startswith('..'))):
            filename = os.path.join(output, os.path.basename(path), entry)
        else:
            filename = os.path.join(output, os.path.basename(src))
        if not os.path.exists(filename):
            shutil.copy(src, filename)
        logging.info('Insert bootstrap code to entry script %s', filename)
        _make_entry(filename, rpath)

def obfuscate_scripts(filepairs, mode, capsule, output):
    if not os.path.exists(output):
        os.makedirs(output)

    prokey = os.path.join(output, 'product.key')
    if not os.path.exists(prokey):
        ZipFile(capsule).extract('product.key', path=output)

    dirs = []
    for x in filepairs:
        dirs.append(os.path.dirname(x[1]))

    for d in set(dirs):
        if not os.path.exists(d):
            os.makedirs(d)

    if filepairs:
        pytransform.encrypt_project_files(prokey, tuple(filepairs), mode)

    os.remove(prokey)

    return filepairs

def make_runtime(capsule, output, licfile=None, platform=None):
    myzip = ZipFile(capsule, 'r')
    myzip.extract('pyshield.key', output)
    myzip.extract('pyshield.lic', output)
    myzip.extract('product.key', output)

    if licfile is None:
        myzip.extract('license.lic', output)
    else:
        shutil.copy2(licfile, os.path.join(output, 'license.lic'))

    if platform is None:
        shutil.copy2(os.path.join(PYARMOR_PATH, dll_name + dll_ext), output)
    else:
        path = os.path.join(PYARMOR_PATH, 'platforms', platform)
        for x in os.listdir(path):
            shutil.copy2(os.path.join(path, x), output)

    shutil.copy2(os.path.join(PYARMOR_PATH, 'pytransform.py'), output)

def make_project_license(capsule, code, output):
    myzip = ZipFile(capsule, 'r')
    myzip.extract('private.key', tempfile.gettempdir())
    prikey = os.path.join(tempfile.tempdir, 'private.key')
    try:
        pytransform.generate_license_file(output, prikey, code)
    finally:
        os.remove(prikey)

def show_hd_info():
    pytransform.show_hd_info()

def build_path(path, relpath):
    return path if os.path.isabs(path) else os.path.join(relpath, path)

def make_command(platform, python, pyarmor, output):
    script = os.path.abspath(pyarmor)
    if platform.startswith('win'):
        filename = os.path.join(output, 'pyarmor.bat')
        with open(filename, 'w') as f:
            f.write('%s %s %%*' % (python, script))
    else:
        filename = os.path.join(output, 'pyarmor')
        with open(filename, 'w') as f:
            f.write('%s %s "$@"' % (python, script))
    os.chmod(filename, 0o755)
    return filename

def get_registration_code():
    try:
        code = pytransform.get_registration_code()
    except Exception:
        code = ''
    return code

if __name__ == '__main__':
    make_entry(sys.argv[1])
