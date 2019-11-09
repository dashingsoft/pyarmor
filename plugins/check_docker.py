def get_license_data():
    from pytransform import _pytransform
    from ctypes import py_object, PYFUNCTYPE
    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(('get_registration_code', _pytransform))
    rcode = dlfunc().decode()
    index = rcode.find(';', rcode.find('*CODE:'))
    return rcode[index+1:]


def check_docker():
    cid = None
    with open("/proc/self/cgroup") as f:
        for line in f:
            if line.split(':', 2)[1] == 'name=systemd':
                cid = line.strip().split('/')[-1]
                break

    if cid is None or cid != get_license_data():
        raise RuntimeError('license not for this machine')
