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
#  @File: cli/context.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: 2022-12-06
#
import configparser
import os
import sys

bootstrap_template = '''# Pyarmor $rev, $timestamp
from $package import __pyarmor__
__pyarmor__(__name__, $path, $code)
'''

runtime_package_template = '''# Pyarmor $rev, $timestamp
from .pyarmor_runtime import __pyarmor__
'''

runtime_package_template2 = '''# Pyarmor $rev, $timestamp
for suffix in '', '_a1', '_a2', '_a3':
    try:
        __pyarmor__ = __import__('pyarmor_runtime' + suffix,
                                 globals(), locals(),
                                 ('__pyarmor__',),
                                 0)
        break
    except ModuleNotFoundError:
        pass
else:
    raise ModuleNotFoundError('no pyarmor_runtime extension found')
'''

runtime_package_template3 = '''# Pyarmor $rev, $timestamp
from .pyarmor_runtime import __pyarmor__
from sys import path
path.insert(0, __file__.replace('__init__.py', 'libs'))
'''


def format_platform(plat, arch):
    from struct import calcsize
    from fnmatch import fnmatchcase

    plat_table = (
        ('windows', ('windows', 'cygwin*')),
        ('darwin', ('darwin',)),
        ('ios', ('ios',)),
        ('linux', ('linux*',)),
        ('freebsd', ('freebsd*', 'openbsd*', 'isilon onefs')),
        ('poky', ('poky',)),
    )

    arch_table = (
        ('x86', ('i?86', )),
        ('x86_64', ('x64', 'x86_64', 'amd64', 'intel')),
        ('arm', ('armv5',)),
        ('armv6', ('armv6l',)),
        ('armv7', ('armv7l',)),
        ('ppc64', ('ppc64le',)),
        ('mips32', ('mips',)),
        ('aarch32', ('aarch32',)),
        ('aarch64', ('aarch64', 'arm64'))
    )

    for alias, platlist in plat_table:
        if any([fnmatchcase(plat, x) for x in platlist]):
            plat = alias
            break

    for alias, archlist in arch_table:
        if any([fnmatchcase(arch, x) for x in archlist]):
            mach = alias
            break

    if plat == 'windows' and mach == 'x86_64':
        bitness = calcsize('P'.encode()) * 8
        if bitness == 32:
            mach = 'x86'

    return os.path.join(plat, mach)


class Context(object):

    def __init__(self, home, local=None, encoding=None):
        self.home_path, path = (home + ',').split(',')[:2]
        self.reg_path = os.path.normpath(os.path.join(self.home_path, path))
        self.local_path = local if local else '.pyarmor'

        # self.encoding is just for reading config file
        self.encoding = encoding
        self.cfg = self._read_config()

        self.inline_plugin_marker = '# PyArmor Plugin: '
        self.runtime_package = 'pyarmor_runtime'
        self.runtime_suffix = '_000000'
        self.runtime_keyfile = '.pyarmor.key'

        self.bootstrap_template = bootstrap_template
        self.runtime_package_templates = (
            runtime_package_template,
            runtime_package_template2,
            runtime_package_template3,
        )

        # Alias format for duplicated input names
        self.alias_suffix = '{0}-{1}'

        self.input_paths = []
        self.outputs = []
        self.resources = []
        self.extra_resources = []

        self.module_relations = {}
        self.module_types = {}
        self.module_builtins = set()
        self.extra_libs = {}

        self.runtime_key = None

        self.cmd_options = {}

    def _read_config(self):
        cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation,
        )
        cfg.read([self.default_config, self.global_config, self.local_config],
                 encoding=self.encoding)
        return cfg

    def read_token(self):
        if os.path.exists(self.license_token):
            with open(self.license_token, 'rb') as f:
                return f.read()

    def save_token(self, data):
        with open(self.license_token, 'wb') as f:
            f.write(data)

    def read_license(self):
        if os.path.exists(self.license_file):
            with open(self.license_file, 'rb') as f:
                return f.read()

    def push(self, options):
        finder = {}
        for opt in ('recursive', 'findall', 'includes', 'excludes'):
            if opt in options:
                finder[opt] = options[opt]
        if finder:
            self.cmd_options['finder'] = finder
        self.cmd_options.update(options)

    def pop(self):
        return self.cmd_options.clear()

    def get_res_filter(self, name, sect='finder'):
        options = {}
        if self.cfg.has_section(sect):
            options.update(self.cfg.items(sect))
        options.update(self.cmd_options.get('finder', {}))
        sect2 = ':'.join(name, sect)
        if self.cfg.has_section(sect2):
            options.update(self.cfg.items(sect2))
        return options

    def get_res_options(self, name, sect):
        options = {}
        if self.cfg.has_section(sect):
            options.update(self.cfg.items(sect))
        sect2 = ':'.join(name, sect)
        if self.cfg.has_section(sect2):
            options.update(self.cfg.items(sect2))
        return options

    def version_info(self, verbose=3):
        #    8.0.1
        #    8.0.1 (trial)
        #    8.0.1 (basic), 002000
        #    8.0.1 (group), 002002, Product
        #    8.0.1 (group), 002002, Product, Company
        rev = '.'.join([str(x) for x in self.version])
        if not verbose:
            return rev

        licinfo = self.license_info
        lictype = 'basic' if licinfo['features'] == 1 else \
            'pro' if licinfo['features'] == 7 else \
            'trial' if licinfo['token'] == 0 else 'unknown'
        verinfo = ['%s (%s)' % (rev, lictype)]

        if verbose > 1:
            verinfo.append(licinfo['licno'][-6:])

        if verbose > 2:
            product = licinfo['product']
            verinfo.append(product if product else 'non-profits')

        if verbose > 3:
            regname = licinfo['regname']
            if regname:
                verinfo.append(regname)

        return ', '.join(verinfo)

    @property
    def version(self):
        return self.cfg.getint('pyarmor', 'major'), \
            self.cfg.getint('pyarmor', 'minor'), \
            self.cfg.getint('pyarmor', 'patch')

    @property
    def python_version(self):
        return sys.version_info[:2]

    @property
    def default_config(self):
        return os.path.join(os.path.dirname(__file__), 'default.cfg')

    @property
    def global_config(self):
        return os.path.join(self.home_path, 'config', 'global')

    @property
    def local_config(self):
        return os.path.join(self.local_path, 'config')

    @property
    def private_capsule(self):
        return os.path.join(self.reg_path, '.pyarmor_capsule.zip')

    @property
    def license_file(self):
        return os.path.join(self.reg_path, 'license.lic')

    @property
    def license_token(self):
        return os.path.join(self.reg_path, '.license.token')

    @property
    def license_info(self):
        from .register import parse_token
        return parse_token(self.read_token())

    @property
    def native_platform(self):
        from platform import system, machine
        return '.'.join([system().lower(), machine().lower()])

    @property
    def pyarmor_platform(self):
        platname = os.getenv('PYARMOR_PLATFORM', self.native_platform)
        return format_platform(*platname.split('.'))

    @property
    def debug_logfile(self):
        return os.path.join(self.home_path, 'pyarmor.debug.log')

    def _opt(self, section, name):
        return self.cfg.getboolean(section, name, vars=self.cmd_options)

    def _opts(self, section, name):
        return self.cfg.get(section, name, vars=self.cmd_options)

    def _opti(self, section, name):
        return self.cfg.getint(section, name, vars=self.cmd_options)

    @property
    def recursive(self):
        return self._opt('finder', 'recursive')

    @property
    def findall(self):
        return self._opt('finder', 'findall')

    @property
    def pyexts(self):
        return self._opts('finder', 'pyexts').split()

    @property
    def enable_jit(self):
        return self._opt('builder', 'enable_jit')

    @property
    def enable_themida(self):
        return self._opt('builder', 'enable_themida')

    @property
    def enable_bcc(self):
        return self._opt('builder', 'enable_bcc')

    @property
    def enable_refactor(self):
        return self._opt('builder', 'enable_refactor')

    @property
    def assert_call(self):
        return self._opt('builder', 'assert_call')

    @property
    def assert_import(self):
        return self._opt('builder', 'assert_import')

    @property
    def mix_name(self):
        return self._opt('builder', 'mix_name')

    @property
    def mix_str(self):
        return self._opt('builder', 'mix_str')

    @property
    def obf_module(self):
        return self._opti('builder', 'obf_module')

    @property
    def obf_code(self):
        return self._opti('builder', 'obf_code')

    @property
    def wrap_mode(self):
        return self._opt('builder', 'wrap_mode')

    @property
    def restrict_module(self):
        return self._opti('builder', 'restrict_module')

    @property
    def relative_import(self):
        v = self._opts('builder', 'relative_import')
        return int(v) if v.isdecimal() else v

    @property
    def runtime_share(self):
        return self._opts('runtime', 'share')

    @property
    def runtime_platforms(self):
        return self._opts('runtime', 'platforms')

    @property
    def runtime_on_error(self):
        return self._opti('runtime', 'on_error')

    @property
    def runtime_outer(self):
        return self._opts('runtime', 'outer')

    @property
    def runtime_period(self):
        period = self._opti('runtime', 'period')
        if period:
            c = period[-1].lower()
            if c.isdecimal():
                return int(period) * 3600

            if c in ('m', 'h', 's'):
                unit = {
                    's': 1,
                    'm': 60,
                    'h': 3600,
                    'd': 3600 * 24,
                }
                return int(period[:-1]) * unit[c]

            return -1

    @property
    def runtime_expired(self):
        return self._opts('runtime', 'expired')

    @property
    def runtime_nts(self):
        return self._opts('runtime', 'nts')

    @property
    def runtime_nts_timeout(self):
        return self._opti('runtime', 'nts_timeout')

    @property
    def runtime_machines(self):
        return self._opts('runtime', 'machines')

    @property
    def runtime_interps(self):
        return self._opts('runtime', 'interps')

    @property
    def runtime_timer(self):
        return self._opti('runtime', 'timer')

    @property
    def runtime_simple_extension_name(self):
        return self._opt('runtime', 'simple_extension_name')

    @property
    def runtime_hooks(self):
        value = self.cfg['runtime'].get('hooks', '')
        if value:
            from ast import literal_eval
            name, encoding = (value + ':utf-8').split(':')[:2]
            for x in self.local_path, self.global_path:
                filename = os.path.join(x, name)
                if os.path.exists(filename):
                    with open(filename, encoding=encoding) as f:
                        return literal_eval(f.read())

    @property
    def runtime_messages(self):
        value = self.cfg['runtime'].get('messages', '')
        if value:
            name, encoding = (value + ':utf-8').split(':')[:2]
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            paths = self.global_path, self.local_path
            cfg.read([os.path.join(x, name) for x in paths], encoding=encoding)
            return cfg

    @property
    def obfuscated_modules(self):
        return set([x.fullname for x in self.resources if x.is_script()])
