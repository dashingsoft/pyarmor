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
    'windows32': '0f0f533b2b3568bef4ffbad22d93cec2',
    'windows64': 'fe454a42cd146bfea7f4c833d863e5fe',
    'linux32': '3f194b707001f4132ae144946cc0a914',
    'linux32/arm': '727f9a40ba5ccc72ccc9a530caa35214',
    'linux64': '74aa1e1ee07961f2c42ae8d9af9f7b64',
    'linux64/arm': 'dacce677af832c5360872dc3086c6acb',
    'darwin64': '23da1bbc5b7768657d8a76a1a403a8c8',
}

def check_lib_pytransform(filename):
    print("Check md5sum for %s..." % filename)
    expected = MD5SUM_LIB_PYTRANSFORM[pytransform.format_platname()]
    with open(filename, 'rb') as f:
        if not md5(f.read()).hexdigest() == expected:
            print("Check failed")
            sys.exit(1)
    print("Check OK.")

def check_obfuscated_script():
    CO_SIZES = 46, 36
    CO_NAMES = set(['pytransform', 'pyarmor_runtime', '__pyarmor__',
                    '__name__', '__file__'])
    print('Check obfuscated script %s ...' % __file__)
    co = sys._getframe(3).f_code
    if not ((set(co.co_names) <= CO_NAMES)
            and (len(co.co_code) in CO_SIZES)):
        print('Obfuscated script has been changed by others')
        sys.exit(1)
    print('Check OK.')

def check_mod_pytransform():
    CO_NAMES = set(['Exception', 'LoadLibrary', 'None', 'PYFUNCTYPE',
                    'PytransformError', '__file__', '_debug_mode',
                    '_get_error_msg', '_handle', '_load_library',
                    '_pytransform', 'abspath', 'basename', 'byteorder',
                    'c_char_p', 'c_int', 'c_void_p', 'calcsize', 'cdll',
                    'dirname', 'encode', 'exists', 'exit',
                    'format_platname', 'get_error_msg', 'init_pytransform',
                    'init_runtime', 'int', 'isinstance', 'join', 'lower',
                    'normpath', 'os', 'path', 'platform', 'print',
                    'pyarmor_init', 'pythonapi', 'restype', 'set_option',
                    'str', 'struct', 'sys', 'system', 'version_info'])

    colist = []

    code = '__code__' if sys.version_info[0] == 3 else 'func_code'
    for name in ('dllmethod', 'init_pytransform', 'init_runtime',
                 '_load_library', 'pyarmor_init', 'pyarmor_runtime'):
        colist.append(getattr(getattr(pytransform, name), code))

    closure = '__closure__' if sys.version_info[0] == 3 else 'func_closure'
    for name in ('init_pytransform', 'init_runtime'):
        colist.append(getattr(getattr(getattr(pytransform, name),
                                      closure)[0].cell_contents, code))
    colist.append(getattr(pytransform.dllmethod, code).co_consts[1])

    for co in colist:
        print('Check %s ...' % co.co_name)
        if not (set(co.co_names) < CO_NAMES):
            print('Check failed')
            sys.exit(1)
        print('Check OK.')

def protect_pytransform():
    try:
        # Be sure obfuscated script is not changed
        check_obfuscated_script()

        # Be sure '_pytransform._name' in 'pytransform.py' is not changed
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
           print('This license for %s will be expired in %d days' % \
                 (rcode, left_days))
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
    show_left_days_of_license()

    # check_expired_date_by_ntp()

    main()
