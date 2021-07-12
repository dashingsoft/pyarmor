import platform
import struct
import sys

from ctypes import cdll, c_char_p, CFUNCTYPE
from fnmatch import fnmatch

plat_table = (
    ('windows', ('windows', 'cygwin-*')),
    ('darwin', ('darwin',)),
    ('ios', ('ios',)),
    ('linux', ('linux*',)),
    ('freebsd', ('freebsd*', 'openbsd*', 'isilon onefs')),
    ('poky', ('poky',)),
)

arch_table = (
    ('x86', ('i?86', )),
    ('x86_64', ('x64', 'x86_64', 'amd64', 'intel')),
    ('arm', ('armv5',)),
    ('armv6', ('armv6l',)),
    ('armv7', ('armv7l',)),
    ('ppc64', ('ppc64le',)),
    ('mips32', ('mips',)),
    ('aarch32', ('aarch32',)),
    ('aarch64', ('aarch64', 'arm64'))
)


def _match_features(patterns, s):
    for pat in patterns:
        if fnmatch(s, pat):
            return True


def _gnu_get_libc_version():
    try:
        prototype = CFUNCTYPE(c_char_p)
        ver = prototype(('gnu_get_libc_version', cdll.LoadLibrary('')))()
        return ver.decode().split('.')
    except Exception:
        pass


def format_platform():
    plat = platform.system().lower()
    mach = platform.machine().lower()

    for alias, platlist in plat_table:
        if _match_features(platlist, plat):
            plat = alias
            break

    if plat == 'linux':
        cname, cver = platform.libc_ver()
        if cname == 'musl':
            plat = 'musl'
        elif cname == 'libc':
            plat = 'android'
        elif cname == 'glibc':
            v = _gnu_get_libc_version()
            if v and len(v) >= 2 and (int(v[0]) * 100 + int(v[1])) < 214:
                plat = 'centos6'

    for alias, archlist in arch_table:
        if _match_features(archlist, mach):
            mach = alias
            break

    if plat == 'windows' and mach == 'x86_64':
        bitness = struct.calcsize('P'.encode()) * 8
        if bitness == 32:
            mach = 'x86'

    return '.'.join([plat, mach])


if __name__ == '__main__':
    print('platform.system is "%s"' % platform.system())
    print('platform.machine is "%s"' % platform.machine())
    print('sys.byteorder is "%s"' % sys.byteorder)
    print('The standard platform name is "%s"' % format_platform())
