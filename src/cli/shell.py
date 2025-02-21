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
#  @File: cli/shell.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Fri Nov 15 10:52:00 CST 2024
#
import configparser
import cmd
import shlex

from .model import SECTIONS, GROUPS


class CfgEntity:
    """Store option to cfg file"""

    def __init__(self, cfgfiles, encoding=None):
        self._cfgfiles = cfgfiles
        self._reader = None
        self._writer = None
        self._index = -1
        self._encoding = encoding

    def _load_cfg(self, filenames):
        cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation(),
        )
        cfg.read(filenames, encoding=self._encoding)
        return cfg

    @property
    def cfgfile(self):
        return self._cfgfiles[self._index]

    @property
    def reader(self):
        if self._reader is None:
            self._reader = self._load_cfg(self._cfgfiles)
        return self._reader

    @property
    def writer(self):
        if self._writer is None:
            self._writer = self._load_cfg(self.cfgfile)
        return self._writer

    def store(self, sect, opt, value):
        for cfg in (self.writer, self.reader):
            if not cfg.has_section(sect):
                cfg.add_section(sect)
            cfg.set(sect, opt, value)

    def fetch(self, sect, opt):
        cfg = self.reader
        if cfg.has_section(sect):
            return cfg[sect].get(opt, None)

    def remove(self, sect, opt=None):
        for cfg in (self.writer, self.reader):
            if cfg.has_section(sect):
                if opt is None:
                    cfg.remove_section(sect)
                else:
                    cfg.remove_option(sect, opt)

    def reset(self, index):
        if self._index == index:
            return
        self._index = index
        self._reader = self._writer = None

    def save(self):
        with open(self.cfgfile, 'w') as f:
            self.writer.write(f)


class Domain:

    def __init__(self, name, default='pyarmor'):
        self.name = name
        self._dirty = False

        self._sections = []
        self._groups = []

        self._default = Section(default, parent=self)
        self._cfgentity = None
        self._children = None

    @property
    def qualname(self):
        return self.name

    @property
    def title(self):
        return '(%s) ' % self.name

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value

    @property
    def groups(self):
        for x in self._groups:
            yield x

    @property
    def sections(self):
        for x in self._sections:
            yield x

    @property
    def options(self):
        if self._default:
            for x in self._default.options:
                yield x

    @property
    def children(self):
        if self._children is None:
            items = {x.name: x for x in self.groups}
            items.update({x.name: x for x in self.sections})
            self._children = items
        return self._children

    @property
    def cfgentity(self):
        return self._cfgentity

    def link(self, cfgentity):
        self._cfgentity = cfgentity

    def save(self, force=False):
        cfgentity = self._cfgentity
        if (self.dirty or force) and cfgentity:
            cfgentity.save()
            self._dirty = False

    def add_section(self, name):
        if self._default and self._default.name == name:
            return
        self._sections.append(Section(name, parent=self))

    def add_group(self, name, sections):
        group = Group(name, parent=self)
        group.add_sections(sections)
        self._groups.append(group)


class Section:

    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.models = SECTIONS.get(name, [])
        self._options = None
        self._children = {}

    @property
    def qualname(self):
        parent = self.parent
        name = self.name
        return ':'.join([parent.qualname, name])

    @property
    def title(self):
        return '({0})[{1}] '.format(*self.qualname.split(':', 1))

    @property
    def options(self):
        if self._options is None:
            self._options = [x.factory(self) for x in self.models]

        for x in self._options:
            yield x

    @property
    def children(self):
        return self._children

    @property
    def cfgentity(self):
        return self.parent.cfgentity

    def store(self, opt, value):
        self.cfgentity.store(self.name, opt, value)

    def fetch(self, opt):
        return self.cfgentity.fetch(self.name, opt)

    def remove(self, opt):
        self.cfgentity.remove(self.name, opt)


class Group(Section):

    def __init__(self, name, parent=None, sections=None):
        super().__init__(name, parent=parent)
        self._groups = []
        self._sections = []

    @property
    def group(self):
        for x in self._group:
            yield x

    @property
    def sections(self):
        for x in self._sections:
            yield x

    @property
    def children(self):
        if self._children is None:
            items = {x.name: x for x in self.groups}
            items.update({x.name: x for x in self.sections})
            self._children = items
        return self._children

    def add_group(self, name, sections):
        group = Group(name, parent=self)
        group.add_sections(sections)
        self._group.append(group)

    def add_sections(self, sections):
        self._sections.extend([
            Section(x, parent=self) for x in sections
        ])


class PyarmorShell(cmd.Cmd):

    intro = 'Type help or ? to list commands.\n'
    col = 60

    def __init__(self, ctx, domain='local'):
        super().__init__()
        self.ctx = ctx
        self._entity = CfgEntity([
            ctx.default_config,
            ctx.global_config,
            ctx.local_config
        ])
        self._domains = self._init_domains()
        self._domain = self._section = self._domains[domain]

    def _init_domains(self):
        gs = Domain('global')
        ls = Domain('local')
        ps = Domain('project', default='project')

        gs.link(self._entity)
        ls.link(self._entity)
        ps.link(self._entity)

        sections = 'finder', 'builder', 'runtime', 'pack'
        [(gs.add_section(x), ls.add_section(x)) for x in sections]

        for domain in (gs, ls):
            for name in ('filter', 'bcc'):
                domain.add_group(name, GROUPS[name])

        ps.add_section('rft')

        return {'global': gs, 'local': ls, 'project': ps}

    @property
    def section(self):
        return self._section

    @property
    def prompt(self):
        return self.section.title

    def get_sections(self, name=''):
        obj = self.section
        sects = [x for x in getattr(obj, 'groups', [])]
        sects.extend([x for x in getattr(obj, 'sections', [])])
        return (sects if name in ('-a', '*', '') else
                [x for x in sects if x.name.startswith(name)])

    def get_options(self, name=''):
        options = [x for x in self.section.options]
        return (options if name in ('-a', '*', '') else
                [x for x in options if x.name.startswith(name)])

    def printf(self, *args):
        print(*args)

    def find(self, opt):
        for item in self.section.options:
            if item.name == opt:
                return item

    def save(self):
        self._domain.save()

    def do_exit(self, arg=None):
        """Finish config and exit"""
        self.save()
        self.printf('')
        self.printf('Thank you for using Pyarmor')
        return True
    do_EOF = do_q = do_exit

    def do_use(self, arg):
        """Switch domain: global, local, project"""
        names = list(self._domains.keys())
        if arg not in names:
            self.printf('Invalid name: ', arg)
            self.printf('Please type one of', str(names))
        elif self._domain.name == arg:
            pass
        else:
            self._domain.save()
            if arg == 'global':
                self._entity.reset(index=1)
            elif self._domain.name == 'global':
                self._entity.reset(index=-1)
            self._domain = self._domains[arg]
            self._section = self._domain

    def do_ls(self, arg):
        """List all the available items in current domain"""
        sections = self.get_sections(arg)
        if sections:
            self.printf('Sections:')
            self.columnize([x.name for x in sections], self.col)
            self.printf('')

        options = self.get_options(arg)
        if options:
            self.printf('Options:')
            self.columnize([x.name for x in options], self.col)
            self.printf('')

    def do_cd(self, arg):
        """Switch to section, .. to parent, blank to top"""
        if arg == '..':
            if self._section is not self._domain:
                self._section = self._section.parent
        elif arg:
            item = self.section.children.get(arg)
            if item:
                self._section = item
            else:
                self.printf('No item', repr(arg))
        else:
            self._section = self._domain

    def do_get(self, arg):
        """Show option value"""
        options = self.get_options(arg)
        if not options:
            self.printf('No found any', repr(arg))
            return
        for opt in options:
            value = opt.value
            if value is not None:
                self.printf('%-20s= %s' % (opt.name, value))

    def do_info(self, arg):
        """List sections, options, and all the values"""
        if arg == '':
            self.do_ls('')
            self.do_get('')
            return
        item = self.section.children.get(arg)
        if item:
            self.do_cd(arg)
            self.do_ls('')
            self.do_get('')
            self.do_cd('..')
        else:
            item = self.find(arg)
            if item:
                self.printf(item.usage())
                self.do_get(arg)
            else:
                self.printf('No found', arg)

    def do_set(self, arg):
        """Set option value"""
        if arg.find(' ') == -1:
            self.printf('Missing value')
            return
        name, value = arg.split(None, 1)
        item = self.find(name)
        if item:
            c = value[:1]
            if c in ('"', "'"):
                value = value.strip(c)
            try:
                item.value = value
                self._domain.dirty = True
            except ValueError as e:
                self.printf(str(e))
        else:
            self.printf('No found', name)

    def do_reset(self, arg):
        """Reset option in the domain"""
        if arg in ('', '*'):
            self.printf('Please specify one option')
            return
        item = self.find(arg)
        if item:
            item.reset()
            self._domain.dirty = True
        else:
            self.printf('No found', arg)

    def do_push(self, arg, silent=False):
        """Append new value to option"""
        if arg.find(' ') == -1:
            self.printf('Missing value')
            return
        name, value = arg.split(None, 1)
        item = self.find(name)
        if item:
            for x in shlex.split(value):
                try:
                    item.push(x)
                except ValueError as e:
                    self.printf(str(e))
                    break
            else:
                self._domain.dirty = True
                self.do_get(name)
        else:
            self.printf('No found', name)

    def do_pop(self, arg):
        """Remove one choice from option"""
        if arg.find(' ') == -1:
            self.printf('Missing value')
            return
        name, value = arg.split(None, 1)
        item = self.find(name)
        if item:
            for x in shlex.split(value):
                item.pop(x)
            self._domain.dirty = True
            self.do_get(name)
        else:
            self.printf('No found', name)


if __name__ == '__main__':
    from os.path import join as joinpath, abspath, expanduser

    from .context import Context

    home = joinpath('~', '.pyarmor')
    home = abspath(expanduser(home))

    ctx = Context(home)
    PyarmorShell(ctx).cmdloop()
