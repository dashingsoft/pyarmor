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
#  @File: cli/plugin.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Fri Apr 21 18:42:14 CST 2023
#
import os

from importlib.util import spec_from_file_location, module_from_spec

from . import logger


__all__ = []


class Plugin(object):

    def __init__(self, ctx=None):
        self.ctx = ctx

    @staticmethod
    def install(ctx, pkg='pyarmor.cli.plugin'):

        for pname in ctx.cfg['builder'].get('plugins', '').split():
            if pname in __all__:
                logger.debug('install plugin: %s', pname)
                ctx.plugins.append(globals().get(pname))
                continue

            for x in '', ctx.local_path, ctx.global_path:
                path = os.path.join(x, pname + '.py')
                if os.path.exists(path):
                    logger.debug('plugin script "%s"', path)
                    break
            else:
                logger.warning('no plugin "%s" found', pname)
                continue

            spec = spec_from_file_location(pkg + '.' + pname, path)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)

            names = getattr(module, '__all__', [])
            logger.debug('install plugins: %s', ' '.join(names))
            ctx.plugins.extend([getattr(module, x, None) for x in names])

    @staticmethod
    def post_build(ctx, pack=None):
        inputs = ctx.input_paths
        outputs = ctx.outputs
        for plugin in [x for x in ctx.plugins if hasattr(x, 'post_build')]:
            plugin.post_build(ctx, inputs, outputs, pack=pack)

    @staticmethod
    def post_key(ctx, keyfile):
        kwargs = {
            'expired': ctx.runtime_expired,
            'devices': ctx.runtime_devices,
            'period': ctx.runtime_period,
            'data': ctx.cmd_options.get('user_data')
        }
        for plugin in [x for x in ctx.plugins if hasattr(x, 'post_key')]:
            plugin.post_key(ctx, keyfile, **kwargs)

    @staticmethod
    def post_runtime(ctx, source, dest, platform):
        for plugin in [x for x in ctx.plugins if hasattr(x, 'post_runtime')]:
            plugin.post_runtime(ctx, source, dest, platform)
