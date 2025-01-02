#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2024 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      Pyarmor                                              #
#                                                           #
#      Version: 9.1.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/model.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Sun Dec  8 07:36:16 CST 2024
#
from textwrap import dedent


class Item:

    def __init__(self, name, cls=None, require=False, many=False):
        self.name = name
        self.cls = cls
        self.require = require
        self.many = many


class Option:

    def __init__(self, name, parent=None, model=None):
        self.name = name
        self.parent = parent
        self.model = model
        self._value = None

    @property
    def value(self):
        if self._value is None:
            self._value = self.parent.fetch(self.name)
            if self._value is None:
                return self.model.value
        return self._value

    @value.setter
    def value(self, data: str):
        if data:
            self.check(data)
            self._value = data
            self.parent.store(self.name, data)
        else:
            self.reset()

    def check(self, data: str):
        pass

    def hints(self):
        return ''

    def usage(self):
        fmt = '%-20s: %s'
        hints = [self.hints()]
        hints.extend([(fmt % x) for x in self.model.hints()])
        if getattr(self, 'CHOICES', None):
            values = ', '.join(self.CHOICES)
            hints.append(fmt % ('Available values', values))
        hints.append('')
        return '\n'.join(hints)

    def push(self, data: str):
        items = self.value.splitlines() if self.value else []
        value = data.strip()
        if value not in items:
            items.append(value)
            self.value = '\n'.join(items)

    def pop(self, data: str):
        items = self.value.splitlines() if self.value else []
        try:
            items.remove(data.strip())
        except ValueError:
            pass
        else:
            self.value = '\n'.join(items)

    def reset(self):
        """Clear option settings"""
        self.parent.remove(self.name)
        self._value = None


class OptionModel:

    def __init__(self, name, cls=None, **kwargs):
        self.name = name
        self.cls = cls
        self.kwargs = kwargs

    def factory(self, parent):
        Cls = globals().get(self.cls, Option)
        return Cls(self.name, parent=parent, model=self)

    @property
    def many(self):
        """This option may has many values"""
        return self.kwargs.get('many', False)

    @property
    def value(self):
        """The default value for this option"""
        return self.kwargs.get('value')

    def hints(self):
        return [('Type', self.cls), ('Many', self.many)]


class PathOption(Option):
    pass


class PkgPathOption(PathOption):

    def hints(self):
        return dedent("""\
        It could be relative path or absolute path.

        If package name is different from last path, use suffix format "path@pkgname"
        """)


class FileOption(PathOption):
    pass


class BoolOption(Option):

    CHOICES = '0', '1'

    def check(self, data: str):
        if data not in self.CHOICES:
            raise ValueError('invalid %s' % repr(data))


class EnumOption(Option):

    def check(self, data: str):
        if data not in self.CHOICES:
            raise ValueError('invalid %s' % repr(data))


class TextOption(Option):
    pass


class NameOption(TextOption):
    pass


class PatternOption(TextOption):
    """re or fnmatch pattern"""
    pass


class ListOption(Option):
    pass


class DictOption(Option):
    pass


class RftAttrEnum(EnumOption):
    """When don't know how to rename attribute

      - ask: query user interactively
      - log: log it but no rename
      - yes: always rename
      - no: do thing
      - err: raise error quit
    """

    CHOICES = 'ask', 'log', 'yes', 'no', 'err'


class RftArgEnum(EnumOption):
    """How to rename argument

    - 0: no rename arguments
    - 1: rename all arguments
    - min: only rename posonly, vararg and kwarg
    - !keyword: no rename keyword only arguments
    - !default: no rename argument which has default and kwarg
    """

    CHOICES = '0', '1', '2', '3', 'no', 'min', '!kw', 'all'


class RftNamePattern(TextOption):
    """Match ast.Name in ast.Tree

    Each pattern includes 2 parts:

    - ModulePattern: fnmatchcase pattern, match module

    - NamePattern: fnmatchcase pattern, match function/class/name
    """
    pass


class RftAttrFilter(ListOption):
    """Filter ast.Attribute transformed to setattr/getattr

    Each ruler include 3 patterns

    - ModulePattern: fnmatchcase pattern, match module

    - ScopePattern: fnmatchcase pattern, match function/class

    - AttributePattern: fnmatchcase pattern, match attribute

      a: match any attribute "a"
      b.a: match only "b.a"
      a*: match any attribute startswith "a"
      b.a*: match any "b" attribute which startswith "a"
      b*.a: match any attribute "a" in parent startswith "b"
      ().a: parent is function call
      [].a: parent is subscript

      *.a: same as "a"
    """
    pass


SECTIONS = {
    'pyarmor': [],
    'finder': [],
    'builder': [],
    'pack': [],

    # Group: filter
    'assert.import': [],
    'assert.call': [],
    'mix.str': [],

    # Group bcc
    'bcc': [],

    # Scope project
    'project': [

        OptionModel(
            name='src',
            cls='PathOption',
            examples=[
                '', '.', 'src', '../src',
                '/home/jondy/project/src1',
                'my projects/project/src4'
                'C:\\test\\src2', 'C:\\工程\\src3',
            ]
        ),

        OptionModel(
            name='scripts',
            cls='FileOption',
            many=True,
            restricts=[
                'ext should be .py, .pyw',
                'relative to src, or absolute path',
            ],
            examples=['foo.py', 'test/run.py']
        ),

        OptionModel(
            name='modules',
            cls='FileOption',
            many=True,
        ),

        OptionModel(
            name='packages',
            cls='PkgPathOption',
            many=True,
        ),

        # Only match name, no path separator
        OptionModel(
            name='excludes',
            cls='PatternOption',
            many=True,
            examples=['__pycache__', 'test*']
        ),

        OptionModel(
            name='recursive',
            cls='BoolOption',
            value=0,
        ),
    ],

    'rft_option': [
        OptionModel(
            name='rft_remove_assert',
            cls='BoolOption',
            value=0,
        ),
        OptionModel(
            name='rft_remove_docstr',
            cls='BoolOption',
            value=0,
        ),
        OptionModel(
            name='rft_builtin',
            cls='BoolOption',
            value=0,
        ),
        OptionModel(
            name='rft_argument',
            cls='RftArgEnum',
            value='1',
        ),
        OptionModel(
            name='on_unknown_attr',
            cls='RftAttrEnum',
            value='log',
        ),
        OptionModel(
            name='rft_auto_export',
            cls='BoolOption',
            value=0,
        ),
        OptionModel(
            name='extra_builtins',
            cls='NameOption',
            many=True,
        ),
        OptionModel(
            name='var_type_table',
            cls='DictOption',
        ),
        OptionModel(
            name='extra_type_info',
            cls='DictOption',
        ),
        OptionModel(
            name='rft_exclude_names',
            cls='RftNamePattern',
            many=True,
        ),
        OptionModel(
            name='rft_exclude_args',
            cls='RftNamePattern',
            many=True,
        ),
        OptionModel(
            name='rft_str_keywords',
            cls='DictOption',
        ),
    ],
    'rft_filter': [
        OptionModel(
            name='obf_attribute',
            cls='BoolOption',
        ),
        OptionModel(
            name='obf_string',
            cls='BoolOption',
        ),
        OptionModel(
            name='obf_include_strings',
            cls='PatternOption',
            many=True,
        ),
        OptionModel(
            name='obf_attr_filters',
            cls='RftAttrFilter',
        ),
        OptionModel(
            name='rft_import',
            cls='BoolOption',
        ),
        OptionModel(
            name='rft_ximport',
            cls='BoolOption',
        ),
        OptionModel(
            name='wildcard_import_table',
            cls='DictOption',
        ),
    ],
}


GROUPS = {
    'filter': ('assert.import', 'assert.call', 'mix.str'),
    'bcc': ('bcc',
            'linux.x86_64.bcc', 'linux.x86.bcc',
            'linux.aarch64.bcc', 'linux.armv7.bcc',
            'darwin.x86_64.bcc', 'darwin.aarch64.bcc',
            'windows.x86_64.bcc', 'windows.x86.bcc',
            'android.x86_64.bcc', 'android.x86.bcc',
            'android.aarch64.bcc', 'android.armv7.bcc',
            'alpine.x86_64.bcc', 'alpine.aarch64.bcc',
            'freebsd.x86_64.bcc'),
}

BUSINESS_MODELS = {

    'Project': [
        Item('scripts', cls='Python.Script', many=True),
        Item('modules', cls='Python.Module', many=True),
        Item('packages', cls='Python.Package', many=True),
    ],

    'StdScript': [
        Item('script', cls='Python.Script', require=True),
        Item('pyarmor_runtime', cls='Python.Extension', require=True),
    ],

    'MiniScript': [
        Item('script', cls='Python.Script', require=True),
        Item('pyarmor_mini', cls='Python.Extension', require=True),
    ],

    'EccScript': [
        Item('script', cls='Python.Script', require=True),
        Item('pyarmor_ecc', cls='Python.Extension', require=True),
    ],

    'VmcScript': [
        Item('script', cls='Python.Script', require=True),
        Item('pyarmor_ecc', cls='Python.Extension', require=True),
    ],

    'RftScript': [
        Item('script', cls='Python.Script', require=True),
    ]
}
