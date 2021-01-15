import platform
import sys
import struct


def import_names():
    plat_table = (
        ('windows', ('windows')),
        ('darwin', ('darwin', 'ios')),
        ('linux', ('linux*',)),
        ('freebsd', ('freebsd*', 'openbsd*')),
        ('poky', ('poky',)),
    )

    arch_table = (
        ('x86', ('i386', 'i486', 'i586', 'i686')),
        ('x86_64', ('x64', 'x86_64', 'amd64', 'intel')),
        ('arm', ('armv5',)),
        ('armv6', ('armv6l',)),
        ('armv7', ('armv7l',)),
        ('ppc64', ('ppc64le',)),
        ('mips32', ('mips',)),
        ('aarch32', ('aarch32',)),
        ('aarch64', ('aarch64', 'arm64'))
    )

    plat = platform.system().lower()
    mach = platform.machine().lower()

    for alias, platlist in plat_table:
        for s in platlist:
            if s.startswith(plat):
                plat = alias
                break

    if plat == 'linux':
        cname, cver = platform.libc_ver()
        if cname == 'musl':
            plat = 'musl'
        elif cname == 'libc':
            plat = 'android'

    for alias, archlist in arch_table:
        if mach in archlist:
            mach = alias
            break

    if plat == 'windows' and mach == 'x86_64':
        bitness = struct.calcsize('P'.encode()) * 8
        if bitness == 32:
            mach = 'x86'

    name = '.'.join([__name__, '%s_%s' % (plat, mach), 'pytransform'])
    m = __import__(name, globals(), locals(), ['*'])
    sys.modules[__name__].__dict__.update(m.__dict__)


import_names()
