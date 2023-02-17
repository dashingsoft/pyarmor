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
        self._scopes = ['global']
        self._cfg = None
        self._reset()

    def _reset(self):
        self._filename = self.ctx.global_config
        self._cfg = configparser.ConfigParser(empty_lines_in_values=False)
        self._cfg.read(self._filename, encoding=self.ctx.encoding)
        self._scopes = ['global', self._filename]

    def _reset_prompt(self):
        prompts = ['(pyarmor) ']
        if self._scopes:
            prompts.insert(0, '::'.join(self._scopes))
        self.prompt = '\n'.join(prompts)

    @property
    def global_path(self):
        return os.path.join(self.ctx.home_path, 'config')

    @property
    def local_path(self):
        return '.pyarmor'

    def do_exit(self, arg):
        'Finish config and exit'
        print('Thank you for using Pyarmor')
        return True
    do_EOF = do_q = do_exit

    def do_global(self, arg):
        'Select global scope'
        self._reset()

    def do_local(self, arg):
        'Select local scope'
        self._filename = self.ctx.local_config
        self._cfg = configparser.ConfigParser(empty_lines_in_values=False)
        self._cfg.read(self._filename, encoding=self.ctx.encoding)
        self._scopes = ['local', self._filename]

    def do_new(self, arg):
        'Create config in global/local scope'
        scope = self._scopes[0]
        path = self.global_path if scope == 'global' else self.local_path
        self._filename = os.path.join(path, arg)
        self._scopes = [scope, self._filename]

    def do_use(self, arg):
        'Select config file'
        scope = self._scopes[0]
        path = self.global_path if scope == 'global' else self.local_path
        self._filename = os.path.join(path, arg)
        self._cfg = configparser.ConfigParser(empty_lines_in_values=False)
        self._cfg.read(self._filename, encoding=self.ctx.encoding)
        self._scopes = [scope, self._filename]

    def do_ls(self, arg):
        '''List all the available items in current scope
        list all config files in scope
        list all sections in file scope
        list all options in section scope
        list option hint in option scope
        '''

    def do_cd(self, arg):
        '''Change scope'''

    def do_rm(self, arg):
        '''Remove item in the scope'''

    def do_get(self, arg):
        'Show option value'

    def do_set(self, arg):
        'Change option value'


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))


if __name__ == '__main__':
    PyarmorShell().cmdloop()
