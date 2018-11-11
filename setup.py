# Always prefer setuptools over distutils
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

# To use a consistent encoding
from codecs import open
from os import listdir, path

from src.config import version
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'src', 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

pyarmor_data_files = [
    'pyshield.key', 'pyshield.lic', 'public.key',
    'product.key', 'license.lic', 'README.rst',
    'user-guide.md', 'mechanism.md',
    'examples/README.md', 'examples/README-ZH.md',
    'examples/*.sh', 'examples/*.bat',
    'examples/simple/*.py', 'examples/testmod/*.py',
    'examples/testpkg/*.py', 'examples/testpkg/mypkg/*.py',
    'examples/pybench/*.py', 'examples/pybench/package/*.py',
    'examples/py2exe/*.py', 'examples/cx_Freeze/*.py',
]

platform_data_files = [
    'platforms/win32/_pytransform.dll',
    'platforms/win_amd64/_pytransform.dll',
    'platforms/linux_i386/_pytransform.so',
    'platforms/linux_x86_64/_pytransform.so',
    'platforms/macosx_x86_64/_pytransform.dylib',
]

from sys import argv
if argv[1] == 'bdist_wheel':
    for opt in argv[1:]:
        if opt.startswith('--plat-name'):
            name = opt.split('=')[1]
            name = 'macosx_x86_64' if name.startswith('macosx_') else \
                'linux_x86_64' if name == 'manylinux1_x86_64' else \
                name
            for i in range(len(platform_data_files)):
                if platform_data_files[i].find(name) > -1:
                    platform_data_files[i] = \
                        platform_data_files[i].split('/')[-1]
                    break
            break

# def _build_file_list(d):
#     return [d + '/' + x for x in listdir(d) if path.isfile(x)]

# other_data_files = [
#     ('docs', ['docs/user-guide.md', 'docs/rationale.md']),
#     ('examples/simple', _build_file_list('docs/examples/simple')),
#     ('examples/py2exe', _build_file_list('docs/examples/py2exe')),
#     ('examples/pybench', _build_file_list('docs/examples/pybench')),
#     ('examples/pybench/package', _build_file_list('docs/examples/pybench/package')),
#     ('examples/odoo', _build_file_list('docs/examples/odoo')),
#     ('examples/odoo/weblogin', _build_file_list('docs/examples/odoo/weblogin')),
#     ('examples/odoo/weblogin2', _build_file_list('docs/examples/odoo/weblogin2')),]

setup(
    name='pyarmor',

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    version=version,
    description='A tool used to obfuscate python scripts, bind obfuscated' \
                ' scripts to fixed machine or expire obfuscated scripts.',
    long_description=long_description,

    url='https://github.com/dashingsoft/pyarmor',
    author='Jondy Zhao',
    author_email='jondy.zhao@gmail.com',

    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
        'Topic :: Security',
        'Topic :: System :: Software Distribution',

        # Pick your license as you wish
        'License :: Free To Use But Restricted',

        # Support platforms
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='protect obfuscate encrypt obfuscation distribute',

    packages=['pyarmor', 'pyarmor.polyfills', 'pyarmor.webui'],
    package_dir={'pyarmor': 'src'},
    package_data={
        'pyarmor': pyarmor_data_files + platform_data_files,
        'pyarmor.webui': ['css/*.css', 'js/*.js', '*.html', '*.js', 'manager.*'],
    },

    # data_files=other_data_files,

    entry_points={
        'console_scripts': [
            'pyarmor=pyarmor.pyarmor:main_entry',
            'pyarmor-webui=pyarmor.webui.server:main',
        ],
    },
)
