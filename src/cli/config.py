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

    def list_value(self, sect, opt, local=True, name=None):
        lines = ['Current settings']
        cfg = self.ctx.cfg
        if cfg.has_section(sect):
            lines.append(str_opt(opt, cfg[sect].get(opt, '')))

        lines.extend(['', 'Global settings'])
        cfg = configparser.ConfigParser(empty_lines_in_values=False)
        cfg.read(self.ctx.global_config)
        if cfg.has_section(sect):
            lines.append(str_opt(opt, cfg[sect].get(opt, '')))

        if local:
            lines.extend(['', 'Local settings'])
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.local_config)
            if cfg.has_section(sect):
                lines.append(str_opt(opt, cfg[sect].get(opt, '')))

        if name:
            lines.extend(['', 'Private "%s" settings' % name])
            cfg = configparser.ConfigParser(empty_lines_in_values=False)
            cfg.read(self.ctx.get_filename(local, name))
            if cfg.has_section(sect):
                lines.append(str_opt(opt, cfg[sect].get(opt, '')))

        return lines

    def set_option(self, sect, opt, local=True, name=None):
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

        return self.list_value(sect, name, local=local, name=name)

    def clear(self, section=None, option=None, local=True, name=None):
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
            if option is None:
                logger.info('remove section "%s"', section)
                cfg.remove_section(section)

            elif cfg.has_option(section, option):
                logger.info('remove option "%s:%s"', section, option)
                cfg.remove_option(section, option)

                if not cfg.options(section):
                    logger.info('remove empty section "%s"', section)
                    cfg.remove_section(section)

            with open(filename, 'w') as f:
                cfg.write(f)

    def run(self, section=None, option=None, local=True, name=None):
        lines = []
        if section is None:
            lines.extend(self.list_sections(local, name))
        elif option is None:
            lines.extend(self.list_options(section, local, name))
        else:
            if option.find('=') == -1:
                lines.extend(self.list_value(section, option, local, name))
            else:
                lines.extend(self.set_option(section, option, local, name))
        print('\n'.join(lines))
