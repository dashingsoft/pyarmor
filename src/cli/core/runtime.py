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
#      Version: 8.2.4 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor/core/runtime.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Tue Jun  6 07:50:00 CST 2023
#

from . import map_platform


class PyarmorRuntime(object):

    @staticmethod
    def get(plat, extra=None, native=True):
        from os import scandir, path as os_path
        prefix = 'pyarmor_runtime'
        extlist = 'so', 'pyd', 'dylib', 'dll'

        # Themida is only available for windows
        if extra == 'themida' and not plat.startswith('windows'):
            extra = None

        pkgpath = os_path.dirname(__file__)
        if native and not extra:
            path = pkgpath
            for entry in scandir(path):
                parts = entry.name.split('.')
                if parts[0] == prefix and parts[-1] in extlist:
                    return entry.name, os_path.abspath(entry.path)

        platname = map_platform(plat)
        dirnames = platname.split('.')
        path = os_path.join(pkgpath, extra if extra else '', *dirnames)
        if not os_path.exists(path):
            from pyarmor.cli.bootstrap import check_prebuilt_runtime_library
            check_prebuilt_runtime_library([platname], extra)

        if os_path.exists(path):
            for entry in scandir(path):
                parts = entry.name.split('.')
                if parts[0] == prefix and parts[-1] in extlist:
                    return entry.name, os_path.abspath(entry.path)

        # Fallback to pyarmor.cli.runtime
        try:
            from pyarmor.cli.runtime import PyarmorRuntime, __VERSION__ as ver
            from logging import getLogger
            getLogger('cli').info('fallback to pyarmor.cli.runtime==%s', ver)
            return PyarmorRuntime.get(plat, extra=extra)
        except ModuleNotFoundError:
            pass
