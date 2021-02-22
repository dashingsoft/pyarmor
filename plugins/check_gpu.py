import re
import subprocess
from pytransform import get_expired_days, get_user_data


def get_expiration_info():
    try:
        # license_info = get_license_info()
        left_days = get_expired_days()
        if left_days == -1:
            print('This license for %s is never expired')
        else:
            print(f'This license for will be expired in {left_days} days')
    except Exception as e:
        print(e)


def check_gpu():
    gpu_uuids = get_gpu_list()
    assert len(gpu_uuids) == 1  # 1 GPU per instance
    if gpu_uuids:
        if len(gpu_uuids) > 1:
            raise RuntimeError(f'This license is issued for one particular GPU, {len(gpu_uuids)} GPUs detected')
        else:
            assert len(gpu_uuids) == 1
            gpu_uuid = gpu_uuids[0]
            if gpu_uuid != get_user_data().decode('utf-8').lower():
                print(f'User data {get_user_data()}')
                raise RuntimeError('A GPU matching the license is not found')
            else:
                print('A GPU license check is passed')
                get_expiration_info()
    else:
        raise RuntimeError('No GPUs detected, this license is issued to particular GPU')


def get_gpu_list():
    try:
        out = subprocess.run(["nvidia-smi", "-L"], check=True, capture_output=True)
        out.check_returncode()
        out = out.stdout.decode('utf-8').lower()
        # output example
        # gpu 0: geforce gtx 1080 ti (uuid: gpu-70ef1701-4072-9722-cc0b-7c7e75ff76db)
        # gpu 1: geforce gtx 1080 ti (uuid: gpu-5b8df9cc-3b3c-d07a-8bd1-e2a51af4cfa9)
        # ...
        uuid_list = re.findall(r'\(uuid: \S+\)', out)
        uuid_list = [uuid.replace('(uuid: ', '').replace(')', '')
                     for uuid in uuid_list]
        return uuid_list
    except:
        # any error means no GPUs available
        return None
