def get_license_data():
    from pytransform import _pytransform
    from ctypes import py_object, PYFUNCTYPE
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('get_registration_code', _pytransform))
    rcode = dlfunc().decode()
    index = rcode.find(';', rcode.find('*CODE:'))
    return rcode[index+1:]


def _check_lib_hdinfo(lib_hdinfo_filename):
    from hashlib import sha384
    lib_hdinfo_checksum = "7838938a424b273c1e9782a1f1aebe3b70421d83a73a091e2502a5206931f0a58c7dee1d4d2d0e313ae6b992f5fa865d"
    with open(lib_hdinfo_filename, 'rb') as f:
        checksum = sha384(f.read()).hexdigest()
    if not checksum == lib_hdinfo_checksum:
        raise RuntimeError('unexpected %s' % lib_hdinfo_filename)


def _check_multi_mac(lib_hdinfo_filename):
    from ctypes import cdll, c_char
    expected_mac_addresses = get_license_data()
    m = cdll.LoadLibrary(lib_hdinfo_filename)
    size = 1024
    t_buf = c_char * size
    buf = t_buf()
    if (m.get_multi_mac(buf, size) == -1):
        raise RuntimeError('cound not get mac addresses')
    if buf.value.decode() != expected_mac_addresses:
        raise RuntimeError('license not for this machine')


def check_multi_mac():
    lib_hdinfo_filename = "/usr/lib/extra_hdinfo.so"
    _check_lib_hdinfo(lib_hdinfo_filename)
    _check_multi_mac(lib_hdinfo_filename)
