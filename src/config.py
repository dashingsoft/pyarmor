from sys import platform

version = '7.4.1'

# The corresponding version of pytransform.so
core_version = 'r49.3'

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
    'version': 'r48.2',
    'platforms': {
        'darwin.x86_64': '5dc133de7b08beda06316a50e1b0dbc1cd9d408feda58c9d38b9ef5389d54720',
        'windows.x86_64': 'bf53e34355d0c932d161f96cba893497936cbcbd6aa9feb7b90e56f436d622d0',
        'linux.x86_64': 'f7af75c3042ee9aa5ca21701fb08c4e4b5331ac66c570192734e06e62a9d703c',
    }
}
