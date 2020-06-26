#! /usr/bin/env python
'''This script is used to get the license information of one package
obfuscated by PyArmor.

Copy it to the obfuscated package, generally it should be in the same
path of runtime module or package 'pytransform', and run it:

    cd /path/to/obfuscated-package
    python get_license_info.py

It also could be run by this way

    cd /path/to/obfuscated-package
    python -m pyarmor.helper.get_license_info

'''
import pytransform

if hasattr(pytransform, 'pyarmor_init'):
    pytransform.pyarmor_init(is_runtime=1)

print('Check obfuscated package in the current path')
print('Get license information from pytransform at %s:' % pytransform.__file__)
for k, v in pytransform.get_license_info().items():
    print('%10s: %s' % (k, '' if v is None else v))
