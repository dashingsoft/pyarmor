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
#  @File: cli/config.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Thu Jan 12 10:27:05 CST 2023
#
import configparser
import fnmatch
import os

from . import logger, CliError


def indent(lines, n=2):
    fmt = ' ' * 2 + '%s'
    return [fmt % x for x in lines]


def str_opt(k, v, n=30):
    v = '\n\t'.join(v.splitlines())
    return '  %s = %s%s' % (k, v[:n], '...' if len(v) > n else '')


class Configer(object):

    SECTIONS = 'pyarmor', 'logging', 'finder', 'builder', 'runtime', \
        'pack', 'bcc', 'mix.str', 'assert.call', 'assert.import'

    def __init__(self, ctx, encoding=None):
        self.ctx = ctx
        self._encoding = encoding

    def _read_config(self, filename):
        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(filename, encoding=self._encoding)
        return cfg

    def list_sections(self, local=True, name=None):
        lines = ['All available sections:']
        cfg = self.ctx.cfg
        lines.extend(indent(self.SECTIONS))

        lines.extend(['', 'Global sections'])
        cfg = self._read_config(self.ctx.global_config)
        lines.extend(indent(cfg.sections()))

        if local:
            lines.extend(['', 'Local sections'])
            cfg = self._read_config(self.ctx.local_config)
            lines.extend(indent(cfg.sections()))

        if name:
            lines.extend(['', 'Private "%s" sections' % name])
            cfg = self._read_config(self.ctx.get_filename(local, name))
            lines.extend(indent(cfg.sections()))

        return lines

    def list_options(self, sect, local=True, name=None):
        lines = ['Current options']

        cfg = self.ctx.cfg
        if cfg.has_section(sect):
            lines.extend([str_opt(*x) for x in cfg.items(sect)])

        lines.extend(['', 'Global options'])
        cfg = self._read_config(self.ctx.global_config)
        if cfg.has_section(sect):
            lines.extend([str_opt(*x) for x in cfg.items(sect)])

        if local:
            lines.extend(['', 'Local options'])
            cfg = self._read_config(self.ctx.local_config)
            if cfg.has_section(sect):
                lines.extend([str_opt(*x) for x in cfg.items(sect)])

        if name:
            lines.extend(['', 'Private "%s" options' % name])

            cfg = self._read_config(self.ctx.get_filename(local, name))
            if cfg.has_section(sect):
                lines.extend([str_opt(*x) for x in cfg.items(sect)])

        return lines

    def _list_value(self, sect, opt, local=True, name=None):
        clines, glines, lines, plines = self.infos

        def format_value(opt):
            v = cfg[sect].get(opt)
            n = 1 << 30
            return 'no option "%s"' % opt if v is None else str_opt(opt, v, n)

        cfg = self.ctx.cfg
        if cfg.has_section(sect):
            clines.append(format_value(opt))

        cfg = self._read_config(self.ctx.global_config)
        if cfg.has_section(sect) and cfg.has_option(sect, opt):
            glines.append(format_value(opt))

        if local:
            cfg = self._read_config(self.ctx.local_config)
            if cfg.has_section(sect) and cfg.has_option(sect, opt):
                lines.append(format_value(opt))

        if name:
            cfg = self._read_config(self.ctx.get_filename(local, name))
            if cfg.has_section(sect) and cfg.has_option(sect, opt):
                plines.append(format_value(opt))

        return clines, glines, lines, plines

    def _set_option(self, sect, opt, value, local=True, name=None):
        ctx = self.ctx
        filename = ctx.get_filename(local=local, name=name)

        cfg = self._read_config(filename)
        if not cfg.has_section(sect):
            cfg.add_section(sect)

        # TBD: input multiple lines
        optname, optvalue = opt, value
        if optvalue and optvalue[:1] in ('+', '-', '=', '^'):
            op = optvalue[:1]
            optvalue = optvalue.strip(op)
            if op == '=':
                op = None
        else:
            op = None
        if optvalue and optvalue[:1] in ("'", '"'):
            optvalue = optvalue.strip(optvalue[0])

        if not optvalue:
            if op is None:
                self._remove(sect, [optname], local, name)
            return

        ctxcfg = ctx.cfg
        old = ctxcfg[sect].get(optname, '') if ctxcfg.has_section(sect) else ''

        if op == '+':
            if (optvalue + ' ').find(old + ' ') == -1:
                optvalue = ('%s %s' % (old, optvalue)).strip()
        elif op == '-':
            optvalue = (old + ' ').replace(optvalue + ' ', '').strip()
        elif op == '^':
            optvalue = '\n'.join((old.splitlines() + [optvalue]))

        logger.info('change option "%s" to new value "%s"', optname, optvalue)
        cfg.set(sect, optname, optvalue)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            cfg.write(f)

        self._list_value(sect, optname, local=local, name=name)

    def _remove(self, section=None, options=None, local=True, name=None):
        ctx = self.ctx
        filename = ctx.get_filename(local=local, name=name)

        if section is None:
            logger.info('remove config file "%s"', filename)
            if os.path.exists(filename):
                os.remove(filename)
            return

        cfg = self._read_config(filename)

        if cfg.has_section(section):
            if not options:
                logger.info('remove section "%s"', section)
                cfg.remove_section(section)
            else:
                for opt in [x for x in options if cfg.has_option(section, x)]:
                    logger.info('remove option "%s:%s"', section, opt)
                    cfg.remove_option(section, opt)

                    if not cfg.options(section):
                        logger.info('remove empty section "%s"', section)
                        cfg.remove_section(section)

            with open(filename, 'w') as f:
                cfg.write(f)

    def _clear(self, section=None, options=None, local=True, name=None):
        ctx = self.ctx
        scope = '%s%s config file' % (
            'local' if local else 'global',
            ' "%s"' % name if name else ''
        )
        filename = ctx.get_filename(local=local, name=name)

        if not filename:
            logger.info('no %s', scope)
            return

        logger.info('remove %s "%s"', scope, filename)
        if os.path.exists(filename):
            os.remove(filename)

    def _parse_opt(self, opt):
        i = opt.find(':')
        if i == -1:
            j = opt.find('=')
            pat, v = (opt, '') if j == -1 else (opt[:j], opt[j:])
            cfg = self.ctx.cfg
            rlist = []
            for sect in self.SECTIONS:
                if cfg.has_section(sect):
                    rlist.append((sect, [x+v for x in cfg.options(sect)
                                         if fnmatch.fnmatch(x, pat)]))
            return [x for x in rlist if x[1]]
        else:
            return [(opt[:i], [opt[i+1:]])]

    def reset(self, options=None, local=True, name=None):
        for pat in options:
            for sect, opts in self._parse_opt(pat):
                self._remove(sect, opts, local, name)

    def run(self, options=None, local=True, name=None):
        lines = []

        if options and len(options) == 1 and options[0].find('=') == -1:
            for sect, opts in self._parse_opt(options[0]):
                title = 'Section: %s' % sect
                lines.extend(['', '-' * 60, title])
                self.infos = [], [], [], []

                for opt in opts:
                    self._list_value(sect, opt, local, name)

                lines.extend(['', 'Current settings'])
                lines.extend(self.infos[0])
                lines.extend(['', 'Global settings'])
                lines.extend(self.infos[1])
                lines.extend(['', 'Local settings'])
                lines.extend(self.infos[2])
                if name:
                    lines.extend(['', 'Private "%s" settings' % name])
                    lines.extend(self.infos[3])

        elif options:
            pairs = []
            prev, op = None, ''
            for opt in options:
                i = opt.find('=')
                if i > 0:
                    pairs.append([opt[:i], opt[i+1:]])
                elif opt in ('+', '=', '-', '^'):
                    op = opt
                elif prev:
                    pairs.append((prev, op + opt))
                    prev, op = None, ''
                else:
                    prev = opt
            if prev:
                raise CliError('no value for option "%s"' % prev)

            for pat, value in pairs:
                sect_opts = self._parse_opt(pat)
                if not sect_opts:
                    logger.debug('new builder option "%s"', pat)
                    sect_opts = [('builder', [pat])]
                for sect, opts in sect_opts:
                    title = 'Section: %s' % sect
                    lines.extend(['', '-' * 60, title])
                    self.infos = [], [], [], []

                    for opt in opts:
                        self._set_option(sect, opt, value, local, name)

                    lines.extend(['', 'Current settings'])
                    lines.extend(self.infos[0])
                    lines.extend(['', 'Global settings'])
                    lines.extend(self.infos[1])
                    lines.extend(['', 'Local settings'])
                    lines.extend(self.infos[2])
                    if name:
                        lines.extend(['', 'Private "%s" settings' % name])
                        lines.extend(self.infos[3])

        else:
            for sect in self.SECTIONS:
                title = 'Section: %s' % sect
                lines.extend(['', '-' * 60, title, ''])
                lines.extend(self.list_options(sect, local, name))

        print('\n'.join(lines))
