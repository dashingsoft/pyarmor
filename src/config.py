from sys import platform

version = '7.6.1'

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
    'version': 'r2',
    'platforms': {
        'darwin.x86_64': 'e15b4863c012f43d6e5de8a1abe12bf5baf2318254ad072f875d3eace2be2848',
        'windows.x86_64': '424ea8b2ffb11ffabf6b8c87c90979c53ce121c98fa593a1902b56d8830cbc76',
        'linux.x86_64': 'd7221bd6e9d889862b900307ae3e2ab117f8330c91e404deb45eeca3a17efce0',
        'darwin.aarch64': 'aa1389afee7942bf4e25a6d956210ea8499ad5f9e83a6398fa4d0ab9af7bd1ab',
        'linux.aarch64': 'd06e6d553f6f1e452913759a56325cc75557eb4b2c860b3f3e3406448d383fa4',
    }
}
