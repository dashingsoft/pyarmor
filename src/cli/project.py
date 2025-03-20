#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2024 Dashingsoft corp.                   #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 9.1.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor/cli/project.py
#
#  @Author: Jondy Zhao(pyarmor@163.com)
#
#  @Create Date: Tue Nov 12 16:38:51 CST 2024
#
#  @Description:
#
#   - Define project object for Pyarmor 9.
#   - Define project commands: init, build
#   - Define targets: std, fly, vmc, ecc, rft

"""Manage projects

Config View
-----------

[project]
global_excludes = .* __pycache__
project_includes = *.py *.pyw
package_includes = *.py *.pyw
recursive = 0

name = str
src = absolute path

modules = pattern pattern ...
packages = pattern path@name @section ...
excludes = patterh patterh ...

pypaths = path modname::path

Examples
--------

1. Create a project with scripts/packages in current path

    $ pyarmor init -r

2. Obfuscate all the scripts in the project

    $ pyarmor build --rft
    $ pyarmor build --mini

3. Config project and print project information

    $ pyarmor env -p
    $ pyarmor env -p set rft:remove_docstr 1

"""
import ast
import glob
import logging
import os
import tokenize

from collections import namedtuple
from fnmatch import fnmatch
from json import loads as jsonloads, load as jsonload
from os.path import (
    abspath, basename, exists, isabs, join as joinpath,
    normpath, relpath, splitext
)
from string import Template
from textwrap import dedent


logger = logging.getLogger('cli.build')


GRAPHVIZ_INDENT = '  '

############################################################
#
# Project File View
#
############################################################

GLOBAL_EXCLS = '.*', '__pycache__'
GLOBAL_INCLS = '*.py', '*.pyw'

ProjectItem = namedtuple(
    'ProjectItem',
    ('name', 'src', 'scripts', 'modules', 'packages',
     'excludes', 'recursive'),
    defaults=['', '', [], [], [], None, False]
)


def scan_path(path, includes=None, excludes=[], **options):
    files, dirs = [], []
    xlist = includes if includes else GLOBAL_INCLS
    with os.scandir(path) as itdir:
        for et in itdir:
            if any([fnmatch(et.name, x) for x in excludes]):
                continue
            if et.is_dir(follow_symlinks=False):
                dirs.append(et.name)
            elif (et.is_file(follow_symlinks=False) and
                  any([fnmatch(et.name, x) for x in xlist])):
                files.append(et.name)
    return files, dirs


def search_item(root, pattern, excludes, recursive=0):
    if not pattern:
        return []

    sep = os.sep if pattern.endswith(os.sep) else ''
    result = []

    pt = pattern if isabs(pattern) else joinpath(root, pattern)
    for item in glob.glob(pt, recursive=recursive):
        name = basename(item.strip(sep))
        if excludes and any([fnmatch(name, x) for x in excludes]):
            continue
        result.append(item)
    return [normpath(x) for x in result]


############################################################
#
# Concepts
#
############################################################

class Module:
    """Module concept"""

    def __init__(self, path, name=None, parent=None):
        self.parent = parent
        self._path = path
        self._name = name if name else splitext(basename(path))[0]

        self._co = None
        self._tree = None
        self._type = None

    @property
    def name(self):
        return '' if self._name == '__init__' else self._name

    @property
    def path(self):
        return self._path

    @property
    def mtype(self):
        return self._type

    @property
    def mtree(self):
        return self._tree

    @property
    def qualname(self):
        if isinstance(self.parent, (Project, type(None))):
            return self._name
        prefix = self.parent.qualname + ('.' if self.name else '')
        return prefix + self.name

    @property
    def project(self):
        """Return project this module belong to"""
        return (self.parent if isinstance(self.parent, Project)
                else self.parent.project)

    @property
    def abspath(self):
        return (self._path if isabs(self._path) else
                joinpath(self.parent.abspath, self._path))

    @property
    def destpath(self):
        s = self.qualname + ('' if self.name else '.__init__')
        return joinpath(*s.split('.')) + splitext(self.path)[-1]

    def compile_file(self, force=False):
        if self._co is not None and not force:
            return

        self.parse_file(force=force)

        logger.info('compile %s ...', self.qualname)
        self._co = compile(self._tree, self.abspath, 'exec')
        logger.info('compile %s end', self.qualname)

    def parse_file(self, force=False):
        if self._tree is not None and not force:
            return

        filename = self.abspath
        with open(filename, 'rb') as f:
            encoding, _ = tokenize.detect_encoding(f.readline)

        with open(filename, 'r', encoding=encoding) as f:
            logger.info('parse %s ...', self.qualname)
            self._tree = ast.parse(f.read(), filename, 'exec')
            logger.info('parse %s end', self.qualname)

    def _as_dot(self):
        return self.name


class Script(Module):
    """Script concept"""

    @property
    def rpaths(self):
        """Extra Python paths for importing module

        If one script has any extra pypath, it need map imported
        module name to project module name

        For example, in the script `import abc`, maybe it uses module
        `pkg.abc` in this project

        This is only used by RFT mode, otherwise it doesn't know where
        to find module `abc`

        This property is used to generate internal `_mapped_modules`
        """
        pass


class Package(Module):
    """Package concept"""

    def __init__(self, path, name=None, parent=None, excludes=[]):
        super().__init__(path, name=name, parent=parent)

        self._modules = None
        self._packages = None
        self._excludes = excludes if excludes else GLOBAL_EXCLS
        self._filters = None

    @property
    def filters(self):
        if self._filters is None:
            self._filters = []
            for x in self._excludes:
                i = x.find(':')
                if i == -1:
                    self._filters.append(x)
                elif fnmatch(self.qualname, x[:i]):
                    self._filters.append(x[i+1:])
        return self._filters

    def load(self):
        excls = self.filters
        files, dirs = scan_path(self.abspath, excludes=excls)
        self._modules = [Module(x, parent=self) for x in files]
        self._packages = [
            Package(x, parent=self, excludes=self._excludes)
            for x in dirs
        ]

    @property
    def modules(self):
        """Each package has many modules

        There is one special module `__init__` for Package
        """
        if self._modules is None:
            self.load()

        for x in self._modules:
            yield x

    @property
    def packages(self):
        """Each package has many sub-packages"""
        if self._packages is None:
            self.load()

        for x in self._packages:
            yield x

    def iter_module(self):
        if self._modules is None or self._packages is None:
            self.load()

        for x in self._modules:
            yield x

        for pkg in self._packages:
            for x in pkg.iter_module():
                yield x

    def _as_dot(self, n=0):
        modules = [x._as_dot() for x in self.modules]
        packages = [x._as_dot(n+1) for x in self.packages]
        sep = '\n' + GRAPHVIZ_INDENT
        source = Template(dedent("""\
        subgraph cluster_$cid {
          label="$name";
          $modules
          $packages
        }""")).substitute(
            cid=id(self),
            name=self.name,
            modules=sep.join(modules),
            packages=sep.join(packages),
        )
        return (
            ('\n' + GRAPHVIZ_INDENT * n).join(source.splitlines())
            if n else source
        )


class Namespace:
    """Namespace concept"""

    @property
    def name(self):
        pass

    @property
    def components(self):
        """Each component has 3 items: path, modules, children

        Each child is Namespace or Package
        """
        return []


class Project:
    """Project conpect

    Project is compose of Python elements and obfuscation settings

    Each project has 4 components:

      - Script
      - Module
      - Package
      - Namespace

    Each component has one unique name in this project except Script

    It may has alias which also can't be duplicated with other names

    Refer
    -----

    https://docs.python.org/3.13/reference/import.html#namespace-packages

    """

    ATTR_LOGFILE = '.pyarmor/project/rft_unknown_attrs.log'
    CALL_LOGFILE = '.pyarmor/project/rft_unknown_calls.log'

    def __init__(self, ctx):
        self.ctx = ctx
        self.src = ''

        self._scripts = []
        self._modules = []
        self._packages = []
        self._namespaces = []

        self._rft_options = None
        self._rft_filters = None
        self._rft_rulers = None

        self._rmodules = None
        self._builtins = None

        self._rft_type_rules = None
        self._rft_include_attrs = None
        self._used_external_types = None

        # Log variable name in chain attributes
        #
        # For example, in module "foo.py":
        #
        #   def fa(x):
        #       x.runner[0].start()
        #
        # Because don't know the type of "x", log it as
        #
        #   self.unknown_vars.append("foo:fa:x")
        #
        # self.unknown_vars = []

        # Log attribute used but not defined in class
        #
        # For example, in module "foo.py":
        #
        #   def fa(x: Fibo):
        #       x.items[0].run()
        #
        # If no found attribute "items" in class "Fibo", log it as
        #
        #   self.unknown_attrs.append("foo:fa:x.items.run ?items")
        #
        self.unknown_attrs = set()

        # Log function which called with **kwargs
        #
        # For example, in the module "foo.py":
        #
        #   class Fibo:
        #
        #       def runner(self, a=1, b=2):
        #           return a + b
        #
        #   c = Fibo()
        #   c.runner(**data)
        #
        # Because the method "Fibo.runner" is called by dict
        # argument "**data", log it as
        #
        #   self.unknown_funcs.append("foo:Fibo.runner")
        #
        self.unknown_funcs = []

        # Log unknown caller with keyword arguments.
        #
        # For example, in the module "foo.py":
        #
        #    def fa(c):
        #        c.runner[2].echo(msg='hello')
        #
        # If don't know where "echo" is defined, log it as
        #
        #     self.unknown_calls.append("foo:fa:c.runner.echo")
        #
        # If it uses dict arguments, for example:
        #
        #    def fa(c):
        #        c.runner[2].echo(**data)
        #
        # Log it with suffix "*"
        #
        #     self.unknown_calls.append("foo:fa:c.runner.echo*")
        #
        self.unknown_calls = None

        # Log all attributes which is external base class attr
        #
        # For example:
        #
        #    class C(dict):
        #
        #        def merge(self, another):
        #            super().merge(another)
        #
        # "merge" will be loged to external_attrs
        # self.external_attrs = []

    @property
    def abspath(self):
        return abspath(self.src)

    @property
    def scripts(self):
        """Project entry points

        One project may has many entry points

        Script can't be imported by other components
        """
        for x in self._scripts:
            yield x

    @property
    def modules(self):
        for x in self._modules:
            yield x

    @property
    def packages(self):
        """Only top packages"""
        for x in self._packages:
            yield x

    @property
    def namespaces(self):
        """Only top namespace"""
        for x in self._namespaces:
            yield x

    @property
    def rft_options(self):
        """Refactor options:

        - remove_assert: bool

          If 1, remove assert node

        - remove_docstr: bool

          If 1, remove all docstring

        - builtin_mode: bool

          0, do not touch any builtin names
          1, as build target, maybe std, mini or plain

        - rft_import: bool

          always 1

        - rft_ximport: bool

          Always 0, do not touch node "from..import *"

        - argument_mode: enum('0', '1', '2', '3')

          0: "no", no reform any argument node
          1: "pos", reform posonly arguments
          2: '!kw', no reform keyword only arguments
          3: "all", reform all arguments

          Note that if function is exported, no arguments reformed

        - obf_attribute: enum(no, yes, all)

          Reform attribute node to setattr() or getattr()

          0, do not reform attribute to setattr or getattr
          1, reform attribute node by rft_attribute_filters
          2, reform all attribute node

        - obf_string: enum(no, yes, all)

          Reform string constant to security mode

          It only works for std/mini target

          It's always 0 for plain target

          0, no reform string
          1, reform string by rft_string_filters
          2, reform all string

        - export_mode: bool

          True: auto export all names in module.__all__

          If class is exported, all class members are exported
          If function is exported, arguments can't be renamed
          Only module variable can be exported separately

        - exclude_names: list

          Move it from rft_filter

        - exclude_funcs: list

          Move it from rft_filter

        - rft_str_keywords: list (not implemented)

          Rename string constant or key in dict constant

          When call function, solve argument not found issue

        - rft_type_rules: dict

          Specify variable type

        - extra_type_info: dict

          Specify extra attribute for module or type

        - wildcard_import_table: dict (unused now)

          When building target, it need import module to get name
          for wildcard import, sometimes it may failed

          In order to avoid importing module in build time, users
          can provide all names in wildcard imported module

        - extra_builtins: list

          By default, builtin names is got from builtin module

          User can append extra builtin names

        - on_unknown_attr: enum(ask, log, yes, no, err)

          When don't know how to refactor attribute

            ask: query user interactively
            log: no touch attr but log it
            yes: rename attr
            no: do thing
            err: raise error
        """
        if self._rft_options is None:
            cfg = self.ctx.cfg
            sect = 'rft'
            if cfg.has_section(sect):
                self._rft_options = dict(cfg.items(sect))
            else:
                self._rft_options = {}
        return self._rft_options

    def rft_opt(self, name):
        return self.rft_options.get(name)

    @property
    def rft_exclude_names(self):
        """Exclude module, class, function

        All names in this scope aren't renamed. For example,

        Exclude module, all classes and functions aren't renamed
        Exclude class, all class attributes aren't renamed

        Each ruler is one chained names
        Each ruler must start with package or module name
        It supports pattern match as fnmatchcase
        Pattern only match one level
        """
        value = self.rft_opt('exclude_names')
        if value:
            for x in value.splitlines():
                yield x

    @property
    def rft_exclude_funcs(self):
        """No touch arguments for listed functions"""
        value = self.rft_opt('exclude_funcs')
        if value:
            for x in value.splitlines():
                yield x

    @property
    def rft_filters(self):
        if self._rft_filters is None:
            cfg = self.ctx.cfg
            sect = 'rft_filter'
            if cfg.has_section(sect):
                self._rft_filters = dict(cfg.items(sect))
            else:
                self._rft_filters = {}
        return self._rft_filters

    @property
    def obf_include_strings(self):
        """A list of re pattern based on obf_string

        All matched string in ast.Tree will be transformed
        """
        value = self.rft_filters.get('obf_include_strings', '')
        for x in value.splitlines():
            yield x

    @property
    def obf_attr_filters(self):
        """A list of re pattern based on obf_attribute

        All matched ast.Attribute will be transformed to call
        setattr() or getattr() to hide attribute name
        """
        value = self.rft_filters.get('obf_attr_filters', '')
        for x in value.splitlines():
            yield x

    @property
    def rft_rulers(self):
        if self._rft_rulers is None:
            cfg = self.ctx.cfg
            sect = 'rft_ruler'
            if cfg.has_section(sect):
                self._rft_rulers = dict(cfg.items(sect))
            else:
                self._rft_rulers = {}
        return self._rft_rulers

    @property
    def rft_attr_rules(self):
        """Refactor attribute rules, for special attribute node

        If can't decide variable type, use rule for chains

        For example, "x.a.b", if "x" of type is unknown

        Use rule "x.a.b" to rename attribute "a", "b"

        Use rule "x.a.b.c" to rename "a", "b", "c"

        Use rule "x.a.b -> *.?.*" to rename "a" only

        Use rule "*.write -> *.write" to keep all write attribute
        """
        value = self.rft_options.get('attr_rules', '')
        for x in value.splitlines():
            yield x

    @property
    def rft_call_rules(self):
        """Refactor keyword argument in call statement

        If can't decide function type, use ruler to rename arg
        """
        value = self.rft_options.get('call_rules', '')
        for x in value.splitlines():
            yield x

    @property
    def rft_arg_rules(self):
        """Refactor rule, for arg name in Function/Call node

        For example, in the call statement

            kwargs = { 'msg': 'hello' }
            foo(**kwargs)

        This kind of rule could be used to rename string `msg`
        """
        value = self.rft_options.get('rft_arg_rules', '')
        for x in value.splitlines():
            yield x

    @property
    def rft_type_rules(self):
        """Specify variable/blockvar type

        Support format:

            modname:scope:var     typename
            modname:scope:var.[?] typename
            modname:scope:func.() typename
            modname:scope:cls.method.() typename

        For blockvar in For/Comprehension/With
            modname:scope:{var}   typename
        """
        if self._rft_type_rules is None:
            vartypes = {}
            lines = self.rft_opt('var_types')
            for line in lines.splitlines() if lines else []:
                varinfo, tname = line.split()
                if varinfo.endswith('}'):
                    info = varinfo[:-1].replace('{', '')
                    modname, varname = info.split(':', 1)
                    vartypes.setdefault(modname, {})
                    mtypes = vartypes[modname]
                    mtypes.setdefault('__ivars__', {})
                    mtypes['__ivars__'][varname] = tname
                else:
                    modname, varname = varinfo.split(':', 1)
                    vartypes.setdefault(modname, {})
                    vartypes[modname][varname] = tname
            self._rft_type_rules = vartypes
        return self._rft_type_rules

    @property
    def builtins(self):
        if self._builtins is None:
            import builtins
            self._builtins = set(dir(builtins))
        return self._builtins

    @property
    def used_external_types(self):
        """Used external types"""
        if self._used_external_types is None:
            used_types = {}
            names = 'builtins'
            for name in names.split():
                if name.endswith('.json'):
                    if exists(name):
                        with open(name) as f:
                            used_types.update(jsonload(f))
                else:
                    modname = name.split('::')[0]
                    alltypes = self._get_external_types(modname)
                    if alltypes:
                        used_types.update(alltypes)
            self._used_external_types = used_types
        return self._used_external_types

    @property
    def rft_external_types(self):
        """External types manual"""
        value = self.rft_options.get('external_types', '')
        if value:
            for x in value.split():
                yield x

    @property
    def rft_external_attrs(self):
        """External attrs manual
        x means append to attrs of rft_external_types
        !x means exclude x from attrs of rft_external_types
        """
        value = self.rft_options.get('external_attrs', '')
        if value:
            for x in value.split():
                yield x

    @property
    def rft_include_attrs(self):
        """List attributes need to be renamed on unknown type"""
        if self._rft_include_attrs is None:
            self._rft_include_attrs = set()
            value = self.rft_options.get('include_attrs', '')
            if value:
                self._rft_include_attrs.update(value.split())
        return self._rft_include_attrs

    def std_options(self):
        """Obfuscation options only for std target

        - std_assert_import
        - std_assert_call
        - std_restrict_module
        - std_expired_date
        - std_bind_devices

        Got from command line, not in config file
        """
        pass

    def get_module(self, qualname):
        """Get module in the project by unique qualname
        It equals one dict: map_qualname_to_module
        """
        if self._rmodules is None:
            self._rmodules = {
                x.qualname: x for x in self.iter_module()
            }
        return self._rmodules.get(qualname)

    def iter_module(self):
        """Iterate all modules in this project"""
        for x in self._scripts:
            yield x

        for x in self._modules:
            yield x

        for child in self._packages + self._namespaces:
            for x in child.iter_module():
                yield x

    def relsrc(self, path):
        return relpath(path, self.src)

    def load(self, data):
        """Init project object with dict

        It equals:

        1. map init data to ProjectItem
        2. map ProjectItem to project files
        """
        dp = joinpath(self.ctx.local_path, 'project')
        os.makedirs(dp, exist_ok=True)

        def vlist(name):
            return [x.strip().replace('%20%', ' ')
                    for x in data.get(name, '').split()]

        src = self.src = data['src']
        name = data.get('name')
        excludes = vlist('excludes') + list(GLOBAL_EXCLS)
        proexcls = [x.strip(':') for x in excludes
                    if x.find(':') < 1]

        scripts = []
        for pat in vlist('scripts'):
            scripts.extend(search_item(src, pat, proexcls))
        self._scripts.extend([
            Script(self.relsrc(x), parent=self) for x in scripts
        ])

        modules = []
        for pat in vlist('modules'):
            modules.extend(search_item(src, pat, proexcls))

        packages = vlist('packages')
        if packages:
            for item in packages:
                # 3 forms: path, path@name, @sect
                i = item.find('@')
                if i == 0:
                    raise NotImplementedError(f'package {item}')
                if i == -1:
                    path, pkgname = item, basename(item)
                else:
                    path, pkgname = item.split('@')
                if not isabs(path):
                    path = joinpath(src, path)
                obj = Package(path,
                              name=pkgname,
                              parent=self,
                              excludes=excludes)
                self._packages.append(obj)

        recursive = data.get('recursive', '0')
        if recursive == '1':
            pkginit = joinpath(src, '__init__.py')
            if exists(pkginit):
                pkgname = name if name else basename(src)
                obj = Package(src,
                              name=pkgname,
                              parent=self,
                              excludes=excludes)
                self._packages.append(obj)
            else:
                files, dirs = scan_path(src, excludes=proexcls)
                modules.extend([joinpath(src, x) for x in files])
                self._packages.extend([
                    Package(x, parent=self) for x in dirs
                ])

        if scripts and modules:
            for x in set(scripts) & set(modules):
                logger.debug('duplicated %s', self.relsrc(x))
                modules.remove(x)
        self._modules.extend([
            Module(self.relsrc(x), parent=self) for x in modules
        ])

        logger.info('load %d scripts', len(self._scripts))
        logger.info('load %d modules', len(self._modules))
        logger.info('load %d packages', len(self._packages))

    def start(self):
        self._logfile = open(self.ATTR_LOGFILE, 'w')
        self._logfile2 = open(self.CALL_LOGFILE, 'w')

    def stop(self):
        self._logfile.close()
        self._logfile2.close()

    def log_unknown_attr(self, line):
        fields = line.split(':')
        attrs = fields[2].split('.')
        start = int(fields[3])
        self.unknown_attrs.update([
            x for x in attrs[start:] if x[:1] not in ('(', '[')
        ])
        self._logfile.write(line + '\n')

    def log_unknown_func(self, func):
        if func not in self.unknown_funcs:
            self.unknown_funcs.append(func)

    def log_unknown_call(self, line):
        self.unknown_calls = True
        self._logfile2.write(line + '\n')

    def _get_external_types(self, modname, pypaths=None):
        from sys import executable
        from subprocess import check_output, CalledProcessError, DEVNULL
        source = Template(dedent("""\
        import json
        import sys
        x = ${pypaths}
        if x:
            sys.path[0:0] = [x] if isinstance(x, str) else x
        import ${name}
        typeinfo = {'${name}': []}
        for key, value in ${name}.__dict__.items():
            if key[:2] == '__':
                continue
            if isinstance(value, type):
                typeinfo['${name}.%s' % key] = [
                    x for x in dir(value) if x[:2] != '__'
                ]
            typeinfo['${name}'].append(key)
        print(json.dumps(typeinfo))
        """)).substitute(name=modname, pypaths=repr(pypaths))

        try:
            output = check_output([executable, '-c', source], stderr=DEVNULL)
            return jsonloads(output)
        except CalledProcessError:
            pass

    def get_external_type(self, modname, clsname=None):
        if not all([x.isidentifier() for x in modname.split('.')]):
            logger.debug('invalid external module: %s', modname)
            return []

        extypes = self.used_external_types
        if modname not in extypes:
            result = self._get_external_types(modname)
            if result:
                extypes.update(result)
            if clsname is None:
                return extypes
        return extypes.get('%s.%s' % (modname, clsname), [])

    def preview_autofix_result(self, mode):
        if mode not in (2, 3):
            return
        output = f'.pyarmor/project/rft_autofix.{mode}.org'

        rulefile = '.pyarmor/project/rft_autofix.rules'
        if not exists(rulefile):
            logger.info('no found %s', rulefile)
            return
        with open(rulefile) as f:
            fixtable = jsonload(f)

        if mode == 2:
            self._preview_autofix_2(fixtable, output)
        elif mode == 3:
            self._preview_autofix_3(fixtable, output)

    def _preview_autofix_2(self, fixtable, output):
        modules = fixtable['modules']
        attrinfo = {}
        with open(self.ATTR_LOGFILE) as f:
            # Line format:
            # modname:scopes:attrs:index:begin_line,end_line
            for line in f:
                line = line.strip()
                fields = line.split(':')
                modname, scope = fields[:2]
                attrs = [x for x in fields[2].split('.')
                         if x[:1] not in ('(', '[')]
                start = int(fields[3])
                lineno = [int(x) for x in fields[4].split(',')]
                for s in attrs[start:]:
                    attrinfo.setdefault(s, [])
                    fname = modules.get(modname, modname)
                    title = ':'.join([
                        modname, scope, '.'.join(attrs)
                    ])
                    attrinfo[s].append([fname, lineno[0], title])

        header = Template(dedent("""\
        * RFT AutoFix Mode 2

        The following attributes have been renamed, if any of
        them should not be renamed, configure it as external
        attribute and run autofix mode again.

        For example, suppose `append` is external attribute:

            pyarmor env -p push rft:external_attrs append
            pyarmor build --autofix 2
            pyarmor build --rft

        Refactoring Attribute List

        $attrs

        """))
        attrsect = Template(dedent("""\
        ** $name

        $srclinks

        """))

        inattrs = fixtable.get('include_attrs', [])
        rftattrs = header.substitute(attrs='\n'.join(
            [f'[[*{x}][{x}]]' for x in inattrs]))
        with open(output, 'w') as fp:
            fp.write(rftattrs)
            for attr in inattrs:
                infos = attrinfo.get(attr)
                if infos is None:
                    continue
                fp.write(attrsect.substitute(
                    name=attr,
                    srclinks='\n'.join([
                        f'- [[file:{fname}::{n}][{title}]]'
                        for fname, n, title in infos
                    ])
                ))

    def _preview_autofix_3(self, fixtable, output):
        modules = fixtable['modules']
        confused_names = fixtable.get('confused_names', [])
        attrules = {}
        rftattrs = {}
        with open(self.ATTR_LOGFILE) as f:
            # Line format:
            # modname:scopes:attrs:index:begin_line,end_line
            for line in f:
                fields = line.strip().split(':')
                modname, scope = fields[:2]
                attrs = [x for x in fields[2].split('.')
                         if x[:1] not in ('(', '[')]
                start = int(fields[3])
                lineno = fields[4].split(',')[0]
                actions = ['*'] * start
                rnames = []
                for s in attrs[start:]:
                    if s in confused_names:
                        actions.append('?')
                        rnames.append(s)
                    else:
                        actions.append('*')
                if rnames:
                    aname = '.'.join(attrs)
                    pat = '.'.join(actions)
                    filename = modules.get(modname, modname)
                    rule = f'{modname}::{scope}:{aname} {pat}'
                    anchor = modname, filename, lineno
                    if rule not in attrules:
                        attrules[rule] = [anchor]
                    else:
                        attrules[rule].append(anchor)
                    s = rnames[0]
                    rftattrs.setdefault(s, set())
                    rftattrs[s].add(rule)

        header = Template(dedent("""\
        * RFT AutoFix Mode 3

        The following attributes have been renamed, if any of
        them should not be renamed, add one attribute rule and
        run autofix mode again.

        For example, there is one line

            *** rftbuild::log_patch_script:cfgpatch.append *.?
            - rftbuild.py::2690

        But `cfgpatch` is builtin type `list`, and its attribute
        `append` shouldn't be renamed

        In this case, replace `?` with `*`, add one rule:

            pyarmor env -p push rft:attr_rules "rftbuild::log_patch_script:cfgpatch.append *.*"

        Then rebuild the project:

            pyarmor build --autofix 3
            pyarmor build --rft

        Refactoring Attribute List

        $attrs

        """))
        attrsect = Template(dedent("""\
        ** $name

        $rules

        """))

        rulesect = Template(dedent("""\
        *** $rule
        $srclinks
        """))

        attrs = sorted(rftattrs.keys())
        with open(output, 'w') as fp:
            fp.write(header.substitute(
                attrs='\n'.join([f'[[*{x}][{x}]]' for x in attrs])
            ))
            for key in attrs:
                rules = rftattrs[key]
                rlist = []
                for r in rules:
                    infos = attrules[r]
                    rlist.append(rulesect.substitute(
                        rule=r,
                        srclinks='\n'.join([
                            f'- [[file:{s}::{n}][{m}:{n}]]'
                            for m, s, n in infos
                        ])
                    ))
                fp.write(attrsect.substitute(
                    name=key,
                    rules='\n'.join(rlist)
                ))

    def _as_dot(self):
        """Map project to dot graph"""
        modules = [x._as_dot() for x in self.modules]
        packages = [x._as_dot() for x in self.packages]
        sep = '\n' + GRAPHVIZ_INDENT * 2
        return Template(dedent("""\
        graph {
          layout=osage
          subgraph cluster_0 {
            label="Project Structure";
            $modules
            $packages
          }
        }""")).substitute(
            modules=sep.join(modules),
            packages=sep.join('\n'.join(packages).splitlines())
        )


if __name__ == '__main__':
    pass
