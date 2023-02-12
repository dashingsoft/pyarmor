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
#  @File: cli/finder.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: 2022-12-06
#
#
import os
import logging

from .errors import CliError
from .resource import FileResource, PathResource


logger = logging.getLogger('Finder')


class Finder(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def prepare(self, input_paths, recursive=False):
        resources = []
        pyexts = self.ctx.pyexts
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
                res.rebuild(recursive, pyexts)
        self.ctx.resources = resources

    def process(self):
        logger.info('search inputs ...')

        logger.debug('recursive mode is %s', self.ctx.recursive)
        logger.debug('find-all mode is %s', self.ctx.findall)
        logger.debug('exts are %s', self.ctx.pyexts)
        self.prepare(self.ctx.input_paths, self.ctx.recursive)

        self.ctx.obfucated_modules = [x.fullname for x in self.ctx.resources]
        logger.info('find %d top resources', len(self.ctx.resources))
