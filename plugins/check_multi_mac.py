from hashlib import sha384
from ctypes import cdll, c_char

lib_hdinfo_filename = "/usr/lib/extra_hdinfo.so"
lib_hdinfo_checksum = "7838938a424b273c1e9782a1f1aebe3b70421d83a73a091e2502a5206931f0a58c7dee1d4d2d0e313ae6b992f5fa865d"
expected_mac_addresses = "00:16:3e:08:20:b4,70:f1:a1:23:f0:94"


def _check_lib_hdinfo():
    with open(lib_hdinfo_filename, 'rb') as f:
        checksum = sha384(f.read()).hexdigest()
    if not checksum == lib_hdinfo_checksum:
        raise RuntimeError('unexpected %s' % lib_hdinfo_filename)


def _check_multi_mac():
    m = cdll.LoadLibrary(lib_hdinfo_filename)
    size = 1024
    t_buf = c_char * size
    buf = t_buf()
    if (m.get_multi_mac(buf, size) == -1):
        raise RuntimeError('cound not get mac addresses')
    if buf.value.decode() != expected_mac_addresses:
        raise RuntimeError('license not for this machine')


def check_multi_mac():
    _check_lib_hdinfo()
    _check_multi_mac()
