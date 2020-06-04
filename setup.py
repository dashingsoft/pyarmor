# Always prefer setuptools over distutils
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# To use a consistent encoding
from codecs import open
from os import path
from sys import argv

from src.config import version
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'src', 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

pyarmor_data_files = [
    'LICENSE', 'LICENSE-ZH',
    'pyshield.key', 'pyshield.lic', 'public.key',
    'product.key', 'license.tri', 'README.rst',
    'protect_code.pt', 'protect_code2.pt', 'public_capsule.zip',
    'plugins/README.md', 'plugins/check_ntp_time.py',
    'plugins/check_docker.py', 'plugins/assert_armored.py',
    'examples/README.md', 'examples/README-ZH.md',
    'examples/*.sh', 'examples/*.bat',
    'examples/simple/*.py', 'examples/testmod/*.py',
    'examples/testpkg/*.py', 'examples/testpkg/mypkg/*.py',
    'examples/pybench/*.py', 'examples/pybench/package/*.py',
    'examples/py2exe/*.py', 'examples/cx_Freeze/*.py',
    'examples/helloworld/*.py',
]

platform_data_files = [
    'platforms/index.json',
    'platforms/windows/x86/_pytransform.dll',
    'platforms/windows/x86_64/_pytransform.dll',
    'platforms/linux/x86/_pytransform.so',
    'platforms/linux/x86_64/_pytransform.so',
    'platforms/darwin/x86_64/_pytransform.dylib',
]

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

setup(
    name='pyarmor',

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    version=version,
    description='A tool used to obfuscate python scripts, bind obfuscated' \
                ' scripts to fixed machine or expire obfuscated scripts.',
    long_description=long_description,

    license='Free To Use But Restricted',

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

    packages=['pyarmor', 'pyarmor.polyfills', 'pyarmor.helper'],
    package_dir={'pyarmor': 'src'},
    package_data={
        'pyarmor': pyarmor_data_files + platform_data_files,
    },

    entry_points={
        'console_scripts': [
            'pyarmor=pyarmor.pyarmor:main_entry',
        ],
    },
)
