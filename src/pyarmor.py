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

'''PyArmor is a command line tool used to obfuscate python scripts,
bind obfuscated scripts to fixed machine or expire obfuscated scripts.

'''

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

from config import version, version_info, purchase_info, \
                   config_filename, capsule_filename, license_filename

from project import Project
from utils import PYARMOR_PATH, make_capsule, make_runtime, \
                  make_project_license, make_entry, show_hd_info, \
                  build_path, make_project_command, get_registration_code, \
                  check_capsule, pytransform_bootstrap, encrypt_script, \
                  get_product_key, upgrade_capsule, save_config, load_config, \
                  get_platform_list, download_pytransform

import packer

DEFAULT_CAPSULE = os.path.expanduser(os.path.join('~', capsule_filename))
DEFAULT_CONFIG = os.path.expanduser(os.path.join('~', config_filename))


def arcommand(func):
    return func


@arcommand
def _init(args):
    '''Create an empty project or reinitialize an existing one.'''
    path = os.path.normpath(args.project)

    if args.child is not None:
        n = args.child
        logging.info('Create child project %d in %s ...', n, path)
        parent = os.path.join(path, config_filename)
        if not os.path.exists(parent):
            raise RuntimeError('No parent project exists in "%s"' % path)
        filename = os.path.join(path, '%s.%d' % (config_filename, n))
        if os.path.exists(filename):
            raise RuntimeError('Child project %d already exists' % n)
        logging.info('Copy %s to %s', parent, filename)
        shutil.copyfile(parent, filename)
        logging.info('Child project %d init successfully.', n)
        return

    logging.info('Create project in %s ...', path)
    if os.path.exists(os.path.join(path, config_filename)):
        raise RuntimeError('A project already exists in "%s"' % path)
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
        project = Project(name=name, title=name, src=src, is_package=1,
                          entry=args.entry if args.entry else '__init__.py')
    else:
        logging.info('Project is configured as standalone application.')
        project = Project(name=name, title=name, src=src, entry=args.entry)

    if args.capsule:
        capsule = os.path.abspath(args.capsule)
        logging.info('Set project capsule to %s', capsule)
    else:
        capsule = os.path.abspath(DEFAULT_CAPSULE)
        logging.info('Use global capsule as project capsule: %s', capsule)
    project._update(dict(capsule=capsule))

    logging.info('Create configure file ...')
    filename = os.path.join(path, config_filename)
    project.save(path)
    logging.info('Configure file %s created', filename)

    if sys.argv[0] == 'pyarmor.py':
        logging.info('Create pyarmor command ...')
        platname = sys.platform
        s = make_project_command(platname, sys.executable, sys.argv[0], path)
        logging.info('PyArmor command %s created', s)

    logging.info('Project init successfully.')


@arcommand
def _config(args):
    '''Update project settings.'''
    for x in ('obf-module-mode', 'obf-code-mode'):
        if getattr(args, x.replace('-', '_')) is not None:
            logging.warning('Option --%s has been deprecated', x)

    project = Project()
    project.open(args.project)
    logging.info('Update project %s ...', args.project)

    if args.src is not None:
        args.src = os.path.abspath(args.src)
        logging.info('Change src to absolute path: %s', args.src)
    if args.capsule is not None:
        args.capsule = os.path.abspath(args.capsule)
        logging.info('Change capsule to absolute path: %s', args.capsule)
    if args.plugins is not None:
        # plugins = project.get('plugins', [])
        if 'clear' in args.plugins:
            logging.info('Clear all plugins')
            args.plugins = []
    keys = project._update(dict(args._get_kwargs()))
    for k in keys:
        logging.info('Change project %s to "%s"', k, getattr(project, k))

    if keys:
        project.save(args.project)
        logging.info('Update project OK.')
    else:
        logging.info('Nothing changed.')


@arcommand
def _info(args):
    '''Show project information.'''
    project = Project()
    project.open(args.project)
    logging.info('Project %s information\n%s', args.project, project.info())


@arcommand
def _build(args):
    '''Build project, obfuscate all scripts in the project.'''
    project = Project()
    project.open(args.project)
    logging.info('Build project %s ...', args.project)

    logging.info('Check project')
    project._check(args.project)

    pro_path = args.project \
        if args.project == '' or os.path.exists(args.project) \
        else os.path.dirname(args.project)

    capsule = build_path(project.capsule, pro_path)
    logging.info('Use capsule: %s', capsule)

    output = build_path(project.output, pro_path) \
        if args.output is None else os.path.normpath(args.output)
    logging.info('Output path is: %s', output)

    platform = args.platform if args.platform else project.get('platform')
    if platform:
        logging.info('Taget platform is: %s', platform)

    if not args.only_runtime:
        src = project.src
        if os.path.abspath(output).startswith(src):
            excludes = ['prune %s' % os.path.abspath(output)[len(src)+1:]]
        else:
            excludes = []

        files = project.get_build_files(args.force, excludes=excludes)
        soutput = os.path.join(output, os.path.basename(src)) \
            if project.get('is_package') else output

        logging.info('Save obfuscated scripts to "%s"', soutput)
        if not os.path.exists(soutput):
            os.makedirs(soutput)

        logging.info('Read public key from capsule')
        prokey = get_product_key(capsule)

        logging.info('%s increment build',
                     'Disable' if args.force else 'Enable')
        logging.info('Search scripts from %s', src)

        logging.info('Obfuscate scripts with mode:')
        if hasattr(project, 'obf_mod'):
            obf_mod = project.obf_mod
        else:
            obf_mod = project.obf_module_mode == 'des'
        if hasattr(project, 'wrap_mode'):
            wrap_mode = project.wrap_mode
            obf_code = project.obf_code
        elif project.obf_code_mode == 'wrap':
            wrap_mode = 1
            obf_code = 1
        else:
            wrap_mode = 0
            obf_code = 0 if project.obf_code_mode == 'none' else 1

        def v(t):
            return 'on' if t else 'off'
        logging.info('Obfuscating the whole module is %s', v(obf_mod))
        logging.info('Obfuscating each function is %s', v(obf_code))
        logging.info('Autowrap each code object mode is %s', v(wrap_mode))

        entries = [build_path(s.strip(), project.src)
                   for s in project.entry.split(',')] if project.entry else []
        protection = project.cross_protection \
            if hasattr(project, 'cross_protection') else 1
        if platform:
            if protection == 1:
                protection = platform
            elif not isinstance(protection, int):
                protection = ','.join([protection, platform])

        for x in files:
            a, b = os.path.join(src, x), os.path.join(soutput, x)
            logging.info('\t%s -> %s', x, b)

            d = os.path.dirname(b)
            if not os.path.exists(d):
                os.makedirs(d)

            if entries and (os.path.abspath(a) in entries):
                pcode = protection
                if hasattr(project, 'plugins'):
                    plugins = project.plugins
            else:
                pcode = 0
                plugins = None

            encrypt_script(prokey, a, b, obf_code=obf_code, obf_mod=obf_mod,
                           wrap_mode=wrap_mode, protection=pcode,
                           plugins=plugins, rpath=project.runtime_path)

        logging.info('%d scripts has been obfuscated', len(files))
        project['build_time'] = time.time()
        project.save(args.project)

        if project.entry:
            make_entry(project.entry, project.src, output,
                       rpath=project.runtime_path,
                       runtime=not args.no_runtime,
                       ispackage=project.get('is_package'))

    if not args.no_runtime:
        routput = output if args.output is not None and args.only_runtime \
            else os.path.join(output, os.path.basename(project.src)) \
            if project.get('is_package') else output
        if not os.path.exists(routput):
            logging.info('Make path: %s', routput)
            os.mkdir(routput)
        logging.info('Make runtime files to %s', routput)
        make_runtime(capsule, routput, platform=platform)
        if project.get('disable_restrict_mode'):
            licode = '*FLAGS:%c*CODE:PyArmor-Project' % chr(1)
            licfile = os.path.join(routput, license_filename)
            logging.info('Generate no restrict mode license file: %s', licfile)
            make_project_license(capsule, licode, licfile)

    else:
        logging.info('\tIn order to import obfuscated scripts, insert ')
        logging.info('\t2 lines in entry script:')
        logging.info('\t\tfrom pytransform import pyarmor_runtime')
        logging.info('\t\tpyarmor_runtime()')

    logging.info('Build project OK.')


@arcommand
def _licenses(args):
    '''Generate licenses for obfuscated scripts.'''
    for x in ('bind-file',):
        if getattr(args, x.replace('-', '_')) is not None:
            logging.warning('Option --%s has been deprecated', x)

    if os.path.exists(os.path.join(args.project, config_filename)):
        logging.info('Generate licenses for project %s ...', args.project)
        project = Project()
        project.open(args.project)
        capsule = build_path(project.capsule, args.project) \
            if args.capsule is None else args.capsule
    else:
        if args.project != '':
            logging.warning('Ignore option --project, there is no project')
        capsule = DEFAULT_CAPSULE if args.capsule is None else args.capsule
        if not (os.path.exists(capsule) and check_capsule(capsule)):
            logging.info('Generate capsule %s', capsule)
            make_capsule(capsule)
        logging.info('Generate licenses with capsule %s ...', capsule)
        project = dict(disable_restrict_mode=0 if args.restrict else 1)

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
        logging.info('The license file generated is in disable restrict mode')
        fmt = '%s*FLAGS:%c' % (fmt, 1)
    else:
        logging.info('The license file generated is in restrict mode')

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
            raise RuntimeError('Bind file %s not found' % bind_file)

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


@arcommand
def _capsule(args):
    '''Generate the capsule explicitly.'''
    capsule = os.path.join(args.path, capsule_filename)
    if args.upgrade:
        logging.info('Preparing to upgrade the capsule %s ...', capsule)
        upgrade_capsule(capsule)
        return

    if os.path.exists(capsule):
        logging.info('Do nothing, capsule %s has been exists', capsule)
    else:
        logging.info('Generating capsule %s ...', capsule)
        make_capsule(capsule)


@arcommand
def _obfuscate(args):
    '''Obfuscate scripts without project.'''
    for x in ('src', 'entry', 'cross-protection'):
        if getattr(args, x.replace('-', '_')) is not None:
            logging.warning('Option --%s has been deprecated', x)

    if args.src is None and not args.scripts:
        raise RuntimeError('No scripts specified')

    path = os.path.abspath(os.path.dirname(args.scripts[0])
                           if args.src is None else args.src)
    logging.info('Source path is "%s"', path)

    entry = args.entry or (args.scripts and args.scripts[0])
    logging.info('Entry script is %s', entry)

    capsule = args.capsule if args.capsule else DEFAULT_CAPSULE
    if os.path.exists(capsule) and check_capsule(capsule):
        logging.info('Use cached capsule %s', capsule)
    else:
        logging.info('Generate capsule %s', capsule)
        make_capsule(capsule)

    output = args.output
    if os.path.abspath(output) == path:
        raise RuntimeError('Output path can not be same as src')

    if args.recursive:
        logging.info('Recursive mode is on')
        pats = ['global-include *.py']

        if args.exclude:
            for x in args.exclude.split(','):
                logging.info('Exclude path "%s"', x)
                pats.append('prune %s' % x)

        if os.path.abspath(output).startswith(path):
            x = os.path.abspath(output)[len(path):].strip('/\\')
            pats.append('prune %s' % x)
            logging.info('Auto exclude output path "%s"', x)

        if hasattr('', 'decode'):
            pats = [p.decode() for p in pats]

        files = Project.build_manifest(pats, path)

    elif args.exact:
        logging.info('Exact mode is on')
        files = [os.path.abspath(x) for x in args.scripts]

    else:
        logging.info('Normal mode is on')
        files = Project.build_globfiles(['*.py'], path)

    logging.info('Save obfuscated scripts to "%s"', output)
    if not os.path.exists(output):
        os.makedirs(output)

    logging.info('Read public key from capsule')
    prokey = get_product_key(capsule)

    logging.info('Obfuscate scripts with default mode')
    cross_protection = 0 if args.no_cross_protection else \
        1 if args.cross_protection is None else args.cross_protection
    if args.platform:
        logging.info('Target platform is %s', args.platform)
        if cross_protection == 1:
            cross_protection = args.platform
        elif isinstance(cross_protection, str):
            cross_protection = ','.join([cross_protection, args.platform])

    for x in files:
        if os.path.isabs(x):
            a, b = x, os.path.join(output, os.path.basename(x))
        else:
            a, b = os.path.join(path, x), os.path.join(output, x)
        logging.info('\t%s -> %s', x, b)
        protection = entry and (os.path.abspath(a) == os.path.abspath(entry)) \
            and cross_protection
        plugins = protection and args.plugins

        d = os.path.dirname(b)
        if not os.path.exists(d):
            os.makedirs(d)

        encrypt_script(prokey, a, b, protection=protection, plugins=plugins)
    logging.info('%d scripts have been obfuscated', len(files))

    make_runtime(capsule, output, platform=args.platform)

    logging.info('Obfuscate scripts with restrict mode %s',
                 'on' if args.restrict else 'off')
    if not args.restrict:
        licode = '*FLAGS:%c*CODE:PyArmor-Project' % chr(1)
        licfile = os.path.join(output, license_filename)
        logging.info('Generate no restrict mode license file: %s', licfile)
        make_project_license(capsule, licode, licfile)

    if (not args.no_bootstrap) and entry and os.path.exists(entry):
        entryname = entry if args.src else os.path.basename(entry)
        if os.path.exists(os.path.join(output, entryname)):
            make_entry(entryname, path, output)
        else:
            logging.info('Use outer entry script "%s"', entry)
            make_entry(entry, path, output)

    logging.info('Obfuscate %d scripts OK.', len(files))


@arcommand
def _check(args):
    '''Check consistency of project.'''
    project = Project()
    project.open(args.project)
    logging.info('Check project %s ...', args.project)
    project._check(args.project)
    logging.info('Check project OK.')


@arcommand
def _benchmark(args):
    '''Run benchmark test in current machine.'''
    logging.info('Start benchmark test ...')
    logging.info('Obfuscate module mode: %s', args.obf_mod)
    logging.info('Obfuscate code mode: %s', args.obf_code)
    logging.info('Obfuscate wrap mode: %s', args.wrap_mode)

    logging.info('Benchmark bootstrap ...')
    path = os.path.normpath(os.path.dirname(__file__))
    p = subprocess.Popen(
        [sys.executable, 'benchmark.py', 'bootstrap',
         str(args.obf_mod), str(args.obf_code), str(args.wrap_mode)],
        cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    logging.info('Benchmark bootstrap OK.')

    logging.info('Run benchmark test ...')
    benchtest = os.path.join(path, '.benchtest')
    p = subprocess.Popen([sys.executable, 'benchmark.py'], cwd=benchtest)
    p.wait()

    if args.debug:
        logging.info('Test scripts are saved in the path: %s', benchtest)
    else:
        logging.info('Remove test path: %s', benchtest)
        shutil.rmtree(benchtest)

    logging.info('Finish benchmark test.')


@arcommand
def _hdinfo(args):
    show_hd_info()


@arcommand
def _register(args):
    '''Make registration code work.'''
    key = 'purchased_code'
    licfile = os.path.join(PYARMOR_PATH, license_filename)

    logging.info('The license file is %s', licfile)
    logging.info('Read pyarmor config from %s', DEFAULT_CONFIG)
    cfg = load_config(DEFAULT_CONFIG)

    if args.backup:
        logging.info('Read code from license file')
        with open(licfile, 'r') as f:
            rcode = f.read().strip()
        logging.info('Got code:\n%s', rcode)

        rlist = cfg.get(key)
        if rlist is None:
            cfg[key] = [rcode]
        elif rcode not in rlist:
            rlist.append(rcode)

        logging.info('Save code to config file')
        save_config(cfg, DEFAULT_CONFIG)

        logging.info('Backup code successfully.')
        return

    def make_pyarmor_license(rcode):
        logging.info('Generating license from:\n%s', rcode)
        with open(licfile, 'w') as f:
            f.write(rcode)
        logging.info('Write code to license file OK')

    if args.restore is not None:
        logging.info('Restore license from index %d', args.restore)
        rcode = cfg.get(key, [])[args.restore]
        make_pyarmor_license(rcode)

    elif args.rcode is not None:
        make_pyarmor_license(args.rcode)

    logging.info('The new code has been taken effect, '
                 'check it by "pyarmor -v".')
    logging.info('If something is wrong with new license, '
                 'please restore trial license by this way:\n'
                 '\tcp %s %s', licfile[:-4] + '.tri', licfile)


@arcommand
def _download(args):
    '''List and download platform-dependent dynamic libraries.'''
    if args.platid:
        logging.info('Download dynamic library for %s', args.platid)
        download_pytransform(args.platid, args.output)

    else:
        lines = []
        plist = get_platform_list()
        pat = None if args.pattern is None else args.pattern.lower()
        for p in plist:
            if pat and pat not in p['platname'] \
               and pat not in ' '.join(p['machines']) \
               and pat not in ' '.join(p['features']).lower():
                continue
            lines.append('')
            lines.append('%16s: %s' % ('id', p['path']))
            lines.append('%16s: %s' % ('platname', p['platname']))
            lines.append('%16s: %s' % ('machines', ', '.join(p['machines'])))
            lines.append('%16s: %s' % ('features', ', '.join(p['features'])))
            lines.append('%16s: %s' % ('remark', p['remark']))
        logging.info('All the available libraries:\n%s', '\n'.join(lines))


def _version_info(short=False):
    rcode = get_registration_code()
    if rcode:
        rcode = rcode.replace('-sn-1.txt', '')
        ver = 'PyArmor Version %s (%s)' % (version, rcode)
    else:
        ver = 'PyArmor Trial Version %s' % version
    return '\n'.join([ver, '' if short else version_info])


def main(args):
    parser = argparse.ArgumentParser(
        prog='pyarmor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog='See "pyarmor <command> -h" for more information '
               'on a specific command.\n\nMore usage refer to '
               'https://pyarmor.readthedocs.io'
    )
    parser.add_argument('-v', '--version', action='version',
                        version=_version_info())
    parser.add_argument('-q', '--silent', action='store_true',
                        help='Suppress all normal output')

    subparsers = parser.add_subparsers(
        title='The most commonly used pyarmor commands are',
        metavar=''
    )

    #
    # Command: obfuscate
    #
    cparser = subparsers.add_parser(
        'obfuscate',
        epilog=_obfuscate.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Obfuscate python scripts')
    cparser.add_argument('-O', '--output', default='dist', metavar='PATH')
    cparser.add_argument('-r', '--recursive', action='store_true',
                         help='Search scripts in recursive mode')
    cparser.add_argument('--exclude',
                         help='Exclude the path in recursive mode. '
                         'Multiple paths are allowed, separated by ","')
    cparser.add_argument('--exact', action='store_true',
                         help='Only obfusate list scripts')
    cparser.add_argument('--no-bootstrap', action='store_true',
                         help='Do not insert bootstrap code to entry script')
    cparser.add_argument('--no-cross-protection', action='store_true',
                         help='Disable restrict mode')
    cparser.add_argument('scripts', metavar='SCRIPT', nargs='*',
                         help='List scripts to obfuscted')
    cparser.add_argument('-s', '--src', metavar='PATH',
                         help='[DEPRECATED]Base path for searching scripts')
    cparser.add_argument('-e', '--entry', metavar='SCRIPT',
                         help='[DEPRECATED]Specify entry script')
    cparser.add_argument('--cross-protection', choices=(0, 1),
                         help='[DEPRECATED]')
    cparser.add_argument('--plugin', dest='plugins', action='append',
                         help='Insert extra code to entry script')
    cparser.add_argument('--restrict', type=int, choices=(0, 1),
                         default=1, help=argparse.SUPPRESS)
    cparser.add_argument('--capsule', help=argparse.SUPPRESS)
    cparser.add_argument('--platform', help='Distribute obfuscated scripts '
                         'to other platform')
    cparser.set_defaults(func=_obfuscate)

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
                       help=argparse.SUPPRESS)
    cparser.add_argument('-P', '--project', default='', help=argparse.SUPPRESS)
    cparser.add_argument('-C', '--capsule', help=argparse.SUPPRESS)
    cparser.add_argument('-O', '--output', help='Output path')
    cparser.add_argument('--restrict', type=int, choices=(0, 1),
                         default=1, help=argparse.SUPPRESS)

    cparser.set_defaults(func=_licenses)

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
    cparser.add_argument('-s', '--src', default='',
                         help='Base path of python scripts')
    cparser.add_argument('--capsule', help=argparse.SUPPRESS)
    cparser.add_argument('--child', type=int, help=argparse.SUPPRESS)
    cparser.add_argument('project', nargs='?', default='', help='Project path')
    cparser.set_defaults(func=_init)

    #
    # Command: config
    #
    cparser = subparsers.add_parser(
        'config',
        epilog=_config.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Update project settings')
    cparser.add_argument('project', nargs='?', metavar='PATH',
                         default='', help='Project path')
    cparser.add_argument('--name')
    cparser.add_argument('--title')
    cparser.add_argument('--src')
    cparser.add_argument('--output')
    cparser.add_argument('--capsule', help=argparse.SUPPRESS)
    cparser.add_argument('--platform', help=argparse.SUPPRESS)
    cparser.add_argument('--manifest', metavar='TEMPLATE',
                         help='Manifest template string')
    cparser.add_argument('--entry', metavar='SCRIPT',
                         help='Entry script of this project')
    cparser.add_argument('--is-package', type=int, choices=(0, 1))
    cparser.add_argument('--disable-restrict-mode', type=int, choices=(0, 1))
    cparser.add_argument('--obf-module-mode', choices=Project.OBF_MODULE_MODE,
                         help='[DEPRECATED] Use --obf-mod instead')
    cparser.add_argument('--obf-code-mode', choices=Project.OBF_CODE_MODE,
                         help='[DEPRECATED] Use --obf-code and --wrap-mode'
                              ' instead')
    cparser.add_argument('--obf-mod', type=int, choices=(0, 1))
    cparser.add_argument('--obf-code', type=int, choices=(0, 1))
    cparser.add_argument('--wrap-mode', type=int, choices=(0, 1))
    cparser.add_argument('--cross-protection', type=int, choices=(0, 1))
    cparser.add_argument('--runtime-path', metavar="RPATH")
    cparser.add_argument('--plugin', dest='plugins', action='append',
                         help='Insert extra code to entry script')
    cparser.set_defaults(func=_config)

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
                         help='Force to obfuscate all scripts')
    cparser.add_argument('-r', '--only-runtime', action='store_true',
                         help='Generate extra runtime files only')
    cparser.add_argument('-n', '--no-runtime', action='store_true',
                         help='DO NOT generate runtime files')
    cparser.add_argument('-O', '--output',
                         help='Output path, override project configuration')
    cparser.add_argument('--platform', help='Distribute obfuscated scripts '
                         'to other platform')
    cparser.set_defaults(func=_build)

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
    cparser.add_argument('-m', '--obf-mod', choices=(0, 1),
                         default=1, type=int)
    cparser.add_argument('-c', '--obf-code', choices=(0, 1),
                         default=1, type=int)
    cparser.add_argument('-w', '--wrap-mode', choices=(0, 1),
                         default=1, type=int)
    cparser.add_argument('--debug', action='store_true',
                         help='Do not clean the test scripts'
                              'generated in real time')
    cparser.set_defaults(func=_benchmark)

    #
    # Command: capsule
    #
    cparser = subparsers.add_parser(
        'capsule',
        epilog=_capsule.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Generate or upgrade the capsule explicitly ')
    cparser.add_argument('--upgrade', action='store_true',
                         help='Upgrade the capsule to latest version')
    cparser.add_argument('path', nargs='?', default=os.path.expanduser('~'),
                         help='Path to save capsule, default is home path')
    cparser.set_defaults(func=_capsule)

    #
    # Command: register
    #
    cparser = subparsers.add_parser(
        'register',
        epilog=_register.__doc__ + purchase_info,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Make registration code work')
    group = cparser.add_mutually_exclusive_group()
    group.add_argument('-r', '--restore', type=int, nargs='?',
                       const=0, metavar='INDEX',
                       help='Restore license by registration code')
    group.add_argument('-b', '--backup', action='store_true',
                       help='Backup current registration code')
    group.add_argument('rcode', nargs='?', metavar='CODE',
                       help='Registration code')
    cparser.set_defaults(func=_register)

    #
    # Command: download
    #
    cparser = subparsers.add_parser(
        'download',
        epilog=_download.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Download platform-dependent dynamic libraries')
    cparser.add_argument('-O', '--output', metavar='NAME',
                         help='Save downloaded file to another path')
    group = cparser.add_mutually_exclusive_group()
    group.add_argument('--list', nargs='?', const='', dest='pattern',
                       help='List all the available platforms')
    group.add_argument('platid', nargs='?',
                       help='Download dynamic library by platform id')
    cparser.set_defaults(func=_download)

    args = parser.parse_args(args)
    if args.silent:
        logging.getLogger().setLevel(100)

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    logging.info(_version_info(short=True))
    logging.debug('PyArmor install path: %s', PYARMOR_PATH)

    args.func(args)


def main_entry():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    try:
        if 'download' not in sys.argv[1:2]:
            pytransform_bootstrap()
            capsule = DEFAULT_CAPSULE
            if not (os.path.exists(capsule) and check_capsule(capsule)):
                logging.info('Generate global capsule %s', capsule)
                make_capsule(capsule)
        main(sys.argv[1:])
    except Exception as e:
        if sys.flags.debug:
            raise
        logging.error('%s', e)
        sys.exit(1)


if __name__ == '__main__':
    main_entry()
