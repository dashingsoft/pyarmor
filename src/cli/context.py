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


class Context(object):

    def __init__(self, home, local=None, encoding=None):
        self.home_path = home
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
        )

        self.bcc_call_function_ex = False

        # Alias format for duplicated input names
        self.alias_suffix = '{0}-{1}'

        self.input_paths = []
        self.outputs = []
        self.resources = []
        self.extra_resources = []

        self.module_relations = {}
        self.module_types = {}
        self.module_builtins = set()
        self.obfuscated_modules = set()
        self.extra_libs = {}

        self.runtime_key = None

        # Context stack
        self._stacks = []

    def _read_config(self):
        cfg = configparser.ConfigParser(empty_lines_in_values=False)
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
        self._stacks.append(options)

    def pop(self):
        return self._stacks.pop()

    def get_core_config(self, encoding=None):
        encoding = encoding if encoding else self.encoding
        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(os.path.join(os.path.dirname(__file__), 'core', 'config'),
                 encoding=encoding)
        return cfg

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
    def core_version(self):
        return self.cfg['pyarmor'].getint('core')

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
        return os.path.join(self.home_path, '.pyarmor_capsule.zip')

    @property
    def license_file(self):
        return os.path.join(self.home_path, 'license.lic')

    @property
    def license_info(self):
        from .register import parse_token
        return parse_token(self.read_token())

    @property
    def license_token(self):
        return os.path.join(self.home_path, '.license.token')

    def _format_platform(self):
        from platform import system, machine
        return '.'.join([system().lower(), machine().lower()])

    @property
    def native_platform(self):
        return os.environ.get('PYARMOR_PLATFORM',
                              self.cfg['pyarmor'].get('platform',
                                                      self._format_platform()))

    @property
    def debug_logfile(self):
        return os.path.join(self.home_path, 'pyarmor.debug.log')

    def _opt(self, section, name):
        return self.cfg.getboolean(section, name, vars=self._stacks[-1])

    def _opts(self, section, name):
        return self.cfg.get(section, name, vars=self._stacks[-1])

    def _opti(self, section, name):
        return self.cfg.getint(section, name, vars=self._stacks[-1])

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
    def prebuilt_runtime(self):
        return self._opts('builder', 'prebuilt_runtime')

    @property
    def target_platforms(self):
        return self._opts('runtime', 'platforms')

    @property
    def outer_name(self):
        return self._opts('runtime', 'outer_name')

    @property
    def check_period(self):
        period = self._opti('runtime', 'check_period')
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
    def expired(self):
        return self._opts('runtime', 'expired')

    @property
    def nts(self):
        return self._opts('runtime', 'nts')

    @property
    def bind_machines(self):
        return self._opts('runtime', 'machines').splitlines()

    @property
    def bind_interps(self):
        return self._opts('runtime', 'interps')

    @property
    def bind_data(self):
        return self._opts('runtime', 'data')
