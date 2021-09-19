import ast
import os
import struct

from ctypes import cdll, py_object, PYFUNCTYPE


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


def _check_ignore_option(source):
    for line in source[:1024].splitlines():
        if not line.strip():
            continue
        if not line.startswith('#'):
            break
        i = line.lower().find('pyarmor option')
        return (i > 0) and (line.find('no-spp-mode') > 0)


def build(source, modname, destname=None):
    if _check_ignore_option(source):
        return None, None

    data = '/Users/jondy/workspace/pytransform/cmap/build/sppmode.so'
    # os.path.join('~', '.pyarmor', '_sppmode.so')
    lib = cdll.LoadLibrary(data)
    fb = PYFUNCTYPE(py_object, py_object)(('sppbuild', lib))
    co, cox, src = fb((ast.parse(source, modname), modname))
    return co, cox
