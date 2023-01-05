import ast
import logging
import random
import sys

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


def find_mixins(mixins):
    result = []
    for name in mixins:
        if name == 'str':
            result.append(ast_mixin_str)
        else:
            refname = 'ast_mixin_' + name
            try:
                mtemp = __import__('mixins', fromlist=(refname,))
            except ModuleNotFoundError:
                raise RuntimeError('no module "mixins" found')
            if not hasattr(mtemp, refname):
                raise RuntimeError('no mixin "%s" found' % name)
            result.append(getattr(mtemp, refname))
    return result


def build_co_module(lines, modname, **kwargs):
    options = _check_inline_option(lines)
    mtree = ast.parse(''.join(lines), modname)

    encoding = kwargs.get('encoding')
    mixins = kwargs.get('mixins')
    if mixins:
        mixargs = {
            'module': modname,
            'encoding': encoding,
            'options': options
        }
        for mixer in find_mixins(mixins):
            mixer(mtree, **mixargs)

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

    def _reform_str(self, s):
        encoding = getattr(self, 'encoding')
        value = bytearray(s.encode(encoding) if encoding else s.encode())
        key = [random.randint(0, 255)] * len(value)
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
            self._is_string_value(node.body[0].value)) else 0

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
        # [self.visit(x) for x in ast.iter_child_nodes(node)]


def ast_mixin_str(mtree, **kwargs):
    if sys.version_info[0] == 2:
        raise RuntimeError("String protection doesn't work for Python 2")

    random.seed()
    snt = StrNodeTransformer()
    snt.encoding = kwargs.get('encoding')
    snt.visit(mtree)
