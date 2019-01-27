import os
import sys

#-----------------------------------------------------------
#
# Part 1: protect dynamic library
#
#-----------------------------------------------------------

import pytransform
from hashlib import md5

MD5SUM_LIB_PYTRANSFORM = {
    'windows32': '156bccd049eb42afe3ae8e1249b4eede',
    'windows64': 'a7039ba4dfe9b23aa3e284af9691da1a',
    'linux32': '3f194b707001f4132ae144946cc0a914',
    'linux32/arm': '727f9a40ba5ccc72ccc9a530caa35214',
    'linux64': '74aa1e1ee07961f2c42ae8d9af9f7b64',
    'linux64/arm': 'dacce677af832c5360872dc3086c6acb',
    'darwin64': '23da1bbc5b7768657d8a76a1a403a8c8',
}

CO_SELF_SIZES = 46, 36
CO_DECORATOR_SIZES = 135, 122, 89, 86, 60
CO_DLLMETHOD_SIZES = 22, 19, 16
CO_LOAD_LIBRARY_SIZES = 662, 648, 646, 634, 628, 456
CO_PYARMOR_INIT_SIZES = 58, 56, 40
CO_PYARMOR_RUNTIME_SIZES = 146, 144, 138, 127, 121, 108
CO_INIT_PYTRANSFORM_SIZES = 83, 80, 58
CO_INIT_RUNTIME_SIZES = 74, 52

CO_SELF_NAMES = ('pytransform', 'pyarmor_runtime', '__pyarmor__',
                 '__name__', '__file__')
CO_DECORATOR_NAMES = ('isinstance', 'str', 'encode', 'int',
                      '_get_error_msg', 'PytransformError')
CO_DLLMETHOD_NAMES = ()
CO_LOAD_LIBRARY_NAMES = ('None', 'os', 'path', 'dirname', '__file__',
                         'normpath', 'platform', 'system', 'lower',
                         'abspath', 'join', 'PytransformError', 'exists',
                         'struct', 'calcsize', 'encode', 'format_platname',
                         'basename', 'cdll', 'LoadLibrary', 'Exception',
                         'set_option', 'sys', 'byteorder', 'c_char_p',
                         '_debug_mode')
CO_PYARMOR_INIT_NAMES = ('_pytransform', 'None', '_load_library',
                         'get_error_msg', '_get_error_msg', 'c_char_p',
                         'restype', 'init_pytransform')
CO_PYARMOR_RUNTIME_NAMES = ('_pytransform', 'None', 'PytransformError', 
                            'pyarmor_init', 'init_runtime', 'print', 'sys',
                            'exit')
CO_INIT_PYTRANSFORM_NAMES = ('sys', 'version_info', 'PYFUNCTYPE', 'c_int',
                             'c_void_p', '_pytransform', 'pythonapi', '_handle')
CO_INIT_RUNTIME_NAMES = ('pyarmor_init', 'PYFUNCTYPE', 'c_int', '_pytransform')

def check_lib_pytransform(filename):
    print("Check md5sum for %s..." % filename)
    expected = MD5SUM_LIB_PYTRANSFORM[pytransform.format_platname()]
    with open(filename, 'rb') as f:
        if not md5(f.read()).hexdigest() == expected:
            print("Check failed")
            sys.exit(1)
    print("Check OK.")

def check_code_object(f_code, sizes, names):
    return set(f_code.co_names) <= set(names) and len(f_code.co_code) in sizes

def check_obfuscated_script():
    print('Check obfuscated script %s ...' % __file__)
    co = sys._getframe(3).f_code
    if not check_code_object(co, CO_SELF_SIZES, CO_SELF_NAMES):
        print('Obfuscated script has been changed by others')
        sys.exit(1)
    print('Check OK.')

def check_mod_pytransform():
    code = '__code__' if sys.version_info[0] == 3 else 'func_code'
    closure = '__closure__' if sys.version_info[0] == 3 else 'func_closure'

    print('Check decorator dllmethod ...')
    co = getattr(pytransform.dllmethod, code).co_consts[1]
    if not check_code_object(co, CO_DECORATOR_SIZES, CO_DECORATOR_NAMES):
        print('Check failed')
        sys.exit(1)
    print('Check OK.')

    for item in [
            ('dllmethod', CO_DLLMETHOD_SIZES, CO_DLLMETHOD_NAMES),
            ('init_pytransform', CO_DECORATOR_SIZES, CO_DECORATOR_NAMES),
            ('init_runtime', CO_DECORATOR_SIZES, CO_DECORATOR_NAMES),
            ('_load_library', CO_LOAD_LIBRARY_SIZES, CO_LOAD_LIBRARY_NAMES),
            ('pyarmor_init', CO_PYARMOR_INIT_SIZES, CO_PYARMOR_INIT_NAMES),
            ('pyarmor_runtime', CO_PYARMOR_RUNTIME_SIZES, CO_PYARMOR_RUNTIME_NAMES)]:
        print('Check function %s ...' % item[0])
        co = getattr(getattr(pytransform, item[0]), code)
        if not check_code_object(co, item[1], item[2]):
            print('Check failed')
            sys.exit(1)
        print('Check OK.')

    for item in [
            ('init_pytransform', CO_INIT_PYTRANSFORM_SIZES, CO_INIT_PYTRANSFORM_NAMES),
            ('init_runtime', CO_INIT_RUNTIME_SIZES, CO_INIT_RUNTIME_NAMES)]:
        print('Check wrapped function %s ...' % item[0])
        co_closures = getattr(getattr(pytransform, item[0]), closure)
        co = getattr(co_closures[0].cell_contents, code)
        if not check_code_object(co, item[1], item[2]):
            print('Check failed')
            sys.exit(1)
        print('Check OK.')

def protect_pytransform():
    try:
        # Be sure obfuscated script is not changed
        check_obfuscated_script()

        # Be sure 'pytransform.py' is not changed
        check_mod_pytransform()

        # Be sure '_pytransform.so' is not changed
        check_lib_pytransform(pytransform._pytransform._name)
    except Exception as e:
        print(e)
        sys.exit(1)

#-----------------------------------------------------------
#
# Part 2: check internet time by ntp server
#
#-----------------------------------------------------------

def check_expired_date_by_ntp():
    from ntplib import NTPClient
    from time import mktime, strptime

    NTP_SERVER = 'europe.pool.ntp.org'
    EXPIRED_DATE = '20190202'

    print('The license will be expired on %s' % EXPIRED_DATE)
    print('Check internet time from %s ...' % NTP_SERVER)
    c = NTPClient()
    response = c.request(NTP_SERVER, version=3)
    if response.tx_time > mktime(strptime(EXPIRED_DATE, '%Y%m%d')):
        print("The license has been expired")
        sys.exit(1)
    print("The license is not expired")

#-----------------------------------------------------------
#
# Part 3: show license information of obfuscated scripts
#
#-----------------------------------------------------------

def show_left_days_of_license():
   try:
       rcode = pytransform.get_license_info()['CODE']
       left_days = pytransform.get_expired_days()
       if left_days == -1:
           print('This license for %s is never expired' % rcode)
       else:
           print('This license %s will be expired in %d days' % (rcode, left_days))
   except Exception as e:
       print(e)
       sys.exit(1)

#-----------------------------------------------------------
#
# Part 4: business code
#
#-----------------------------------------------------------

def hello():
    print('Hello world!')

def sum(a, b):
    return a + b

def main():
    hello()
    print('1 + 1 = %d' % sum(1, 1))

if __name__ == '__main__':

    protect_pytransform()
    check_expired_date_by_ntp()
    show_left_days_of_license()
    
    main()
