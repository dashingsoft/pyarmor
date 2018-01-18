#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2018 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 4.0.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2018/01/17
#
#  @Description:
#
#   A tool used to import or un encrypted python scripts.
#
'''
mkdir projects/myproject
cd projects/myproject
pyarmor init
pyarmor update --manifest=''
pyarmor info
pyarmor build
'''
import logging
import os
import sys

try:
    import argparse
except ImportError:
    # argparse is new in version 2.7
    import polyfills.argparse as argparse

from config import (version, version_info, trial_info,
                    platform, dll_ext, dll_name)

from utils import make_config, make_capsule

def armorcommand(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
    wrap.__doc__ = func.__doc__
    return wrap

@armorcommand
def _init(args):
    '''Create an empty repository or reinitialize an existing one

This command creates an empty repository in the PATH/NAME - basically
a configure file project.json, a project capsule project.zip will be
created.

If --capsule is specified, copy CAPSULE to project.zip other than
create a new capsule.

EXAMPLES

* Create a default project.

    python pyarmor.py init --path=projects myproject

* Create a project with existing capsule

    python pyarmor.py init --path=projects -C project2/project.zip myproject

    '''
    logging.info('Create project in %s ...', os.path.abspath(args.path))

    path = os.path.join(args.path, args.name[0])
    if os.path.exists(path):
        logging.info('Prject path %s has been exists', path)
    else:
        logging.info('Make project directory %s', path)
        os.mkdir(path)        

    logging.info('Create configure file ...')
    filename = os.path.join(path, 'project.json')
    make_config(filename)
    logging.info('Configure file %s created', filename)

    logging.info('Create project capsule ...')
    filename = os.path.join(args.path, 'project.zip')
    make_capsule(filename)
    logging.info('Project capsule %s created', filename)

    logging.info('Project init successfully.')

@armorcommand
def _update(args):
    pass

def _info(args):
    pass

def _license(args):
    pass

def _target(args):
    pass

def _obfuscate(args):
    pass

def _build(args):
    pass

def _check(args):
    pass

def _benchmark(args):
    pass

def _hdinfo(args):
    pass

class ArgumentDefaultsRawFormatter(argparse.ArgumentDefaultsHelpFormatter):

    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

def main(args):

    parser = argparse.ArgumentParser(
        prog='pyarmor.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog='See "pyarmor.py <command> -h" for more information ' \
               'on a specific command.'
    )
    parser.add_argument('-v', '--version', action='version',
                        version='Show version information')

    subparsers = parser.add_subparsers(
        title='The most commonly used pyarmor commands are',
        metavar='<command>'
    )

    parser_init = subparsers.add_parser(
        'init',
        epilog=_init.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Create an empty project or reinitialize an existing one'
    )
    parser_init.add_argument('name', nargs=1, metavar='NAME', default='',
                             help='Project name')
    parser_init.add_argument('-p', '--path', default='',
                             help='Parent path of project')
    parser_init.add_argument('-C', '--capsule',
                             help='Capsule filename of another project')
    parser_init.add_argument('--src', required=True,
                             help='Path of python scripts')
    parser_init.set_defaults(func=_init)

    parser_update = subparsers.add_parser('update', help='Update a project')
    parser_update.set_defaults(func=_update)

    parser_info = subparsers.add_parser('info', help='Show project information')
    parser_info.set_defaults(func=_info)

    parser_check = subparsers.add_parser('check', help='Check consistency of project')
    parser_check.set_defaults(func=_check)

    parser_build = subparsers.add_parser('build', help='Build project, obfuscate all the scripts in the project')
    parser_build.set_defaults(func=_build)

    parser_target = subparsers.add_parser('target', help='Manage target for project')
    parser_target.set_defaults(func=_target)

    parser_license = subparsers.add_parser('license', help='Manage licenses for project')
    parser_license.set_defaults(func=_license)

    parser_hdinfo = subparsers.add_parser('hdinfo', help='Show hardware information')
    parser_hdinfo.set_defaults(func=_hdinfo)

    parser_benchmark = subparsers.add_parser('benchmark', help='Run benchmark test in current machine')
    parser_benchmark.set_defaults(func=_benchmark)

    parser_obfuscate = subparsers.add_parser('obfuscate', help='Obfuscate python scripts')
    parser_obfuscate.set_defaults(func=_obfuscate)

    args = parser.parse_args(args)
    args.func(args)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main(sys.argv[1:])
