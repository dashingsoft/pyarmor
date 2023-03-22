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
        ('i686', ('i?86', )),
        ('x86_64', ('x64', 'x86_64', 'amd64', 'intel')),
        ('arm', ('armv5',)),
        ('armv6l', ('armv6l',)),
        ('armv7l', ('armv7l',)),
        ('ppc64', ('ppc64',)),
        ('ppc64le', ('ppc64le',)),
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

    return '.'.join([plat, mach])


class Context(object):

    def __init__(self, home, gpath='', lpath='', rpath='', encoding=None):
        self.home_path = os.path.normpath(home)
        self.global_path = os.path.join(home, gpath if gpath else 'config')
        self.local_path = lpath if lpath else '.pyarmor'
        self.reg_path = self.home_path if not rpath else \
            rpath if os.path.isabs(rpath) else \
            os.path.join(self.home_path, rpath)

        # self.encoding is just for reading config file
        self.encoding = encoding
        cfglist = self.default_config, self.global_config, self.local_config
        self.cfg = self._read_config(cfglist, encoding=encoding)

        self.inline_plugin_marker = '# pyarmor: '
        self.runtime_package = 'pyarmor_runtime'
        # self.runtime_suffix = '_000000'
        # default inner key filename within runtime package
        self.runtime_keyfile = '.pyarmor.ikey'

        self.bootstrap_template = bootstrap_template
        self.runtime_package_templates = (
            runtime_package_template,
            runtime_package_template2,
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
        self.obfuscated_modules = set()

        self.runtime_key = None

        self.cmd_options = {}

    def _read_config(self, filelist, encoding=None):
        cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation(),
        )
        cfg.read(filelist, encoding=encoding)
        return cfg

    def _named_config(self, name, encoding=None):
        flist = [os.path.join(x, name)
                 for x in (self.global_path, self.local_path)]
        return self._read_config(flist, encoding=encoding)

    def read_token(self):
        if os.path.exists(self.license_token):
            with open(self.license_token, 'rb') as f:
                return f.read()

    def save_token(self, data):
        with open(self.license_token, 'wb') as f:
            f.write(data)

    def clear_token(self):
        if os.path.exists(self.license_token):
            with open(self.license_token, 'wb') as f:
                f.close()

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

    def get_res_options(self, name, sect='finder'):
        options = {}
        if self.cfg.has_section(sect):
            options.update(self.cfg.items(sect))
        if sect == 'finder':
            options.update(self.cmd_options.get('finder', {}))
        extra_sect = ':'.join([name, sect])
        if self.cfg.has_section(extra_sect):
            options.update(self.cfg.items(extra_sect))
        cfg = self._named_config(name + '.ruler')
        if cfg.has_section(sect):
            options.update(cfg.items(sect))
        return options

    def get_path(self, local=True):
        return self.local_path if local else self.global_path

    def get_filename(self, local=True, name=None):
        return os.path.join(self.get_path(local), name + '.ruler') if name \
            else self.local_config if local else self.global_config

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
        getint = self.cfg.getint
        return [getint('pyarmor', x) for x in ('major', 'minor', 'patch')]

    @property
    def python_version(self):
        return sys.version_info[:2]

    @property
    def default_config(self):
        return os.path.join(os.path.dirname(__file__), 'default.cfg')

    @property
    def global_config(self):
        return os.path.join(self.global_path, 'global')

    @property
    def local_config(self):
        return os.path.join(self.local_path, 'config')

    @property
    def private_capsule(self):
        filename = os.path.join(self.reg_path, '.pyarmor_capsule.zip')
        if not os.path.exists(filename):
            from shutil import copy
            path = os.path.dirname(__file__)
            public_capsule = os.path.join(path, '..', 'public_capsule.zip')
            os.makedirs(self.reg_path, exist_ok=True)
            copy(public_capsule, filename)
        return filename

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
    def runtime_suffix(self):
        return '_' + self.license_info['licno'][-6:]

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
        return self.cfg['logging'].get('debug_logfile', 'pyarmor.debug.log')

    @property
    def trace_logfile(self):
        return self.cfg['logging'].get('trace_logfile', 'pyarmor.trace.log')

    def _optb(self, section, name):
        return self.cfg.getboolean(section, name, vars=self.cmd_options)

    def _opts(self, section, name):
        return self.cfg.get(section, name, vars=self.cmd_options)

    def _opti(self, section, name):
        return self.cfg.getint(section, name, vars=self.cmd_options)

    @property
    def recursive(self):
        return self._optb('finder', 'recursive')

    @property
    def findall(self):
        return self._optb('finder', 'findall')

    @property
    def pyexts(self):
        return self._opts('finder', 'pyexts').split()

    @property
    def enable_jit(self):
        return self._optb('builder', 'enable_jit')

    @property
    def enable_themida(self):
        return self._optb('builder', 'enable_themida')

    @property
    def enable_bcc(self):
        return self._optb('builder', 'enable_bcc')

    @property
    def enable_rft(self):
        return self._optb('builder', 'enable_rft')

    @property
    def assert_call(self):
        return self._optb('builder', 'assert_call')

    @property
    def assert_import(self):
        return self._optb('builder', 'assert_import')

    @property
    def mix_coname(self):
        return self._optb('builder', 'mix_coname')

    @property
    def mix_localnames(self):
        return self._optb('builder', 'mix_localnames')

    @property
    def mix_argnames(self):
        return self._optb('builder', 'mix_argnames')

    @property
    def mix_str(self):
        return self._optb('builder', 'mix_str')

    @property
    def obf_module(self):
        return self._opti('builder', 'obf_module')

    @property
    def obf_code(self):
        return self._opti('builder', 'obf_code')

    @property
    def wrap_mode(self):
        return self._optb('builder', 'wrap_mode')

    @property
    def restrict_module(self):
        return self._opti('builder', 'restrict_module')

    @property
    def import_check_license(self):
        return self._optb('builder', 'import_check_license')

    @property
    def clear_module_co(self):
        return self._optb('builder', 'clear_module_co')

    @property
    def import_prefix(self):
        v = self._opts('builder', 'import_prefix')
        return int(v) if v.isdecimal() else v

    @property
    def exclude_restrict_modules(self):
        return self._opts('builder', 'exclude_restrict_modules')

    @property
    def co_threshold(self):
        return self._opti('builder', 'co_threshold')

    @property
    def jit_iv_threshold(self):
        return self._opti('builder', 'jit_iv_threshold')

    @property
    def exclude_co_names(self):
        return self.cfg['builder'].get('exclude_co_names', '').split()

    @property
    def outer_keyname(self):
        self.cfg['builder'].get('outer_keyname', 'pyarmor.rkey')

    @property
    def use_runtime(self):
        return self.cmd_options.get('use_runtime',
                                    self.cfg['builder'].get('use_runtime'))

    #
    # runtime configuration
    #
    def _rt_opt(self, opt):
        return self.cmd_options.get(opt, self.cfg['runtime'].get(opt))

    @property
    def runtime_platforms(self):
        return self._rt_opt('platforms')

    @property
    def runtime_on_error(self):
        return self._opti('runtime', 'on_error')

    @property
    def runtime_outer(self):
        return self._optb('runtime', 'outer')

    @property
    def runtime_period(self):
        period = self._rt_opt('period')
        if period:
            c = period[-1].lower()
            if c.isdecimal():
                return int(period) * 3600

            if c in ('m', 'h', 's'):
                unit = {
                    's': 1,
                    'm': 60,
                    'h': 3600,
                }
                return int(period[:-1]) * unit[c]

            return -1

    @property
    def runtime_expired(self):
        return self._rt_opt('expired')

    @property
    def runtime_nts(self):
        return self._opts('runtime', 'nts')

    @property
    def runtime_nts_timeout(self):
        return self._opti('runtime', 'nts_timeout')

    @property
    def runtime_devices(self):
        value = self._rt_opt('devices')
        return value.splitlines() if isinstance(value, str) else value

    @property
    def runtime_interps(self):
        return self._rt_opt('interps')

    @property
    def runtime_timer(self):
        return self._opti('runtime', 'timer')

    @property
    def runtime_simple_extension_name(self):
        return self._optb('runtime', 'simple_extension_name')

    @property
    def runtime_hooks(self):
        value = self._rt_opt('hooks')
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
            cfg = self._named_config(name, encoding=encoding)
            if cfg.has_section('runtime.message'):
                return cfg
