from distutils.util import get_platform

version = '4.1.2'

version_info = '''
Pyarmor is a tool used to import or run the encrypted python scripts.
Only by a few extra files, pyarmor can run and imported encrypted
files in the normal python environments.

Pyarmor just likes an enhancement which let python could run or import
encrypted files.

'''

trial_info = '''
You're using trail version. Free trial version that never expires,
but project capsule generated is fixed by hardcode, so all the
encrypted files are encrypted by same key.

A registration code is required to generate random project capsule.
If Pyarmor is helpful for you, please purchase one by visiting

https://shopper.mycommerce.com/checkout/cart/add/55259-1

If you have received a registration code, just replace the content
of "license.lic" with registration code only (no newline).

Enjoy it!

'''

help_footer = '''
For more information, refer to https://github.com/dashingsoft/pyarmor
'''

# The last three components of the filename before the extension are
# called "compatibility tags." The compatibility tags express the
# package's basic interpreter requirements and are detailed in PEP
# 425(https://www.python.org/dev/peps/pep-0425).
plat_name = get_platform().split('-')
plat_name = '_'.join(plat_name if len(plat_name) < 3 else plat_name[0:3:2])

dll_ext = '.so' if plat_name.startswith('linux') else \
          '.dylib' if plat_name.startswith('macosx') else \
          '.dll'
dll_name = '_pytransform'

entry_code = '''from pytransform import pyarmor_runtime
pyarmor_runtime(%s)
'''

config_filename = '.pyarmor_config'

capsule_filename = '.pyarmor_capsule.zip'

license_filename = 'license.lic'

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
