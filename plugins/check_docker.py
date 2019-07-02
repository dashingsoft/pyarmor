from pytransform import get_license_code


def check_docker_id():
    cid = None
    with open("/proc/self/cgroup") as f:
        for line in f:
            if line.split(':', 2)[1] == 'name=systemd':
                cid = line.strip().split('/')[-1]
                break

    if cid is None or cid != get_license_code():
        raise RuntimeError('license not for this machine')
