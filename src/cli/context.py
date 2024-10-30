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

multi_runtime_package_template = '''# Pyarmor $rev, $timestamp
def __pyarmor__():
    import platform
    import sys
    from struct import calcsize

    def format_system():
        plat = platform.system().lower()
        plat = ('cygwin' if plat.startswith('cygwin') else
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
            ('x86', ('i386', 'i486', 'i586', 'i686', 'x86')),
            ('x86_64', ('x64', 'x86_64', 'amd64', 'intel')),
            ('arm', ('armv5',)),
            ('armv6', ('armv6l',)),
            ('armv7', ('armv7l',)),
            ('aarch32', ('aarch32',)),
            ('aarch64', ('aarch64', 'arm64')),
            ('ppc64le', ('ppc64le',)),
            ('mips32el', ('mipsel', 'mips32el')),
            ('mips64el', ('mips64el',)),
            ('riscv64', ('riscv64',)),
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
    # mach = 'universal' if plat == 'darwin' else mach
    name = '.'.join(['_'.join([plat, mach]), 'pyarmor_runtime'])
    return __import__(name, globals(), locals(), ['__pyarmor__'], level=1)
__pyarmor__ = __pyarmor__().__pyarmor__
'''

runtime_package_template3 = '''# Pyarmor $rev, $timestamp
from importlib.machinery import ExtensionFileLoader
from sysconfig import get_platform
__pyarmor__ = ExtensionFileLoader(
    '.pyarmor_runtime', __file__.replace('__init__.py', 'pyarmor_runtime.so')
).load_module().__pyarmor__
'''


def format_platform(plat=None, arch=None):
    from struct import calcsize
    from fnmatch import fnmatchcase

    # Fix pyarmor.cli.core 6.5.2 issue, may be removed in 6.5.3
    if plat is None and arch is None:
        if os.getenv('PYARMOR_PLATFORM'):
            plat, arch = os.getenv('PYARMOR_PLATFORM').split('.')
        else:
            from platform import system, machine
            plat, arch = system().lower(), machine().lower()

    plat_table = (
        ('windows', ('windows',)),
        ('cygwin', ('cygwin*',)),
        ('darwin', ('darwin',)),
        ('linux', ('linux*',)),
        ('freebsd', ('freebsd*', 'openbsd*', 'isilon onefs')),
    )

    arch_table = (
        ('x86', ('i?86', 'x86')),
        ('x86_64', ('x64', 'x86_64', 'amd64', 'intel')),
        ('arm', ('armv5',)),
        ('armv6', ('armv6l',)),
        ('armv7', ('armv7l',)),
        ('aarch32', ('aarch32',)),
        ('aarch64', ('aarch64', 'arm64')),
        ('ppc64le', ('ppc64le',)),
        ('mips32el', ('mipsel', 'mips32el')),
        ('mips64el', ('mips64el',)),
        ('riscv64', ('riscv64',)),
    )

    for alias, platlist in plat_table:
        if any([fnmatchcase(plat, x) for x in platlist]):
            plat = alias
            break

    for alias, archlist in arch_table:
        if any([fnmatchcase(arch, x) for x in archlist]):
            mach = alias
            break
    else:
        raise RuntimeError('unsupported arch "%s"' % arch)

    if plat == 'linux' and hasattr(sys, 'getandroidapilevel'):
        plat = 'android'

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

        # self.runtime_package = 'pyarmor_runtime'
        # self.runtime_suffix = '_000000'
        # default inner key filename within runtime package
        self.runtime_keyfile = '.pyarmor.ikey'

        self.bootstrap_template = bootstrap_template

        # Alias format for duplicated input names
        self.alias_suffix = '{0}-{1}'

        self.input_paths = []
        self.outputs = []
        self.resources = []
        self.extra_resources = []

        self.module_relations = {}
        self.module_types = {}
        self.variable_types = {}
        self.module_builtins = set()

        self.obfuscated_modules = set()
        self.extra_libs = {}

        self.rft_auto_excludes = set(['super'])
        self.rft_export_names = set()
        self.rft_transform_op = '?'

        self.runtime_key = None

        self.cmd_options = {}
        self.plugins = []

    def _read_config(self, filelist, encoding=None):
        cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation(),
        )
        cfg.read(filelist, encoding=encoding)
        return cfg

    def _named_config(self, name, encoding=None):
        nlist = []
        if self.cfg.getboolean('builder', 'propagate_package_options'):
            i = name.find('.')
            while i > -1:
                nlist.append(name[:i])
                i = name.find('.', i+1)
        nlist.append(name)
        flist = [os.path.join(b, a)
                 for a in nlist
                 for b in (self.global_path, self.local_path)]
        return self._read_config(flist, encoding=encoding)

    def read_token(self):
        for filename in (self.license_group_token, self.license_token):
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    return f.read()

    def save_token(self, data):
        with open(self.license_token, 'wb') as f:
            if not data.endswith(b'=='):
                raise RuntimeError('got invalid token %r' % data)
            f.write(data)

    def save_group_token(self, data):
        with open(self.license_group_token, 'wb') as f:
            if not data.endswith(b'=='):
                raise RuntimeError('got invalid token %r' % data)
            f.write(data)

    def clear_token(self):
        if os.path.exists(self.license_token):
            with open(self.license_token, 'wb') as f:
                f.close()

    def group_device_file(self, devid):
        filename = 'pyarmor-group-device.%s' % devid
        return os.path.join(self.local_path, 'group', filename)

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
        elif sect == 'builder':
            options.update(self.cmd_options)
        extra_sect = ':'.join([name, sect])
        if self.cfg.has_section(extra_sect):
            options.update(self.cfg.items(extra_sect))
        if name:
            # If input path is '.', package name will start with '..'
            cfg = self._named_config(name.strip('.') + '.ruler')
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
        rev = '.'.join(self.version)
        if not verbose:
            return rev

        licinfo = self.license_info
        lictype = 'basic' if licinfo['features'] in (1, 17) else \
            'pro' if licinfo['features'] == 7 else \
            'group' if licinfo['features'] == 15 else \
            'ci' if licinfo['features'] == 23 else \
            'trial' if licinfo['token'] == 0 else 'unknown'
        verinfo = ['%s (%s)' % (rev, lictype)]

        if verbose > 1:
            verinfo.append(licinfo['licno'][-6:])

        if verbose > 2:
            pname = licinfo['product']
            verinfo.append(pname)

        if verbose > 3:
            regname = licinfo['regname']
            if regname:
                verinfo.append(regname)

        return ', '.join(verinfo)

    @property
    def version(self):
        return [self.cfg.get('pyarmor', x) for x in ('major', 'minor', 'patch')]

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

    def _make_public_capsule(self, filename):
        from shutil import copy
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        path = os.path.dirname(__file__)
        public_capsule = os.path.join(path, 'public_capsule.zip')
        copy(public_capsule, filename)

    @property
    def private_capsule(self):
        filename = os.path.join(self.reg_path, '.pyarmor_capsule.zip')
        if not os.path.exists(filename):
            self._make_public_capsule(filename)
        return filename

    @property
    def license_file(self):
        return os.path.join(self.reg_path, 'license.lic')

    @property
    def license_token(self):
        return os.path.join(self.reg_path, '.license.token')

    @property
    def license_group_token(self):
        return os.path.join(self.reg_path, '.license.group.token')

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
    def target_platforms(self):
        platforms = self.cmd_options.get('platforms')
        return platforms if platforms else [self.native_platform]

    def _check_logpath(self, logfile):
        path = os.path.dirname(logfile)
        if path not in ('', '.') and not os.path.exists(path):
            os.makedirs(path)
        return logfile

    @property
    def debug_logfile(self):
        return self._check_logpath(
            self.cfg['logging'].get('debug_logfile', 'pyarmor.debug.log'))

    @property
    def trace_logfile(self):
        return self._check_logpath(
            self.cfg['logging'].get('trace_logfile', 'pyarmor.trace.log'))

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
    def enable_themida(self):
        return self._optb('builder', 'enable_themida')

    @property
    def enable_jit(self):
        return self._optb('builder', 'enable_jit')

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
    def clear_frame_locals(self):
        return self._optb('builder', 'clear_frame_locals')

    @property
    def import_prefix(self):
        v = self._opts('builder', 'import_prefix')
        return int(v) if v.isdecimal() else v

    @property
    def exclude_restrict_modules(self):
        return self._opts('builder', 'exclude_restrict_modules').split()

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
        return self.cfg['builder'].get('outer_keyname', 'pyarmor.rkey')

    @property
    def use_runtime(self):
        return self.cmd_options.get('use_runtime',
                                    self.cfg['builder'].get('use_runtime'))

    @property
    def inline_plugin_marker(self):
        marker = self.cfg['builder'].get('inline_plugin_marker', 'false')
        if marker.lower() not in ('', 'false', '0'):
            return '# %s: ' % marker

    #
    # runtime configuration
    #
    def _rt_opt(self, opt):
        return self.cmd_options.get(opt, self.cfg['runtime'].get(opt))

    @property
    def runtime_suffix(self):
        return self.license_info['licno'][-6:]

    @property
    def runtime_package_name(self):
        fmt = self.cfg.get('runtime', 'package_name_format')
        return fmt.format(suffix=self.runtime_suffix)

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
        interps = self._rt_opt('interps')
        rules = interps.splitlines() if interps else []
        cfg = self.cfg['builder']
        if cfg.getboolean('check_debugger', False):
            rules.append('check-debugger')
        if cfg.getboolean('check_interp', False):
            rules.append('check-interp')
        if self.runtime_hook('pyarmor_runtime'):
            rules.append('py:bootstrap')
        return '\n'.join(rules)

    @property
    def runtime_timer(self):
        return self._opti('runtime', 'timer')

    @property
    def runtime_simple_extension_name(self):
        return self._optb('runtime', 'simple_extension_name')

    @property
    def runtime_user_data(self):
        data = b''
        filename = self.cmd_options.get('user_data')
        if filename:
            if filename[0] == '@':
                with open(filename[1:], 'rb') as f:
                    data = f.read()
            else:
                data = filename.encode()

        return data

    @property
    def runtime_messages(self):
        value = self.cfg['runtime'].get('messages', '')
        if value:
            name, encoding = (value + ':utf-8').split(':')[:2]
            cfg = self._named_config(name, encoding=encoding)
            if cfg.has_section('runtime.message'):
                return cfg

    def runtime_package_template(self, platforms):
        return runtime_package_template if len(platforms) < 2 else \
            multi_runtime_package_template

    @property
    def runtime_obf_key_mode(self):
        return self._opti('runtime', 'obf_key_mode')

    @property
    def runtime_patch_extension(self):
        return self._opti('runtime', 'patch_extension')

    #
    # RFT settings
    #

    def rft_output_script(self, name):
        return self._check_logpath(os.path.join(self.local_path, 'rft', name))

    def rft_set_exclude_table(self, encoding=None):
        filename = os.path.join(self.local_path, 'rft_exclude_table')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding=encoding) as f:
            f.write(' '.join(self.rft_auto_excludes))

    def rft_get_exclude_table(self, encoding=None):
        filename = os.path.join(self.local_path, 'rft_exclude_table')
        if os.path.exists(filename):
            with open(filename, encoding=encoding) as f:
                return f.read().split()
        return []

    #
    # BCC settings
    #

    @property
    def bcc_build_path(self):
        path = os.path.join(self.local_path, 'bcc')
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def bcc_encoding(self):
        return self.cfg['builder'].get('encoding', 'utf-8')

    #
    # Plugin and hook
    #
    def runtime_hook(self, modname):
        for path in self.local_path, self.global_path:
            filename = os.path.join(path, 'hooks', modname + '.py')
            if os.path.exists(filename):
                encoding = self.cfg['builder'].get('encoding', 'utf-8')
                with open(filename, encoding=encoding) as f:
                    return f.read()

    def runtime_plugin(self, source, target, platforms):
        from .plugin import Plugin
        Plugin.post_runtime(self, source, target, platforms)

    #
    # Core data, new in 8.3
    #
    def _core_data(self, name):
        n = __file__.find('context.py')
        with open(__file__[:n] + name, 'rb') as f:
            return f.read()

    @property
    def core_data_1(self):
        return self._core_data('core.data.1')

    @property
    def core_data_2(self):
        return self._core_data('core.data.2')

    @property
    def core_data_3(self):
        return self._core_data('core.data.3')

    #
    # Get http proxy of token server
    #
    @property
    def token_http_proxy(self):
        http_proxy = os.environb.get(b'http_proxy', b'')
        if not http_proxy:
            return b''
        i = http_proxy.find(b'@')
        if i > 0:
            from base64 import b64encode
            header = b'Authorization: Basic %s\r\n' % b64encode(http_proxy[:i])
        else:
            header = b''
        i += 1
        j = http_proxy.find(b':', i)
        if j == -1:
            host = http_proxy[i:]
            port = b'80'
        else:
            host = http_proxy[i:j]
            port = http_proxy[j+1:]
        url = b'http://pyarmor.dashingsoft.com'
        return b'\x00'.join([host, port, url, header, b'\x00'])

    def request_token(self, url, timeout=6.0):
        from urllib.request import urlopen

        def get_response(host):
            try:
                from ssl import _create_unverified_context
                context = _create_unverified_context()
                req = 'https://%s%s' % (host, url)
            except Exception:
                context = None
                req = 'http://%s%s' % (host, url)
            return urlopen(req, None, timeout, context=context)

        with get_response('pyarmor.dashingsoft.com') as res:
            return res.read()

    #
    # Pack options for auto/onefile/onefolder mode
    #
    @property
    def pyi_options(self):
        from json import loads as json_loads
        from shlex import split as split_opt
        pyi_opts = []
        jsmarker = 'json::'
        for line in self.cfg['pack'].get('pyi_options', '').splitlines():
            line = line.strip()
            if line.startswith(jsmarker):
                pyi_opts.extend(json_loads(line[len(jsmarker):]))
            elif line.startswith('-'):
                pyi_opts.extend(split_opt(line))
            elif line:
                pyi_opts.append(line)
        return pyi_opts

    @property
    def pack_basepath(self):
        return os.path.join(self.local_path, 'pack')

    @property
    def pack_obfpath(self):
        return os.path.join(self.pack_basepath, 'dist')
