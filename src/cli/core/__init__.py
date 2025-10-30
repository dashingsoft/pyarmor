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
#  @File: pyarmor/core/__init__.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Thu Jan 12 17:29:25 CST 2023
#

__VERSION__ = '8.1.0'

PLATFORM_NAMES = (
    'windows.x86_64', 'windows.x86', 'cygwin.x86_64',
    'darwin.x86_64', 'darwin.arm64',
    'linux.x86_64', 'linux.x86', 'linux.aarch64', 'linux.armv7',
    'linux.mips32el', 'linux.mips64el', 'linux.ppc64le', 'linux.riscv64',
    'alpine.x86_64', 'alpine.aarch64',
    'alpine.mips32el', 'alpine.mips64el', 'alpine.ppc64le', 'alpine.riscv64',
    'freebsd.x86_64',
    'android.x86_64', 'android.x86', 'android.aarch64', 'android.armv7',
)


def map_platform(platname):
    if platname == 'darwin.aarch64':
        return 'darwin.arm64'
    if platname.startswith('musl.'):
        return '.'.join('alpine', platname[5:])
    return platname


def check_and_install_prebuilt_package():
    import os
    from pyarmor.cli.context import format_platform
    from pyarmor.cli.bootstrap import check_prebuilt_runtime_library
    from platform import system, machine

    platname = os.getenv(
        'PYARMOR_PLATFORM',
        format_platform(system().lower(), machine().lower()))
    platname = map_platform(platname)
    if platname not in PLATFORM_NAMES:
        raise RuntimeError('"%s" is still not supported by Pyarmor' % platname)

    plat, arch = platname.split('.')
    if not os.path.exists(os.path.join(os.path.dirname(__file__), plat, arch)):
        check_prebuilt_runtime_library([platname])

    return plat, arch


def _import_pytransform3():
    try:
        return __import__(
            'pytransform3', globals=globals(), locals=locals(),
            fromlist=('__pyarmor__',), level=1
        )
    except ModuleNotFoundError:
        plat, arch = check_and_install_prebuilt_package()
        modname = '.'.join([plat, arch, 'pytransform3'])
        return __import__(
            modname, globals=globals(), locals=locals(),
            fromlist=('__pyarmor__',), level=1
        )


class Pytransform3(object):

    _pytransform3 = None

    @staticmethod
    def init(ctx=None):
        if Pytransform3._pytransform3 is None:
            Pytransform3._pytransform3 = m = _import_pytransform3()
            if ctx:
                m.init_ctx(ctx)
        return Pytransform3._pytransform3

    @staticmethod
    def generate_obfuscated_script(ctx, res):
        m = Pytransform3.init(ctx)
        return m.generate_obfuscated_script(ctx, res)

    @staticmethod
    def generate_runtime_package(ctx, output, platforms=None):
        m = Pytransform3.init(ctx)
        return m.generate_runtime_package(ctx, output, platforms)

    @staticmethod
    def generate_runtime_key(ctx, outer=None):
        m = Pytransform3.init(ctx)
        return m.generate_runtime_key(ctx, outer)

    @staticmethod
    def pre_build(ctx):
        m = Pytransform3.init(ctx)
        return m.pre_build(ctx)

    @staticmethod
    def post_build(ctx):
        m = Pytransform3.init(ctx)
        return m.post_build(ctx)

    @staticmethod
    def get_hd_info(hdtype, name=None):
        m = Pytransform3.init()
        return m.get_hd_info(hdtype, name) if name \
            else m.get_hd_info(hdtype)

    @staticmethod
    def version():
        m = Pytransform3.init()
        return m.revision


#
# Compatiable for pyarmor.cli < 8.3
#

class PyarmorRuntime(object):

    @staticmethod
    def get(plat, extra=None):
        from os import scandir, path as os_path
        if not extra:
            prefix = 'pyarmor_runtime'
            for entry in scandir(os_path.dirname(__file__)):
                parts = entry.name.split('.')
                if parts[0] == prefix and parts[-1] in ('so', 'pyd', 'dylib'):
                    return entry.name, os_path.abspath(entry.path)
