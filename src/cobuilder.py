import ast
import logging
import sys

from random import seed, randint

from sppmode import build_co as sppbuild


def _check_inline_option(lines):
    options = []
    marker = 'pyarmor options:'
    for line in lines[:1000]:
        if not line.strip():
            continue
        if not line.startswith('#'):
            break
        i = line.lower().find(marker)
        if i > 0:
            options.extend(line[i+len(marker):].strip().split(','))
    return [x.strip() for x in options]


def build_co_module(lines, modname, **kwargs):
    options = _check_inline_option(lines)
    mtree = ast.parse(''.join(lines), modname)

    encoding = kwargs.get('encoding')
    if 'str' in kwargs.get('reforms', []):
        if sys.version_info[0] == 2:
            raise RuntimeError("String protection doesn't work for Python 2")
        protect_string_const(mtree, encoding)

    sppmode = kwargs.get('sppmode')

    if sppmode and 'no-spp-mode' in options:
        logging.info('Ignore this module because of no-spp-mode inline option')
        sppmode = False

    if sppmode:
        mtree.pyarmor_options = options
        co = sppbuild(mtree, modname)
        if not co:
            kwargs['sppmode'] = False
            return build_co_module(lines, modname, kwargs)
    else:
        co = compile(mtree, modname, 'exec')

    return sppmode, co


def reform_str_const(node, encoding=None):
    s = node.s if isinstance(node, ast.Str) else node.value
    value = bytearray(s.encode(encoding) if encoding else s.encode())
    key = [randint(0, 255)] * len(value)
    data = [x ^ y for x, y in zip(value, key)]
    expr = 'bytearray([%s]).decode(%s)' % (
        ','.join(['%s ^ %s' % k for k in zip(data, key)]),
        '' if encoding is None else encoding)
    obfnode = ast.parse(expr).body[0].value
    ast.copy_location(obfnode, node)
    ast.fix_missing_locations(obfnode)
    return obfnode


def is_str_const(node):
    return isinstance(node.s if isinstance(node, ast.Str)
                      else node.value if isinstance(node, ast.Constant)
                      else None, str)


class StringPatcher(ast.NodeTransformer):

    def visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for i in range(len(value)):
                    if is_str_const(value[i]):
                        value[i] = reform_str_const(value[i], self.encoding)
                    elif isinstance(value[i], ast.AST):
                        self.visit(value[i])
            elif is_str_const(value):
                setattr(node, field, reform_str_const(value, self.encoding))
            elif isinstance(value, ast.AST):
                self.visit(value)
        # [self.visit(x) for x in ast.iter_child_nodes(node)]


def protect_string_const(mtree, encoding=None):
    seed()

    patcher = StringPatcher()
    patcher.encoding = encoding
    patcher.visit(mtree)
