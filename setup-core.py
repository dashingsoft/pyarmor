from setuptools import setup
from sys import argv

from src.config import version, support_platforms

long_description = '''PyArmor is a command line tool used to obfuscate python scripts,
bind obfuscated scripts to fixed machine or expire obfuscated scripts.

The core of PyArmor is written by C, this package includes the
prebuilt dynamic libraries for different platforms:
{platforms}

Each platform above has its own wheel, the platform tag is simply
`distutils.util.get_platform()` with all hyphens - and periods
. replaced with underscore _. Refer to
https://www.python.org/dev/peps/pep-0425

The following platforms haven't the corresponding wheel because PyPi
don't support these platform flags. But all of them can be downloaded from
http://pyarmor.dashingsoft.com/downloads/platforms
{others}

Send email to jondy.zhao@gmail.com if you'd like to run PyArmor in
other platform.

'''.format(platforms='\n- '.join([''] + [x for x, _ in support_platforms[0]]),
           others='\n- '.join([''] + [x for x, _ in support_platforms[1]]))


def get_plat_path():
    for opt in argv[1:]:
        if opt.startswith('--plat-name'):
            name = opt.split('=')[1]
            return dict(support_platforms[0]).get(name, name)


setup(
    name='pyarmor-core',

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    version=version,
    description='A packcage includes the prebuilt binary library for PyArmor',
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

    keywords='obfuscation pyarmor',

    packages=['pyarmor'],
    package_dir={'pyarmor': 'src/platforms/' + get_plat_path()},
    package_data={
        'pyarmor': ['_pytransform.*']
    },
)
