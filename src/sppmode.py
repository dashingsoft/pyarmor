import ast
import logging
import os
import platform
import struct
import sys

from ctypes import cdll, py_object, pythonapi, PYFUNCTYPE

_spplib = None


def mixin(obfcode, sppcode=None):
    n = 64
    s = obfcode.find(r", b'") + 4
    t = obfcode.rfind("',")
    if sppcode is None:
        sppcode = b'\x00' * 16

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
    return [x.strip() for x in options]


def build(source, modname, destname=None):
    options = _check_inline_option(source)
    if 'no-spp-mode' in options:
        return False

    mtree = ast.parse(source, modname)
    mtree.pyarmor_options = options

    if not os.environ.get('PYARMOR_CC'):
        _check_ccompiler()

    fb = _load_sppbuild()
    return fb((mtree, modname))


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


def _check_ccompiler():
    from subprocess import check_output
    if sys.platform.startswith('linux'):
        cc = os.environ.get('CC', 'gcc')
    elif sys.platform.startswith('darwin'):
        cc = os.environ.get('CC', 'clang')
    elif sys.platform.startswith('win'):
        from utils import PYARMOR_HOME as path
        for cc in [os.environ.get('CC', os.environ.get('CLANG', '')),
                   os.path.join(path, 'clang.exe'),
                   r'C:\Program Files\LLVM\bin\clang.exe']:
            if cc.endswith('clang.exe') and os.path.exists(cc):
                break
        else:
            cc = 'clang.exe'
    try:
        check_output([cc, '--version'])
    except Exception:
        raise RuntimeError('No available c compiler found')
    os.environ['PYARMOR_CC'] = cc
    logging.info('Set PYARMOR_CC to "%s"', os.environ['PYARMOR_CC'])
