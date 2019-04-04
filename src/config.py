from distutils.util import get_platform

version = '5.2.5'

version_info = '''
PyArmor is a command line tool used to obfuscate python scripts, bind
obfuscated scripts to fixed machine or expire obfuscated scripts.

For more information, refer to http://pyarmor.dashingsoft.com
'''

# The last three components of the filename before the extension are
# called "compatibility tags." The compatibility tags express the
# package's basic interpreter requirements and are detailed in PEP
# 425(https://www.python.org/dev/peps/pep-0425).
plat_name = get_platform().split('-')
plat_name = '_'.join(plat_name if len(plat_name) < 3 else plat_name[0:3:2])
plat_name = plat_name.replace('i586', 'i386').replace('i686', 'i386') \
                                             .replace('intel', 'x86_64')
dll_ext = '.so' if plat_name.startswith('linux') else \
          '.dylib' if plat_name.startswith('macosx') else \
          '.dll'
dll_name = '_pytransform'

entry_lines = 'from %spytransform import pyarmor_runtime\n', \
              'pyarmor_runtime(%s)\n'

config_filename = '.pyarmor_config'

capsule_filename = '.pyarmor_capsule.zip'

license_filename = 'license.lic'

protect_code_template = 'protect_code.pt'

default_output_path = 'dist'

default_manifest_template = 'global-include *.py'

default_obf_module_mode = 'des'

default_obf_code_mode = 'des'


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
You're using trail version. Free trial version that never expires,
but project capsule generated is fixed by hardcode, so all the
encrypted files are encrypted by same key.

A registration code is required to generate random project capsule.
If PyArmor is helpful for you, please purchase one by visiting

  https://order.shareit.com/cart/add?vendorid=200089125&PRODUCT[300871197]=1

If you have received a registration code, just replace the content
of "license.lic" with registration code only (no newline).

Enjoy it!

'''

help_footer = '''
For more information, refer to http://pyarmor.dashingsoft.com
'''
