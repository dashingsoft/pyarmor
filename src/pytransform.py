# Because ctypes is new from Python 2.5, so pytransform doesn't work
# before Python 2.5
#
from ctypes import cdll, c_char, c_char_p, c_int, c_void_p, \
                   pythonapi, py_object, PYFUNCTYPE
from ctypes.util import find_library

import os
import sys
import platform
import struct

#
# Global
#
_pytransform = None
_get_error_msg = None

class PytransformError(Exception):
    pass

def dllmethod(func):
    def wrap(*args, **kwargs):
        args = [(s.encode() if isinstance(s, str) else s) for s in args]
        result = func(*args, **kwargs)
        errmsg = _get_error_msg()
        if errmsg:
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
    init_module(major, minor, pythonapi._handle)

@dllmethod
def init_runtime(systrace=0, sysprofile=1, threadtrace=0, threadprofile=1):
    pyarmor_init()
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_int, c_int)
    _init_runtime = prototype(('init_runtime', _pytransform))
    _init_runtime(systrace, sysprofile, threadtrace, threadprofile)

@dllmethod
def import_module(modname, filename):
    prototype = PYFUNCTYPE(py_object, c_char_p, c_char_p)
    _import_module = prototype(('import_module', _pytransform))
    return _import_module(modname, filename)

@dllmethod
def exec_file(filename):
    prototype = PYFUNCTYPE(c_int, c_char_p)
    _exec_file = prototype(('exec_file', _pytransform))
    return _exec_file(filename)

@dllmethod
def encrypt_project_files(proname, filelist, mode=0):
    prototype = PYFUNCTYPE(c_int, c_char_p, py_object, c_int)
    dlfunc = prototype(('encrypt_project_files', _pytransform))
    return dlfunc(proname, filelist, mode)

@dllmethod
def encrypt_files(key, filelist, mode=0):
    t_key = c_char * 32
    prototype = PYFUNCTYPE(c_int, t_key, py_object, c_int)
    dlfunc = prototype(('encrypt_files', _pytransform))
    return dlfunc(t_key(*key), filelist, mode)

def generate_project_capsule(licfile):
    prikey, pubkey, prolic = _generate_project_capsule()
    capkey = _encode_capsule_key_file(licfile)
    return prikey, pubkey, capkey, prolic

@dllmethod
def _generate_project_capsule():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('generate_project_capsule', _pytransform))
    return dlfunc()

@dllmethod
def _encode_capsule_key_file(licfile):
    prototype = PYFUNCTYPE(py_object, c_char_p, c_char_p)
    dlfunc = prototype(('encode_capsule_key_file', _pytransform))
    return dlfunc(licfile, None)

@dllmethod
def generate_module_key(pubname, key):
    t_key = c_char * 32
    prototype = PYFUNCTYPE(py_object, c_char_p, t_key, c_char_p)
    dlfunc = prototype(('generate_module_key', _pytransform))
    return dlfunc(pubname, t_key(*key), None)

@dllmethod
def generate_license_file(filename, priname, rcode, start=-1, count=1):
    prototype = PYFUNCTYPE(c_int, c_char_p, c_char_p, c_char_p, c_int, c_int)
    dlfunc = prototype(('generate_project_license_files', _pytransform))
    return dlfunc(filename, priname, rcode, start, count)

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
def get_trial_days():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('get_trial_days', _pytransform))
    return dlfunc()

@dllmethod
def version_info():
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('version_info', _pytransform))
    return dlfunc()

def get_hd_sn():
    size = 256
    t_sn = c_char * size
    sn = t_sn()
    if (_pytransform.get_hd_sn(sn, size) == -1):
        return ''
    return sn.value.decode()

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

def format_platname():
    plat = platform.system().lower()
    bitness = struct.calcsize('P'.encode()) * 8
    return '%s%s' % (plat, bitness)

# Load _pytransform library
def _load_library(path=None, is_runtime=0):
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
        bitness = struct.calcsize('P'.encode()) * 8
        libpath = os.path.join(path, 'platforms', format_platname())
        filename = os.path.join(libpath, os.path.basename(filename))
        if not os.path.exists(filename):
            raise PytransformError('Could not find "%s"' % filename)

    try:
        m = cdll.LoadLibrary(filename)
    except Exception as e:
        raise PytransformError('Load %s failed:\n%s' % (filename, e))

    if plat == 'linux':
        m.set_option('libc'.encode(), find_library('c').encode())

    # Required from Python3.6
    m.set_option('byteorder'.encode(), sys.byteorder.encode())

    # m.set_option('enable_trace_log'.encode(), c_char_p(1))
    m.set_option('enable_trial_license'.encode(), c_char_p(not is_runtime))

    # # Deprecated from v3.4
    # m.set_option('enable_encrypt_generator'.encode(), c_char_p(1))
    # # Deprecated from v3.4
    # m.set_option('disable_obfmode_encrypt'.encode(), c_char_p(1))

    if not os.path.abspath('.') == os.path.abspath(path):
        m.set_option('pyshield_path'.encode(), path.encode())
    return m

def pyarmor_init(path=None, is_runtime=0):
    global _pytransform
    global _get_error_msg
    if _pytransform is None:
        _pytransform = _load_library(path, is_runtime)
        _get_error_msg = _pytransform.get_error_msg
        _get_error_msg.restype = c_char_p
        init_pytransform()

def pyarmor_runtime(path=None):
    try:
        pyarmor_init(path, is_runtime=1)
    except PytransformError as e:
        print(e)
        sys.exit(1)
    init_runtime(0, 0, 0, 0)
