import ast
import logging
import os
import platform
import struct
import sys

from ctypes import cdll, py_object, pythonapi, PYFUNCTYPE

_spplib = None


def mixin(obfcode, sppcode):
    n = 64
    s = obfcode.find(r", b'") + 4
    t = obfcode.rfind("',")

    oh = bytes([int('0x'+x, 16) for x in obfcode[s+2:s+n*4].split(r'\x')])
    vs = struct.unpack("I", oh[36:40])[0] | 16
    nx = struct.pack("I", struct.unpack("I", oh[32:36])[0] + n)
    bh = oh[:36] + struct.pack("I", vs) + oh[40:56] + nx + oh[60:]
    ph = oh[:32] + struct.pack("I", len(sppcode)) + oh[36:]

    def to_str(code):
        return r'\x' + '\\x'.join(['%02x' % c for c in bytearray(code)])

    return ''.join([obfcode[:s], to_str(bh), obfcode[s+n*4:t],
                    to_str(ph), to_str(sppcode), obfcode[t:]])


def _check_inline_option(source):
    options = []
    marker = 'pyarmor options:'
    for line in source[:1024].splitlines():
        if not line.strip():
            continue
        if not line.startswith('#'):
            break
        i = line.lower().find(marker)
        if i > 0:
            options.extend(line[i+len(marker)].strip().split(','))
    return set([x.strip() for x in options])


class ExportDecorator(ast.NodeTransformer):

    SPP_EXPORT_DECORATOR = '''
def spp_export_api(f):

    def wrap(*args, **kwargs):
        return f(*args, **kwargs)

    return wrap
'''

    def visit(self, node):
        a = ast.parse(self.SPP_EXPORT_DECORATOR).body[0]
        node.body.insert(0, a)
        a.lineno = a.end_lineno = 1
        a.col_offset = a.end_col_offset = 1
        ast.fix_missing_locations(a)


def build(source, modname, destname=None):
    options = _check_inline_option(source)
    if 'no-spp-mode' in options:
        return None, None

    mtree = ast.parse(source, modname)
    if 'spp-export' in options:
        ExportDecorator().visit(mtree)

    fb = _load_sppbuild()
    co, cox, src = fb((mtree, modname))

    if sys._debug_pyarmor and destname:
        _write_debug_file(co, cox, src, destname)

    return co, cox


def _load_sppbuild():
    global _spplib
    if _spplib is None:
        from utils import PYARMOR_PATH as libpath
        plat = platform.system().lower()
        mach = platform.machine().lower()
        if mach != 'x86_64':
            raise RuntimeError('sppmode now only works in x86_64 platform')
        ext = '.dll' if plat.startswith('win') else '.so'
        name = os.path.join(libpath, 'platforms', plat, mach, 'sppmode' + ext)
        _spplib = cdll.LoadLibrary(name)
        if _spplib.sppinit(pythonapi._handle) != 0:
            raise RuntimeError('Init sppmode failed')
    return PYFUNCTYPE(py_object, py_object)(('sppbuild', _spplib))


def _write_debug_file(co, cox, src, destname):
    if co:
        from marshal import dumps
        filename = destname + '.co'
        logging.info('Write file %s', filename)
        with open(destname + '.co', 'wb') as f:
            f.write(dumps(co))
    if cox:
        filename = destname + '.cox'
        logging.info('Write file %s', filename)
        with open(destname + '.cox', 'wb') as f:
            f.write(cox)
    if src:
        filename = destname + '.c'
        logging.info('Write file %s', filename)
        with open(destname + '.c', 'w') as f:
            f.write(src)
