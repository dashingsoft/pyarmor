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
#  @File: cli/resource.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: 2022-12-06
#
import ast
import os

from datetime import datetime
from fnmatch import fnmatch
from string import Template


class Resource(object):

    def __init__(self, path, name=None, parent=None):
        self.parent = parent
        self.path = path
        self.name = name if name else self._format_name(path)

    def __str__(self):
        return self.fullname

    def _format_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]

    def is_top(self):
        return self.parent is None

    def is_script(self):
        return isinstance(self, (FileResource, PycResource))

    @property
    def fullname(self):
        return self.name if self.is_top() else \
            '.'.join([self.parent.fullname, self.name])

    @property
    def fullpath(self):
        return self.path if self.is_top() else \
            os.path.join(self.parent.fullpath, self.path)

    @property
    def pkgname(self):
        # if input path is '.', then pkgname will start with '..'
        suffix = '.__init__'
        if self.fullname.endswith(suffix):
            return self.fullname[:-len(suffix)]
        return self.fullname

    @property
    def output_path(self):
        return '' if self.is_top() else \
            os.path.join(self.parent.output_path, self.parent.name)


class FileResource(Resource):

    def __init__(self, path, name=None, parent=None):
        super().__init__(path, name=name, parent=parent)

        self.mtree = None
        self.mco = None

        self.shebang = ''

        # Do not touch these nodes in final protector
        self.exclude_nodes = set()
        # Do not touch these code objects in final patcher
        self.exclude_co_objects = set()

    def __str__(self):
        return 'file %s%s' % (self.name, self.pyext)

    def __iter__(self):
        yield self

    @property
    def pyext(self):
        return os.path.splitext(self.path)[-1]

    @property
    def output_filename(self):
        return os.path.join(self.output_path, self.name + self.pyext)

    @property
    def frozenname(self):
        n = self.fullname.find('.__init__')
        return '<frozen %s>' % self.fullname[:None if n == -1 else n]

    @property
    def is_pyc(self):
        return self.pyext.lower() == '.pyc'

    def _get_encoding(self, encoding):
        from codecs import BOM_UTF8
        from re import search as research
        with open(self.fullpath, 'rb') as f:
            line = f.read(80)
            if line and line[:3] == BOM_UTF8:
                return 'utf-8'
            if line and line[0] == 35:
                n = line.find(b'\n')
                m = research(r'coding[=:]\s*([-\w.]+)', line[:n].decode())
                if m:
                    return m.group(1)
                if n > -1 and len(line) > (n+1) and line[n+1] == 35:
                    k = n + 1
                    n = line.find(b'\n', k)
                    m = research(r'coding[=:]\s*([-\w.]+)', line[k:n].decode())
                    return m and m.group(1)
        return encoding

    def readlines(self, encoding=None):
        if not os.path.exists(self.fullpath):
            raise RuntimeError('file "%s" doesn\'t exists' % self.fullpath)

        with open(self.fullpath, encoding=self._get_encoding(encoding)) as f:
            # file.read() can't read the whole data of big files
            lines = f.readlines()
            if lines and lines[0].startswith('#!'):
                self.shebang = lines[0]
            return lines

    def reparse(self, lines=None, encoding=None):
        if lines is None:
            lines = self.readlines(encoding=encoding)
        self.mtree = ast.parse(''.join(lines), self.frozenname, 'exec')

    def _recompile_pyc(self):
        from importlib._bootstrap_external import SourcelessFileLoader
        path, name = self.fullpath, self.pkgname
        self.mco = SourcelessFileLoader(name, path).get_code(name)

    def recompile(self, mtree=None, optimize=1):
        if self.is_pyc:
            return self._recompile_pyc()

        if mtree is None:
            mtree = self.mtree
        assert (mtree is not None)
        self.mco = compile(mtree, self.frozenname, 'exec', optimize=optimize)

    def clean(self):
        self.lines = None
        self.mtree = None
        self.mco = None
        if hasattr(self, 'jit_iv'):
            self.jit_iv = None
        if hasattr(self, 'jit_data'):
            self.jit_data = None

    def generate_output(self, tpl, code, relative=0, pkgname='pyarmor_runtime',
                        bootpath='__file__', rev=''):
        if relative == 0:
            prefix = ''
        elif relative == 1:
            prefix = '.' * self.fullname.count('.')
        else:
            assert (isinstance(relative, str))
            prefix = relative + '.'
            if self.fullname.startswith(prefix):
                prefix = '.' * self.fullname.count('.')
            elif prefix.startswith(self.pkgname + '.'):
                prefix = prefix[len(self.pkgname):]

        source = Template(tpl).safe_substitute(
            timestamp=datetime.now().isoformat(),
            package=prefix + pkgname,
            path=bootpath,
            code=repr(code),
            rev=rev)
        return (self.shebang + source) if self.shebang else source


class PycResource(FileResource):

    def recompile(self, mtree=None, optimize=1):
        from importlib._bootstrap_external import SourcelessFileLoader
        path, name = self.fullpath, self.pkgname
        self.mco = SourcelessFileLoader(name, path).get_code(name)


class PathResource(Resource):

    def __init__(self, path, name=None, parent=None):
        super().__init__(path, name=os.path.basename(path), parent=parent)
        self.respaths = []
        self.resfiles = []

    def __str__(self):
        return 'path %s' % self.fullname

    def __iter__(self):
        for res in self.resfiles:
            if res:
                yield res
        for child in self.respaths:
            for res in child:
                yield res

    def rebuild(self, **options):
        pyexts = options.get('pyexts', ['.py'])
        recursive = options.get('recursive', False)
        includes = options.get('includes', '').split()
        excludes = options.get('excludes', '').split()
        patterns = options.get('data_files', '').split()

        def in_filter(path, name):
            fullpath = os.path.join(path, name)
            ext = os.path.splitext(name)[1]
            return not ex_filter(path, name) and (
                (ext and ext in pyexts)
                or any([fnmatch(fullpath, x) for x in includes]))

        def ex_filter(path, name):
            fullpath = os.path.join(path, name)
            return excludes and any([fnmatch(fullpath, x) for x in excludes])

        def is_res(path, name):
            s = os.path.join(path, name)
            return any([fnmatch(s, x) for x in patterns])

        for path, dirnames, filenames in os.walk(self.fullpath):
            self.resfiles = [x for x in [
                FileResource(name, parent=self) if in_filter(path, name)
                else Resource(name, parent=self) if is_res(path, name)
                else None for name in filenames
            ] if x]
            self.respaths = [PathResource(name, parent=self)
                             for name in dirnames
                             if not ex_filter(path, name)]
            break

        if recursive:
            for res in self.respaths:
                res.rebuild(**options)
