# These module alos are used by protection code, so that protection
# code needn't import anything
import os
import platform
import sys
import struct

# Because ctypes is new from Python 2.5, so pytransform doesn't work
# before Python 2.5
#
from ctypes import cdll, c_char, c_char_p, c_int, c_void_p, \
    pythonapi, py_object, PYFUNCTYPE, CFUNCTYPE
from fnmatch import fnmatch

#
# Support Platforms
#
plat_path = 'platforms'

plat_table = (
    ('windows', ('windows', 'cygwin-*')),
    ('darwin', ('darwin', 'ios')),
    ('linux', ('linux*',)),
    ('freebsd', ('freebsd*', 'openbsd*')),
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

#
# Hardware type
#
HT_HARDDISK, HT_IFMAC, HT_IPV4, HT_IPV6, HT_DOMAIN = range(5)

#
# Global
#
_pytransform = None


class PytransformError(Exception):
    pass


def dllmethod(func):
    def wrap(*args, **kwargs):
        return func(*args, **kwargs)
    return wrap


@dllmethod
def version_info():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('version_info', _pytransform))
    return dlfunc()


@dllmethod
def init_pytransform():
    major, minor = sys.version_info[0:2]
    # Python2.5 no sys.maxsize but sys.maxint
    # bitness = 64 if sys.maxsize > 2**32 else 32
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_void_p)
    init_module = prototype(('init_module', _pytransform))
    ret = init_module(major, minor, pythonapi._handle)
    if (ret & 0xF000) == 0x1000:
        raise PytransformError('Initialize python wrapper failed (%d)'
                               % (ret & 0xFFF))
    return ret


@dllmethod
def init_runtime():
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_int, c_int)
    _init_runtime = prototype(('init_runtime', _pytransform))
    return _init_runtime(0, 0, 0, 0)


@dllmethod
def encrypt_code_object(pubkey, co, flags, suffix=''):
    _pytransform.set_option(6, suffix.encode())
    prototype = PYFUNCTYPE(py_object, py_object, py_object, c_int)
    dlfunc = prototype(('encrypt_code_object', _pytransform))
    return dlfunc(pubkey, co, flags)


@dllmethod
def generate_license_file(filename, priname, rcode, start=-1, count=1):
    prototype = PYFUNCTYPE(c_int, c_char_p, c_char_p, c_char_p, c_int, c_int)
    dlfunc = prototype(('generate_project_license_files', _pytransform))
    return dlfunc(filename.encode(), priname.encode(), rcode.encode(),
                  start, count) if sys.version_info[0] == 3 \
        else dlfunc(filename, priname, rcode, start, count)


@dllmethod
def generate_license_key(prikey, keysize, rcode):
    prototype = PYFUNCTYPE(py_object, c_char_p, c_int, c_char_p)
    dlfunc = prototype(('generate_license_key', _pytransform))
    return dlfunc(prikey, keysize, rcode) if sys.version_info[0] == 2 \
        else dlfunc(prikey, keysize, rcode.encode())


@dllmethod
def get_registration_code():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('get_registration_code', _pytransform))
    return dlfunc()


@dllmethod
def get_expired_days():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('get_expired_days', _pytransform))
    return dlfunc()


@dllmethod
def clean_obj(obj, kind):
    prototype = PYFUNCTYPE(c_int, py_object, c_int)
    dlfunc = prototype(('clean_obj', _pytransform))
    return dlfunc(obj, kind)


def clean_str(*args):
    tdict = {
        'str': 0,
        'bytearray': 1,
        'unicode': 2
    }
    for obj in args:
        k = tdict.get(type(obj).__name__)
        if k is None:
            raise RuntimeError('Can not clean object: %s' % obj)
        clean_obj(obj, k)


def get_hd_info(hdtype, name=None):
    if hdtype not in range(HT_DOMAIN + 1):
        raise RuntimeError('Invalid parameter hdtype: %s' % hdtype)
    size = 256
    t_buf = c_char * size
    buf = t_buf()
    cname = c_char_p(0 if name is None
                     else name.encode('utf-8') if hasattr('name', 'encode')
                     else name)
    if (_pytransform.get_hd_info(hdtype, buf, size, cname) == -1):
        raise PytransformError('Get hardware information failed')
    return buf.value.decode()


def show_hd_info():
    return _pytransform.show_hd_info()


def assert_armored(*names):
    prototype = PYFUNCTYPE(py_object, py_object)
    dlfunc = prototype(('assert_armored', _pytransform))

    def wrapper(func):
        def wrap_execute(*args, **kwargs):
            dlfunc(names)
            return func(*args, **kwargs)
        return wrap_execute
    return wrapper


def get_license_info():
    info = {
        'ISSUER': None,
        'EXPIRED': None,
        'HARDDISK': None,
        'IFMAC': None,
        'IFIPV4': None,
        'DOMAIN': None,
        'DATA': None,
        'CODE': None,
    }
    rcode = get_registration_code().decode()
    if rcode.startswith('*VERSION:'):
        index = rcode.find('\n')
        info['ISSUER'] = rcode[9:index].split('.')[0].replace('-sn-1.txt', '')
        rcode = rcode[index+1:]

    index = 0
    if rcode.startswith('*TIME:'):
        from time import ctime
        index = rcode.find('\n')
        info['EXPIRED'] = ctime(float(rcode[6:index]))
        index += 1

    if rcode[index:].startswith('*FLAGS:'):
        index += len('*FLAGS:') + 1
        info['FLAGS'] = ord(rcode[index - 1])

    prev = None
    start = index
    for k in ['HARDDISK', 'IFMAC', 'IFIPV4', 'DOMAIN', 'FIXKEY', 'CODE']:
        index = rcode.find('*%s:' % k)
        if index > -1:
            if prev is not None:
                info[prev] = rcode[start:index]
            prev = k
            start = index + len(k) + 2
    info['CODE'] = rcode[start:]
    i = info['CODE'].find(';')
    if i > 0:
        info['DATA'] = info['CODE'][i+1:]
        info['CODE'] = info['CODE'][:i]
    return info


def get_license_code():
    return get_license_info()['CODE']


def get_user_data():
    return get_license_info()['DATA']


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


def format_platform(platid=None):
    if platid:
        return os.path.normpath(platid)

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

    return os.path.join(plat, mach)


# Load _pytransform library
def _load_library(path=None, is_runtime=0, platid=None, suffix='', advanced=0):
    path = os.path.dirname(__file__) if path is None \
        else os.path.normpath(path)

    plat = platform.system().lower()
    name = '_pytransform' + suffix
    if plat == 'linux':
        filename = os.path.abspath(os.path.join(path, name + '.so'))
    elif plat == 'darwin':
        filename = os.path.join(path, name + '.dylib')
    elif plat == 'windows':
        filename = os.path.join(path, name + '.dll')
    elif plat == 'freebsd':
        filename = os.path.join(path, name + '.so')
    else:
        raise PytransformError('Platform %s not supported' % plat)

    if platid is not None and os.path.isfile(platid):
        filename = platid
    elif platid is not None or not os.path.exists(filename) or not is_runtime:
        libpath = platid if platid is not None and os.path.isabs(platid) else \
            os.path.join(path, plat_path, format_platform(platid))
        filename = os.path.join(libpath, os.path.basename(filename))

    if not os.path.exists(filename):
        raise PytransformError('Could not find "%s"' % filename)

    try:
        m = cdll.LoadLibrary(filename)
    except Exception as e:
        if sys.flags.debug:
            print('Load %s failed:\n%s' % (filename, e))
        raise

    # Removed from v4.6.1
    # if plat == 'linux':
    #     m.set_option(-1, find_library('c').encode())

    if not os.path.abspath('.') == os.path.abspath(path):
        m.set_option(1, path.encode() if sys.version_info[0] == 3 else path)

    # Required from Python3.6
    m.set_option(2, sys.byteorder.encode())

    if sys.flags.debug:
        m.set_option(3, c_char_p(1))
    m.set_option(4, c_char_p(not is_runtime))

    # Disable advanced mode by default
    m.set_option(5, c_char_p(not advanced))

    # Set suffix for private package
    if suffix:
        m.set_option(6, suffix.encode())

    return m


def pyarmor_init(path=None, is_runtime=0, platid=None, suffix='', advanced=0):
    global _pytransform
    _pytransform = _load_library(path, is_runtime, platid, suffix, advanced)
    return init_pytransform()


def pyarmor_runtime(path=None, suffix='', advanced=0):
    if _pytransform is not None:
        return

    try:
        pyarmor_init(path, is_runtime=1, suffix=suffix, advanced=advanced)
        init_runtime()
    except Exception as e:
        if sys.flags.debug or hasattr(sys, '_catch_pyarmor'):
            raise
        sys.stderr.write("%s\n" % str(e))
        sys.exit(1)


# ----------------------------------------------------------
# End of pytransform
# ----------------------------------------------------------

#
# Not available from v5.6
#


def generate_capsule(licfile):
    prikey, pubkey, prolic = _generate_project_capsule()
    capkey, newkey = _generate_pytransform_key(licfile, pubkey)
    return prikey, pubkey, capkey, newkey, prolic


@dllmethod
def _generate_project_capsule():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('generate_project_capsule', _pytransform))
    return dlfunc()


@dllmethod
def _generate_pytransform_key(licfile, pubkey):
    prototype = PYFUNCTYPE(py_object, c_char_p, py_object)
    dlfunc = prototype(('generate_pytransform_key', _pytransform))
    return dlfunc(licfile.encode() if sys.version_info[0] == 3 else licfile,
                  pubkey)


#
# Deprecated functions from v5.1
#
@dllmethod
def encrypt_project_files(proname, filelist, mode=0):
    prototype = PYFUNCTYPE(c_int, c_char_p, py_object, c_int)
    dlfunc = prototype(('encrypt_project_files', _pytransform))
    return dlfunc(proname.encode(), filelist, mode)


def generate_project_capsule(licfile):
    prikey, pubkey, prolic = _generate_project_capsule()
    capkey = _encode_capsule_key_file(licfile)
    return prikey, pubkey, capkey, prolic


@dllmethod
def _encode_capsule_key_file(licfile):
    prototype = PYFUNCTYPE(py_object, c_char_p, c_char_p)
    dlfunc = prototype(('encode_capsule_key_file', _pytransform))
    return dlfunc(licfile.encode(), None)


@dllmethod
def encrypt_files(key, filelist, mode=0):
    t_key = c_char * 32
    prototype = PYFUNCTYPE(c_int, t_key, py_object, c_int)
    dlfunc = prototype(('encrypt_files', _pytransform))
    return dlfunc(t_key(*key), filelist, mode)


@dllmethod
def generate_module_key(pubname, key):
    t_key = c_char * 32
    prototype = PYFUNCTYPE(py_object, c_char_p, t_key, c_char_p)
    dlfunc = prototype(('generate_module_key', _pytransform))
    return dlfunc(pubname.encode(), t_key(*key), None)

#
# Compatible for PyArmor v3.0
#
@dllmethod
def old_init_runtime(systrace=0, sysprofile=1, threadtrace=0, threadprofile=1):
    '''Only for old version, before PyArmor 3'''
    pyarmor_init(is_runtime=1)
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_int, c_int)
    _init_runtime = prototype(('init_runtime', _pytransform))
    return _init_runtime(systrace, sysprofile, threadtrace, threadprofile)


@dllmethod
def import_module(modname, filename):
    '''Only for old version, before PyArmor 3'''
    prototype = PYFUNCTYPE(py_object, c_char_p, c_char_p)
    _import_module = prototype(('import_module', _pytransform))
    return _import_module(modname.encode(), filename.encode())


@dllmethod
def exec_file(filename):
    '''Only for old version, before PyArmor 3'''
    prototype = PYFUNCTYPE(c_int, c_char_p)
    _exec_file = prototype(('exec_file', _pytransform))
    return _exec_file(filename.encode())
