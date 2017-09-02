#!/usr/bin/env python
#

import sys
import os

from config import version

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def get_description():
    README = os.path.abspath(os.path.join(os.path.dirname(__file__), 'README.rst'))
    with open(README, 'r') as f:
        return f.read()

def main():
    args = dict(
        name='pyarmor',
        version=version,
        description='A command line tool used to import or run encrypted python scripts.',
        long_description=get_description(),
        keywords=['encrypt', 'distribute'],
        py_modules=['pyarmor', 'pytransform', 'pyimcore', 'config'],
        author='Jondy Zhao',
        author_email='jondy.zhao@gmail.com',
        maintainer='Jondy Zhao',
        maintainer_email='jondy.zhao@gmail.com',
        url='https://github.com/dashingsoft/pyarmor',
        platforms='Windows,Linux',
        license='Shareware',
        )
    setup(**args)

if __name__ == '__main__':
    main()
