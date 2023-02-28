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
#      Version: 8.0.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/generate.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: 2022-12-06
#
import logging
import os
import shutil

from .errors import CliError
from .core import Pytransform3
from .resource import FileResource, PathResource

logger = logging.getLogger('Builder')


class Finder(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def prepare(self, input_paths):
        resources = []
        for path in input_paths:
            if not os.path.exists(path):
                raise CliError('argument "%s" doesn\'t exists' % path)
            if os.path.isfile(path):
                logger.info('find script %s', path)
                res = FileResource(path)
                resources.append(res)
            else:
                logger.info('find package at %s', path)
                res = PathResource(path)
                resources.append(res)
                options = self.ctx.get_res_options(res.fullname)
                res.rebuild(**options)
        self.ctx.resources = resources

    def process(self, pack=None):
        logger.info('search inputs ...')
        self.prepare(self.ctx.input_paths)
        logger.info('find %d top resources', len(self.ctx.resources))

        modules = [x.fullname for res in self.ctx.resources for x in res
                   if x.is_script()]
        self.ctx.obfuscated_modules.update(modules)

        # TBD: implement it in next Release
        # if pack:
        #     from .repack import list_modules
        #     self.ctx.obfuscated_modules.update(list_modules(pack))


class Builder(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def format_output(self, outputs, count=0):
        try:
            output = outputs[count]
        except IndexError:
            output = self.ctx.alias_suffix.format(outputs[0], count)
        return output

    def generate_runtime_key(self, outer=None):
        return Pytransform3.generate_runtime_key(self.ctx, outer)

    def generate_runtime_package(self, output):
        if self.ctx.runtime_key is None:
            self.ctx.runtime_key = self.generate_runtime_key()
        Pytransform3.generate_runtime_package(self.ctx, output)

    def _pack_script(self, bundle, output, entry=None, codesign=None):
        from .repack import repacker
        build = os.path.join('.pyarmor', 'build')
        repacker(bundle, output, build, entry=entry, codesign=codesign)
        shutil.rmtree(build)

    def _obfuscate_scripts(self):
        rev = self.ctx.version_info(verbose=2)
        template = self.ctx.bootstrap_template
        relative = self.ctx.import_prefix
        pkgname = self.ctx.runtime_package + self.ctx.runtime_suffix
        bootpath = self.ctx.cfg.get('builder', 'bootstrap_file')

        namelist = []
        for res in self.ctx.resources:
            logger.info('process resource "%s"', res.fullname)
            name = res.name
            path = self.format_output(self.ctx.outputs, namelist.count(name))
            namelist.append(name)
            os.makedirs(path, exist_ok=True)

            for r in res:
                if not r.is_script():
                    logger.info('copy data file %s', r.path)
                    shutil.copy2(r.path, path)
                    continue

                logger.info('obfuscating %s', r)
                code = Pytransform3.generate_obfuscated_script(self.ctx, r)
                source = r.generate_output(
                    template, code, relative=relative, pkgname=pkgname,
                    bootpath=bootpath, rev=rev
                )

                fullpath = os.path.join(path, r.output_filename)
                os.makedirs(os.path.dirname(fullpath), exist_ok=True)

                logger.info('write %s', fullpath)
                with open(fullpath, 'w') as f:
                    f.write(source)

    def process(self, options, pack=None):
        for opt in options['inputs']:
            if not os.path.exists(opt):
                raise CliError('no found input "%s"' % opt)
        self.ctx.input_paths = options['inputs']

        output = options.get('output', 'dist')
        self.ctx.outputs = output.split(',')

        finder = Finder(self.ctx)
        finder.process(pack=pack)

        Pytransform3.pre_build(self.ctx)

        self.ctx.runtime_key = self.generate_runtime_key()

        if not options.get('no_runtime'):
            logger.info('start to generate runtime files')
            self.generate_runtime_package(self.ctx.outputs[0])
            logger.info('generate runtime files OK')

        logger.info('start to obfuscate scripts')
        self._obfuscate_scripts()
        logger.info('obfuscate scripts OK')

        Pytransform3.post_build(self.ctx)

        if pack:
            self._pack_script(pack, output)
