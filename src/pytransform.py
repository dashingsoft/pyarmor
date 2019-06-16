# Because ctypes is new from Python 2.5, so pytransform doesn't work
# before Python 2.5
#
from ctypes import cdll, c_char, c_char_p, c_int, c_void_p, \
                   pythonapi, py_object, PYFUNCTYPE

import os
import sys
import platform
import struct

#
# Hardware type
#
HT_HARDDISK, HT_IFMAC, HT_IPV4, HT_IPV6, HT_DOMAIN = range(5)

#
# Global
#
_pytransform = None
_get_error_msg = None
_debug_mode = sys.flags.debug

class PytransformError(Exception):
    pass

def dllmethod(func):
    def wrap(*args, **kwargs):
        # args = [(s.encode() if isinstance(s, str) else s) for s in args]
        result = func(*args, **kwargs)
        if isinstance(result, int) and result != 0:
            errmsg = _get_error_msg()
            if not isinstance(errmsg, str):
                errmsg = errmsg.decode()
            raise PytransformError(errmsg)
        return result
    return wrap

@dllmethod
def init_pytransform():
    major, minor = sys.version_info[0:2]
    # Python2.5 no sys.maxsize but sys.maxint
    # bitness = 64 if sys.maxsize > 2**32 else 32
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_void_p)
    init_module = prototype(('init_module', _pytransform))
    return init_module(major, minor, pythonapi._handle)

@dllmethod
def init_runtime():
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_int, c_int)
    _init_runtime = prototype(('init_runtime', _pytransform))
    return _init_runtime(0, 0, 0, 0)

@dllmethod
def encrypt_code_object(pubkey, co, flags):
    prototype = PYFUNCTYPE(py_object, py_object, py_object, c_int)
    dlfunc = prototype(('encrypt_code_object', _pytransform))
    return dlfunc(pubkey, co, flags)

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

@dllmethod
def generate_license_file(filename, priname, rcode, start=-1, count=1):
    prototype = PYFUNCTYPE(c_int, c_char_p, c_char_p, c_char_p, c_int, c_int)
    dlfunc = prototype(('generate_project_license_files', _pytransform))
    return dlfunc(filename.encode(), priname.encode(), rcode.encode(),
                  start, count) if sys.version_info[0] == 3 \
        else dlfunc(filename, priname, rcode, start, count)

@dllmethod
def get_registration_code():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('get_registration_code', _pytransform))
    return dlfunc()

def get_expired_days():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('get_expired_days', _pytransform))
    return dlfunc()

def get_hd_info(hdtype, size=256):
    t_buf = c_char * size
    buf = t_buf()
    if (_pytransform.get_hd_info(hdtype, buf, size) == -1):
        raise PytransformError(_get_error_msg())
    return buf.value.decode()

def show_hd_info():
    return _pytransform.show_hd_info()

def get_license_info():
    info = {
        'expired': 'Never',
        'restrict_mode': 'Enabled',
        'HARDDISK': 'Any',
        'IFMAC': 'Any',
        'IFIPV4': 'Any',
        'DOMAIN': 'Any',
        'CODE': '',
    }
    rcode = get_registration_code().decode()
    if rcode is None:
        raise PytransformError(_get_error_msg())
    index = 0
    if rcode.startswith('*TIME:'):
        from time import ctime
        index = rcode.find('\n')
        info['expired'] = ctime(float(rcode[6:index]))
        index += 1

    if rcode[index:].startswith('*FLAGS:'):
        info['restrict_mode'] = 'Disabled'
        index += len('*FLAGS:') + 1

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

    return info

def get_license_code():
    return get_license_info()['CODE']

def format_platname(platname=None):
    if platname is None:
        plat = platform.system().lower()
        bitness = struct.calcsize('P'.encode()) * 8
        platname = '%s%s' % (plat, bitness)
    mach = platform.machine().lower()
    return platname if mach in (
        'intel', 'x86', 'i386', 'i486', 'i586', 'i686',
        'x64', 'x86_64', 'amd64'
        ) else os.path.join(platname, mach)

# Load _pytransform library
def _load_library(path=None, is_runtime=0, platname=None):
    path = os.path.dirname(__file__) if path is None \
        else os.path.normpath(path)

    plat = platform.system().lower()
    if plat == 'linux':
        filename = os.path.abspath(os.path.join(path, '_pytransform.so'))
    elif plat == 'darwin':
        filename = os.path.join(path, '_pytransform.dylib')
    elif plat == 'windows':
        filename = os.path.join(path, '_pytransform.dll')
    elif plat == 'freebsd':
        filename = os.path.join(path, '_pytransform.so')
    else:
        raise PytransformError('Platform %s not supported' % plat)

    if not os.path.exists(filename):
        if is_runtime:
            raise PytransformError('Could not find "%s"' % filename)
        libpath = os.path.join(path, 'platforms', format_platname(platname))
        filename = os.path.join(libpath, os.path.basename(filename))
        if not os.path.exists(filename):
            raise PytransformError('Could not find "%s"' % filename)

    try:
        m = cdll.LoadLibrary(filename)
    except Exception as e:
        raise PytransformError('Load %s failed:\n%s' % (filename, e))

    # Removed from v4.6.1
    # if plat == 'linux':
    #     m.set_option(-1, find_library('c').encode())

    if not os.path.abspath('.') == os.path.abspath(path):
        m.set_option(1, path.encode() if sys.version_info[0] == 3 else path)

    # Required from Python3.6
    m.set_option(2, sys.byteorder.encode())

    m.set_option(3, c_char_p(_debug_mode))
    m.set_option(4, c_char_p(not is_runtime))

    return m

def pyarmor_init(path=None, is_runtime=0, platname=None):
    global _pytransform
    global _get_error_msg
    _pytransform = _load_library(path, is_runtime, platname)
    _get_error_msg = _pytransform.get_error_msg
    _get_error_msg.restype = c_char_p
    return init_pytransform()

def pyarmor_runtime(path=None):
    try:
        if pyarmor_init(path, is_runtime=1) == 0:
            init_runtime()
    except PytransformError as e:
        print(e)
        sys.exit(1)

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
