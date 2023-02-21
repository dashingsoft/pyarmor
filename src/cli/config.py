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
import logging
import os

logger = logging.getLogger('Pyarmor')


def indent(lines, n=2):
    fmt = ' ' * 2 + '%s'
    return [fmt % x for x in lines]


def str_opt(k, v, n=30):
    return '  %s = %s%s' % (k, v[:n], '...' if len(v) > n else '')


class Configer(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def list_sections(self, local=True, name=None):
        lines = ['All available sections:']
        cfg = self.ctx.cfg
        lines.extend(indent(cfg.sections()))

        lines.extend(['', 'Global sections'])
        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(self.ctx.global_config)
        lines.extend(indent(cfg.sections()))

        if local:
            lines.extend(['', 'Local sections'])
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.local_config)
            lines.extend(indent(cfg.sections()))

        if name:
            lines.extend(['', 'Private "%s" sections' % name])
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.get_filename(local, name))
            lines.extend(indent(cfg.sections()))

        return lines

    def list_options(self, sect, local=True, name=None):
        lines = ['Current options in section "%s":' % sect]

        cfg = self.ctx.cfg
        if cfg.has_section(sect):
            lines.extend([str_opt(*x) for x in cfg.items(sect)])

        lines.extend(['', 'Global options'])
        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(self.ctx.global_config)
        if cfg.has_section(sect):
            lines.extend([str_opt(*x) for x in cfg.items(sect)])

        if local:
            lines.extend(['', 'Local options'])
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.local_config)
            if cfg.has_section(sect):
                lines.extend([str_opt(*x) for x in cfg.items(sect)])

        if name:
            lines.extend(['', 'Private "%s" options' % name])
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.get_filename(local, name))
            if cfg.has_section(sect):
                lines.extend([str_opt(*x) for x in cfg.items(sect)])

        return lines

    def _list_value(self, sect, opt, local=True, name=None):
        clines, glines, lines, plines = self.infos

        def format_value(opt):
            v = cfg[sect].get(opt)
            return 'no option "%s"' % opt if v is None else str_opt(opt, v)

        cfg = self.ctx.cfg
        if cfg.has_section(sect):
            clines.append(format_value(opt))

        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(self.ctx.global_config)
        if cfg.has_section(sect) and cfg.has_option(sect, opt):
            glines.append(format_value(opt))

        if local:
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.local_config)
            if cfg.has_section(sect) and cfg.has_option(sect, opt):
                lines.append(format_value(opt))

        if name:
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.get_filename(local, name))
            if cfg.has_section(sect) and cfg.has_option(sect, opt):
                plines.append(format_value(opt))

        return clines, glines, lines, plines

    def _set_option(self, sect, opt, local=True, name=None):
        ctx = self.ctx
        filename = ctx.get_filename(local=local, name=name)

        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(filename)
        if not cfg.has_section(sect):
            cfg.add_section(sect)

        # TBD: input multiple lines
        name, value = opt.split('=', 2)
        if value and value[0] in ("'", '"'):
            value = value.strip(value[0])

        if not value:
            return self.clear(sect, name, local, name)

        logger.info('change option "%s" to new value "%s"', name, value)
        cfg.set(sect, name, value)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            cfg.write(f)

        self._list_value(sect, name, local=local, name=name)

    def remove(self, section=None, options=None, local=True, name=None):
        ctx = self.ctx
        filename = ctx.get_filename(local=local, name=name)

        if section is None:
            logger.info('remove config file "%s"', filename)
            if os.path.exists(filename):
                os.remove(filename)
            return

        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(filename)

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

    def clear(self, section=None, options=None, local=True, name=None):
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

    def run(self, section=None, options=None, local=True, name=None):
        lines = []

        if section is None:
            lines.extend(self.list_sections(local, name))

        elif not options:
            lines.extend(self.list_options(section, local, name))

        else:
            self.infos = [], [], [], []
            for opt in options:
                if opt.find('=') == -1:
                    self._list_value(section, opt, local, name)
                else:
                    self._set_option(section, opt, local, name)
            lines.extend(['', 'Current settings'])
            lines.extend(self.infos[0])
            lines.extend(['', 'Global settings'])
            lines.extend(self.infos[1])
            lines.extend(['', 'Local settings'])
            lines.extend(self.infos[2])
            if name:
                lines.extend(['', 'Private "%s" settings' % name])
                lines.extend(self.infos[3])

        print('\n'.join(lines))
