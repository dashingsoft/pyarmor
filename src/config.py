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
    'version': 'r1.dev2',
    'platforms': {
        'darwin.x86_64': '083446edf256a7f2b0f4692756960787027951b47e20e3618c85dbec6b673927',
        'windows.x86_64': 'a773a9ace90a8e4df7c51fcf1059b516a3627b6f47ea37b4a38feca835549c21',
        'linux.x86_64': '4b352acce57f3562a5fc612dff4b92b956f4b7023132e453f260d0a23495c3d5',
        'darwin.aarch64': '6ded7eea375437da0fc3f868cbbdfb83242d9073a0f5654d90f0488024467277',
        'linux.aarch64': '1ea933ae3b44bcbe5b5bb41dc3ab69a4deb598f748ea43de898de7b0207e25bb',
    }
}
