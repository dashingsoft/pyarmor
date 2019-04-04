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
import re
import shutil
import sys
import tempfile
from time import gmtime, strftime
from zipfile import ZipFile

import pytransform
from config import plat_name, dll_ext, dll_name, entry_lines, \
                   protect_code_template

PYARMOR_PATH = os.getenv('PYARMOR_PATH', os.path.dirname(__file__))

def pytransform_bootstrap(path=None):
    path = PYARMOR_PATH if path is None else path
    libname = dll_name + dll_ext
    if not os.path.exists(os.path.join(path, libname)):
        libpath = os.path.join(path, 'platforms')
        sysname = pytransform.format_platname()
        if not os.path.exists(os.path.join(libpath, sysname, libname)):
            logging.info('Searching %s for %s ...', libname, plat_name)
            src = os.path.join(libpath, plat_name, libname)
            if not os.path.exists(src):
                raise RuntimeError('No available library for this platform')
            logging.info('Found: "%s"', src)
            logging.info('Copy to %s', path)
            shutil.copy(src, path)
            logging.info('Bootstrap OK.\n')
    pytransform.pyarmor_init()

def make_capsule(filename):
    path = PYARMOR_PATH
    logging.info('PyArmor install path: %s', path)

    for a in 'public.key', 'license.lic':
        x = os.path.join(path, a)
        if not os.path.exists(x):
            raise RuntimeError('No %s found in pyarmor' % x)
    licfile = os.path.join(path, 'license.lic')

    logging.info('Generating project key ...')
    pri, pubx, capkey, newkey, lic = pytransform.generate_capsule(licfile)
    logging.info('Generate project key OK.')

    logging.info('Writing capsule to %s ...', filename)
    myzip = ZipFile(filename, 'w')
    try:
        myzip.write(os.path.join(path, 'public.key'), 'pyshield.key')
        myzip.writestr('pyshield.lic', capkey)
        # myzip.write(os.path.join(path, 'pytransform.py'), 'pytransform.py')
        myzip.writestr('private.key', pri)
        myzip.writestr('product.key', pubx)
        myzip.writestr('pytransform.key', newkey)
        myzip.writestr('license.lic', lic)
    finally:
        myzip.close()
    logging.info('Write capsule OK.')

def check_capsule(capsule):
    if os.path.getmtime(capsule) < os.path.getmtime(
            os.path.join(PYARMOR_PATH, 'license.lic')):
        logging.info('Capsule %s has been out of date', capsule)

        suffix = strftime('%Y%m%d%H%M%S', gmtime())
        logging.info('Rename it as %s.%s', capsule, suffix)
        os.rename(capsule, capsule + '.' + suffix)
        return False
    return True

def _make_entry(filename, rpath=None):
    entry_code = entry_lines[0] % (
        '.' if os.path.basename(filename) == '__init__.py' else '')

    with open(filename, 'r') as f:
        lines = f.readlines()
    # Fix empty file issue
    n = 0
    for n in range(len(lines)):
        if lines[n].strip() == '' or lines[n].find('__future__') > 0:
            continue
        if not lines[n][0] == '#':
            break
    for line in lines[n:]:
        if line.strip() == entry_code.strip():
            return

    with open(filename, 'w') as f:
        f.write(''.join(lines[:n]))
        f.write(entry_code)
        f.write(entry_lines[1] % ('' if rpath is None else repr(rpath)))
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
    if 'pytransform.key' in myzip.namelist():
        myzip.extract('pytransform.key', output)
    else:
        myzip.extract('pyshield.key', output)
        myzip.extract('pyshield.lic', output)
        myzip.extract('product.key', output)

    if licfile is None:
        myzip.extract('license.lic', output)
    else:
        shutil.copy2(licfile, os.path.join(output, 'license.lic'))

    if platform is None:
        libname = dll_name + dll_ext
        libfile = os.path.join(PYARMOR_PATH, libname)
        if not os.path.exists(libfile):
            sysname = pytransform.format_platname()
            libpath = os.path.join(PYARMOR_PATH, 'platforms')
            libfile = os.path.join(libpath, sysname, libname)
        shutil.copy2(libfile, output)
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
        code = pytransform.get_license_info()['CODE']
    except Exception:
        code = None
    return code

def make_protect_pytransform(template=None, filename=None, rpath=None):
    if filename is None:
        filename = pytransform._pytransform._name
    if template is None:
        template = os.path.join(PYARMOR_PATH, protect_code_template)
    size = os.path.getsize(filename) & 0xFFFFFFF0
    n = size >> 2
    with open(filename, 'rb') as f:
        buf = f.read(size)
    fmt = 'I' * n
    cosum = sum(pytransform.struct.unpack(fmt, buf)) & 0xFFFFFFFF

    with open(template) as f:
        buf = f.read()

    code = '__code__' if sys.version_info[0] == 3 else 'func_code'
    closure = '__closure__' if sys.version_info[0] == 3 else 'func_closure'
    rpath = 'pytransform.os.path.dirname(__file__)' if rpath is None \
            else repr(rpath)
    return buf.format(code=code, closure=closure, size=size, checksum=cosum,
                      rpath=rpath, filename=repr(os.path.basename(filename)))

def _frozen_modname(filename, filename2):
    names = os.path.normpath(filename).split(os.sep)
    names2 = os.path.normpath(filename2).split(os.sep)
    k = -1
    while True:
        try:
            if names[k] != names2[k]:
                break
        except IndexError:
            break
        k -= 1
    if names[-1] == '__init__.py':
        dotnames = names[k if k == -2 else k + 1:-1]
    else:
        names[-1] = names[-1][:-3]
        dotnames = names[k+1:]
    return "<frozen %s>" % '.'.join(dotnames)

def _guess_encoding(filename):
    with open(filename, 'rb') as f:
        line = f.read(80)
        if line and line[0] == 35:
            n = line.find(b'\n')
            if n == -1:
                n = 80
            elif n < 60 and line[n+1] == 35:
                k = line[n+1:].find(b'\n')
                n += k + 1
            m = re.search(r'coding[=:]\s*([-\w.]+)', line[:n].decode())
            return m and m.group(1)

def encrypt_script(pubkey, filename, destname, wrap_mode=1, obf_code=1,
                   obf_mod=1, protection=0, rpath=None):
    if sys.version_info[0] == 2:
        with open(filename, 'r') as f:
            lines = f.readlines()
    else:
        encoding = _guess_encoding(filename)
        with open(filename, 'r', encoding=encoding) as f:
            lines = f.readlines()

    if protection:
        n = 0
        for line in lines:
            if line.startswith('# No PyArmor Protection Code'):
                break
            elif (line.startswith('# {PyArmor Protection Code}')
                  or line.startswith("if __name__ == '__main__':")
                  or line.startswith('if __name__ == "__main__":')):
                logging.info('Patch this entry script with protection code')
                template = None if protection == 1 else protection
                lines[n:n] = make_protect_pytransform(template, rpath=rpath)
                break
            n += 1

    modname = _frozen_modname(filename, destname)
    co = compile(''.join(lines), modname, 'exec')

    flags = obf_code | obf_mod << 8 | wrap_mode << 16
    s = pytransform.encrypt_code_object(pubkey, co, flags)

    with open(destname, 'w') as f:
        f.write(s.decode())

def get_product_key(capsule):
    output = tempfile.gettempdir()
    keyfile = os.path.join(output, 'product.key')
    ZipFile(capsule).extract('product.key', path=output)
    try:
        with open(keyfile, 'rb') as f:
            return f.read()
    finally:
        os.remove(keyfile)

def upgrade_capsule(capsule):
    myzip = ZipFile(capsule, 'r')
    try:
        if 'pytransform.key' in myzip.namelist():
            logging.info('The capsule is latest, nothing to do')
            return
        logging.info('Read product key from old capsule')
        pubkey = myzip.read('product.key')
    finally:
        myzip.close()

    myzip = ZipFile(capsule, 'a')
    try:
        logging.info('Generate new key')
        licfile = os.path.join(PYARMOR_PATH, 'license.lic')
        _, newkey = pytransform._generate_pytransform_key(licfile, pubkey)
        logging.info('Write new key pytransform.key to the capsule')
        myzip.writestr('pytransform.key', newkey)
    finally:
        myzip.close()

    logging.info('Upgrade capsule OK.')

if __name__ == '__main__':
    make_entry(sys.argv[1])
