#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2023 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      Pyarmor                                              #
#                                                           #
#      Version: 8.2.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor/cli/bootstrap.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Fri Apr 14 17:43:59 CST 2023
#
import logging
import os
import shutil
import sys

from subprocess import check_output, check_call, Popen, PIPE


def check_prebuilt_runtime_library(platnames, extra=None, rtver=''):
    pkgpath = os.path.normpath(os.path.dirname(__file__))
    corepath = os.path.join(pkgpath, 'core')
    if not os.path.exists(corepath):
        raise RuntimeError('no found "{0}", please run "pip install {0}" to '
                           'install it'.format('pyarmor.cli.core'))

    instcmd = [sys.executable, '-m', 'pip', 'install',
               '--disable-pip-version-check']

    # Before Pyarmor 8.3, prefer to "pyarmor.cli.runtime"
    # It could be disabled by
    #     pyarmor cfg pyarmor:cli.runtime = false
    if rtver.find('.') > 0:
        runtime_pkgpath = os.path.join(pkgpath, 'runtime')
        if os.path.exists(runtime_pkgpath):
            from pyarmor.cli.runtime import __VERSION__ as current_rtver
            if current_rtver == rtver:
                return

        pkgver = 'pyarmor.cli.runtime~=%s' % rtver
        logging.info('install "%s" for cross platforms', pkgver)
        try:
            return check_call(instcmd + [pkgver])
        except Exception:
            logging.warning('failed to install "%s"' % pkgver)

    # From Pyarmor 8.3, prefer to "pyarmor.cli.core.PLATFORM"
    from pyarmor.cli.core import __VERSION__ as corever

    pkgnames = set(extra if isinstance(extra, list) else
                   [extra] if isinstance(extra, str) else
                   ['themida'] if extra else [])
    if platnames:
        for plat in platnames:
            pkgnames.add(plat.split('.')[0])

    for entry in os.scandir(corepath):
        if entry.name in pkgnames:
            m = __import__('pyarmor.cli.core.' + entry.name,
                           globals(), locals(),
                           ['__VERSION__'], 0)
            if getattr(m, '__VERSION__', None) == corever:
                pkgnames.remove(entry.name)

    if pkgnames:
        pkgvers = ['pyarmor.cli.core.%s~=%s' % (x, corever) for x in pkgnames]
        logging.info('install packages %s for cross platforms', str(pkgvers))
        try:
            check_call(instcmd + pkgvers)
        except Exception as e:
            logging.error('%s', e)
            raise RuntimeError('failed to install runtime packages')


def _shell_cmd(cmdlist):
    logging.info('run: %s', ' '.join(cmdlist))
    p = Popen(cmdlist, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return p.returncode, stderr


def _check_extension(fullpath):
    if not os.path.exists(fullpath):
        logging.error('please re-install pyarmor.cli.core to fix this problem')
        raise RuntimeError('no found extension "%s"' % fullpath)


def _fixup_darwin_rpath(fullpath, pyver):
    output = check_output(['otool', '-L', sys.executable])
    for line in output.splitlines():
        if line.find(b'Frameworks/Python.framework/Versions') > 0:
            pydll = line.split()[0].decode()
            logging.info('found CPython library "%s"', pydll)
            break

        if line.find(('libpython' + pyver).encode('utf-8')) > 0:
            pydll = line.split()[0].decode()
            logging.info('found CPython library "%s"', pydll)
            break
    else:
        raise RuntimeError('no found CPython library')

    # old = '@rpath/Frameworks/Python.framework/Versions/%s/Python' % pyver
    old = '@rpath/lib/libpython%s.dylib' % pyver
    cmdlist = ['install_name_tool', '-change', old, pydll, fullpath]
    rc, err = _shell_cmd(cmdlist)
    if rc:
        raise RuntimeError('install_name_tool failed (%d): %s' % (rc, err))

    identity = '-'
    cmdlist = ['codesign', '-s', identity, '--force',
               '--all-architectures', '--timestamp', fullpath]
    rc, err = _shell_cmd(cmdlist)
    if rc:
        raise RuntimeError('codesign failed (%d): %s' % (rc, err))


def _fixup_darwin(path, filename, pyver):
    fullpath = os.path.join(path, filename)
    _check_extension(fullpath)

    if not os.access(path, os.W_OK):
        logging.error('please run Python with super user or anyone who has'
                      'write permission on path "%s"', path)
        raise RuntimeError('current user has no write permission')

    backup = fullpath + '.bak'
    if os.path.exists(backup):
        logging.info('create backup file "%s"', backup)
        shutil.copy2(fullpath, backup)

    try:
        logging.info('start to fixup extension "%s"', fullpath)
        _fixup_darwin_rpath(fullpath, pyver)

        logging.info('fixup extension "pytransform3" successfully')
        logging.info('try command ``pyarmor gen foo.py`` to make sure '
                     'it works')
        logging.info('if something is wrong, please restore it from '
                     'backup file')
    except Exception:
        logging.error('fixup extension "pytransform3" failed')
        shutil.move(backup, fullpath)
        raise


def _fixup_linux(path, filename, pyver):
    fullpath = os.path.join(path, filename)
    _check_extension(fullpath)

    rc = _shell_cmd(['ldd', fullpath])
    if rc:
        logging.info('try to install package "libpython%s" to fix it' % pyver)
    else:
        logging.info('nothing to do in this platform')


def _fixup_windows(path, filename, pyver):
    fullpath = os.path.join(path, filename)
    _check_extension(fullpath)
    logging.info('nothing to do in this platform')


def auto_fix(path):
    '''Deprecated since Pyarmor 8.3.0'''
    pyver = '%s.%s' % sys.version_info[:2]
    plat = sys.platform.lower()

    if plat.startswith('darwin'):
        _fixup_darwin(path, 'pytransform3.so', pyver)

    elif plat.startswith('win'):
        _fixup_windows(path, 'pytransform3.pyd', pyver)

    elif plat.startswith('linux'):
        _fixup_windows(path, 'pytransform3.so', pyver)

    else:
        logging.info('nothing to fixup in this platform "%s"', plat)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )

    logging.info('Python: %d.%d', *sys.version_info[:2])
    corepath = os.path.join(os.path.dirname(__file__), 'core')
    logging.info('pyarmor.cli.core: %s', corepath)
    # auto_fix(corepath)
    logging.warning('this feature has been deprecated since Pyarmor 8.3.0')
    logging.info('nothing to do')


if __name__ == '__main__':
    main()
