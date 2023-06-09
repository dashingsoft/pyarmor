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


__all__ = ['CodesignPlugin', 'MultiPythonPlugin', 'PlatformTagPlugin',
           'PycPlugin']


class Plugin(object):

    def __init__(self, ctx=None):
        self.ctx = ctx

    @staticmethod
    def install(ctx, pkg='pyarmor.cli.plugin'):
        ctx.Plugin = Plugin

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

    @staticmethod
    def post_bcc(ctx, res, csource):
        for plugin in [x for x in ctx.plugins if hasattr(x, 'post_bcc')]:
            patched_csource = plugin.post_bcc(ctx, res, csource)
            if patched_csource:
                csource = patched_csource
        return csource


class PycPlugin:
    '''Change all obfuscated scripts name entension from ".pyc" to ".py"'''

    @staticmethod
    def post_build(ctx, inputs, outputs, pack):
        for path, dirnames, filenames in os.walk(outputs[0]):
            for x in filenames:
                if x.endswith('.pyc'):
                    pycname = os.path.join(path, x)
                    os.replace(pycname, pycname[:-1])


class CodesignPlugin:
    '''codesign darwin runtime extension "pyarmor_runtime"'''

    @staticmethod
    def post_runtime(ctx, source, dest, platform):
        if platform.startswith('darwin'):
            from subprocess import check_call, CalledProcessError, DEVNULL
            identity = ctx.cfg['pack'].get('codesign_identify', '-')
            cmdlist = ['codesign', '-f', '-s', identity,
                       '--all-architectures', '--timestamp', dest]
            logger.info('%s', ' '.join(cmdlist))
            try:
                check_call(cmdlist, stdout=DEVNULL, stderr=DEVNULL)
            except CalledProcessError as e:
                logger.warning('codesign command failed with error code %d',
                               e.returncode)
            except Exception as e:
                logger.warning('codesign command failed with:\n%s', e)


class PlatformTagPlugin:
    '''Rename runtime extension "pyarmor_runtime" with platform tag.'''

    @staticmethod
    def post_runtime(ctx, source, dest, platform):
        pyver = '%s%s' % ctx.python_version[:2]
        if platform.startswith('windows.'):
            tag = 'cp%s' % pyver
            tagname = '.'.join(['pyarmor_runtime', tag, 'pyd'])
            logger.info('rename "%s" to "%s"', dest, tagname)
            os.rename(dest, dest.replace('pyarmor_runtime.pyd', tagname))
        elif platform.startswith('darwin.'):
            tag = 'cpython-%s-darwin' % pyver
            tagname = '.'.join(['pyarmor_runtime', tag, 'so'])
            logger.info('rename "%s" to "%s"', dest, tagname)
            os.rename(dest, dest.replace('pyarmor_runtime.so', tagname))
        elif platform.startswith('linux.'):
            arch = platform.split('.')[1]
            tag = 'cpython-%s-%s-linux-gnu' % (pyver, arch)
            tagname = '.'.join(['pyarmor_runtime', tag, 'so'])
            logger.info('rename "%s" to "%s"', dest, tagname)
            os.rename(dest, dest.replace('pyarmor_runtime.so', tagname))
        else:
            raise RuntimeError('PlatformTagPlugin unknown "%s"' % platform)


class MultiPythonPlugin:
    '''Refine runtime package to support multiple python versions'''

    RUNTIME_PATH = None
    RUNTIME_FILES = []

    @staticmethod
    def post_runtime(ctx, source, dest, platform):
        MultiPythonPlugin.RUNTIME_PATH = os.path.dirname(dest)
        MultiPythonPlugin.RUNTIME_FILES.append(dest)

    @staticmethod
    def post_build(ctx, inputs, outputs, pack):
        '''Rewrite runtime package __init__.py'''
        from shutil import move, rmtree
        pyver = 'py%s%s' % ctx.python_version[:2]
        platforms = ctx.target_platforms

        native = len(platforms) == 1 and platforms[0] == ctx.native_platform
        pkgpath = MultiPythonPlugin.RUNTIME_PATH if native else \
            os.path.dirname(MultiPythonPlugin.RUNTIME_PATH)
        verpath = os.path.join(pkgpath, pyver)
        if os.path.exists(verpath):
            rmtree(verpath)
        os.makedirs(verpath)

        pkgscript = os.path.join(pkgpath, '__init__.py')
        with open(pkgscript) as f:
            lines = f.readlines()
        start = 1 if lines[0].startswith('#') else 0

        if native:
            lines[start:] = '\n'.join([
                'from sys import version_info as py_version',
                '{0} = __import__("py%d%d.pyarmor_runtime" % py_version[:2],'
                ' globals(), locals(), ["{0}"], 1).{0}'.format('__pyarmor__')
            ])
            with open(pkgscript, 'w') as f:
                f.write(''.join(lines))
            for x in MultiPythonPlugin.RUNTIME_FILES:
                move(x, verpath)
        else:
            lines[start:start] = 'from sys import version_info as py_version\n'
            with open(pkgscript, 'w') as f:
                f.write(''.join(lines).replace(
                    "join(['_'", "join(['py%d%d' % py_version[:2], '_'"))
            for x in MultiPythonPlugin.RUNTIME_FILES:
                move(os.path.dirname(x), verpath)

        MultiPythonPlugin.RUNTIME_FILES.clear()
