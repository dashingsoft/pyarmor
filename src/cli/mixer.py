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
#  @File: cli/mixer.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: 2022-12-06
#
import ast

from random import randint


class StrNodeTransformer(ast.NodeTransformer):

    def _reform_str(self, s):
        encoding = getattr(self, 'encoding')
        value = bytearray(s.encode(encoding) if encoding else s.encode())
        key = [randint(0, 255)] * len(value)
        data = [x ^ y for x, y in zip(value, key)]
        expr = 'bytearray([%s]).decode(%s)' % (
            ','.join(['%s ^ %s' % k for k in zip(data, key)]),
            '' if encoding is None else repr(encoding))
        return ast.parse(expr).body[0].value

    def _reform_value(self, value):
        if isinstance(value, str):
            return self._reform_str(value)

        elif isinstance(value, dict):
            return ast.Dict(**{
                'keys': [ast.Constant(value=x) for x in value.keys()],
                'values': [self._reform_str(x) if isinstance(x, str)
                           else self._reform_value(x) for x in value.values()]
            })

        elif isinstance(value, (list, tuple, set)):
            elts = [self._reform_str(x) if isinstance(x, str)
                    else self._reform_value(x) for x in value]
            if isinstance(value, set):
                return ast.Set(elts=elts)
            else:
                cls = ast.List if isinstance(value, list) else ast.Tuple
                return cls(elts=elts, ctx=ast.Load())

        else:
            return ast.Constant(value=value)

    def reform_node(self, node):
        value = node.s if isinstance(node, ast.Str) else node.value
        if not isinstance(value, (list, tuple, set, dict, str)):
            return node

        obfnode = self._reform_value(value)
        ast.copy_location(obfnode, node)
        ast.fix_missing_locations(obfnode)
        return obfnode

    def filter_node(self, node):
        return isinstance(node, (ast.Str, ast.Constant))

    def _is_string_value(self, value):
        return isinstance(value, ast.Str) or (
            isinstance(value, ast.Constant) and isinstance(value.value, str))

    def ignore_docstring(self, node):
        return 1 if (
            isinstance(node, ast.Module) and len(node.body) > 1 and
            isinstance(node.body[1], ast.ImportFrom) and
            node.body[1].module == '__future__' and
            ast.get_docstring(node) is not None) else 0

    def visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                start = self.ignore_docstring(node) if field == 'body' else 0
                for i in range(start, len(value)):
                    if self.filter_node(value[i]):
                        value[i] = self.reform_node(value[i])
                    elif isinstance(value[i], ast.AST):
                        self.visit(value[i])
            elif self.filter_node(value):
                setattr(node, field, self.reform_node(value))
            elif isinstance(value, ast.AST):
                self.visit(value)


class StrProtector(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def process(self, res):
        snt = StrNodeTransformer()
        snt.encoding = self.ctx.encoding
        snt.visit(res.mtree)
