'''
Get bind key for CPython Library

   python get_bind_key.py

'''
from sys import platform
from ctypes import CFUNCTYPE, cdll, pythonapi, string_at, c_void_p, c_char_p


def get_bind_key():
    if platform.startswith('win'):
        from ctypes import windll
        dlsym = windll.kernel32.GetProcAddressA
    else:
        prototype = CFUNCTYPE(c_void_p, c_void_p, c_char_p)
        dlsym = prototype(('dlsym', cdll.LoadLibrary(None)))

    refunc1 = dlsym(pythonapi._handle, b'PyEval_EvalCode')
    refunc2 = dlsym(pythonapi._handle, b'PyEval_GetFrame')

    size = refunc2 - refunc1
    code = string_at(refunc1, size)

    print('Get bind key: %s' % sum(bytearray(code)))


if __name__ == '__main__':
    get_bind_key()
