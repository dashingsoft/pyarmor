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
#      Version: 3.4.0 -                                     #
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

'''See "pyarmor.py <command> -h" for more information on a specific command.'''

import json
import logging
import os
import shutil
import subprocess
import sys
import time

try:
    import argparse
except ImportError:
    # argparse is new in version 2.7
    import polyfills.argparse as argparse

from config import version, plat_name, dll_ext, dll_name, \
                   default_obf_module_mode, default_obf_code_mode, \
                   config_filename, capsule_filename, license_filename

from project import Project
from utils import make_capsule, obfuscate_scripts, make_runtime, \
                  make_project_license, make_entry, show_hd_info, \
                  build_path, make_command, get_registration_code, \
                  check_capsule

import packer

DEFAULT_CAPSULE = os.path.expanduser(os.path.join('~', capsule_filename))

def armorcommand(func):
    return func
    # def wrap(*args, **kwargs):
    #     try:
    #         return func(*args, **kwargs)
    #     except Exception as e:
    #         logging.exception(e)
    # wrap.__doc__ = func.__doc__
    # return wrap

@armorcommand
def _init(args):
    '''Create an empty project or reinitialize an existing one

EXAMPLES

    pyarmor init --src=examples/simple --entry=queens.py project1
    '''
    if args.clone:
        logging.info('Warning: option --clone is deprecated, use --capsule instead ')
        _clone(args)
        return

    path = args.project
    logging.info('Create project in %s ...', path)

    if not os.path.exists(path):
        logging.info('Make project directory %s', path)
        os.makedirs(path)

    src = os.path.abspath(args.src)
    logging.info('Python scripts base path: %s', src)

    name = os.path.basename(os.path.abspath(path))
    if (args.type == 'pkg') or \
       (args.type == 'auto' and os.path.exists(os.path.join(src,
                                                            '__init__.py'))):
        logging.info('Project is configured as package')
        project = Project(name=name, title=name, src=src,
                          entry=args.entry if args.entry else '__init__.py',
                          is_package=1, obf_code_mode='wrap')
    else:
        logging.info('Project is configured as standalone application.')
        project = Project(name=name, title=name, src=src, entry=args.entry)

    if args.capsule:
        capsule = os.path.abspath(args.capsule)
        logging.info('Share capsule with %s', capsule)
        project._update(dict(capsule=capsule))
    else:
        logging.info('Create project capsule ...')
        filename = os.path.join(path, capsule_filename)
        make_capsule(filename)
        logging.info('Project capsule %s created', filename)

    logging.info('Create configure file ...')
    filename = os.path.join(path, config_filename)
    project.save(path)
    logging.info('Configure file %s created', filename)

    logging.info('Create pyarmor command ...')
    script = make_command(plat_name, sys.executable, sys.argv[0], path)
    logging.info('Pyarmor command %s created', script)

    logging.info('Project init successfully.')

def _clone(args):
    path = args.project
    logging.info('Create project in %s ...', path)

    if not os.path.exists(path):
        logging.info('Make project directory %s', path)
        os.makedirs(path)

    src = os.path.abspath(args.src)
    logging.info('Python scripts base path: %s', src)

    logging.info('Clone project from path: %s', args.clone)
    for s in (config_filename, capsule_filename):
        logging.info('\tCopy file "%s"', s)
        shutil.copy(os.path.join(args.clone, s), os.path.join(path, s))

    logging.info('Init project settings')
    project = Project()
    project.open(path)
    name = os.path.basename(os.path.abspath(path))
    project._update(dict(name=name, title=name, src=src, entry=args.entry))
    project.save(path)

    if args.type != 'auto':
        logging.info('Option --type is ignored when --clone is specified')

    logging.info('Create pyarmor command ...')
    script = make_command(plat_name, sys.executable, sys.argv[0], path)
    logging.info('Pyarmor command %s created', script)

    logging.info('Project init successfully.')

@armorcommand
def _update(args):
    '''Update project settings.

Option --manifest is comma-separated list of manifest template
command, same as MANIFEST.in of Python Distutils. The default value is
"global-include *.py"

Option --entry is comma-separated list of entry scripts, relative to
src path of project.

Examples,

    cd projects/project1
    ./pyarmor config --entry "main.py, another/main.py"
                     --manifest "global-include *.py, exclude test*.py"
                     --obf-module-mode des
                     --obf-code-mode des
                     --runtime-path "/opt/odoo/pyarmor"

    '''
    project = Project()
    project.open(args.project)
    logging.info('Update project %s ...', args.project)

    if args.src is not None:
        args.src = os.path.abspath(args.src)
        logging.info('Change src to absolute path: %s', args.src)
    if args.capsule is not None:
        args.capsule = os.path.abspath(args.capsule)
        logging.info('Change capsule to absolute path: %s', args.capsule)
    keys = project._update(dict(args._get_kwargs()))
    logging.info('Changed attributes: %s', keys)

    project.save(args.project)
    logging.info('Update project OK.')

@armorcommand
def _info(args):
    '''Show project information'''
    project = Project()
    project.open(args.project)
    logging.info('Project %s information\n%s', args.project, project.info())

@armorcommand
def _build(args):
    '''Build project, obfuscate all scripts in the project.'''
    project = Project()
    project.open(args.project)
    logging.info('Build project %s ...', args.project)

    capsule = build_path(project.capsule, args.project)
    logging.info('Use capsule: %s', capsule)

    output = build_path(project.output, args.project) \
             if args.output is None else args.output
    logging.info('Output path is: %s', output)

    if not args.only_runtime:
        mode = project.get_obfuscate_mode()
        files = project.get_build_files(args.force)
        src = project.src
        soutput = os.path.join(output, os.path.basename(src)) \
                  if project.get('is_package') else output
        filepairs = [(os.path.join(src, x), os.path.join(soutput, x))
                     for x in files]

        logging.info('%s increment build',
                     'Disable' if args.force else 'Enable')
        logging.info('Search scripts from %s', src)
        logging.info('Obfuscate %d scripts with mode %s', len(files), mode)
        for x in files:
            logging.info('\t%s', x)
        logging.info('Save obfuscated scripts to %s', soutput)

        obfuscate_scripts(filepairs, mode, capsule, soutput)

        # for x in targets:
        #     output = os.path.join(project.output, x)
        #     pairs = [(os.path.join(src, x), os.path.join(output, x))
        #              for x in files]
        #     for src, dst in pairs:
        #         try:
        #             shutil.copy2(src, dst)
        #         except Exception:
        #             os.makedirs(os.path.dirname(dst))
        #             shutil.copy2(src, dst)
        project['build_time'] = time.time()
        project.save(args.project)

        if project.entry:
            make_entry(project.entry, project.src, output,
                       rpath=project.runtime_path,
                       ispackage=project.get('is_package'))

    if not args.no_runtime:
        routput = os.path.join(output, os.path.basename(project.src)) \
            if project.get('is_package') else output
        if not os.path.exists(routput):
            logging.info('Make path: %s', routput)
            os.mkdir(routput)
        logging.info('Make runtime files to %s', routput)
        make_runtime(capsule, routput)
        if project.get('disable_restrict_mode'):
            licode = '*FLAGS:%c*CODE:Pyarmor-Project' % chr(1)
            licfile = os.path.join(routput, license_filename)
            logging.info('Generate no restrict mode license file: %s', licfile)
            make_project_license(capsule, licode, licfile)

    else:
        logging.info('\tIn order to import obfuscated scripts, insert ')
        logging.info('\t2 lines in entry script:')
        logging.info('\t\tfrom pytransfrom import pyarmor_runtime')
        logging.info('\t\tpyarmor_runtime()')

    logging.info('Build project OK.')

@armorcommand
def _licenses(args):
    '''Generate licenses for obfuscated scripts.

Examples,

* Expired license for global capsule

    pyarmor licenses --expired=2018-05-12 Customer-Jordan

* Bind license to fixed harddisk and expired someday for project

    cd projects/myproject
    ./pyarmor licenses -e 2018-05-12 \\
              --bind-disk '100304PBN2081SF3NJ5T' Customer-Tom
    '''
    if os.path.exists(os.path.join(args.project, config_filename)):
        logging.info('Generate licenses for project %s ...', args.project)
        project = Project()
        project.open(args.project)
        capsule = build_path(project.capsule, args.project) \
            if args.capsule is None else args.capsule
    else:
        if args.project != '':
            logging.warning('Ignore option --project, no project in %s',
                            args.project)
        capsule = DEFAULT_CAPSULE if args.capsule is None else args.capsule
        if not (os.path.exists(capsule) and check_capsule(capsule)):
            logging.info('Generate capsule %s', capsule)
            make_capsule(capsule)
        logging.info('Generate licenses with capsule %s ...', capsule)
        project = {
            'disable_restrict_mode': 0 if args.restrict else 1,
        }

    licpath = os.path.join(
        args.project if args.output is None else args.output,
        'licenses')
    if os.path.exists(licpath):
        logging.info('Output path of licenses: %s', licpath)
    else:
        logging.info('Make output path of licenses: %s', licpath)
        os.mkdir(licpath)

    if args.expired is None:
        fmt = ''
    else:
        fmt = '*TIME:%.0f\n' % \
              time.mktime(time.strptime(args.expired, '%Y-%m-%d'))

    if project.get('disable_restrict_mode'):
        logging.info('The license files generated is in disable restrict mode')
        fmt = '%s*FLAGS:%c' % (fmt, 1)
    else:
        logging.info('The license files generated is in restrict mode')

    if args.bind_disk:
        fmt = '%s*HARDDISK:%s' % (fmt, args.bind_disk)

    if args.bind_mac:
        fmt = '%s*IFMAC:%s' % (fmt, args.bind_mac)

    if args.bind_ipv4:
        fmt = '%s*IFIPV4:%s' % (fmt, args.bind_ipv4)

    # if args.bind_ipv6:
    #     fmt = '%s*IFIPV6:%s' % (fmt, args.bind_ipv6)

    if args.bind_domain:
        fmt = '%s*DOMAIN:%s' % (fmt, args.bind_domain)

    if args.bind_file:
        bind_file, bind_key = args.bind_file.split(';', 2)
        if os.path.exists(bind_file):
            f = open(bind_file, 'rb')
            s = f.read()
            f.close()
            if sys.version_info[0] == 3:
                fmt = '%s*FIXKEY:%s;%s' % (fmt, bind_key, s.decode())
            else:
                fmt = '%s*FIXKEY:%s;%s' % (fmt, bind_key, s)
        else:
            raise RuntimeError('Bind file %s not found' % bindfile)

    # Prefix of registration code
    fmt = fmt + '*CODE:'

    for rcode in args.codes:
        output = os.path.join(licpath, rcode)
        if not os.path.exists(output):
            logging.info('Make path: %s', output)
            os.mkdir(output)

        licfile = os.path.join(output, license_filename)
        licode = fmt + rcode
        txtinfo = licode.replace('\n', r'\n')
        if args.expired:
            txtinfo = '"Expired:%s%s"' % (args.expired,
                                          txtinfo[txtinfo.find(r'\n')+2:])
        logging.info('Generate license: %s', txtinfo)
        make_project_license(capsule, licode, licfile)
        logging.info('Write license file: %s', licfile)

        logging.info('Write information to %s.txt', licfile)
        with open(os.path.join(licfile + '.txt'), 'w') as f:
            f.write(txtinfo)

    logging.info('Generate %d licenses OK.', len(args.codes))

@armorcommand
def _target(args):
    project = Project()
    project.open(args.project)

    name = args.name[0]
    if args.remove:
        logging.info('Remove target from project %s ...', args.project)
        project.remove_target(name)
    else:
        logging.info('Add target to project %s ...', args.project)
        project.add_target(name, args.platform, args.license)
    project.save(args.project)

@armorcommand
def _capsule(args):
    '''Make capsule separately'''
    capsule = os.path.join(args.path, capsule_filename)
    logging.info('Generating capsule %s ...', capsule)
    if os.path.exists(capsule):
        logging.info('Do nothing, capsule %s has been exists', capsule)
    else:
        make_capsule(capsule)

@armorcommand
def _obfuscate(args):
    '''Obfuscate scripts without project'''
    if args.src is None and args.entry is None and not args.scripts:
        raise RuntimeError('No entry script')

    entry = args.entry or args.scripts[0]
    path = os.path.abspath(os.path.dirname(entry) if args.src is None
                           else args.src)
    logging.info('Obfuscate scripts in path "%s" ...', path)

    capsule = args.capsule if args.capsule else DEFAULT_CAPSULE
    if os.path.exists(capsule) and check_capsule(capsule):
        logging.info('Use cached capsule %s', capsule)
    else:
        logging.info('Generate capsule %s', capsule)
        make_capsule(capsule)

    output = args.output
    if args.recursive:
        pats = ['global-include *.py', 'prune build', 'prune dist']
        if hasattr('', 'decode'):
            pats = [p.decode()  for p in pats]
        files = Project.build_manifest(pats, path)
    else:
        files = Project.build_globfiles(['*.py'], path)
    filepairs = [(os.path.join(path, x), os.path.join(output, x))
                 for x in files]

    if args.restrict:
        logging.info('Restrict mode is eanbled')
        mode = Project.map_obfuscate_mode(
            default_obf_module_mode, default_obf_code_mode)
    else:
        logging.info('Restrict mode is disabled')
        mode = Project.map_obfuscate_mode(
            default_obf_module_mode, 'wrap')

    logging.info('Obfuscate scripts with mode %s', mode)
    logging.info('Save obfuscated scripts to "%s"', output)
    for a, b in filepairs:
        logging.info('\t%s -> %s', a, b)
    obfuscate_scripts(filepairs, mode, capsule, output)

    logging.info('Make runtime files')
    make_runtime(capsule, output)
    if not args.restrict:
        licode = '*FLAGS:%c*CODE:Pyarmor-Project' % chr(1)
        licfile = os.path.join(output, license_filename)
        logging.info('Generate no restrict mode license file: %s', licfile)
        make_project_license(capsule, licode, licfile)

    make_entry(os.path.basename(entry), path, output)
    for script in args.scripts[1:]:
        make_entry(os.path.basename(script), path, output)

    logging.info('Obfuscate %d scripts OK.', len(files))

@armorcommand
def _check(args):
    '''Check consistency of project'''
    project = Project()
    project.open(args.project)
    logging.info('Check project %s ...', args.project)
    project._check(args.project)
    logging.info('Check project OK.')

@armorcommand
def _benchmark(args):
    '''Run benchmark test in current machine'''
    logging.info('Start benchmark test ...')
    logging.info('Obfuscate module mode: %s', args.obf_module_mode)
    logging.info('Obfuscate bytecode mode: %s', args.obf_code_mode)

    logging.info('Benchmark bootstrap ...')
    mode = Project.map_obfuscate_mode(args.obf_module_mode,
                                      args.obf_code_mode)
    p = subprocess.Popen(
        [sys.executable, 'benchmark.py', 'bootstrap', str(mode)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    logging.info('Benchmark bootstrap OK.')

    logging.info('Run benchmark test ...')
    p = subprocess.Popen([sys.executable, 'benchmark.py'], cwd='.benchtest')
    p.wait()

    logging.info('Finish benchmark test.')

@armorcommand
def _hdinfo(args):
    show_hd_info()

def _version_info():
    rcode = get_registration_code()
    if rcode == '':
        return 'Pyarmor Trial Version %s\n' % version
    else:
        return 'Pyarmor Version %s\n\nRegistration code: %s' % (version, rcode)

def main(args):
    parser = argparse.ArgumentParser(
        prog='pyarmor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Pyarmor is a command line tool used to obfuscate ' \
                    'python scripts, bind obfuscated scripts to fixed ' \
                    'machine or expire obfuscated scripts.',
        epilog=__doc__,
    )
    parser.add_argument('-v', '--version', action='version',
                        version=_version_info())

    subparsers = parser.add_subparsers(
        title='The most commonly used pyarmor commands are',
        metavar='<command>'
    )

    #
    # Command: capsule
    #
    cparser = subparsers.add_parser(
        'capsule',
        epilog=_capsule.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Make capsule separately')
    cparser.add_argument('path', nargs='?', default='',
                         help='Path to save capsule, default is current path')
    cparser.set_defaults(func=_capsule)

    #
    # Command: obfuscate
    #
    cparser = subparsers.add_parser(
        'obfuscate',
        epilog=_obfuscate.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Obfuscate python scripts')
    cparser.add_argument('-O', '--output', default='dist', metavar='PATH')
    cparser.add_argument('-e', '--entry', metavar='SCRIPT',
                         help='Entry script [DEPRECATED]')
    cparser.add_argument('-r', '--recursive', action='store_true',
                         help='Match files recursively')
    cparser.add_argument('-s', '--src', metavar='PATH',
                         help='Base path for search python scripts')
    cparser.add_argument('-d', '--no-restrict', action='store_true',
                         help='Disable restrict mode [DEPRECATED]');
    cparser.add_argument('--restrict', action='store_true',
                         help='Enable restrict mode');
    cparser.add_argument('--capsule', help='Use this capsule to obfuscate code')
    cparser.add_argument('scripts', metavar='SCRIPT', nargs='*',
                         help='Scripts to obfuscted')
    cparser.set_defaults(func=_obfuscate)

    #
    # Command: init
    #
    cparser = subparsers.add_parser(
        'init',
        epilog=_init.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Create a project to manage obfuscated scripts'
    )
    cparser.add_argument('-t', '--type', default='auto',
                         choices=('auto', 'app', 'pkg'))
    cparser.add_argument('-e', '--entry',
                         help='Entry script of this project')
    cparser.add_argument('-s', '--src', required=True,
                         help='Base path of python scripts')
    cparser.add_argument('-C', '--clone', metavar='PATH',
                         help='[Deprecated] Clone project')
    cparser.add_argument('--capsule',
                         help='Use this capsule other than creating new one')
    cparser.add_argument('project', nargs='?', help='Project path')
    cparser.set_defaults(func=_init)


    #
    # Command: config
    #
    cparser = subparsers.add_parser(
        'config',
        epilog=_update.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Update project information')
    cparser.add_argument('project', nargs='?', metavar='PATH',
                         default='', help='Project path')
    cparser.add_argument('--name')
    cparser.add_argument('--title')
    cparser.add_argument('--src')
    cparser.add_argument('--output')
    cparser.add_argument('--capsule', help='Project capsule')
    cparser.add_argument('--manifest', metavar='TEMPLATE',
                         help='Manifest template string')
    cparser.add_argument('--entry', metavar='SCRIPT',
                         help='Entry script of this project')
    cparser.add_argument('--is-package', type=int, choices=(0, 1))
    cparser.add_argument('--disable-restrict-mode', type=int, choices=(0, 1))
    cparser.add_argument('--obf-module-mode', choices=Project.OBF_MODULE_MODE)
    cparser.add_argument('--obf-code-mode', choices=Project.OBF_CODE_MODE)
    cparser.add_argument('--runtime-path', metavar="RPATH")
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
    cparser.add_argument('project', nargs='?', metavar='PATH',
                         default='', help='Project path')
    cparser.set_defaults(func=_info)

    #
    # Command: check
    #
    cparser = subparsers.add_parser(
        'check',
        epilog=_check.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Check consistency of project')
    cparser.add_argument('project', nargs='?', metavar='PATH',
                         default='', help='Project path')
    cparser.set_defaults(func=_check)

    #
    # Command: build
    #
    cparser = subparsers.add_parser(
        'build',
        epilog=_build.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Obfuscate all the scripts in the project')
    cparser.add_argument('project', nargs='?', metavar='PATH', default='',
                         help='Project path')
    cparser.add_argument('-B', '--force', action='store_true',
                         help='Obfuscate all scripts even if it\'s not updated')
    cparser.add_argument('-r', '--only-runtime', action='store_true',
                         help='Generate extra runtime files only')
    cparser.add_argument('-n', '--no-runtime', action='store_true',
                         help='DO NOT generate extra runtime files')
    cparser.add_argument('-O', '--output',
                         help='Output path, override project configuration')
    cparser.set_defaults(func=_build)

    #
    # Command: target
    #
    # cparser = subparsers.add_parser('target', help='Manage target for project')
    # cparser.add_argument('name', metavar='NAME', nargs=1,
    #                      help='Target name')
    # group = cparser.add_argument_group('Target definition')
    # group.add_argument('-p', '--platform', metavar='PLATFORM',
    #                    help='Target platform to run obfuscated scripts')
    # group.add_argument('-c', '--license', metavar='CODE',
    #                    help='License code for this target')
    # cparser.add_argument('--remove', action='store_true',
    #                      help='Remove target from project')
    # cparser.add_argument('-P', '--project', required=True, default='',
    #                      help='Project path or configure file')
    # cparser.set_defaults(func=_target)

    #
    # Command: license
    #
    cparser = subparsers.add_parser(
        'licenses',
        epilog=_licenses.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Generate new licenses for obfuscated scripts'
    )
    cparser.add_argument('codes', nargs='+', metavar='CODE',
                         help='Registration code for this license')
    group = cparser.add_argument_group('Bind license to hardware')
    group.add_argument('-e', '--expired', metavar='YYYY-MM-DD',
                       help='Expired date for this license')
    group.add_argument('-d', '--bind-disk', metavar='SN',
                       help='Bind license to serial number of harddisk')
    group.add_argument('-4', '--bind-ipv4', metavar='a.b.c.d',
                       help='Bind license to ipv4 addr')
    # group.add_argument('-6', '--bind-ipv6', metavar='a:b:c:d',
    #                    help='Bind license to ipv6 addr')
    group.add_argument('-m', '--bind-mac', metavar='x:x:x:x',
                       help='Bind license to mac addr')
    group.add_argument('--bind-domain', metavar='DOMAIN',
                       help='Bind license to domain name')
    group.add_argument('--bind-file', metavar='filename;target_filename',
                       help='Bind license to fixed file')
    cparser.add_argument('-P', '--project', default='', help='Project path')
    cparser.add_argument('-C', '--capsule', help='Project capsule')
    cparser.add_argument('-O', '--output', help='Output path')
    cparser.add_argument('--restrict', action='store_const',
                         const=1, help='Generate a license for restrict mode')
    cparser.set_defaults(func=_licenses)

    #
    # Command: hdinfo
    #
    cparser = subparsers.add_parser(
        'hdinfo',
        epilog=_hdinfo.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Show hardware information'
    )
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
    cparser.add_argument('-m', '--obf-module-mode',
                         choices=Project.OBF_MODULE_MODE,
                         default=default_obf_module_mode)
    cparser.add_argument('-c', '--obf-code-mode',
                         choices=Project.OBF_CODE_MODE,
                         default=default_obf_code_mode)
    cparser.set_defaults(func=_benchmark)


    #
    # Command: pack
    #
    cparser = subparsers.add_parser(
        'pack',
        epilog=packer.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Pack obfuscated scripts to one bundle'
    )
    packer.add_arguments(cparser)
    cparser.set_defaults(func=packer.packer)

    args = parser.parse_args(args)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

def main_entry():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main(sys.argv[1:])

if __name__ == '__main__':
    main_entry()
