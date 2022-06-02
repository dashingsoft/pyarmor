from sys import platform

version = '7.5.0'

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
    'version': 'r50.4',
    'platforms': {
        'darwin.x86_64': '75ae0ab2f1124acbd72caf2a78f5c444c2a5d556aabf3c2ea975a2e96a3a8e32',
        'windows.x86_64': 'c8845476ac8913871565cc1632fbd1e6926db398a32c649d70c8d1c6e86928a6',
        'linux.x86_64': '70e8c2468702ad4d6644670803bd5bdf77e1d905bacff8884696b5f228057586',
        'darwin.aarch64': 'dd102b537c037e2abb57bda0b4cfec695798ad24b6df8a1f2dbb75bca0ba41e9',
        'linux.aarch64': '96669ca1dabaa4575ac59c6097cc66d5d7641087e2c8f66e590a64792b56174c',
    }
}
