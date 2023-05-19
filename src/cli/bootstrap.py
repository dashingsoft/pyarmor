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

from subprocess import check_output, Popen, PIPE


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
        raise RuntimeError('current user has no permission')

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


def main(path):
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
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


if __name__ == '__main__':
    main(os.path.abspath(os.path.dirname(__file__)))
