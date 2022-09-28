from sys import platform

version = '7.7.0'

# The corresponding version of pytransform.so
core_version = 'r52.6'

version_info = '''
PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

For more information, refer to https://pyarmor.readthedocs.io
'''

purchase_info = '''
If there is no registration code yet, please purchase one by command

    pyarmor register --buy
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
    'version': 'r4.dev1',
    'platforms': {
        'darwin.x86_64': '581d549cc054f6d863f67069a149bf53e4f4fb608dd6ad531d9d497ee0adb773',
        'windows.x86_64': '2f9509d345b42ad66dde6f38925ec9bc6008569b189d0b63ca269c716623fcbc',
        'linux.x86_64': '0b7e885947b52b4373ae19e3410736a35e9dbc9a561c4b20d8f13628cb9a37c3',
        'darwin.aarch64': 'ffbb70a443235e14cc0f498037ce7a93b07b4f35efb94fcdbf25d021d597d3e7',
        'linux.aarch64': '8550a3c130c22dbd98a82c8a801f3538a2fec910fc2160a4c64505b9f1b87d6e',
    }
}
