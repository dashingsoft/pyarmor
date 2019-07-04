from distutils.util import get_platform

version = '5.4.4'

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

default_obf_module_mode = 'des'
default_obf_code_mode = 'des'

platform_prefix = 'https://pyarmor.dashingsoft.com/downloads/platforms'
platform_config = 'index.json'


#
# DEPRECATED From v3.4.0, all the follwing lines will be removed from v4
#

# Extra suffix char for encrypted python scripts
ext_char = 'e'

wrap_runner = '''import pyimcore
from pytransform import exec_file
exec_file('%s')
'''

trial_info = '''
You're using trail version. Free trial version never expires,
the limitations are

- The maximum size of code object is 35728 bytes in trial version
- The scripts obfuscated by trial version are not private. It means
  anyone could generate the license file which works for these
  obfuscated scripts.

A registration code is required to obfuscate big code object or
generate private obfuscated scripts.

If PyArmor is helpful for you, please purchase one by visiting

  https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1

If you have received a registration code, run the following command to
make it effective::

  pyarmor register REGISTRATION_CODE

Enjoy it!

'''

help_footer = '''
For more information, refer to http://pyarmor.dashingsoft.com
'''

download_url = 'http://pyarmor.dashingsoft.com/downloads/platforms'
support_platforms = [
    (
        ('win32', 'win32'),
        ('win_amd64', 'win_amd64'),
        ('manylinux1_i686', 'linux_i386'),
        ('manylinux1_x86_64', 'linux_x86_64'),
        ('macosx_10_11_x86_64', 'macosx_x86_64'),
    ),
    (
        ('linux_ppc64', 'ppc64le'),
        ('linux_armv5', 'armv5'),
        ('linux_armv7', 'armv7'),
        ('linux_aarch32', 'armv8.32-bit'),
        ('linux_aarch64', 'armv8.64-bit'),
        ('linux.musl_x86_64', 'alpine'),
        ('ios_arm64', 'ios.arm64'),
        ('freebsd_x86_64', 'freebsd'),
    )
]
