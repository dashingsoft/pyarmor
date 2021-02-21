def check_multiple_machine():
    from ctypes import c_char, py_object, PYFUNCTYPE

    def _get_license_data():
        try:
            from pytransform import _pytransform
        except Exception:
            # For super mode
            from pytransform import get_license_data
            return get_license_data().decode()

        prototype = PYFUNCTYPE(py_object)
        dlfunc = prototype(('get_registration_code', _pytransform))
        rcode = dlfunc().decode()
        index = rcode.find(';', rcode.find('*CODE:'))
        return rcode[index+1:]

    def _get_hd_info():
        HT_HARDDISK = 0
        try:
            from pytransform import _pytransform
        except Exception:
            # For super mode
            from pytransform import get_hd_info
            return get_hd_info(0)

        size = 256
        t_buf = c_char * size
        buf = t_buf()
        if (_pytransform.get_hd_info(HT_HARDDISK, buf, size) == -1):
            raise RuntimeError('Get hardware information failed')
        return buf.value.decode()

    if _get_hd_info() not in _get_license_data().split(';'):
        raise RuntimeError('This license is not for this machine')
