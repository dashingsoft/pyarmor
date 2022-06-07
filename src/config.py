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
    'version': 'v1',
    'platforms': {
        'darwin.x86_64': 'bd7b778e2f33de12fccb08802f2f88ad314c9199c6f8aaa837a161264295e786',
        'windows.x86_64': '8cd9501b94a6312562806ba730a94ffe0072390de1a0ec3ffd29308e124e4cef',
        'linux.x86_64': 'f63d7119c217d8f2fc50e8db2a14e85343d59778049a8047f362b6c3cc7e4818',
        'darwin.aarch64': '366ea86df90e681f4a20fc83467e8bd1ab4947073c7d16d3f0d85d7a6282de65',
        'linux.aarch64': '2c875d19c779f08bd533992e52c15159c3e92aba1a9d92ebaf036131cc3063ff',
    }
}
