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
    platform_urls, platform_config, key_url, core_version, capsule_filename

PYARMOR_PATH = os.getenv('PYARMOR_PATH', os.path.dirname(__file__))
PYARMOR_HOME = os.getenv('PYARMOR_HOME', os.path.join('~', '.pyarmor'))
PLATFORM_PATH = os.path.join(PYARMOR_PATH, pytransform.plat_path)

HOME_PATH = os.path.abspath(os.path.expanduser(PYARMOR_HOME))
CROSS_PLATFORM_PATH = os.path.join(HOME_PATH, pytransform.plat_path)

DEFAULT_CAPSULE = os.path.join(HOME_PATH, capsule_filename)
# From v6.2.0, change the location of default capsule to ~/.pyarmor/
OLD_CAPSULE = os.path.join(HOME_PATH, '..', capsule_filename)

FEATURE_ANTI = 1
FEATURE_JIT = 2
FEATURE_ADV = 4
FEATURE_MAPOP = 8
FEATURE_VM = 16


def _format_platid(platid=None):
    if platid is None:
        platid = pytransform.format_platform()
    if os.path.isabs(platid) or os.path.isfile(platid):
        return os.path.normpath(platid)
    return platid.replace('\\', '/').replace('/', '.')


def _search_downloaded_files(path, platid, libname):
    libpath = os.path.join(path, platid)
    if os.path.exists(libpath):
        for x in os.listdir(libpath):
            if os.path.exists(os.path.join(libpath, x, libname)):
                return os.path.join(platid, x)


def pytransform_bootstrap(capsule=None, force=False):
    if pytransform._pytransform is not None and not force:
        logging.debug('No bootstrap, pytransform has been loaded')
        return
    logging.debug('PyArmor installation path: %s', PYARMOR_PATH)
    logging.debug('PyArmor home path: %s', HOME_PATH)
    path = PYARMOR_PATH
    licfile = os.path.join(path, 'license.lic')
    if not os.path.exists(licfile):
        if not os.getenv('PYARMOR_HOME',
                         os.getenv('HOME', os.getenv('USERPROFILE'))):
            logging.info('Create trial license file: %s', licfile)
            shutil.copy(os.path.join(path, 'license.tri'), licfile)
        else:
            licfile = os.path.join(HOME_PATH, 'license.lic')
            if not os.path.exists(licfile):
                if not os.path.exists(HOME_PATH):
                    logging.info('Create pyarmor home path: %s', HOME_PATH)
                    os.makedirs(HOME_PATH)
                old_license = os.path.join(HOME_PATH, '..', 'license.lic')
                if os.path.exists(old_license):
                    logging.info('Create license file %s from old license %s',
                                 licfile, old_license)
                    shutil.move(old_license, licfile)
                else:
                    logging.info('Create trial license file: %s', licfile)
                    shutil.copy(os.path.join(path, 'license.tri'), licfile)

    libname = dll_name + dll_ext
    platid = pytransform.format_platform()
    logging.debug('Native platform is %s', _format_platid(platid))

    if os.getenv('PYARMOR_PLATFORM'):
        p = os.getenv('PYARMOR_PLATFORM')
        logging.info('PYARMOR_PLATFORM is %s', p)
        platid = os.path.normpath(p) if os.path.isabs(p) or os.path.isfile(p) \
            else os.path.join(*os.path.normpath(p).split('.'))
        logging.debug('Build platform is %s', _format_platid(platid))

    if os.path.isabs(platid):
        if not os.path.exists(os.path.join(platid, libname)):
            raise RuntimeError('No dynamic library found at %s', platid)
    elif not os.path.isfile(platid):
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
                    rid = download_pytransform(platid, libpath, firstonly=1)[0]
                    platid = os.path.join(*rid.split('.'))
        if libpath == CROSS_PLATFORM_PATH:
            platid = os.path.abspath(os.path.join(libpath, platid))

    pytransform.pyarmor_init(platid=platid)
    logging.debug('Loaded dynamic library: %s', pytransform._pytransform._name)

    ver = pytransform.version_info()
    logging.debug('The version of core library is %s', ver)
    if ver[0] < 32:
        raise RuntimeError('PyArmor does not work with this core library '
                           '(r%d), which reversion < r32, please run '
                           '"pyarmor download --update" to fix it' % ver[0])

    if capsule is not None and not os.path.exists(capsule):
        logging.info('Generating public capsule ...')
        make_capsule(capsule)


def _get_remote_file(urls, path, timeout=30.0):
    while urls:
        prefix = urls[0]
        url = '/'.join([prefix, path])
        logging.info('Getting remote file: %s', url)
        try:
            return urlopen(url, timeout=timeout)
        except Exception as e:
            urls.pop(0)
            logging.info('Could not get file from %s: %s', prefix, e)


def _get_platform_list(platid=None):
    filename = os.path.join(PLATFORM_PATH, platform_config)
    logging.debug('Load platform list from %s', filename)

    if not os.path.exists(filename):
        filename = os.path.join(CROSS_PLATFORM_PATH, platform_config)
        logging.debug('Load platform list from %s', filename)

    if not os.path.exists(filename):
        urls = [x.format(version=core_version) for x in platform_urls]
        res = _get_remote_file(urls, 'index.json', timeout=5.0)
        if res is None:
            raise RuntimeError('No platform list file %s found' % filename)
        if not os.path.exists(CROSS_PLATFORM_PATH):
            logging.info('Create platform path: %s' % CROSS_PLATFORM_PATH)
            os.makedirs(CROSS_PLATFORM_PATH)
        logging.info('Write cached platform list file %s' % filename)
        with open(filename, 'wb') as f:
            f.write(res.read())

    with open(filename) as f:
        cfg = json_loads(f.read())

    ver = cfg.get('version')
    if not ver.split('.')[0] == core_version.split('.')[0]:
        logging.warning('The core library excepted version is %s, '
                        'but got %s from platform list file %s',
                        core_version, cfg.get('version'), filename)

    return cfg.get('platforms', []) if platid is None \
        else [x for x in cfg.get('platforms', [])
              if (platid is None
                  or (x['id'] == platid)
                  or (x['id'].find(platid + '.') == 0)
                  or (x['path'] == platid))]


def get_platform_list(platid=None):
    return _get_platform_list(platid=platid)


def download_pytransform(platid, output=None, url=None, firstonly=False):
    platid = _format_platid(platid)
    urls = [x.format(version=core_version)
            for x in (platform_urls if url is None else [url])]

    logging.info('Search library for platform: %s', platid)
    plist = _get_platform_list(platid=platid)
    if not plist:
        logging.error('Unsupport platform %s', platid)
        raise RuntimeError('No available library for this platform')

    if firstonly:
        plist = plist[:1]

    result = [p['id'] for p in plist]
    logging.info('Found available libraries: %s', result)

    if output is None:
        output = CROSS_PLATFORM_PATH

    if not os.path.exists(output):
        logging.info('Create cross platforms path: %s', output)
        os.makedirs(output)

    if not os.access(output, os.W_OK):
        logging.error('Cound not download library file to %s', output)
        raise RuntimeError('No write permission for target path')

    for p in plist:
        libname = p['filename']
        path = '/'.join([p['path'], libname])

        logging.info('Downloading library file for %s ...', p['id'])
        timeout = 300.0 if 'VM' in p['features'] else 120.0
        res = _get_remote_file(urls, path, timeout=timeout)

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
    platforms = dict([(p['id'], p) for p in _get_platform_list()])
    path = os.path.join(CROSS_PLATFORM_PATH, '*', '*', '*')
    flist = glob(os.path.join(path, '_pytransform.*')) + \
        glob(os.path.join(path, 'py*', 'pytransform.*'))

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

    if not plist:
        logging.info('Nothing updated')
        return

    for platid in plist:
        download_pytransform(platid)
    logging.info('Update library successfully')


def make_capsule(filename):
    if os.path.exists(OLD_CAPSULE):
        logging.info('Move old capsule %s to %s', OLD_CAPSULE, filename)
        shutil.move(OLD_CAPSULE, filename)
        return

    if get_registration_code():
        logging.error('The registered version would use private capsule.'
                      '\n\t Please run `pyarmor register KEYFILE` '
                      'to restore your private capsule.')
        raise RuntimeError('Could not generate private capsule.')
    public_capsule = os.path.join(PYARMOR_PATH, 'public_capsule.zip')
    logging.debug('Copy %s to %s', public_capsule, filename)
    shutil.copy(public_capsule, filename)
    logging.debug('Generate public capsule %s OK.', filename)


def check_capsule(capsule):
    if os.path.getmtime(capsule) < os.path.getmtime(
            os.path.join(PYARMOR_PATH, 'license.lic')):
        logging.info('Capsule %s has been out of date', capsule)

        suffix = strftime('%Y%m%d%H%M%S', gmtime())
        logging.info('Rename it as %s.%s', capsule, suffix)
        os.rename(capsule, capsule + '.' + suffix)
        return False
    return True


def _make_entry(filename, rpath=None, relative=None, shell=None, suffix=''):
    pkg = os.path.basename(filename) == '__init__.py'
    entry_code = entry_lines[0] % (
        '.' if (relative is True) or ((relative is None) and pkg) else '',
        suffix)

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
        paras = []
        if rpath is not None:
            paras.append(repr(rpath))
        if suffix:
            paras.append('suffix=%s' % repr(suffix))
        f.write(entry_lines[1] % ', '.join(paras))
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


def make_entry(entris, path, output, rpath=None, relative=None, suffix=''):
    for entry in entris.split(','):
        entry = entry.strip()
        filename = build_path(entry, output)
        src = build_path(entry, path)
        if os.path.exists(filename):
            shell = _get_script_shell(src)
        else:
            shell = None
            logging.info('Copy entry script %s to %s', src, relpath(filename))
            shutil.copy(src, filename)
        if shell:
            logging.info('Insert shell line: %s', shell.strip())
        logging.info('Insert bootstrap code to entry script %s',
                     relpath(filename))
        _make_entry(filename, rpath, relative=relative, shell=shell,
                    suffix=suffix)


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


def _get_library_filename(platid, checksums=None):
    if os.path.isabs(platid) or os.path.isfile(platid):
        if not os.path.exists(platid):
            raise RuntimeError('No platform library %s found' % platid)
        return platid

    xlist = [str(x) for x in platid.split('.')]
    n = len(xlist)

    if n < 3:
        raise RuntimeError('Missing features in platform name %s' % platid)

    if (xlist[2] == '7') and xlist[1] in ('x86', 'x86_64') and \
       xlist[0] in ('windows', 'darwin', 'linux'):
        path = os.path.join(PLATFORM_PATH, *xlist[:2])
        names = [x for x in os.listdir(path) if x.startswith('_pytransform.')]
        if names:
            return os.path.join(path, names[0])

    names = None
    path = os.path.join(CROSS_PLATFORM_PATH, *xlist)
    if os.path.exists(path):
        names = [x for x in os.listdir(path) if x.find('pytransform.') > -1]
        if len(names) > 1:
            raise RuntimeError('Invalid platform data, there is more than '
                               '1 file in the path %s', path)
    if not names:
        download_pytransform(platid)
        return _get_library_filename(platid, checksums)

    filename = os.path.join(path, names[0])
    if checksums is not None and platid in checksums:
        with open(filename, 'rb') as f:
            data = f.read()
        if hashlib.sha256(data).hexdigest() != checksums[platid]:
            if hasattr(sys, '_debug_pyarmor'):
                logging.warning('Found library %s for platform %s, but it does'
                                ' not match this pyarmor', filename, platid)
                return filename
            logging.info('The platform %s is out of date', platid)
            download_pytransform(platid)
            return _get_library_filename(platid, checksums)

    return filename


def _build_platforms(platforms):
    results = []
    checksums = dict([(p['id'], p['sha256']) for p in _get_platform_list()])
    n = len(platforms)

    if not os.path.exists(CROSS_PLATFORM_PATH):
        logging.info('Create cross platforms path: %s', CROSS_PLATFORM_PATH)
        os.makedirs(CROSS_PLATFORM_PATH)

    for platid in platforms:
        if (n > 1) and (os.path.isabs(platid) or os.path.isfile(platid)):
            raise RuntimeError('Invalid platform `%s`, for multiple platforms '
                               'it must be `platform.machine`' % platid)
        if (n > 1) and platid.startswith('vs2015.'):
            raise RuntimeError('The platform `%s` does not work '
                               'in multiple platforms target' % platid)
        filename = _get_library_filename(platid, checksums)
        results.append(filename)

    logging.debug('Target dynamic library: %s', results)
    return results


def _build_license_file(capsule, licfile, output=None):
    if licfile is None:
        myzip = ZipFile(capsule, 'r')
        try:
            if 'default.lic' in myzip.namelist():
                logging.info('Read default license from capsule')
                lickey = myzip.read('default.lic')
            else:
                logging.info('Generate default license file')
                lickey = make_license_key(capsule, 'PyArmor-Project')
        finally:
            myzip.close()
    elif licfile == 'no-restrict':
        logging.info('Generate no restrict mode license file')
        licode = '*FLAGS:%c*CODE:PyArmor-Project' % chr(1)
        lickey = make_license_key(capsule, licode)
    elif licfile in ('no', 'outer'):
        logging.info('Use outer license file')
        lickey = b''
    else:
        logging.info('Generate license file from  %s', relpath(licfile))
        with open(licfile, 'rb') as f:
            lickey = f.read()
    if output is not None and lickey:
        logging.info('Write license file: %s', output)
        with open(output, 'wb') as f:
            f.write(lickey)
    return lickey


def make_runtime(capsule, output, licfile=None, platforms=None, package=False,
                 suffix='', supermode=False):
    if supermode:
        return _make_super_runtime(capsule, output, platforms, licfile=licfile,
                                   suffix=suffix)

    if package:
        output = os.path.join(output, 'pytransform' + suffix)
    if not os.path.exists(output):
        os.makedirs(output)
    logging.info('Generating runtime files to %s', relpath(output))

    checklist = []
    keylist = _build_keylist(capsule, licfile)

    def copy3(src, dst, onlycopy=False):
        x = os.path.basename(src)
        if suffix:
            x = x.replace('.', ''.join([suffix, '.']))
            logging.info('Rename it to %s', x)
        target = os.path.join(dst, x)
        shutil.copy2(src, target)

        if onlycopy:
            return

        logging.info('Patch library %s', target)
        data = _patch_extension(target, keylist, suffix)
        with open(target, 'wb') as f:
            f.write(data)
        checklist.append(sum(bytearray(data)))

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
        copy3(libfile, output)

    elif len(platforms) == 1:
        filename = _build_platforms(platforms)[0]
        logging.info('Copying %s', filename)
        copy3(filename, output)
    else:
        libpath = os.path.join(output, pytransform.plat_path)
        logging.info('Create library path to support multiple platforms: %s',
                     libpath)
        if not os.path.exists(libpath):
            os.mkdir(libpath)

        filenames = _build_platforms(platforms)
        for platid, filename in list(zip(platforms, filenames)):
            logging.info('Copying %s', filename)
            path = os.path.join(libpath, *platid.split('.')[:2])
            logging.info('To %s', path)
            if not os.path.exists(path):
                os.makedirs(path)
            copy3(filename, path)

    filename = os.path.join(PYARMOR_PATH, 'pytransform.py')
    if package:
        logging.info('Copying %s', filename)
        logging.info('Rename it to %s/__init__.py', os.path.basename(output))
        shutil.copy2(filename, os.path.join(output, '__init__.py'))
    else:
        logging.info('Copying %s', filename)
        copy3(filename, output, onlycopy=True)

    logging.info('Generate runtime files OK')
    return checklist


def copy_runtime(path, output, licfile=None, dryrun=False):
    logging.info('Copying runtime files from %s', path)
    logging.info('To %s', output)
    if not os.path.exists(output):
        os.makedirs(output)

    def copy3(src, dst):
        if dryrun:
            return
        if os.path.isdir(src):
            if os.path.exists(dst):
                logging.info('Remove old path %s', dst)
                shutil.rmtree(dst)
            logging.info('Copying directory %s', os.path.basename(src))
            shutil.copytree(src, dst)
        else:
            logging.info('Copying file %s', os.path.basename(src))
            shutil.copy2(src, dst)

    name = None
    tlist = []
    for x in os.listdir(path):
        root, ext = os.path.splitext(x)
        if root in ('pytransform_protection', 'pytransform_bootstrap'):
            continue
        src = os.path.join(path, x)
        dst = os.path.join(output, x)
        if x.startswith('pytransform'):
            copy3(src, dst)
            name = x
            tlist.append(ext)
        elif x.stratswith('_pytransform') or x == 'platforms':
            copy3(src, dst)

    if name is None:
        raise RuntimeError('No module "pytransform" found in runtime package')

    if (('' in tlist or '.py' in tlist) and len(tlist) > 1):
        raise RuntimeError('Multiple runtime modules found')

    if licfile and not dryrun:
        if not os.path.exists(licfile):
            raise RuntimeError('No found license file "%s"' % licfile)
        logging.info('Copying outer license %s', licfile)
        dst = os.path.join(output, '' if name.find('.') > 0 else name)
        logging.info('To %s/license.lic', dst)
        shutil.copy2(licfile, os.path.join(dst, 'license.lic'))


def make_project_license(capsule, code, output):
    myzip = ZipFile(capsule, 'r')
    myzip.extract('private.key', tempfile.gettempdir())
    prikey = os.path.join(tempfile.tempdir, 'private.key')
    try:
        pytransform.generate_license_file(output, prikey, code)
    finally:
        os.remove(prikey)


def make_license_key(capsule, code, output=None, key=None):
    prikey = ZipFile(capsule, 'r').read('private.key') \
        if key is None else key
    size = len(prikey)
    lickey = pytransform.generate_license_key(prikey, size, code)
    if output is None:
        return lickey
    elif output in ('stdout', 'stderr'):
        getattr(sys, output).write(
            lickey.decode() if hasattr(lickey, 'decode') else lickey)
    else:
        with open(output, 'wb') as f:
            f.write(lickey)


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
        for name in plugins:
            if name == 'on':
                logging.info('Enable inline plugin')
                result.append(['<inline>', '<plugin>', 0])
                continue
            i = 1 if name[0] == '@' else 0
            filename = name[i:] + ('' if name.endswith('.py') else '.py')
            key = os.path.basename(name[i:])
            if not os.path.exists(filename):
                if os.path.isabs(filename):
                    raise RuntimeError('No script found for plugin %s' % name)
                for path in [os.path.join(x, 'plugins')
                             for x in (HOME_PATH, PYARMOR_PATH)]:
                    testname = build_path(filename, path)
                    if os.path.exists(testname):
                        filename = testname
                        break
                else:
                    raise RuntimeError('No script found for plugin %s' % name)
            logging.info('Found plugin %s at: %s', key, filename)
            result.append([key, filename, not i])
        return result


def _patch_plugins(plugins):
    result = []
    for key, filename, x in plugins:
        if x:
            logging.info('Apply plugin %s', key)
            lines = _readlines(filename)
            result.append(''.join(lines))
    return ['\n'.join(result)]


def _filter_call_marker(plugins, name):
    for plugin in plugins:
        if plugin[0] == name:
            plugin[-1] = True
            return True


def _build_source_keylist(source, code, closure):
    result = []
    flist = ('dllmethod', 'init_pytransform', 'init_runtime', '_load_library',
             'get_registration_code', 'get_expired_days', 'get_hd_info',
             'get_license_info', 'get_license_code', 'format_platform',
             'pyarmor_init', 'pyarmor_runtime', 'assert_armored')

    def _make_value(co):
        return len(co.co_names), len(co.co_consts), len(co.co_code)

    def _make_code_key(co):
        v1 = _make_value(co)
        v2 = _make_value(co.co_consts[1]) if co.co_name == 'dllmethod' else None
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


def _get_checksum(filename):
    size = os.path.getsize(filename) & 0xFFFFFFF0
    n = size >> 2
    with open(filename, 'rb') as f:
        buf = f.read(size)
    fmt = 'I' * n
    return sum(struct.unpack(fmt, buf)) & 0xFFFFFFFF


def _make_protection_code(relative, checksums, suffix='', multiple=False):
    template = os.path.join(PYARMOR_PATH, protect_code_template % '')
    with open(template) as f:
        buf = f.read()

    code = '__code__' if sys.version_info[0] == 3 else 'func_code'
    closure = '__closure__' if sys.version_info[0] == 3 else 'func_closure'
    keylist = _build_pytransform_keylist(pytransform, code, closure)
    rpath = '{0}.os.path.dirname({0}.__file__)'.format('pytransform')
    spath = '{0}.os.path.join({0}.plat_path, {0}.format_platform())'.format(
        'pytransform') if multiple else repr('')
    return buf.format(code=code, closure=closure, rpath=rpath, spath=spath,
                      checksum=str(checksums), keylist=keylist, suffix=suffix,
                      relative='from . ' if relative else '')


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
            m = re.search(r'coding[=:]\s*([-\w.]+)', line[:n].decode())
            if m:
                return m.group(1)
            if n > -1 and len(line) > (n+1) and line[n+1] == 35:
                k = n + 1
                n = line.find(b'\n', k)
                m = re.search(r'coding[=:]\s*([-\w.]+)', line[k:n].decode())
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
                   obf_mod=1, adv_mode=0, rest_mode=1, entry=0, protection=0,
                   platforms=None, plugins=None, rpath=None, suffix=''):
    lines = _readlines(filename)
    if plugins:
        n = 0
        k = -1
        plist = []
        stub_marker = '# {PyArmor Plugins}'
        inline_marker = '# PyArmor Plugin: '
        call_markers = '# pyarmor_', '# @pyarmor_'
        for line in lines:
            if line.startswith(stub_marker):
                k = n + 1
            else:
                i = line.find(inline_marker)
                if i > -1:
                    plist.append((n if k == -1 else n+1, i, inline_marker))
                else:
                    for marker in call_markers:
                        i = line.find(marker)
                        if i == -1:
                            continue
                        name = line[i+len(marker):line.find('(')].strip()
                        if _filter_call_marker(plugins, name):
                            plist.append((n if k == -1 else n+1, i, marker))
            n += 1
        if k > -1:
            logging.info('Patch this script with plugins')
            lines[k:k] = _patch_plugins(plugins)
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
                if os.path.exists(protection):
                    logging.info('Use template: %s', protection)
                    with open(protection) as f:
                        lines[n:n] = [f.read()]
                else:
                    lines[n:n] = [protection]
                break
            n += 1

    if hasattr(sys, '_debug_pyarmor') and (protection or plugins):
        patched_script = filename + '.pyarmor-patched'
        logging.info('Write patched script for debugging: %s', patched_script)
        with open(patched_script, 'w') as f:
            f.write(''.join(lines))

    modname = _frozen_modname(filename, destname)
    co = compile(''.join(lines), modname, 'exec')

    if (adv_mode & 0x7) > 1 and sys.version_info[0] > 2:
        co = _check_code_object_for_super_mode(co, lines, modname)

    flags = obf_code | obf_mod << 8 | (wrap_mode | (adv_mode << 4)) << 16 | \
        ((0x34 if rest_mode == 5 else 0xB0 if rest_mode == 4
          else 0xF0 if rest_mode == 3 else 0x70 if rest_mode == 2
          else 0x10 if rest_mode else 0) | (8 if entry else 0)) << 24
    s = pytransform.encrypt_code_object(pubkey, co, flags, suffix=suffix)

    with open(destname, 'w') as f:
        f.write(s.decode())


def get_product_key(capsule):
    return ZipFile(capsule).read('product.key')


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
        if hasattr(sys, '_debug_pyarmor'):
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
    if (not legency) and \
       not os.getenv('PYARMOR_HOME',
                     os.getenv('HOME', os.getenv('USERPROFILE'))):
        logging.debug('Force traditional way because no HOME set')
        legency = True
    old_path = HOME_PATH if legency else PYARMOR_PATH
    old_license = os.path.join(old_path, 'license.lic')
    if os.path.exists(old_license):
        logging.info('Remove old license file `%s`', old_license)
        os.remove(old_license)

    path = PYARMOR_PATH if legency else HOME_PATH
    if not os.path.exists(path):
        logging.info('Create path: %s', path)
        os.makedirs(path)
    logging.info('Save registration data to: %s', path)
    f = ZipFile(filename, 'r')
    try:
        for item in ('license.lic', '.pyarmor_capsule.zip'):
            logging.info('Extracting %s' % item)
            f.extract(item, path=path)
    finally:
        f.close()


def relpath(path, start=os.curdir):
    try:
        r = os.path.relpath(path, start)
        return path if r.count('..') > 1 else r
    except Exception:
        return path


def _reboot_pytransform(platid):
    os.putenv('PYARMOR_PLATFORM', platid)
    if sys.platform == 'win32' and sys.argv[0].endswith('pyarmor'):
        p = Popen(sys.argv)
    else:
        p = Popen([sys.executable] + sys.argv)
    p.wait()
    return p.returncode


def _get_preferred_platid(platname, features=None):
    if os.path.isabs(platname) or os.path.isfile(platname):
        return platname

    nlist = platname.split('.')
    name = '.'.join(nlist[:2])

    if name in ('linux.arm', 'linux.ppc64', 'linux.mips64',
                'linux.mips64el', 'musl.x86_64', 'musl.arm', 'musl.mips32',
                'darwin.arm64', 'freebsd.x86_64', 'android.aarch64',
                'poky.x86', 'vs2015.x86_64', 'vs2015.x86'):
        if features and '0' not in features:
            raise RuntimeError('No feature %s for platform %s', features, name)
        features = ['0']

    elif len(nlist) > 2:
        if features and nlist[2] not in features:
            raise RuntimeError('Feature conflicts for platname %s', name)
        features = nlist[2:3]

    elif features is None:
        features = ['7', '3', '0']

    pyver = None
    if '8' in features or '11' in features or '25' in features:
        pyver = 'py%d%d' % sys.version_info[:2]

    plist = [x['id'] for x in _get_platform_list() if x['name'] == name]
    for platid in plist:
        ns = [str(x) for x in platid.split('.')]
        if (features is None or str(ns[2]) in features) \
           and (pyver is None or pyver in ns[3:]):
            return platid


def check_cross_platform(platforms, supermode=False, vmode=False):
    if not platforms:
        platforms = []
    fn1 = pytransform.version_info()[2]

    features = None
    if vmode:
        features = ['25' if supermode else '21']
        if sys.platform not in ('win32',):
            raise RuntimeError('VM Protect mode only works for Windows')
        for platid in platforms:
            if not platid.starswith('windows'):
                raise RuntimeError('VM Protect mode only works for Windows')
            nlist = platid.split('.')
            if len(nlist) > 2:
                raise RuntimeError('Invalid platform name for VM mode')
        if not len(platforms):
            platforms = [_format_platid()]
    elif supermode:
        features = ['11' if (fn1 & FEATURE_JIT) else '8']
        if not len(platforms):
            v = 'py%d%d' % sys.version_info[:2]
            platforms = ['.'.join([_format_platid(), features[0], v])]

    result = []
    for name in platforms:
        platid = _get_preferred_platid(name, features=features)
        if platid is None:
            msg = 'default' if features is None else features
            raise RuntimeError('No available dynamic library for %s '
                               'with features %s' % (name, msg))
        result.append(platid)

    reboot = None
    if result and not (os.path.isabs(result[0]) or os.path.isfile(result[0])):
        platid = result[0]
        nlist = platid.split('.')
        fn2 = int(nlist[2])
        if fn2 in (21, 25):
            n = 21
        elif fn2 in (0, 8):
            n = 0
        else:
            n = 7
        if (n != fn1) and not (n & fn1 & 0x12):
            reboot = '.'.join([_format_platid(), str(n)])
            os.environ['PYARMOR_PLATFORM'] = reboot

        logging.info('Update target platforms to: %s', result)
        for p in result[1:]:
            fn3 = int(p.split('.')[2])
            if (n != fn3) and not (n & fn3):
                raise RuntimeError('Multi platforms conflict, platform %s'
                                   ' could not mixed with %s' % (p, platid))

    if reboot:
        logging.info('====================================================')
        logging.info('Reload PyArmor with platform: %s', reboot)
        logging.info('====================================================')
        pytransform_bootstrap(force=True)
        # _reboot_pytransform(reboot)
        # return False

    return result


def compatible_platform_names(platforms):
    '''Only for compatibility, it may be removed in next major version.'''
    if not platforms:
        return platforms

    old_forms = {
        'armv5': 'linux.arm',
        'ppc64le': 'linux.ppc64',
        'ios.arm64': 'darwin.arm64',
        'freebsd': 'freebsd.x86_64',
        'alpine': 'musl.x86_64',
        'alpine.arm': 'musl.arm',
        'alpine.x86_64': 'musl.x86_64',
        'poky-i586': 'poky.x86',
    }

    result = []
    for names in platforms:
        for name in names.split(','):
            name = name.strip()
            if name in old_forms:
                logging.warning(
                    'This platform name `%s` has been deprecated, '
                    'use `%s` instead. Display all standard platform '
                    'names by `pyarmor download --help-platform`',
                    name, old_forms[name])
                result.append(old_forms[name])
            else:
                result.append(name)
    return result


def make_bootstrap_script(output, capsule=None, relative=None, suffix=''):
    filename = os.path.basename(output)
    co = compile('', filename, 'exec')
    flags = 0x18000000
    prokey = get_product_key(capsule)
    buf = pytransform.encrypt_code_object(prokey, co, flags, suffix=suffix)
    with open(output, 'w') as f:
        f.write(buf.decode())
    _make_entry(output, relative=relative, suffix=suffix)


def get_name_suffix():
    rcode = get_registration_code()
    if rcode is None:
        return ''

    m, n = rcode.replace('-sn-1.txt', '').split('-')[-2:]
    d = {
        'vax': 'vax',
        'clickbank': 'vac',
        'shareit': 'vas',
        'regnow': 'var',
        'Pyarmor': 'vad',
    }
    if len(n) > 6:
        n = n[-6:]
    pad = '0' * (6 - len(n))
    return '_'.join(['', d.get(m, 'unk'), pad + n])


def get_bind_key(filename):
    if not os.path.exists(filename):
        raise RuntimeError('Bind file %s not found' % filename)

    with open(filename, 'rb') as f:
        buf = f.read()
    size = len(buf) >> 2
    fmt = 'I' * size
    return sum(struct.unpack(fmt, buf[:size*4]))


def make_super_bootstrap(source, filename, output, relative=None, suffix=''):
    pkg = os.path.basename(filename) == '__init__.py'
    level = ''
    if (relative is True) or ((relative is None) and pkg):
        n = len(filename[len(output)+1:].replace('\\', '/').split('/'))
        level = '.' * n
    bootstrap = 'from %spytransform%s import pyarmor\n' % (level, suffix)

    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith(bootstrap):
            return

    lines.insert(0, bootstrap)

    shell = _get_script_shell(source)
    if shell:
        lines.insert(0, shell)

    with open(filename, 'w') as f:
        f.write(''.join(lines))


def _patch_extension(filename, keylist, suffix=''):
    logging.debug('Patching %s', relpath(filename))
    patkey = b'\x60\x70\x00\x0f'
    patlen = len(patkey)
    sizelist = [len(x) for x in keylist]
    big_endian = False

    def write_integer(data, offset, value):
        if big_endian:
            offset += 3
            step = -1
        else:
            step = 1
        for i in range(4):
            data[offset] = value & 0xFF
            offset += step
            value >>= 8

    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    n = len(data)
    for i in range(n):
        if data[i:i+patlen] == patkey:
            fmt = 'I' * 8
            header = struct.unpack(fmt, bytes(data[i:i+32]))
            if sum(header[2:]) not in (912, 1452):
                continue
            logging.debug('Found pattern at %x', i)
            max_size = header[1]
            if sum(sizelist) > max_size:
                raise RuntimeError('Too much license data')

            break
    else:
        # Maybe big endian
        patkey = b'\x0f\x00\x70\x60'
        for i in range(n):
            if data[i:i+patlen] == patkey:
                fmt = 'I' * 8
                header = struct.unpack('>' + fmt, bytes(data[i:i+32]))
                if sum(header[2:]) not in (912, 1452):
                    continue
                logging.debug('Found pattern at %x', i)
                max_size = header[1]
                if sum(sizelist) > max_size:
                    raise RuntimeError('Too much license data')
                big_endian = True
                break
        else:
            raise RuntimeError('Invalid extension, no data found')

    write_integer(data, i + 12, sizelist[0])
    write_integer(data, i + 16, sizelist[0])
    write_integer(data, i + 20, sizelist[1])
    write_integer(data, i + 24, sizelist[0] + sizelist[1])
    write_integer(data, i + 28, sizelist[2])

    offset = i + 32
    for j in range(3):
        size = sizelist[j]
        if size:
            logging.debug('Patch %d bytes from %x', size, offset)
            data[offset:offset+size] = keylist[j]
            offset += size

    logging.info('Patch library file OK')

    if suffix:
        marker = bytes(b'_vax_000000')
        k = len(marker)
        for i in range(n):
            if data[i:i+k] == marker:
                logging.debug('Found marker at %x', i)
                data[i:i+k] = bytes(suffix.encode())

    return data


def _build_keylist(capsule, licfile):
    myzip = ZipFile(capsule, 'r')
    if 'pytransform.key' not in myzip.namelist():
        raise RuntimeError('No pytransform.key found in capsule')
    logging.info('Extract pytransform.key')
    keydata = myzip.read('pytransform.key')
    myzip.close()

    lickey = _build_license_file(capsule, licfile)

    if sys.version_info[0] == 2:
        size1 = ord(keydata[0]) + ord(keydata[1]) * 256
        size2 = ord(keydata[2]) + ord(keydata[3]) * 256
    else:
        size1 = keydata[0] + keydata[1] * 256
        size2 = keydata[2] + keydata[3] * 256

    k1 = 16
    k2 = k1 + size1

    return keydata[k1:k2], keydata[k2:k2+size2], lickey


def _make_super_runtime(capsule, output, platforms, licfile=None, suffix=''):
    logging.info('Generating super runtime library to %s', relpath(output))
    if not os.path.exists(output):
        os.makedirs(output)

    if not platforms:
        raise RuntimeError('No platform specified in Super mode')
    elif len(platforms) == 1:
        filelist = _build_platforms(platforms)[:1]
    else:
        filelist = _build_platforms(platforms)

    keylist = _build_keylist(capsule, licfile)
    namelist = []
    checklist = []
    for filename in filelist:
        logging.info('Copying %s', filename)

        name = os.path.basename(filename)
        if suffix:
            k = name.rfind('pytransform') + len('pytransform')
            name = name[:k] + suffix + name[k:]
            logging.info('Rename extension to %s', name)
        if name in namelist:
            raise RuntimeError('Multiple platforms confilt with '
                               'same extension name "%s"' % name)
        namelist.append(name)

        target = os.path.join(output, name)
        shutil.copy2(filename, target)

        logging.info('Patch extension %s', target)
        data = _patch_extension(target, keylist, suffix)

        with open(target, 'wb') as f:
            f.write(data)
        checklist.append(sum(bytearray(data)))

    logging.info('Generate runtime files OK')
    return checklist


def _make_protection_code2(relative, checklist, suffix=''):
    template = os.path.join(PYARMOR_PATH, protect_code_template % '2')
    logging.info('Use protection template: %s', relpath(template))
    with open(template) as f:
        buf = f.read()

    return buf.format(relative='from . ' if relative else '',
                      checklist=checklist, suffix=suffix)


def make_protection_code(args, multiple=False, supermode=False):
    return _make_protection_code2(*args) if supermode \
        else _make_protection_code(*args, multiple=multiple)


def _check_code_object_for_super_mode(co, lines, name):
    from dis import hasjabs, hasjrel, get_instructions
    HEADER_SIZE = 8
    hasjins = hasjabs + hasjrel

    def is_special_code_object(co):
        has_special_jabs = False
        has_header_label = True if co.co_code[6:7] == b'\x90' else False
        for ins in get_instructions(co):
            if ins.opcode in hasjabs and \
               (ins.arg & ~0xF) in (0xF0, 0xFFF0, 0xFFFFF0):
                has_special_jabs = True
            if has_header_label:
                if has_special_jabs:
                    return True
                continue
            if ins.offset < HEADER_SIZE:
                if ins.is_jump_target or ins.opcode in hasjins:
                    has_header_label = True
            elif not has_header_label:
                break

    def check_code_object(co):
        co_list = [co] if is_special_code_object(co) else []
        for obj in [x for x in co.co_consts if hasattr(x, 'co_code')]:
            co_list.extend(check_code_object(obj))
        return co_list

    co_list = check_code_object(co)
    if co_list:
        pat = re.compile(r'^\s*')
        for c in co_list:
            # In some cases, co_lnotab[1] is not the first statement
            i = c.co_firstlineno - 1
            k = i + c.co_lnotab[1]
            while i < k:
                s = lines[i].strip()
                if s.endswith('):') or (s.endswith(':') and s.find('->') > -1):
                    break
                i += 1
            else:
                logging.error('Function does not end with "):"')
                raise RuntimeError('Patch function "%s" failed' % c.co_name)
            i += 1
            docs = c.co_consts[0]
            n_docs = len(docs.splitlines()) if isinstance(docs, str) else 0
            while i < k:
                if lines[i].strip():
                    if n_docs:
                        i += n_docs
                        n_docs = 0
                        continue
                    break
                i += 1
            logging.info('\tPatch function "%s" at line %s', c.co_name, i + 1)
            s = lines[i]
            indent = pat.match(s).group(0)
            lines[i] = '%s[None, None]\n%s' % (indent, s)
        co = compile(''.join(lines), name, 'exec')

    return co


if __name__ == '__main__':
    make_entry(sys.argv[1])
