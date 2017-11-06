# Because ctypes is new from Python 2.5, so pytransform doesn't work
# before Python 2.5
#
# And _pytransform will decrypted bytescode by sys.setprofile and
# threading.setprofile, so if scripts set its own profile, pytransform
# maybe doesn't work. Besides, if your python built with Py_DEBUG or
# Py_TRACE_REFS, _pytransform will not work either in order to protect
# encrypted bytescode.

from ctypes import cdll, c_char, c_char_p, c_int, c_void_p, \
                   pythonapi, py_object, PYFUNCTYPE
from ctypes.util import find_library

# It seems imp must be imported even if there is no used in module
import imp
import os
import sys

# Options
_verbose_mode = 1
_debug_mode = 0

class PytransformError(Exception):
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)
        if _debug_mode:
            self._print_stack()

    @classmethod
    def _print_stack(self):
        try:
            from traceback import print_stack
        except Exception:
            _debug_mode = 0
            sys.stderr.write('Disabled debug mode.\n')
        else:
            print_stack()

def dllmethod(func):
    def format_message(msg, *args, **kwargs):
        if _verbose_mode:
            s1 = str(args)[:-1]
            s2 = ', '.join(['%s=%s' % (k, repr(v)) for k, v in kwargs.items()])
            sep = ', ' if (s1 and s2) else ''
            line = 'Call with arguments: %s%s%s)' % (s1, sep, s2)
            return msg
        return msg.split('\n')[-1]
    def wrap(*args, **kwargs):
        args = [(s.encode() if isinstance(s, str) else s) for s in args]
        result = func(*args, **kwargs)
        errmsg = _get_error_msg()
        if errmsg:
            raise PytransformError(format_message(errmsg, *args, **kwargs))
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
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_int, c_int)
    _init_runtime = prototype(('init_runtime', _pytransform))
    _init_runtime(systrace, sysprofile, threadtrace, threadprofile)

@dllmethod
def import_module(modname, filename):
    global _import_module
    if _import_module is None:
        prototype = PYFUNCTYPE(py_object, c_char_p, c_char_p)
        _import_module = prototype(('import_module', _pytransform))
    return _import_module(modname, filename)
_import_module = None

@dllmethod
def exec_file(filename):
    global _exec_file
    if _exec_file is None:
        prototype = PYFUNCTYPE(c_int, c_char_p)
        _exec_file = prototype(('exec_file', _pytransform))
    return _exec_file(filename)
_exec_file = None

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

# Load _pytransform library
def _load_library():
    try:
        path = os.path.dirname(sys.modules['pytransform'].__file__)
        if sys.platform.startswith('linux'):
            if path == '':
                m = cdll.LoadLibrary(os.path.abspath('_pytransform.so'))
            else:
                m = cdll.LoadLibrary(os.path.join(path, '_pytransform.so'))
            m.set_option('libc'.encode(), find_library('c').encode())
        elif sys.platform.startswith('darwin'):
            m = cdll.LoadLibrary(os.path.join(path, '_pytransform.dylib'))
        else:
            m = cdll.LoadLibrary(os.path.join(path, '_pytransform.dll'))
    except Exception:
        raise PytransformError('Could not load library _pytransform.')

    # m.set_option('enable_trace_log'.encode(), c_char_p(1))
    # m.set_option('enable_encrypt_generator'.encode(), c_char_p(1))
    if not os.path.abspath('.') == os.path.abspath(path):
        m.set_option('pyshield_path'.encode(), path.encode())
    return m

_pytransform = _load_library()
_get_error_msg = _pytransform.get_error_msg
_get_error_msg.restype = c_char_p
init_pytransform()
