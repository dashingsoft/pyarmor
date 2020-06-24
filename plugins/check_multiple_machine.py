def check_multiple_machine():
    from ctypes import c_char
    from pytransform import _pytransform, HT_HARDDISK
    from ctypes import py_object, PYFUNCTYPE

    def _get_license_data():
        prototype = PYFUNCTYPE(py_object)
        dlfunc = prototype(('get_registration_code', _pytransform))
        rcode = dlfunc().decode()
        index = rcode.find(';', rcode.find('*CODE:'))
        return rcode[index+1:]

    def _get_hd_info():
        size = 256
        t_buf = c_char * size
        buf = t_buf()
        if (_pytransform.get_hd_info(HT_HARDDISK, buf, size) == -1):
            raise RuntimeError('Get hardware information failed')
        return buf.value.decode()

    if _get_license_data().find(_get_hd_info()) == -1:
        raise RuntimeError('This license is not for this machine')
