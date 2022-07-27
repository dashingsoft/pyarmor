from sys import platform

version = '7.6.0'

# The corresponding version of pytransform.so
core_version = 'r51.5'

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
    'version': 'r2.dev1',
    'platforms': {
        'darwin.x86_64': '00a484acdc8ff6fab2068f52dc20f40f8c73bdd6da20788496329a936639fea1',
        'windows.x86_64': 'bbdc5347962561a20bd936d2f60e0e63323269dd2a391e4cb5e95774c947f5ff',
        'linux.x86_64': '5149a5f193cd9a593b3617bdb6bbf0d98e07b99ca6216381e86bd78b1aaf1b47',
        'darwin.aarch64': 'aa1389afee7942bf4e25a6d956210ea8499ad5f9e83a6398fa4d0ab9af7bd1ab',
        'linux.aarch64': '271b4074002e89d11e2137d5cbc68cf0cd19571f0724e508186989c6ca1aa261',
    }
}
