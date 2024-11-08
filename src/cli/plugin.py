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
           'PycPlugin', 'DarwinUniversalPlugin']


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
            logger.debug('call post build plugin %s', plugin)
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
            logger.debug('call post key plugin %s', plugin)
            plugin.post_key(ctx, keyfile, **kwargs)

    @staticmethod
    def post_runtime(ctx, source, dest, platform):
        for plugin in [x for x in ctx.plugins if hasattr(x, 'post_runtime')]:
            logger.debug('call post runtime plugin %s', plugin)
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


def osx_sign_binary(dest, identity=None):
    from subprocess import check_call, CalledProcessError, DEVNULL
    cmdlist = ['codesign', '-f', '-s', identity,
               '--all-architectures', '--timestamp', dest]
    logger.debug('%s', ' '.join(cmdlist))
    try:
        check_call(cmdlist, stdout=DEVNULL, stderr=DEVNULL)
    except CalledProcessError as e:
        logger.warning('codesign command failed with error code %d',
                       e.returncode)
    except Exception as e:
        logger.warning('codesign command failed with:\n%s', e)


class CodesignPlugin:
    '''codesign darwin runtime extension "pyarmor_runtime"'''

    @staticmethod
    def post_runtime(ctx, source, dest, platform):
        if platform.startswith('darwin'):
            identity = ctx.cfg['pack'].get('codesign_identify', '-')
            osx_sign_binary(dest, identity)


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

        oneplat = len(platforms) == 1
        pkgpath = MultiPythonPlugin.RUNTIME_PATH if oneplat else \
            os.path.dirname(MultiPythonPlugin.RUNTIME_PATH)
        verpath = os.path.join(pkgpath, pyver)
        if os.path.exists(verpath):
            rmtree(verpath)
        os.makedirs(verpath)

        pkgscript = os.path.join(pkgpath, '__init__.py')
        with open(pkgscript) as f:
            lines = f.readlines()
        start = 1 if lines[0].startswith('#') else 0

        if oneplat:
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


def osx_merge_binary(target, rtpath, plats):
    from subprocess import check_call, CalledProcessError, DEVNULL
    cmdlist = ['lipo', '-create', '-output', target]
    for plat in plats:
        filename = os.path.join(rtpath, plat, 'pyarmor_runtime.so')
        arch = 'x86_64' if plat == 'darwin_x86_64' else 'arm64'
        cmdlist.extend(['-arch', arch, filename])
    try:
        check_call(cmdlist, stdout=DEVNULL, stderr=DEVNULL)
        return True
    except CalledProcessError as e:
        logger.warning('lipo command "%s" failed with error code %d',
                       ' '.join(cmdlist), e.returncode)
    except Exception as e:
        logger.warning('lipo command "%s" failed with:\n%s',
                       ' '.join(cmdlist), e)


def find_runtime_package(ctx, output):
    prefix = ctx.import_prefix
    rtname = ctx.runtime_package_name
    if not prefix:
        return os.path.join(output, rtname)
    if isinstance(prefix, str):
        return os.path.join(output, prefix.replace('.', os.path.sep), rtname)
    with os.scandir(output) as iterator:
        for entry in iterator:
            if entry.is_dir():
                if rtname in os.listdir(entry.path):
                    return os.path.join(entry.path, rtname)


class DarwinUniversalPlugin:

    @staticmethod
    def post_build(ctx, inputs, outputs, pack):
        from shutil import rmtree

        if not ctx.native_platform.startswith('darwin.'):
            return

        def rebuild_init(oneplat, init_script):
            with open(init_script, 'r') as f:
                lines = f.readlines()
            if oneplat:
                lines[1:] = ['from .pyarmor_runtime import __pyarmor__']
            else:
                for i in range(1, len(lines)):
                    if lines[i].strip().startswith("# mach = 'universal'"):
                        lines[i] = lines[i].replace('# ', '')
                        break
            with open(init_script, 'w') as f:
                f.write(''.join(lines))

        rtpath = find_runtime_package(ctx, outputs[0])
        if rtpath is None or not os.path.exists(rtpath):
            logger.debug('no found runtime package "%s"', rtpath)
            return
        dirs = [x.name for x in os.scandir(rtpath) if x.is_dir()]
        plats = set(['darwin_x86_64', 'darwin_arm64', 'darwin_aarch64'])
        plats = plats.intersection(set(dirs))
        if len(plats) > 1:
            oneplat = all([x.startswith('darwin_') for x in dirs])
            if oneplat:
                target = rtpath
            else:
                target = os.path.join(rtpath, 'darwin_universal')
                os.makedirs(target, exist_ok=True)
            target = os.path.join(target, 'pyarmor_runtime.so')

            if not osx_merge_binary(target, rtpath, plats):
                return

            rebuild_init(oneplat, os.path.join(rtpath, '__init__.py'))
            identity = ctx.cfg['pack'].get('codesign_identify', '-')
            osx_sign_binary(target, identity)

            # Clean old files
            [rmtree(os.path.join(rtpath, x)) for x in plats]
