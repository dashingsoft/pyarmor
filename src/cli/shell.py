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
#  @File: cli/shell.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Thu Jan 12 10:27:05 CST 2023
#
import configparser
import cmd
import os


class PyarmorShell(cmd.Cmd):

    intro = 'Welcome to the Pyarmor shell. Type help or ? to list commands.\n'
    prompt = '(pyarmor) '

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self._reset()

    def _reset(self):
        ctx = self.ctx
        cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation(),
        )
        cfg.read([ctx.default_config, ctx.global_config, ctx.local_config])
        self._cfg = cfg

    def _reset_prompt(self):
        prompts = ['(pyarmor) ']
        self.prompt = '\n'.join(prompts)

    def do_exit(self, arg):
        'Finish config and exit'
        print('Thank you for using Pyarmor')
        return True
    do_EOF = do_q = do_exit

    def do_use(self, arg):
        'Select config file'

    def do_ls(self, arg):
        '''List all the available items in current scope'''

    def do_cd(self, arg):
        '''Change scope'''

    def do_rm(self, arg):
        '''Remove item in the scope'''

    def do_set(self, arg):
        'Change option value'

    def do_show(self, arg):
        'Show option value'


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))


if __name__ == '__main__':
    PyarmorShell().cmdloop()
