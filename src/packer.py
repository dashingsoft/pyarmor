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
#      Version: 4.3.2 -                                     #
#                                                           #
#############################################################
#
#
#  @File: packer.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2018/11/08
#
#  @Description:
#
#   Pack obfuscated Python scripts with any of third party
#   tools: py2exe, py2app, cx_Freeze, PyInstaller
#

import logging
import os
import shutil
import subprocess
import sys
import time

from distutils.util import get_platform
from zipfile import PyZipFile

try:
    import argparse
except ImportError:
    # argparse is new in version 2.7
    import polyfills.argparse as argparse

try:
    from pyarmor import main as call_armor
except ImportError:
    from pyarmor.pyarmor import main as call_armor

def armorcommand(func):
    def wrap(*args, **kwargs):
        old = os.getcwd()
        os.chdir(os.path.dirname(__file__))
        try:
            return func(*args, **kwargs)
        finally:
            os.chdir(old)
    return wrap

@armorcommand
def _packer(src, entry, setup, packcmd, dist, libname):
    dest = os.path.dirname(setup)
    script = os.path.basename(setup)

    output = os.path.join(dest, dist)
    project = os.path.join('projects', 'build-for-packer')

    options = 'init', '--type', 'app', '--src', src, '--entry', entry, project
    call_armor(options)

    filters = ('global-include *.py', 'prune build, prune dist',
               'exclude %s %s pytransform.py' % (entry, script))
    options = ('config', '--runtime-path', '',  '--disable-restrict-mode', '1',
               '--manifest', ','.join(filters), project)
    call_armor(options)

    options = 'build', '--no-runtime', project
    call_armor(options)

    shutil.copy('pytransform.py', src)
    shutil.copy(os.path.join(src, entry), '%s.bak' % entry)
    shutil.move(os.path.join(project, 'dist', entry), src)

    p = subprocess.Popen([sys.executable, script, packcmd], cwd=dest)
    p.wait()
    shutil.move('%s.bak' % entry, os.path.join(src, entry))

    with ZipFile(os.path.join(output, libname), 'a') as f:
        f.writepy(os.path.join(project, 'dist'))

    options = 'build', '--only-runtime', '--output', 'runtimes', project
    call_armor(options)

    for s in os.listdir(os.path.join(project, 'runtimes')):
        if s == 'pytransform.py':
            continue
        shutil.copy(os.path.join(project, 'runtimes', s), output)

def packer(args):
    bintype = 'freeze' if args.type.lower().endswith('freeze') else 'py2exe'

    src = os.path.dirname(args.entry) if args.path is None else args.path
    entry = os.path.basename(args.entry) if args.path is None \
        else os.path.relpath(args.entry, args.path)
    setup = os.path.join(src, 'setup.py') if args.setup is None else args.setup

    dist = os.path.join(
        'build', 'exe.%s-%s' % (get_platform(), sys.version[0:3])
    ) if bintype == 'freeze' else 'dist'

    packcmd = 'py2exe' if bintype == 'py2exe' else 'build'
    libname = 'library.zip' if bintype == 'py2exe' else \
        'python%s%s.zip' % sys.version_info[:2]

    _packer(src, entry, setup, packcmd, dist, libname)

def main(args):
    parser = argparse.ArgumentParser(
        prog='packer.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Pack obfuscated scripts',
        epilog=__doc__,
    )
    parser.add_argument('-v', '--version', action='version', version='v0.1')

    parser.add_argument('-t', '--type', default='py2exe',
                        choices=('py2exe', 'py2app', 'cx_Freeze', 'PyInstaller'))
    parser.add_argument('-p', '--path', help='Source path of Python scripts')
    parser.add_argument('-s', '--setup', help='Setup script')
    parser.add_argument('entry', metavar='Script', nargs=1, help='Entry script')

    parser.set_defaults(func=packer)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main(sys.argv[1:])
