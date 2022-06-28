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
    mixins = kwargs.get('mixins')
    if mixins:
        for mixer in mixins:
            if mixer == 'str':
                ast_mixin_str(mtree, encoding=encoding)
            else:
                raise NotImplementedError('mixer "%s"' % mixer)

    sppmode = kwargs.get('sppmode')
    if sppmode and 'no-spp-mode' in options:
        logging.info('Ignore this module because of no-spp-mode inline option')
        sppmode = False

    if sppmode:
        mtree.pyarmor_options = options
        co = sppbuild(mtree, modname)
        if not co:
            kwargs['sppmode'] = False
            return build_co_module(lines, modname, **kwargs)
    else:
        co = compile(mtree, modname, 'exec')

    return sppmode, co


class StrNodeTransformer(ast.NodeTransformer):

    def reform_node(self, node):
        encoding = getattr(self, 'encoding')
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

    def filter_node(self, node):
        return isinstance(node.s if isinstance(node, ast.Str)
                          else node.value if isinstance(node, ast.Constant)
                          else None, str)

    def visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for i in range(len(value)):
                    if self.filter_node(value[i]):
                        value[i] = self.reform_node(value[i])
                    elif isinstance(value[i], ast.AST):
                        self.visit(value[i])
            elif self.filter_node(value):
                setattr(node, field, self.reform_node(value))
            elif isinstance(value, ast.AST):
                self.visit(value)
        # [self.visit(x) for x in ast.iter_child_nodes(node)]


def ast_mixin_str(mtree, encoding=None):
    if sys.version_info[0] == 2:
        raise RuntimeError("String protection doesn't work for Python 2")

    seed()
    snt = StrNodeTransformer()
    snt.encoding = encoding
    snt.visit(mtree)
