from sys import platform

version = '7.5.1'

# The corresponding version of pytransform.so
core_version = 'r50.4'

version_info = '''
PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

For more information, refer to https://pyarmor.readthedocs.io
'''

purchase_info = '''

If there is no registration code yet, please purchase one by command

    pyarmor register --buy

Or open the following url in any webbrowser directly

https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1

'''

dll_name = '_pytransform'
dll_ext = '.dylib' if platform == 'darwin' \
    else '.dll' if platform in ('win32', 'cygwin') else '.so'


entry_lines = 'from %spytransform%s import pyarmor_runtime\n', \
              'pyarmor_runtime(%s)\n'
protect_code_template = 'protect_code%s.pt'

config_filename = '.pyarmor_config'
capsule_filename = '.pyarmor_capsule.zip'
license_filename = 'license.lic'
default_output_path = 'dist'
default_manifest_template = 'global-include *.py'

platform_old_urls = (
    'https://github.com/dashingsoft/pyarmor-core/raw/r41.15a/platforms',
    'https://pyarmor.dashingsoft.com/downloads/r41.15a',
)
platform_config = 'index.json'
platform_url = 'https://pyarmor.dashingsoft.com/files/{version}'

key_url = 'https://api.dashingsoft.com/product/key/%s/query'
reg_url = 'https://api.dashingsoft.com/product/key/activate/%s/'
buy_url = 'https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1'
help_url = 'https://pyarmor.readthedocs.io/{lang}/v%s/{page}' % version

sppmode_info = {
    'version': 'r1.dev3',
    'platforms': {
        'darwin.x86_64': '229a506ae3d351cbe1f4e5039c87d255009c5abc92c92100e2eece1d9578b5f2',
        'windows.x86_64': '48c7298f1225f91bbcd14ffe01ffc992717217e6d590eb46703c5805c518a773',
        'linux.x86_64': '220de6f34ed5aa9a7b407ca64a6b1c45712691b24f217e2001bc529ad91d8642',
        'darwin.aarch64': 'ae37468bd7207eb064f391819af9f0efe8178baf0661e2607f0083c7668d870b',
        'linux.aarch64': '54fdd923c33f6b076efee3e19a72f1f0ad49493d14c3512e10758fcd3c40305e',
    }
}
