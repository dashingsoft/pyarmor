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

__VERSION__ = '4.3.dev1'


def format_platform():
    import platform
    import sys
    from struct import calcsize

    def format_system():
        plat = platform.system().lower()
        plat = ('windows' if plat.startswith('cygwin') else
                'linux' if plat.startswith('linux') else
                'freebsd' if plat.startswith(
                    ('freebsd', 'openbsd', 'isilon onefs')) else plat)
        if plat == 'linux':
            if hasattr(sys, 'getandroidapilevel'):
                plat = 'android'
            else:
                cname, cver = platform.libc_ver()
                if cname == 'musl':
                    plat = 'alpine'
                elif cname == 'libc':
                    plat = 'android'
        return plat

    def format_machine():
        mach = platform.machine().lower()
        arch_table = (
            ('x86', ('i386', 'i486', 'i586', 'i686')),
            ('x86_64', ('x64', 'x86_64', 'amd64', 'intel')),
            ('arm', ('armv5',)),
            ('armv6', ('armv6l',)),
            ('armv7', ('armv7l',)),
            ('aarch32', ('aarch32',)),
            ('aarch64', ('aarch64', 'arm64'))
        )
        for alias, archlist in arch_table:
            if mach in archlist:
                mach = alias
                break
        return mach

    plat, mach = format_system(), format_machine()
    if plat == 'windows' and mach == 'x86_64':
        bitness = calcsize('P'.encode()) * 8
        if bitness == 32:
            mach = 'x86'
    return plat, mach


def _import_pytransform3():
    try:
        return __import__(
            'pytransform3', globals=globals(), locals=locals(),
            fromlist=('__pyarmor__',), level=1
        )
    except ModuleNotFoundError:
        plat, arch = format_platform()
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
    def _update_token(ctx):
        m = Pytransform3.init(ctx)
        m.init_ctx(ctx)

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
