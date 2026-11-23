#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2026 Dashingsoft corp.                   #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 9.4.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor/cli/packer.py
#
#  @Author: Jondy Zhao(pyarmor@163.com)
#
#  @Create Date: Mon Nov 23 09:11:59 2026
#

import logging
import marshal
import os
import shutil
import sys

from fnmatch import fnmatch
from subprocess import check_call, DEVNULL

logger = logging.getLogger('packer')


def autoclean_output(output, autoclean=True):
    if os.path.exists(output) and autoclean:
        n = len(os.path.abspath(output).split(os.sep))
        if n < 3:
            prompt = 'Are you sure to remove path "%s" (y/n)? '
            choice = input(prompt % output).lower()[:1]
            if not choice == 'y':
                return
        logger.info('clean output path "%s"', output)
        shutil.rmtree(output)


SPEC_PATCH_CODE = '''
import marshal
import os

from PyInstaller.compat import base_prefix, EXTENSION_SUFFIXES
from sys import prefix, exec_prefix
from fnmatch import fnmatch

exlist = set([base_prefix, prefix, exec_prefix])
expats = [os.path.join(os.path.normpath(x), '*') for x in exlist]

src = {src!r}
resfile = {resfile!r}
hookscript = {hookscript!r}

nsrc = len(src) + 1
rsrc = os.path.relpath(src)
rsrc = '' if rsrc == '.' else rsrc
psrc = os.path.join(src, '*')

hiddenimports = set([])
plist = set([])
mlist = []

for name, path, kind in a.pure:
    if name.startswith('pyi_rth'):
        continue
    hiddenimports.add(name)
    if fnmatch(path, psrc) and not any([fnmatch(path, x) for x in expats]):
        if name.find('.') == -1 and os.path.basename(path) != '__init__.py':
            mlist.append(os.path.join(rsrc, path[nsrc:]))
        else:
            pkgname = os.path.dirname(path[nsrc:]).split(os.sep)[0]
            plist.add(os.path.join(rsrc, pkgname))

for name, path, kind in a.binaries:
    if kind == 'EXTENSION':
        for x in EXTENSION_SUFFIXES:
            if fnmatch(name, '*' + x):
                name = name[:-len(x)]
                break
        hiddenimports.add(name.replace(os.sep, '.'))

with open(resfile, 'wb') as f:
    marshal.dump(mlist + list(plist), f)
with open(hookscript, 'w', encoding='utf-8') as f:
    f.write("hiddenimports=[%s]" % ", ".join([repr(x) for x in hiddenimports]))
'''


class Packer:
    """Pack obfuscated scripts for Pyarmor 9.

    Args:
        project: Project object
        mode: onefile or onedir
        output: final output path
    """

    def __init__(self, project, mode, output):
        self.project = project
        self.ctx = project.ctx
        self.output = output if output else 'dist'

        if mode is None:
            def do_nothing(*args, **kwargs): pass
            self.analysis = do_nothing
            self.build = do_nothing
            self.obfpath = self.output
            return

        self.script = project.scripts[0]
        self.name = os.path.splitext(os.path.basename(self.script))[0]
        self.obfpath = os.path.normpath(self.ctx.pack_obfpath)
        self.packpath = os.path.normpath(self.ctx.pack_basepath)
        self.workpath = os.path.join(self.packpath, 'build')

        self.pyicmd = [sys.executable, '-m', 'PyInstaller']
        self.autoclean = mode in ('FC', 'DC')
        self.modeopt = '-F' if mode in ('onefile', 'F', 'FC') else '-D'
        self._init_opts()

    def _init_opts(self):
        self.pyiopts = []

        opts = self.project.pack_options
        exopts = '--noconfirm', '-y', '--onefile', '-F', '--onedir', '-D'
        exvalues = '--distpath', '--specpath', '--workpath'

        n = 0
        while n < len(opts):
            x = opts[n]
            if x in ('--name', '-n'):
                self.name = opts[n+1]

            if x in ('--noconfirm', '-y'):
                self.autoclean = True

            if x in exvalues:
                n += 1
            elif x not in exopts:
                self.pyiopts.append(x)
            n += 1

    def analysis(self):
        """Got imported modules and packages by PyInstaller

        Generate hook script
        Return file/dir list need to be obfuscated
        """
        cmdspec = [sys.executable, '-m', 'PyInstaller.utils.cliutils.makespec']
        cmdspec.extend(self.pyiopts)
        cmdspec.append(self.script)
        logger.debug('%s', ' '.join(cmdspec))
        logger.info('call PyInstaller to generate specfile')
        check_call(cmdspec, stdout=DEVNULL, stderr=DEVNULL)

        specfile = self.name + '.spec'
        rtname = self.ctx.runtime_package_name
        resfile = os.path.join(self.packpath, 'resources.list')
        hookscript = os.path.join(self.packpath, 'hook-%s.py' % rtname)
        self._patch_specfile(specfile, hookscript, resfile)

        cmdlist = self.pyicmd + ['--clean', '--workpath', self.workpath]
        cmdlist.append(specfile)
        logger.debug('%s', ' '.join(cmdlist))
        logger.info('call PyInstaller to analysis, '
                    'it may take several minutes ...')
        check_call(cmdlist, stdout=DEVNULL, stderr=DEVNULL)

        with open(resfile, 'rb') as f:
            reslist = marshal.load(f)

        return reslist

    def build(self):
        """Generate final bundle to output"""
        obfscript = os.path.join(self.obfpath, os.path.basename(self.script))
        cmdlist = self.pyicmd + [
            '--clean',
            '--distpath', self.output,
            '--workpath', self.workpath,
            '--additional-hooks-dir', self.packpath,
            self.modeopt
        ]
        cmdlist.extend(self.pyiopts)
        cmdlist.append(obfscript)

        logger.debug('%s', ' '.join(cmdlist))
        logger.info('call PyInstaller to generate final bundle ...\n')
        check_call(cmdlist)
        logger.info('')
        logger.info('the final bundle has been generated to "%s" successfully',
                    self.output)

    def _patch_specfile(self, specfile, hookscript, resfile):
        lines = []
        with open(specfile, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('pyz = PYZ'):
                    break
                lines.append(line)
            else:
                logger.error('no found line starts with "pyz = PYZ"')
                raise RuntimeError('unsupported specfile "%s"' % specfile)

        lines.append(SPEC_PATCH_CODE.format(
            src=os.path.abspath(os.path.dirname(self.script)),
            hookscript=os.path.abspath(hookscript),
            resfile=os.path.abspath(resfile)))

        with open(specfile, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))

    def _check(self):
        autoclean_output(self.output, self.autoclean)
