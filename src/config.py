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
        'darwin.x86_64': '30adf113ad3568eb819bb1789340025aa8afa16ad9b8577bfb6e654bb3cf55a6',
        'windows.x86_64': '0b79d39bed010bd742fa0567658ce7e1ac7188f5ac77070ee3258a744c83b347',
        'linux.x86_64': '6892a4fa7871355c949c8c936142f2bfb1b0eae95c40774f135b6e8bee04861e',
        'darwin.aarch64': 'f34e6a7caaf7c4b225bba8a6663782cb346285373bf80926636aeb3f6e84697f',
        'linux.aarch64': '5ea34d0def4ae5edb27e3f4220e2ef1b13afceb1dc83cdfe69f3a50495d2c838',
    }
}
