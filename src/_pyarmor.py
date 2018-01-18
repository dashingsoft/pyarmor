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
#   A tool used to import or run obfuscated python scripts.
#
'''See "pyarmor.py <command> -h" for more information on a specific command.

Here an example to show how to use obfuscated scripts:

* Create a project to include all .py files in "examples/pybench"

    python pyarmor.py init --path=projects --src=examples/pybench \
                           --entry=pybench.py myproject

* Build project, it will obfuscate all .py files and save them in
  default output path "build"

    python pyarmor.py build projects/myproject

* Run obfuscated script in the output path "build"

    cd build
    python pybench.py

'''
import json
import logging
import os
import shutil
import sys

try:
    import argparse
except ImportError:
    # argparse is new in version 2.7
    import polyfills.argparse as argparse

from config import  version, version_info, trial_info, \
                    platform, dll_ext, dll_name

from project import Project
from utils import make_capsule, build_manifest, obfuscate_scripts, make_runtime, make_project_license

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

Option --src specifies where to find python source files. By default,
  all .py files in this directory will be included in this project.

Option --entry specifies main script, which could be run directly
after obfuscated.

If --capsule is specified, copy CAPSULE to project.zip other than
create a new capsule.

EXAMPLES

* Create a default project.

    python pyarmor.py init --path=projects --src=examples myproject

* Create a project with existing capsule

    python pyarmor.py init --path=projects -C project2/project.zip \
                           --src=examples myproject

    '''
    name = args.name[0]
    logging.info('Create project %s in %s ...', name, args.path)

    path = os.path.join(args.path, name)
    if os.path.exists(path):
        logging.info('Prject path %s has been exists', path)
    else:
        logging.info('Make project directory %s', path)
        os.mkdir(path)

    project = Project(name=name, title=name.capitalize(),
                      src=args.src, entry=args.entry)
    logging.info('Create configure file ...')
    filename = os.path.join(path, 'project.json')
    project.dump(filename)
    logging.info('Configure file %s created', filename)

    logging.info('Create project capsule ...')
    filename = os.path.join(path, 'project.zip')
    if args.capsule is None:
        make_capsule(filename)
    else:
        logging.info('Copy %s to %s', args.capsule, filename)
        shutil.copy2(args.capsule, filename)
    logging.info('Project capsule %s created', filename)

    logging.info('Project init successfully.')

@armorcommand
def _update(args):
    cfile = args.project
    logging.info('Update project %s ...', os.path.dirname(cfile))

    project = Project()
    project.load(cfile)

    keys = project._update(dict(args._get_kwargs()))
    logging.info('Changed attributes: %s', keys)

    project.dump(cfile)
    logging.info('Update project OK.')

@armorcommand
def _info(args):
    cfile = args.project
    logging.info('Show project %s ...', os.path.dirname(cfile))

    project = Project()
    project.load(cfile)

    logging.info('\n%s', json.dumps(project, indent=2))

@armorcommand
def _build(args):
    cfile = args.project
    logging.info('Build project %s ...', os.path.dirname(cfile))

    project = Project()
    project.load(cfile)

    if args.target is None:
        targets = [ '' ]
        targets.extend(project.targets)
    else:
        targets = args.target.split(',')

    if not args.only_runtime:
        t = targets[0]
        capsule = project.capsule
        output = os.path.join(project.output, t)
        mode = project.get_obfuscate_mode()
        files = project.get_build_files(args.force)
        obfuscate_scripts(files, mode, capsule, output)

        for x in targets[1:]:
            pass
            
        project.build_time = time.time()

    if not args.no_runtime:
        capsule = project.capsule
        for x in targets:
            platform, licfile = project.get_target(x)
            output = os.path.join(project.output, x)
            make_runtime(capsule, output, licfile, platform)

@armorcommand
def _license(args):
    pass

@armorcommand
def _target(args):
    pass

@armorcommand
def _obfuscate(args):
    pass

@armorcommand
def _check(args):
    pass

@armorcommand
def _benchmark(args):
    pass

@armorcommand
def _hdinfo(args):
    pass

class ArgumentDefaultsRawFormatter(argparse.ArgumentDefaultsHelpFormatter):

    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

def main(args):

    parser = argparse.ArgumentParser(
        prog='pyarmor.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='pyarmor used to import or run obfuscated python scripts.',
        epilog=__doc__,
    )
    parser.add_argument('-v', '--version', action='version',
                        version='Show version information')

    subparsers = parser.add_subparsers(
        title='The most commonly used pyarmor commands are',
        metavar='<command>'
    )

    #
    # Command: init
    #
    cparser = subparsers.add_parser(
        'init',
        epilog=_init.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Create an empty project or reinitialize an existing one'
    )
    cparser.add_argument('name', nargs=1, metavar='NAME', default='',
                         help='Project name')
    cparser.add_argument('-p', '--path', default='',
                         help='Parent path of project')
    cparser.add_argument('-C', '--capsule',
                         help='Capsule filename of another project')
    cparser.add_argument('--entry',
                         help='Entry script of this project')
    cparser.add_argument('--src', required=True,
                         help='Base path of python scripts')
    cparser.set_defaults(func=_init)


    #
    # Command: update
    #
    cparser = subparsers.add_parser(
        'update',
        epilog=_update.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Update project information')
    cparser.add_argument('project', nargs='?', metavar='PROJECT',
                         default='project.json',
                         help='Project configure file')
    cparser.add_argument('--name')
    cparser.add_argument('--title')
    cparser.add_argument('--description')
    cparser.add_argument('--src')
    cparser.add_argument('--output', metavar='PATH')
    cparser.add_argument('--manifest', metavar='TEMPLATE',
                         help='Manifest template string')
    cparser.add_argument('--entry', metavar='SCRIPT',
                         help='Entry script of this project')
    cparser.add_argument('--obf-module-mode',
                         choices=Project.OBF_MODULE_MODE)
    cparser.add_argument('--obf-code-mode',
                         choices=Project.OBF_CODE_MODE)
    cparser.set_defaults(func=_update)

    #
    # Command: info
    #
    cparser = subparsers.add_parser(
        'info',
        epilog=_info.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Show project information'
    )
    cparser.add_argument('project', nargs='?', metavar='PROJECT',
                         default='project.json',
                         help='Project path or configure file')
    # cparser.add_argument('-a', '--all', action='store_true',
    #                          help='Show all of project information')
    # cparser.add_argument('-b', '--basic', action='store_true',
    #                          help='Show project basic information')
    # cparser.add_argument('-c', '--license', action='store_true',
    #                          help='Show project license information')
    # cparser.add_argument('-t', '--target', action='store_true',
    #                          help='Show project target information')
    # cparser.add_argument('--verbose', action='store_true',
    #                          help='Show detail information')
    cparser.set_defaults(func=_info)

    #
    # Command: check
    #
    cparser = subparsers.add_parser('check',
                                    help='Check consistency of project')
    cparser.add_argument('project', nargs='?', metavar='PROJECT',
                         default='project.json',
                         help='Project configure file')
    cparser.set_defaults(func=_check)

    #
    # Command: build
    #
    cparser = subparsers.add_parser(
        'build',
        epilog=_build.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Build project, obfuscate all the scripts in the project')
    cparser.add_argument('project', nargs='?', metavar='PROJECT',
                         help='Project path or configure file')
    cparser.add_argument('-B', '--force', action='store_true',
                         help='Obfuscate all scripts even if it\'s not updated')
    cparser.add_argument('-r', '--only-runtime', action='store_true',
                         help='Generate extra runtime files only')
    cparser.add_argument('-n', '--no-runtime', action='store_true',
                         help='DO NOT generate extra runtime files')
    cparser.add_argument('-t', '--target',
                         help='Build these targets only')
    cparser.set_defaults(func=_build)

    #
    # Command: target
    #
    cparser = subparsers.add_parser('target', help='Manage target for project')
    cparser.add_argument('name', metavar='NAME', nargs=1,
                         help='Target name')
    group = cparser.add_argument_group('Target definition')
    group.add_argument('-p', '--platform', metavar='PLATFORM',
                       help='Target platform to run obfuscated scripts')
    group.add_argument('-c', '--license', metavar='CODE',
                       help='License code for this target')
    cparser.add_argument('--remove', action='store_true',
                         help='Remove target from project')
    cparser.add_argument('-P', '--project', required=True, default='',
                         help='Project path or configure file')
    cparser.set_defaults(func=_target)

    #
    # Command: license
    #
    cparser = subparsers.add_parser(
        'license',
        help='Manage licenses for project'
    )
    cparser.add_argument('code', nargs='+', metavar='CODE',
                         help='Registration code for this license')

    group = cparser.add_argument_group('Bind license to hardware')
    group.add_argument('-d', '--bind-harddisk', metavar='SN',
                       help='Bind license to serial number of harddisk')
    group.add_argument('-4', '--bind-ipv4', metavar='a.b.c.d',
                       help='Bind license to ipv4 addr')
    group.add_argument('-6', '--bind-ipv6', metavar='a:b:c:d',
                       help='Bind license to ipv6 addr')
    group.add_argument('-m', '--bind-mac', metavar='x:x:x:x',
                       help='Bind license to mac addr')

    cparser.add_argument('--remove', action='store_true',
                                help='Remove license from project')
    cparser.add_argument('-P', '--project', required=True, default='',
                                help='Project path or configure file')

    cparser.set_defaults(func=_license)

    #
    # Command: hdinfo
    #
    cparser = subparsers.add_parser(
        'hdinfo',
        epilog=_hdinfo.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Show hardware information'
    )
    cparser.add_argument('-a', '--all', action='store_true',
                         help='Show all known hardware information')
    cparser.add_argument('-4', '--ipv4', action='store_true',
                         help='Show ipv4 address of this machine')
    cparser.add_argument('-6', '--ipv6', action='store_true',
                         help='Show ipv4 address of this machine')
    cparser.add_argument('-m', '--mac', action='store_true',
                         help='Show mac address of primary netcard')
    cparser.add_argument('-d', '--harddisk', action='store_true',
                         help='Show serial number of primary harddisk')
    cparser.set_defaults(func=_hdinfo)

    #
    # Command: benchmark
    #
    cparser = subparsers.add_parser(
        'benchmark',
        epilog=_benchmark.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Run benchmark test in current machine'
    )
    cparser.add_argument('--obf-module-mode',
                         choices=Project.OBF_MODULE_MODE, default='DES')
    cparser.add_argument('--obf-code-mode',
                         choices=Project.OBF_CODE_MODE, default='DES')
    cparser.set_defaults(func=_benchmark)

    #
    # Command: obfuscate
    #
    cparser = subparsers.add_parser('obfuscate', help='Obfuscate python scripts')
    cparser.set_defaults(func=_obfuscate)

    args = parser.parse_args(args)
    args.func(args)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main(sys.argv[1:])
