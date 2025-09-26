from sys import platform

version = '9.2.0'

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
runtime_filename = 'runtime.cfg'
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
buy_url = 'https://jondy.github.io/paypal/index.html'
help_url = 'https://pyarmor.readthedocs.io/{lang}/v%s/{page}' % version

sppmode_info = {
    'version': 'r4',
    'platforms': {
        'darwin.x86_64': '73a5abdbd9bc37e46c1e374eeec9ca81dd2b7fce842a250e7fc478d6653ae8e4',
        'windows.x86_64': '6af4b642a62eebacc2611ea4f60f3fed25f4cb7251a9e1ce39f4109cb23f628e',
        'linux.x86_64': '9e2f29d38035b5db2f12ba7afc337b2e41a57cf32abbc50a0b3502d074343704',
        'darwin.aarch64': 'f6daa1f0d2f287488d188b32f1ac2896dee5ed39cf1374d53ad9c05610dd1a67',
        'linux.aarch64': 'f20a533f7f0181b51575600d69390e3df2d112e3cd617db93b9e062037a00bd8',
    }
}
