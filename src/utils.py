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
import hashlib
import logging
import os
import re
import shutil
import sys
import tempfile
from codecs import BOM_UTF8
from json import dumps as json_dumps, loads as json_loads
from time import gmtime, strftime
from zipfile import ZipFile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import pytransform
from config import dll_ext, dll_name, entry_lines, protect_code_template, \
                   platform_urls, platform_config, key_url, version

PYARMOR_PATH = os.getenv('PYARMOR_PATH', os.path.dirname(__file__))


def pytransform_bootstrap(path=None, capsule=None):
    path = PYARMOR_PATH if path is None else path
    licfile = os.path.join(path, 'license.lic')
    if not os.path.exists(licfile):
        if not os.access(path, os.W_OK):
            logging.error('Bootstrap need write file "license.lic" to %s, '
                          'please run pyarmor with sudo for first time',
                          path)
            raise RuntimeError('No write permission for target path')
        shutil.copy(os.path.join(PYARMOR_PATH, 'license.tri'), licfile)

    libname = dll_name + dll_ext
    platname = None
    if not os.path.exists(os.path.join(path, libname)):
        libpath = os.path.join(path, 'platforms')
        platname = os.getenv('PYARMOR_PLATFORM')
        platid = pytransform.format_platname(platname)
        if not os.path.exists(os.path.join(libpath, platid, libname)):
            download_pytransform(platid)
            logging.info('Bootstrap OK.\n')
    pytransform.pyarmor_init(platname=platname)

    if capsule is not None and 'register' not in sys.argv[1:2]:
        if not os.path.exists(capsule):
            logging.info('Generating public capsule ...')
            make_capsule(capsule)


def _get_remote_file(urls, path, timeout=3.0):
    while urls:
        prefix = urls[0]
        url = '/'.join([prefix, 'platforms', path])
        logging.info('Getting remote file: %s', url)
        try:
            return urlopen(url, timeout=timeout)
        except Exception as e:
            urls.pop(0)
            logging.info('Could not get file from %s: %s', prefix, e)


def _get_platform_list(urls, platid=None):
    f = _get_remote_file(urls, platform_config)
    if f is None:
        raise RuntimeError('No available site to download library file')

    if platid is not None:
        platid = platid.replace('\\', '/')
        if platid.find('/') == -1:
            name, mach = platid, pytransform.platform.machine().lower()
        else:
            name, mach = platid.split('/', 1)
        logging.info('Search library for %s and arch %s', name, mach)

    logging.info('Loading platforms information')
    cfg = json_loads(f.read().decode())

    compatible = cfg.get('compatible', '').split()
    if compatible and compatible[-1] > version:
        raise RuntimeError('The core library v%s is not compatible with '
                           'PyArmor v%s' % (compatible[-1], version))
    return cfg.get('platforms', []) if platid is None \
        else [x for x in cfg.get('platforms', [])
              if platid == x['path'] or (
                      name == x['platname'] and mach in x['machines'])]


def get_platform_list():
    return _get_platform_list(platform_urls[:])


def download_pytransform(platid, saveas=None, url=None):
    urls = platform_urls[:] if url is None else ([url] + platform_urls)
    plist = _get_platform_list(urls, platid)
    if not plist:
        logging.error('Unsupport platform %s', platid)
        raise RuntimeError('No available library for this platform')

    p = plist[0]
    libname = p['filename']
    path = '/'.join([p['path'], libname])
    logging.info('Found available library %s', path)

    if not os.access(PYARMOR_PATH, os.W_OK):
        logging.error('Cound not download library file to %s', PYARMOR_PATH)
        raise RuntimeError('No write permission for target path')

    logging.info('Downloading library file ...')
    res = _get_remote_file(urls, path, timeout=60)

    dest = os.path.join(PYARMOR_PATH, 'platforms',
                        platid if saveas is None else saveas)
    if not os.path.exists(dest):
        logging.info('Create target path: %s', dest)
        os.makedirs(dest)

    data = res.read()
    if hashlib.sha256(data).hexdigest() != p['sha256']:
        raise RuntimeError('Verify downloaded library failed')

    target = os.path.join(dest, libname)
    logging.info('Writing target file: %s', target)
    with open(target, 'wb') as f:
        f.write(data)
    logging.info('Download pytransform library file successfully.')


def make_capsule(filename):
    if get_registration_code():
        logging.error('The registered version would use private capsule.'
                      '\n\t Please run `pyarmor register KEYFILE` '
                      'to restore your private capsule.')
        raise RuntimeError('Could not generate private capsule.')
    public_capsule = os.path.join(PYARMOR_PATH, 'public_capsule.zip')
    logging.info('Copy %s to %s', public_capsule, filename)
    shutil.copy(public_capsule, filename)
    logging.info('Generate public capsule %s OK.', filename)


def check_capsule(capsule):
    if os.path.getmtime(capsule) < os.path.getmtime(
            os.path.join(PYARMOR_PATH, 'license.lic')):
        logging.info('Capsule %s has been out of date', capsule)

        suffix = strftime('%Y%m%d%H%M%S', gmtime())
        logging.info('Rename it as %s.%s', capsule, suffix)
        os.rename(capsule, capsule + '.' + suffix)
        return False
    return True


def _make_entry(filename, rpath=None, runtime=True, shell=None):
    ispkg = os.path.basename(filename) == '__init__.py'
    entry_code = entry_lines[0] % ('.' if runtime and ispkg else '')

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
        if shell:
            f.write(shell)
        f.write(entry_code)
        f.write(entry_lines[1] % ('' if rpath is None else repr(rpath)))
        f.write(''.join(lines[n:]))


def _get_script_shell(script):
    with open(script, 'r') as f:
        try:
            line = f.read(60)
            if len(line) > 2 and line[:2] == '#!':
                i = line.find('\n') + 1
                if i > 0:
                    return line[:i]
        except Exception:
            pass


def make_entry(entris, path, output, rpath=None, runtime=True, ispackage=False):
    if ispackage:
        output = os.path.join(output, os.path.basename(path))
    for entry in entris.split(','):
        entry = entry.strip()
        filename = build_path(entry, output)
        src = build_path(entry, path)
        if os.path.exists(filename):
            shell = _get_script_shell(src)
        else:
            shell = None
            logging.info('Copy entry script %s to %s', src, filename)
            shutil.copy(src, filename)
        if shell:
            logging.info('Insert shell line: %s', shell)
        logging.info('Insert bootstrap code to entry script %s', filename)
        _make_entry(filename, rpath, runtime=runtime, shell=shell)


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


def _get_platform_library(platname):
    path = os.path.join(PYARMOR_PATH, 'platforms', platname)
    for x in os.listdir(path):
        if x.startswith('_pytransform.'):
            return os.path.join(path, x)
    raise RuntimeError('No dynamic library found for %s' % platname)


def make_runtime(capsule, output, licfile=None, platform=None):
    logging.info('Generating runtime files to %s', output)

    myzip = ZipFile(capsule, 'r')
    if 'pytransform.key' in myzip.namelist():
        logging.info('Extract pytransform.key')
        myzip.extract('pytransform.key', output)
    else:
        logging.info('Extract pyshield.key, pyshield.lic, product.key')
        myzip.extract('pyshield.key', output)
        myzip.extract('pyshield.lic', output)
        myzip.extract('product.key', output)

    if licfile is None:
        logging.info('Extract license.lic')
        myzip.extract('license.lic', output)
    else:
        logging.info('Copying %s', licfile)
        shutil.copy2(licfile, os.path.join(output, 'license.lic'))

    if platform is None:
        libfile = pytransform._pytransform._name
        if not os.path.exists(libfile):
            libname = dll_name + dll_ext
            libfile = os.path.join(PYARMOR_PATH, libname)
            if not os.path.exists(libfile):
                pname = pytransform.format_platname()
                libpath = os.path.join(PYARMOR_PATH, 'platforms')
                libfile = os.path.join(libpath, pname, libname)
        logging.info('Copying %s', libfile)
        shutil.copy2(libfile, output)
    else:
        filename = _get_platform_library(platform)
        logging.info('Copying %s', filename)
        shutil.copy2(filename, output)

    filename = os.path.join(PYARMOR_PATH, 'pytransform.py')
    shutil.copy2(filename, output)

    logging.info('Generate runtime files OK')


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


def make_project_command(platform, python, pyarmor, output):
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


def patch_plugins(plugins):
    result = []
    path = os.getenv('PYARMOR_PLUGIN', '')
    for name in plugins:
        filename = name if name.endswith('.py') else (name + '.py')
        filename = build_path(filename, path)
        if not os.path.exists(filename):
            raise RuntimeError('No plugin script %s found' % filename)
        with open(filename, 'r') as f:
            result.append(f.read())
    return result


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
        if line and line[:3] == BOM_UTF8:
            return 'utf-8'
        if line and line[0] == 35:
            n = line.find(b'\n')
            if n == -1:
                n = 80
            elif len(line) > (n+1) and line[n+1] == 35:
                k = line[n+1:].find(b'\n')
                n += k + 1
            m = re.search(r'coding[=:]\s*([-\w.]+)', line[:n].decode())
            return m and m.group(1)


def encrypt_script(pubkey, filename, destname, wrap_mode=1, obf_code=1,
                   obf_mod=1, adv_mode=0, rest_mode=1, protection=0,
                   plugins=None, rpath=None):
    if sys.version_info[0] == 2:
        with open(filename, 'r') as f:
            lines = f.readlines()
    else:
        encoding = _guess_encoding(filename)
        with open(filename, 'r', encoding=encoding) as f:
            lines = f.readlines()
        if encoding == 'utf-8' and lines:
            i = lines[0].find('#')
            if i > 0:
                lines[0] = lines[0][i:]

    if plugins:
        n = 0
        k = -1
        plist = []
        marker = '# PyArmor Plugin:'
        for line in lines:
            if line.startswith('# {PyArmor Plugins}'):
                k = n + 1
            elif (line.startswith("if __name__ == '__main__':")
                  or line.startswith('if __name__ == "__main__":')):
                if k == -1:
                    k = n
            else:
                i = line.find(marker)
                if i > -1:
                    plist.append((n+1, i))
            n += 1
        if k > -1:
            logging.info('Patch this entry script with plugins')
            lines[k:k] = patch_plugins(plugins)
        for n, i in plist:
            lines[n] = lines[n][:i] + lines[n][i+len(marker):].lstrip()

    if protection:
        n = 0
        for line in lines:
            if line.startswith('# No PyArmor Protection Code') or \
               line.startswith('# {No PyArmor Protection Code}'):
                break
            elif (line.startswith('# {PyArmor Protection Code}')
                  or line.startswith("if __name__ == '__main__':")
                  or line.startswith('if __name__ == "__main__":')):
                logging.info('Patch this entry script with protection code')
                template, target = None, None
                if not isinstance(protection, int):
                    if protection.find(',') == -1:
                        target = _get_platform_library(protection)
                    else:
                        template, platname = protection.split(',')
                        target = _get_platform_library(platname)
                if template:
                    logging.info('Use template: %s', template)
                if target:
                    logging.info('Target dynamic library: %s', target)
                lines[n:n] = [make_protect_pytransform(template=template,
                                                       filename=target,
                                                       rpath=rpath)]
                break
            n += 1

    if sys.flags.debug and (protection or plugins):
        with open(filename + '.pyarmor-patched', 'w') as f:
            f.write(''.join(lines))

    modname = _frozen_modname(filename, destname)
    co = compile(''.join(lines), modname, 'exec')

    flags = obf_code | obf_mod << 8 | wrap_mode << 16 | adv_mode << 24 \
        | (11 if rest_mode == 4 else 15 if rest_mode == 3 else
           7 if rest_mode == 2 else rest_mode) << 28
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


def load_config(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            cfg = json_loads(f.read())
    else:
        cfg = {}
    return cfg


def save_config(cfg, filename=None):
    s = json_dumps(cfg, indent=2)
    with open(filename, 'w') as f:
        f.write(s)


def query_keyinfo(key):
    try:
        res = urlopen(key_url % key, timeout=3.0)
        customer = json_loads(res.read().decode())
    except Exception as e:
        if sys.flags.debug:
            logging.warning(e)
        return 'Because of internet exception, could not query ' \
               'registration information.'

    name = customer['name']
    email = customer['email']
    if name and email:
        info = 'This code is authorized to %s <%s>' % (name, email)
    else:
        info = 'Warning: this code may NOT be issued by PyArmor officially.' \
               '\nPlease contact the author Jondy Zhao <jondy.zhao@gmail.com>'
    return info


def register_keyfile(filename):
    f = ZipFile(filename, 'r')
    try:
        homepath = os.path.expanduser('~')
        for item in [('license key', 'license.lic', PYARMOR_PATH),
                     ('private capsule', '.pyarmor_capsule.zip', homepath)]:
            logging.info('Extract %s "%s" to %s' % item)
            f.extract(item[1], path=item[-1])
    finally:
        f.close()


if __name__ == '__main__':
    make_entry(sys.argv[1])
