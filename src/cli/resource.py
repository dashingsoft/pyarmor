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
from fnmatch import fnmatchcase
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
        return isinstance(self, FileResource)

    @property
    def fullname(self):
        return self.name if self.is_top() else \
            '.'.join([self.parent.fullname, self.name])

    @property
    def fullpath(self):
        return self.path if self.is_top() else \
            os.path.join(self.parent.fullpath, self.path)


class FileResource(Resource):

    def __init__(self, path, name=None, parent=None):
        super().__init__(path, name=name, parent=parent)

        self.mtree = None
        self.mco = None

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
        return self.fullname.replace('.', os.path.sep) + self.pyext

    def readlines(self, encoding=None):
        if not os.path.exists(self.fullpath):
            raise RuntimeError('file "%s" doesn\'t exists' % self.fullpath)

        with open(self.fullpath, encoding=encoding) as f:
            # file.read() can't read the whole data of big files
            return f.readlines()

    def reparse(self, lines=None, encoding=None):
        if lines is None:
            lines = self.readlines(encoding=encoding)
        co_filename = '<%s>' % self.fullname
        self.mtree = ast.parse(''.join(lines), co_filename, 'exec')

    def recompile(self, mtree=None, optimize=1):
        if mtree is None:
            mtree = self.mtree
        assert mtree is not None
        co_filename = '<%s>' % self.fullname
        self.mco = compile(mtree, co_filename, 'exec', optimize=optimize)

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
            prefix = '.' * (self.fullname.count('.') + relative - 1)
        else:
            assert(isinstance(relative, str))
            prefix = relative + '.'
            if self.fullname.startswith(prefix):
                prefix = '.' * (self.fullname.count('.') + 1)

        return Template(tpl).safe_substitute(
            timestamp=datetime.now().isoformat(),
            package=prefix + pkgname,
            path=bootpath,
            code=repr(code),
            rev=rev)


class PathResource(Resource):

    def __init__(self, path, name=None, parent=None):
        super().__init__(path, name=name, parent=parent)
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
        includes = options.get('includes', [])
        excludes = options.get('excludes', [])
        patterns = options.get('data_files', '').split()

        def in_filter(name):
            return not ex_filter(name) and (
                os.path.splitext(name)[1] in pyexts
                or any([fnmatchcase(name, x) for x in includes]))

        def ex_filter(name):
            return excludes and any([fnmatchcase(name, x) for x in excludes])

        def is_res(name):
            return any([fnmatchcase(name, x) for x in patterns])

        for dirpath, dirnames, filenames in os.walk(self.fullpath):
            self.resfiles = [FileResource(name, parent=self) if in_filter(name)
                             else Resource(name, parent=self) if is_res(name)
                             else None for name in filenames]
            self.respaths = [PathResource(name, parent=self)
                             for name in dirnames
                             if not ex_filter(name)]
            break

        if recursive:
            for res in self.respaths:
                res.rebuild(recursive=True)
