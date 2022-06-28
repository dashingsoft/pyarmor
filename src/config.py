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
    'version': 'r1',
    'platforms': {
        'darwin.x86_64': '37da88dcdec2e3f2a6693e199fd291ca8d47b9d11a299a3f3fbba80b07c9cf62',
        'windows.x86_64': 'd8989df0b159a7b0de1f563ebeca80c6377083b593654eacf073c8e91a7b7423',
        'linux.x86_64': 'a6f36e5390ad54b861e69b4c725a64e62e5fc6237276f6f19c82a3826cf172da',
        'darwin.aarch64': 'bf90c8aebfe359f647512c5857c88cdb07d75e936381f52e21dcd04bfe37afd6',
        'linux.aarch64': '744483af8cf7747888ed5fdbd9578408e9ef00f97fc416b076b27433c7cfa69a',
    }
}
