from distutils.util import get_platform

version = '5.7.3'

# The corresponding version of _pytransform.so
core_version = 'r6.0'

version_info = '''
PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

For more information, refer to https://pyarmor.readthedocs.io
'''

purchase_info = '''

If there is no registration code yet, please purchase one by visiting

https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1

'''

# The last three components of the filename before the extension are
# called "compatibility tags." The compatibility tags express the
# package's basic interpreter requirements and are detailed in PEP
# 425(https://www.python.org/dev/peps/pep-0425).
plat_name = get_platform().split('-')
plat_name = '_'.join(plat_name if len(plat_name) < 3 else plat_name[0:3:2])
plat_name = plat_name.replace('i586', 'i386') \
                     .replace('i686', 'i386') \
                     .replace('armv7l', 'armv7') \
                     .replace('intel', 'x86_64')
dll_ext = '.so' if plat_name.startswith('linux') else \
          '.dylib' if plat_name.startswith('macosx') else \
          '.dll'
dll_name = '_pytransform'

entry_lines = 'from %spytransform import pyarmor_runtime\n', \
              'pyarmor_runtime(%s)\n'
protect_code_template = 'protect_code.pt'

config_filename = '.pyarmor_config'
capsule_filename = '.pyarmor_capsule.zip'
license_filename = 'license.lic'
default_output_path = 'dist'
default_manifest_template = 'global-include *.py'

platform_urls = [
    'https://github.com/dashingsoft/pyarmor-core/raw/%s/platforms' %
    core_version,
    'https://pyarmor.dashingsoft.com/downloads/latest'
    ]
platform_config = 'index.json'

key_url = 'https://api.dashingsoft.com/product/key/%s/query'
