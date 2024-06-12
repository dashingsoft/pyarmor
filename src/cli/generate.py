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
import os
import shutil

from . import logger, CliError
from .core import Pytransform3
from .resource import FileResource, PathResource


class Finder(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def _build_resource(self, pathlist):
        resources = []
        for path in pathlist:
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
        return resources

    def prepare(self, input_paths):
        self.ctx.resources = self._build_resource(input_paths)

    def process_extra(self, contents):
        extra_paths = [x for x in contents if x.endswith('.pyc')]
        for pyz in [x for x in contents if x.endswith('.pyz_extracted')]:
            extra_paths.extend([os.path.join(pyz, x) for x in os.listdir(pyz)])
        resnames = [x.pkgname for x in self.ctx.resources]
        for res in self._build_resource(extra_paths):
            if res.pkgname not in resnames:
                self.ctx.obfuscated_modules.add(res.pkgname)
                self.ctx.extra_resources.append(res)

    def append(self, resources):
        resnames = [x.pkgname for x in self.ctx.resources]
        for res in self._build_resource(resources):
            if res.pkgname not in resnames:
                self.ctx.obfuscated_modules.add(res.pkgname)
                self.ctx.resources.append(res)

    def process(self):
        logger.info('search inputs ...')
        self.prepare(self.ctx.input_paths)
        logger.info('find %d top resources', len(self.ctx.resources))

        modules = [x.fullname for res in self.ctx.resources for x in res
                   if x.is_script()]
        self.ctx.obfuscated_modules.update(modules)


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

    def _generate_obfuscated_script(self, res):
        try:
            return Pytransform3.generate_obfuscated_script(self.ctx, res)
        except RuntimeError as e:
            if str(e) != 'out of license':
                raise

    def _copy_script(self, path, res):
        logger.warning('%s is not obfuscated because out of license', res)
        fullpath = os.path.join(path, res.output_filename)
        output = os.path.dirname(fullpath)
        os.makedirs(output, exist_ok=True)
        logger.info('write %s (not obfuscated)', fullpath)
        shutil.copy2(res.fullpath, output)

    def _obfuscate_scripts(self):
        rev = self.ctx.version_info()
        template = self.ctx.bootstrap_template
        relative = self.ctx.import_prefix
        pkgname = self.ctx.runtime_package_name
        bootpath = self.ctx.cfg.get('builder', 'bootstrap_file')
        encoding = self.ctx.cfg.get('builder', 'encoding')

        plugins = [x for x in self.ctx.plugins if hasattr(x, 'post_script')]

        namelist = []
        for res in self.ctx.resources + self.ctx.extra_resources:
            logger.info('process resource "%s"', res.fullname)
            name = res.name
            path = self.format_output(self.ctx.outputs, namelist.count(name))
            namelist.append(name)
            os.makedirs(path, exist_ok=True)

            for r in res:
                if not r.is_script():
                    logger.info('copy data file %s', r.fullpath)
                    data_path = os.path.join(path, r.output_path)
                    os.makedirs(data_path, exist_ok=True)
                    shutil.copy2(r.fullpath, data_path)
                    continue

                logger.info('obfuscating %s', r)
                code = Pytransform3.generate_obfuscated_script(self.ctx, r)
                source = r.generate_output(
                    template, code, relative=relative, pkgname=pkgname,
                    bootpath=bootpath, rev=rev
                )

                fullpath = os.path.join(path, r.output_filename)
                os.makedirs(os.path.dirname(fullpath), exist_ok=True)

                for plugin in plugins:
                    patched_source = plugin.post_script(self.ctx, r, source)
                    if patched_source:
                        source = patched_source

                logger.info('write %s', fullpath)
                with open(fullpath, 'w', encoding=encoding) as f:
                    f.write(source)

    def process(self, options, packer=None):
        for opt in options['inputs']:
            if not os.path.exists(opt):
                raise CliError('no found input "%s"' % opt)
        self.ctx.input_paths = options['inputs']

        output = options.get('output', 'dist')
        self.ctx.outputs = output.split(',')

        finder = Finder(self.ctx)
        finder.process()

        if packer and hasattr(packer, 'analysis'):
            auto_resources = packer.analysis()
            logger.info('find extra resources: %s', auto_resources)
            finder.append(auto_resources)

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
