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

    def process(self):
        logger.info('search inputs ...')
        self.prepare(self.ctx.input_paths)
        logger.info('find %d top resources', len(self.ctx.resources))


class Builder(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def format_output(self, outputs, count=0):
        try:
            output = outputs[count]
        except IndexError:
            output = self.ctx.alias_suffix.format(outputs[0], count)
        return output

    def generate_runtime_key(self, outer=False):
        return Pytransform3.generate_runtime_key(self.ctx, outer)

    def generate_runtime_package(self, output):
        self.ctx.runtime_key = Pytransform3.generate_runtime_key(self.ctx)
        Pytransform3.generate_runtime_package(self.ctx, output)

    def _obfuscate_scripts(self):
        rev = self.ctx.version_info(verbose=2)
        template = self.ctx.bootstrap_template
        relative = self.ctx.relative_import
        pkgname = self.ctx.runtime_package + self.ctx.runtime_suffix
        bootpath = self.ctx.cfg.get('builder', 'bootstrap_file')

        namelist = []
        for res in self.ctx.resources:
            logger.info('process script "%s"', res.fullname)
            name = res.name
            path = self.format_output(self.ctx.outputs, namelist.count(name))
            namelist.append(name)
            os.makedirs(path, exist_ok=True)

            for r in res:
                if not res.is_script():
                    logger.info('copy data file %s', res.path)
                    shutil.copy2(res.path, path)
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

    def process(self, options, no_runtime=False, pack=False):
        for opt in options['inputs']:
            if not os.path.exists(opt):
                raise CliError('no found input "%s"' % opt)
        self.ctx.input_paths = options['inputs']

        output = options.get('output', 'dist')
        self.ctx.outputs = output.split(',')

        finder = Finder(self.ctx)
        finder.process()

        if self.ctx.enable_refactor:
            Pytransform3.refactor_preprocess(self.ctx)

        self.ctx.runtime_key = Pytransform3.generate_runtime_key(self.ctx)
        if not no_runtime:
            logger.info('start to generate runtime files')
            self.generate_runtime_package(self.ctx.outputs[0])
            logger.info('generate runtime files OK')

        logger.info('start to obfuscate scripts')
        self._obfuscate_scripts()
        logger.info('obfuscate scripts OK')

        if self.ctx.enable_refactor:
            Pytransform3.refactor_postprocess(self.ctx)

        if pack:
            pass
