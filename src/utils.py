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
import struct
import sys
import tempfile
from codecs import BOM_UTF8
from glob import glob
from json import dumps as json_dumps, loads as json_loads
from subprocess import Popen
from time import gmtime, strftime
from zipfile import ZipFile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import pytransform
from config import dll_ext, dll_name, entry_lines, protect_code_template, \
    platform_urls, platform_config, key_url, core_version

PYARMOR_PATH = os.getenv('PYARMOR_PATH', os.path.dirname(__file__))
PLATFORM_PATH = os.path.join(PYARMOR_PATH, pytransform.plat_path)
DATA_PATH = os.path.expanduser(os.path.join('~', '.pyarmor'))
CROSS_PLATFORM_PATH = os.path.join(DATA_PATH, pytransform.plat_path)


def _format_platid(platid=None):
    if platid is None:
        platid = pytransform.format_platform()
    if os.path.isabs(platid):
        return os.path.normpath(platid)
    return platid.replace('\\', '/').replace('/', '.')


def _search_downloaded_files(path, platid, libname):
    libpath = os.path.join(path, platid)
    if os.path.exists(libpath):
        for x in os.listdir(libpath):
            if os.path.exists(os.path.join(libpath, x, libname)):
                return os.path.join(platid, x)


def pytransform_bootstrap(capsule=None):
    logging.debug('PyArmor installation path: %s', PYARMOR_PATH)
    logging.debug('PyArmor data path: %s', DATA_PATH)
    path = PYARMOR_PATH
    licfile = os.path.join(path, 'license.lic')
    if not os.path.exists(licfile):
        if not os.getenv('HOME', os.getenv('USERPROFILE')):
            logging.info('Create trial license file: %s', licfile)
            shutil.copy(os.path.join(path, 'license.tri'), licfile)
        else:
            licfile = os.path.join(DATA_PATH, 'license.lic')
            if not os.path.exists(licfile):
                if not os.path.exists(DATA_PATH):
                    logging.info('Create pyarmor data path: %s', DATA_PATH)
                    os.makedirs(DATA_PATH)
                logging.info('Create trial license file: %s', licfile)
                shutil.copy(os.path.join(path, 'license.tri'), licfile)

    libname = dll_name + dll_ext
    platid = pytransform.format_platform()
    logging.debug('Native platform is %s', _format_platid(platid))

    if os.getenv('PYARMOR_PLATFORM'):
        p = os.getenv('PYARMOR_PLATFORM')
        logging.info('PYARMOR_PLATFORM is set to %s', p)
        platid = os.path.join(*os.path.normpath(p).split('.'))
        logging.debug('Build platform is %s', _format_platid(platid))

    if os.path.isabs(platid):
        if not os.path.exists(os.path.join(platid, dll_name)):
            raise RuntimeError('No dynamic library found at %s', platid)
    else:
        libpath = PLATFORM_PATH
        logging.debug('Search dynamic library in the path: %s', libpath)
        if not os.path.exists(os.path.join(libpath, platid, libname)):
            libpath = CROSS_PLATFORM_PATH
            logging.debug('Search dynamic library in the path: %s', libpath)
            if not os.path.exists(os.path.join(libpath, platid, libname)):
                found = _search_downloaded_files(libpath, platid, libname)
                if found:
                    logging.debug('Found available dynamic library %s', found)
                    platid = found
                else:
                    if not os.path.exists(libpath):
                        logging.info('Create cross platform libraries path %s',
                                     libpath)
                        os.makedirs(libpath)
                    rid = download_pytransform(platid, libpath, index=0)[0]
                    platid = os.path.join(*rid.split('.'))
        if libpath == CROSS_PLATFORM_PATH:
            platid = os.path.abspath(os.path.join(libpath, platid))

    pytransform.pyarmor_init(platid=platid)
    logging.debug('Loaded dynamic library: %s', pytransform._pytransform._name)

    ver = pytransform.version_info()
    logging.debug('The version of core library is %s', ver)
    if ver[0] < 8:
        raise RuntimeError('PyArmor does not work with this core library '
                           '(r%d), which reversion < 8' % ver[0])

    if capsule is not None and not os.path.exists(capsule):
        logging.info('Generating public capsule ...')
        make_capsule(capsule)


def _get_remote_file(urls, path, timeout=3.0):
    while urls:
        prefix = urls[0]
        url = '/'.join([prefix, path])
        logging.info('Getting remote file: %s', url)
        try:
            return urlopen(url, timeout=timeout)
        except Exception as e:
            urls.pop(0)
            logging.info('Could not get file from %s: %s', prefix, e)


def _get_platform_list(urls, platid=None):
    cfg = None
    if not os.path.exists(CROSS_PLATFORM_PATH):
        logging.info('Create cross platforms path: %s', CROSS_PLATFORM_PATH)
        os.makedirs(CROSS_PLATFORM_PATH)
    filename = os.path.join(PLATFORM_PATH, platform_config)
    if os.path.exists(filename):
        with open(filename) as f:
            cfg = json_loads(f.read())
        if cfg.get('version') == core_version:
            logging.info('Load platforms information from %s', filename)
        else:
            cfg = None
    if cfg is None:
        f = _get_remote_file(urls, platform_config)
        if f is None:
            raise RuntimeError('Download platform list file failed')

        logging.info('Load platform informations from remote file')
        data = f.read().decode()
        cfg = json_loads(data)

        if cfg.get('version') == core_version:
            logging.info('Cache platform informations to %s', filename)
            with open(filename, 'w') as f:
                f.write(data)
        else:
            logging.warning('The core library excepted version is %s, '
                            'but got %s from remote server',
                            core_version, cfg.get('version'))

    if platid is not None:
        logging.info('Search library for platform: %s', platid)

    return cfg.get('platforms', []) if platid is None \
        else [x for x in cfg.get('platforms', [])
              if (platid is None
                  or (x['id'] == platid)
                  or (x['id'].find(platid + '.') == 0)
                  or (x['path'] == platid))]


def get_platform_list():
    return _get_platform_list(platform_urls[:])


def download_pytransform(platid, output=None, url=None, index=None):
    platid = _format_platid(platid)
    urls = platform_urls[:] if url is None else ([url] + platform_urls)
    plist = _get_platform_list(urls, platid)
    if not plist:
        logging.error('Unsupport platform %s', platid)
        raise RuntimeError('No available library for this platform')

    if index is not None:
        plist = plist[index:index + 1]

    result = [p['id'] for p in plist]
    logging.info('Found available libraries: %s', result)

    if output is None:
        output = CROSS_PLATFORM_PATH
    if not os.access(output, os.W_OK):
        logging.error('Cound not download library file to %s', output)
        raise RuntimeError('No write permission for target path')

    for p in plist:
        libname = p['filename']
        path = '/'.join([p['path'], libname])

        logging.info('Downloading library file for %s ...', p['id'])
        res = _get_remote_file(urls, path, timeout=60)

        if res is None:
            raise RuntimeError('Download library file failed')

        dest = os.path.join(output, *p['id'].split('.'))
        if not os.path.exists(dest):
            logging.info('Create target path: %s', dest)
            os.makedirs(dest)

        data = res.read()
        if hashlib.sha256(data).hexdigest() != p['sha256']:
            raise RuntimeError('Verify dynamic library failed')

        target = os.path.join(dest, libname)
        logging.info('Writing target file: %s', target)
        with open(target, 'wb') as f:
            f.write(data)

        logging.info('Download dynamic library %s OK', p['id'])

    return result


def update_pytransform(pattern):
    platforms = dict([(p['id'], p) for p in get_platform_list()])
    path = os.path.join(CROSS_PLATFORM_PATH, '*', '*', '*', '_pytransform.*')
    flist = glob(path)

    plist = []
    n = len(CROSS_PLATFORM_PATH) + 1
    for filename in flist:
        platid = _format_platid(os.path.dirname(filename)[n:])
        if not ((pattern == '*') or platid.startswith(pattern)):
            continue
        p = platforms.get(platid)
        if p is None:
            logging.warning('No %s found in supported platforms', platid)
        else:
            with open(filename, 'rb') as f:
                data = f.read()
            if hashlib.sha256(data).hexdigest() == p['sha256']:
                logging.info('The platform %s has been latest', platid)
            else:
                plist.append(p['id'])

    if plist:
        for platid in plist:
            download_pytransform(platid)
    else:
        logging.info('Nothing updated')


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


def _make_entry(filename, rpath=None, relative=None, shell=None):
    pkg = os.path.basename(filename) == '__init__.py'
    entry_code = entry_lines[0] % (
        '.' if (relative is True) or ((relative is None) and pkg) else '')

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


def make_entry(entris, path, output, rpath=None, relative=None):
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
            logging.info('Insert shell line: %s', shell.strip())
        logging.info('Insert bootstrap code to entry script %s', filename)
        _make_entry(filename, rpath, relative=relative, shell=shell)


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


def _get_platform_library_filename(platid):
    if os.path.isabs(platid):
        plist = [platid]
    else:
        n = pytransform.version_info()[2]
        t = list(platid.split('.'))
        plist = [os.path.join(PLATFORM_PATH, *t)] if n & 2 else []
        if len(t) == 2:
            t.append(n)
            for k in ([3, 7] if n & 2 else [0, 4, 5]):
                t[-1] = str(k)
                plist.append(os.path.join(CROSS_PLATFORM_PATH, *t))
        else:
            plist.append(os.path.join(CROSS_PLATFORM_PATH, *t))

    for path in plist:
        if not os.path.exists(path):
            continue
        for x in os.listdir(path):
            if x.startswith('_pytransform.'):
                return os.path.join(path, x)


def _build_platforms(platforms):
    results = []
    checksums = dict([(p['id'], p['sha256']) for p in get_platform_list()])
    n = len(platforms)
    for platid in platforms:
        if (n > 1) and os.path.isabs(platid):
            raise RuntimeError('Invalid platform `%s`, for multiple '
                               'platforms it must be `platform.machine`',
                               platid)
        filename = _get_platform_library_filename(platid)
        if filename is None:
            logging.info('No dynamic library found for %s' % platid)
            download_pytransform(platid)
            filename = _get_platform_library_filename(platid)
            if filename is None:
                raise RuntimeError('No dynamic library found for %s' % platid)

        if platid in checksums:
            with open(filename, 'rb') as f:
                data = f.read()
            if hashlib.sha256(data).hexdigest() != checksums[platid]:
                logging.info('The platform %s is out of date', platid)
                download_pytransform(platid)
        results.append(filename)

    logging.debug('Target dynamic library: %s', results)
    return results


def make_runtime(capsule, output, licfile=None, platforms=None, package=False):
    if package:
        output = os.path.join(output, 'pytransform')
        if not os.path.exists(output):
            os.makedirs(output)
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
        logging.info('Copying %s as license file', licfile)
        shutil.copy2(licfile, os.path.join(output, 'license.lic'))

    if not platforms:
        libfile = pytransform._pytransform._name
        if not os.path.exists(libfile):
            libname = dll_name + dll_ext
            libfile = os.path.join(PYARMOR_PATH, libname)
            if not os.path.exists(libfile):
                pname = pytransform.format_platform()
                libpath = os.path.join(PYARMOR_PATH, 'platforms')
                libfile = os.path.join(libpath, pname, libname)
        logging.info('Copying %s', libfile)
        shutil.copy2(libfile, output)
    elif len(platforms) == 1:
        filename = _build_platforms(platforms)[0]
        logging.info('Copying %s', filename)
        shutil.copy2(filename, output)
    else:
        libpath = os.path.join(output, pytransform.plat_path)
        logging.info('Create library path to support multiple platforms: %s',
                     libpath)
        if not os.path.exists(libpath):
            os.mkdir(libpath)

        filenames = _build_platforms(platforms)
        for platid, filename in list(zip(platforms, filenames)):
            logging.info('Copying %s', filename)
            path = os.path.join(libpath, *platid.split('.'))
            logging.info('To %s', path)
            if not os.path.exists(path):
                os.makedirs(path)
            shutil.copy2(filename, path)

    filename = os.path.join(PYARMOR_PATH, 'pytransform.py')
    shutil.copy2(filename, os.path.join(output, '__init__.py') if package
                 else output)

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


def build_path(path, start):
    return path if os.path.isabs(path) else os.path.join(start, path)


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


def search_plugins(plugins):
    if plugins:
        result = []
        path = os.getenv('PYARMOR_PLUGIN', '')
        for name in plugins:
            i = 1 if name[0] == '@' else 0
            filename = name[i:] + '.py'
            key = os.path.basename(name[i:])
            if not os.path.exists(filename):
                filename = build_path(filename, path)
                if not os.path.exists(filename):
                    raise RuntimeError('No script found for plugin %s' % name)
            logging.info('Found plugin %s at: %s', key, filename)
            result.append((key, filename, not i))
        return result


def _patch_plugins(plugins, pnames):
    result = []
    for key, filename, x in plugins:
        if x or (key in pnames):
            logging.info('Apply plugin %s', key)
            lines = _readlines(filename)
            result.append(''.join(lines))
    if pnames and not result:
        raise RuntimeError('There are plugin calls, but no plugin definition')
    return ['\n'.join(result)]


def _filter_call_marker(plugins, marker, name):
    if marker.startswith('# PyArmor'):
        return True
    for key, filename, x in plugins:
        if name == key:
            return True


def _build_source_keylist(source, code, closure):
    result = []
    flist = ('dllmethod', 'init_pytransform', 'init_runtime', '_load_library',
             'get_registration_code', 'get_expired_days', 'get_hd_info',
             'get_license_info', 'get_license_code', 'format_platform',
             'pyarmor_init', 'pyarmor_runtime')

    def _make_value(co):
        return len(co.co_names), len(co.co_consts), len(co.co_code)

    def _make_code_key(co):
        v1 = _make_value(co)
        v2 = _make_value(co.co_consts[1]) if co.co_name == 'dllmethod'else None
        co_closure = getattr(co, closure, None)
        v3 = _make_value(getattr(co_closure[0].cell_contents, code)) \
            if co_closure else None
        return v1, v2, v3

    mod_co = compile(source, 'pytransform', 'exec')
    result.append((-1, _make_code_key(mod_co)))
    mod_consts = mod_co.co_consts
    for i in range(len(mod_consts)):
        co_const = mod_consts[i]
        co = getattr(co_const, code, None)
        if co and co.co_name in flist:
            result.append((i, _make_code_key(co)))
    return result


def _build_pytransform_keylist(mod, code, closure):
    result = []
    flist = ('dllmethod', 'init_pytransform', 'init_runtime', '_load_library',
             'get_registration_code', 'get_expired_days', 'get_hd_info',
             'get_license_info', 'get_license_code', 'format_platform',
             'pyarmor_init', 'pyarmor_runtime', '_match_features')

    def _make_value(co):
        return len(co.co_names), len(co.co_consts), len(co.co_code)

    def _make_code_key(co):
        v1 = _make_value(co)
        v2 = _make_value(co.co_consts[1]) if co.co_name == 'dllmethod'else None
        co_closure = getattr(co, closure, None)
        v3 = _make_value(getattr(co_closure[0].cell_contents, code)) \
            if co_closure else None
        return v1, v2, v3

    for name in flist:
        co = getattr(getattr(mod, name), code)
        result.append((name, _make_code_key(co)))
    return result


def _make_protect_pytransform(template, filenames=None, rpath=None):
    if filenames is None:
        filenames = [pytransform._pytransform._name]
    checksums = []
    for name in filenames:
        size = os.path.getsize(name) & 0xFFFFFFF0
        n = size >> 2
        with open(name, 'rb') as f:
            buf = f.read(size)
        fmt = 'I' * n
        cosum = sum(struct.unpack(fmt, buf)) & 0xFFFFFFFF
        checksums.append(cosum)

    with open(template) as f:
        buf = f.read()

    code = '__code__' if sys.version_info[0] == 3 else 'func_code'
    closure = '__closure__' if sys.version_info[0] == 3 else 'func_closure'
    keylist = _build_pytransform_keylist(pytransform, code, closure)
    rpath = 'pytransform.os.path.dirname(pytransform.__file__)' \
        if rpath is None else repr(rpath)
    spath = 'pytransform.os.path.join(pytransform.plat_path, ' \
        'pytransform.format_platform())' if len(filenames) > 1 else repr('')
    return buf.format(code=code, closure=closure, rpath=rpath, spath=spath,
                      checksum=str(checksums), keylist=keylist)


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


def _readlines(filename):
    if sys.version_info[0] == 2:
        with open(filename, 'r') as f:
            lines = f.readlines()
    else:
        encoding = _guess_encoding(filename)
        try:
            with open(filename, 'r', encoding=encoding) as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            encoding = 'utf-8'
            with open(filename, 'r', encoding=encoding) as f:
                lines = f.readlines()
        # Try to remove any UTF BOM bytes
        if encoding == 'utf-8' and lines:
            i = 0
            for c in lines[0]:
                if ord(c) < 128:
                    break
                i += 1
            if i:
                lines[0] = lines[0][i:]
    return lines


def encrypt_script(pubkey, filename, destname, wrap_mode=1, obf_code=1,
                   obf_mod=1, adv_mode=0, rest_mode=1, protection=0,
                   platforms=None, plugins=None, rpath=None):
    lines = _readlines(filename)
    if plugins:
        n = 0
        k = -1
        plist = []
        pnames = []
        markers = '# PyArmor Plugin: ', '# pyarmor_', '# @pyarmor_'
        for line in lines:
            if line.startswith('# {PyArmor Plugins}'):
                k = n + 1
            else:
                for marker in markers:
                    i = line.find(marker)
                    if i > -1:
                        name = line[i+len(marker):].strip().strip('@')
                        t = name.find('(')
                        name = (name if t == -1 else name[:t]).strip()
                        if _filter_call_marker(plugins, marker, name):
                            plist.append((n+1, i, marker))
                            pnames.append(name)
            n += 1
        if k > -1:
            logging.info('Patch this script with plugins')
            lines[k:k] = _patch_plugins(plugins, pnames)
        for n, i, m in plist:
            c = '@' if m[2] == '@' else ''
            lines[n] = lines[n][:i] + c + lines[n][i+len(m):]

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
                template = os.path.join(PYARMOR_PATH, protect_code_template) \
                    if isinstance(protection, int) else protection
                logging.info('Use template: %s', template)
                targets = _build_platforms(platforms) if platforms else None
                lines[n:n] = [_make_protect_pytransform(template=template,
                                                        filenames=targets,
                                                        rpath=rpath)]
                break
            n += 1

    if sys.flags.debug and (protection or plugins):
        patched_script = filename + '.pyarmor-patched'
        logging.info('Write patched script for debugging: %s', patched_script)
        with open(patched_script, 'w') as f:
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


def register_keyfile(filename, legency=False):
    if not legency and not os.getenv('HOME', os.getenv('USERPROFILE')):
        logging.debug('Force traditional way because no HOME set')
        legency = True
    old_path = DATA_PATH if legency else PYARMOR_PATH
    old_license = os.path.join(old_path, 'license.lic')
    if os.path.exists(old_license):
        logging.info('Remove old license file `%s`', old_license)
        os.remove(old_license)

    home = os.path.expanduser('~')
    path = PYARMOR_PATH if legency else DATA_PATH
    if not os.path.exists(path):
        logging.info('Create path: %s', path)
        os.makedirs(path)

    f = ZipFile(filename, 'r')
    try:
        for item in [('license key', 'license.lic', path),
                     ('private capsule', '.pyarmor_capsule.zip', home)]:
            logging.info('Extract %s "%s" to %s' % item)
            f.extract(item[1], path=item[-1])
    finally:
        f.close()


def relpath(path, start=os.curdir):
    try:
        return os.path.relpath(path, start)
    except Exception:
        return path


def check_cross_platform(platforms):
    if os.getenv('PYARMOR_PLATFORM'):
        return
    for name in platforms:
        if name in ('linux.arm', 'android.aarch64', 'linux.ppc64',
                    'darwin.arm64', 'freebsd.x86_64', 'alpine.x86_64',
                    'alpine.arm', 'poky.x86'):
            logging.info('===========================================')
            logging.info('Reboot PyArmor to obfuscate the scripts for '
                         'platform %s', name)
            logging.info('===========================================')
            os.putenv('PYARMOR_PLATFORM', '.'.join([_format_platid(), '0']))
            p = Popen([sys.executable] + sys.argv)
            p.wait()
            sys.exit(p.returncode)


def compatible_platform_names(platforms):
    '''Only for compatibility, it will be removed in next major version.'''
    if not platforms:
        return platforms

    old_forms = {
        'armv5': 'linux.arm',
        'ppc64le': 'linux.ppc64',
        'ios.arm64': 'darwin.arm64',
        'freebsd': 'freebsd.x86_64',
        'alpine': 'alpine.x86_64',
        'poky-i586': 'poky.x86',
    }

    names = []
    for name in platforms:
        if name in old_forms:
            logging.warning('This platform name `%s` has been deprecated, '
                            'use `%s` instead. Display all standard platform '
                            'names by `pyarmor download --help-platorm`',
                            name, old_forms[name])
            names.append(old_forms[name])
        else:
            names.append(name)
    return names


def make_bootstrap_script(output, capsule=None, relative=None):
    filename = os.path.basename(output)
    co = compile('', filename, 'exec')
    flags = 0x18000000
    prokey = get_product_key(capsule)
    buf = pytransform.encrypt_code_object(prokey, co, flags)
    with open(output, 'w') as f:
        f.write(buf.decode())
    _make_entry(output, relative=relative)


if __name__ == '__main__':
    make_entry(sys.argv[1])
