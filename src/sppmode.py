import ast
import os
import struct

from ctypes import cdll, c_char_p, c_int, c_void_p, py_object, PYFUNCTYPE


def mixin(obfcode, sppcode):
    n = 64
    s = obfcode.find(r", b'") + 4
    t = obfcode.rfind("',")

    oh = eval(obfcode[s:s+n*4] + "'")
    vs = struct.unpack("I", oh[36:40]) | 16
    bh = oh[:36] + struct.pack("I", vs) + oh[40:56] + oh[32:36] + oh[60:]
    ph = oh[:32] + struct.pack("I", len(sppcode) + n) + oh[36:]

    def to_str(code):
        return '\\x'.join(['%02x' % c for c in bytearray(code)])

    return ''.join([obfcode[:s], to_str(bh), obfcode[s+n*4:t],
                    to_str(ph), to_str(sppcode), obfcode[t:]])


def build(source, dotname):
    data = os.path.join('~', '.pyarmor', '_sppmode.so')
    lib = cdll.LoadLibrary(data)
    fb = PYFUNCTYPE(py_object, py_object, c_char_p)(('sppbuild', lib))
    return fb(ast.parse(source, dotname), dotname)
