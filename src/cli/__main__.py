#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2023 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      Pyarmor                                              #
#                                                           #
#      Version: 8.0.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/main.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Thu Jan 12 10:27:05 CST 2023
#
import argparse
import logging
import os
import sys

from . import logger, CliError
from .context import Context
from .register import Register, WebRegister, check_license_version
from .config import Configer
from .shell import PyarmorShell
from .plugin import Plugin
from .generate import Builder
from .bootstrap import check_prebuilt_runtime_library
from .command import Commander


def _cmd_gen_key(builder, options):
    n = len(options['inputs'])
    if n > 1:
        logger.error('please check online documentation to learn')
        logger.error('how to use command "pyarmor gen key"')
        raise CliError('invalid arguments: %s' % options['inputs'][1:])
    keyname = builder.ctx.outer_keyname

    logger.info('start to generate outer runtime key "%s"', keyname)
    data = builder.generate_runtime_key(outer=True)
    output = options.get('output', 'dist')
    if output == 'pipe':
        logger.info('return runtime key by pipe')
        return data
    os.makedirs(output, exist_ok=True)

    target = os.path.join(output, keyname)
    logger.info('write %s', target)
    with open(target, 'wb') as f:
        f.write(data)

    Plugin.post_key(builder.ctx, target)
    logger.info('generate outer runtime key OK')


def _cmd_gen_runtime(builder, options):
    if len(options['inputs']) > 1:
        logger.error('please check online documentation to learn')
        logger.error('how to use command "pyarmor gen runtime"')
        raise CliError('invalid arguments: %s' % options['inputs'][1:])

    output = options.get('output', 'dist')

    logger.info('start to generate runtime package')
    builder.generate_runtime_package(output)

    keyname = os.path.join(output, builder.ctx.runtime_keyfile)
    logger.info('write "%s"', keyname)
    with open(keyname, 'wb') as f:
        f.write(builder.ctx.runtime_key)
    logger.info('generate runtime package to "%s" OK', output)


def format_gen_args(ctx, args):
    options = {}
    for x in ('recursive', 'findall', 'output', 'no_runtime',
              'enable_bcc', 'enable_jit', 'enable_rft', 'enable_themida',
              'obf_module', 'obf_code', 'assert_import', 'assert_call',
              'mix_str', 'import_prefix', 'restrict_module',
              'platforms', 'outer', 'period', 'expired', 'devices'):
        v = getattr(args, x)
        if v is not None:
            options[x] = v

    if options.get('platforms'):
        platforms = []
        for item in options['platforms']:
            platforms.extend([x.strip() for x in item.split(',')])
        options['platforms'] = platforms
    elif ctx.runtime_platforms:
        options['platforms'] = ctx.runtime_platforms.split()
        logger.info('get runtime platforms from configuration file')
    if options.get('platforms'):
        logger.info('use runtime platforms: %s', options['platforms'])

    if args.inputs:
        options['inputs'] = [os.path.normpath(x) for x in args.inputs]

    if args.use_runtime:
        options['no_runtime'] = True
        options['use_runtime'] = args.use_runtime

    if (options.get('restrict_module', 0) == 2
        and ctx.cfg['builder'].get('private_module_as_restrict', 0)):
        options['restrict_module'] = 3

    if options.get('assert_call') or options.get('assert_import'):
        if options.get('restrict_module', 0) < 2:
            logger.debug('implicitly set restrict_module = 2')
            options['restrict_module'] = 2

    if args.enables:
        for x in args.enables:
            options['enable_' + x] = True

    if args.prefix:
        options['import_prefix'] = args.prefix

    if args.no_wrap:
        options['wrap_mode'] = 0

    if args.includes:
        options['includes'] = ' '.join(args.includes)
    if args.excludes:
        options['excludes'] = ' '.join(args.excludes)

    if args.bind_data:
        options['user_data'] = args.bind_data

    if args.pack:
        dist_path = ctx.pack_obfpath
        logger.info('implicitly save obfuscated scripts to "%s"', dist_path)
        options['output'] = dist_path

    return options


# Unused
def check_cross_platform(ctx, platforms):
    rtver = ctx.cfg.get('pyarmor', 'cli.runtime')
    cmd = 'pip install pyarmor.cli.runtime~=%s.0' % rtver
    try:
        from pyarmor.cli import runtime
    except (ImportError, ModuleNotFoundError):
        logger.error('cross platform need package "pyarmor.cli.runtime"')
        logger.error('please run "%s" to fix it', cmd)
        raise CliError('no package "pyarmor.cli.runtime" found')

    if runtime.__VERSION__ != rtver:
        logger.error('please run "%s" to fix it', cmd)
        raise CliError('unexpected "pyarmor.cli.runtime" version')

    platnames = []
    for path in runtime.__path__:
        logger.debug('search runtime platforms at: %s', path)
        platnames.extend(os.listdir(os.path.join(path, 'libs')))

    map_platform = runtime.map_platform
    unknown = set([map_platform(x) for x in platforms]) - set(platnames)

    if unknown:
        logger.error('please check documentation "References/Environments"')
        raise CliError('unsupported platforms "%s"' % ', '.join(unknown))


def check_gen_context(ctx, args):
    platforms = ctx.runtime_platforms
    if platforms and set(platforms) != set([ctx.pyarmor_platform]):
        if ctx.enable_bcc:
            raise CliError('bcc mode does not support cross platform')
        rtver = ctx.cfg['pyarmor'].get('cli.runtime', '')
        check_prebuilt_runtime_library(platforms, ctx.enable_themida, rtver)

    elif ctx.enable_themida:
        if not ctx.pyarmor_platform.startswith('windows'):
            raise CliError('--enable-themida only works for Windows')
        rtver = ctx.cfg['pyarmor'].get('cli.runtime', '')
        check_prebuilt_runtime_library([], ['themida'], rtver)

    if ctx.enable_bcc:
        plat, arch = ctx.pyarmor_platform.split('.')
        if arch not in ('x86_64', 'aarch64', 'x86', 'armv7'):
            raise CliError('bcc mode still not support arch "%s"' % arch)

    if args.no_runtime and not ctx.runtime_outer:
        raise CliError('--outer is required if using --no_runtime')

    if ctx.use_runtime and not ctx.runtime_outer:
        if not os.path.exists(ctx.use_runtime):
            raise CliError('no runtime package at "%s"', ctx.use_runtime)
        if any([ctx.runtime_devices, ctx.runtime_period, ctx.runtime_expired]):
            raise CliError('--use-runtime conflicts with any -e, --period, -b')
        keyname = os.path.join(ctx.use_runtime, ctx.runtime_keyfile)
        if not os.path.exists(keyname):
            logger.info('please run `pyarmor gen runtime ...` to generate'
                        ' shared runtime package at first')
            raise CliError('no runtime key in "%s"', ctx.use_runtime)
        # TBD: check runtime package is not generated by --outer

    if ctx.runtime_outer and any(
            [ctx.runtime_devices, ctx.runtime_period, ctx.runtime_expired]):
        # Fix issue 2069
        if args.inputs[0].lower() not in ('key', 'k'):
            raise CliError('--outer conflicts with any -e, --period, -b')

    if args.pack:
        choices = 'onefile', 'onedir', 'F', 'D', 'FC', 'DC'
        if args.pack not in choices and not os.path.isfile(args.pack):
            raise CliError('--pack must be an executable file, specfile, '
                           '"onefile" or "onedir"')
        if args.no_runtime:
            raise CliError('--pack conficts with --no-runtime, --use-runtime')
        if ctx.import_prefix:
            raise CliError('--pack conficts with -i, --prefix')


def cmd_gen(ctx, args):
    options = format_gen_args(ctx, args)
    logger.debug('command options: %s', options)
    check_license_version(ctx)

    ctx.push(options)
    check_gen_context(ctx, args)

    builder = Builder(ctx)

    Plugin.install(ctx)
    if args.inputs[0].lower() in ('key', 'k'):
        return _cmd_gen_key(builder, options)
    elif args.inputs[0].lower() in ('runtime', 'run', 'r'):
        _cmd_gen_runtime(builder, options)
    elif args.pack:
        from .repack import find_packer
        Repacker = find_packer(args.pack)
        packer = Repacker(ctx, args.pack, options['inputs'], args.output)
        packer.check()
        builder.process(options, packer=packer)
        Plugin.post_build(ctx, pack=args.pack)
        packer.build()
    else:
        builder.process(options)
        Plugin.post_build(ctx)


def cmd_cfg(ctx, args):
    scope = 'global' if args.scope else 'local'
    cfg = Configer(ctx, encoding=args.encoding)
    name = 'reset' if args.reset else 'run'
    getattr(cfg, name)(args.options, scope == 'local', args.name)


def cmd_reg(ctx, args):
    if args.buy:
        from webbrowser import open_new_tab
        open_new_tab(ctx.cfg['pyarmor']['buyurl'])
        return

    if args.device and not args.regfile:
        reg = Register(ctx)
        reg.generate_group_device(args.device)
        logger.info('device file has been generated successfully')
        return

    regfile = args.regfile
    if not regfile:
        reg = Register(ctx)
        logger.info('Current license information:\n\n%s', reg)
        return

    if regfile.endswith('.txt') and not args.product:
        logger.error('please use -p to specify product name for this license')
        raise CliError('missing product name')

    if regfile.endswith('.zip') and args.product:
        logger.error('please do not use -p for non initial registration')
        raise CliError('unwanted product name')

    upgrade = args.upgrade
    if upgrade:
        if not regfile.endswith('.txt'):
            raise CliError('upgrade need text file "pyarmor-keycode-xxxx.txt"')
        url = 'https://github.com/dashingsoft/pyarmor/issues/980'
        msg = ("",
               "Pyarmor 8 changes EULA and uses new commands",
               "It's different from previous Pyarmor totally",
               "Please read this import notes first:",
               url,
               "Do not upgrade to Pyarmor 8 if don't know what are changed",
               "", "")
        prompt = 'I have known the changes of Pyarmor 8? (yes/no/help) '
        choice = input('\n'.join(msg) + prompt).lower()[:1]
        if choice == 'h':
            import webbrowser
            webbrowser.open(url)
        if not choice == 'y':
            logger.info('abort upgrade')
            return

    if args.device:
        if not regfile.endswith('.zip'):
            logger.error('invalid registeration file "%s"', regfile)
            raise CliError('please use ".zip" file to register group device')
        regsvr = WebRegister(ctx)
        regsvr.check_request_interval()
        regsvr.request_device_regfile(regfile, args.device)
        logger.info('The device regfile has been generated successfully')

    elif args.ci:
        regsvr = WebRegister(ctx)
        regsvr.check_request_interval()
        regsvr.request_ci_regfile(regfile)

    elif regfile.endswith('.zip'):
        reg = Register(ctx)
        logger.info('register "%s"', regfile)
        reg.register_regfile(regfile)
        logger.info('This license registration information:\n\n%s', str(reg))

    else:
        regsvr = WebRegister(ctx)
        regsvr.check_request_interval()
        info, msg = regsvr.prepare(regfile, args.product, upgrade=upgrade)
        prompt = 'Are you sure to continue? (yes/no) '
        if args.confirm:
            from time import sleep
            sleep(1.0)
        elif input(msg + prompt) not in ('y', 'yes', 'Y', 'Yes'):
            logger.info('abort registration')
            return
        # Free upgrade to Pyarmor Basic
        if upgrade and not info['upgrade']:
            return regsvr.register(regfile, args.product, upgrade=True)

        if upgrade:
            regsvr.upgrade_to_pro(regfile, args.product)
        else:
            group = info['lictype'] == 'GROUP'
            regsvr.register(regfile, args.product, group=group)


def cmd_man(ctx, args):
    from subprocess import check_call, check_output, STDOUT

    try:
        m = __import__('pyarmor.man')
    except ModuleNotFoundError:
        logger.info('pyarmor.man is still not installed')
        if input('Install it now? (Y/n) ') not in ('Y', 'y'):
            return
        m = None

    if m is None:
        try:
            logger.info('installing package "pyarmor.man"...')
            check_output([sys.executable, '-m', 'pip',
                          'install', '-U', 'pyarmor.man'],
                         stderr=STDOUT)
            logger.info('install package "pyarmor.man" OK')
        except Exception:
            logger.error('install package "pyarmor.man" failed')
            logger.error('please install it manually:')
            logger.error('\tpip install -U pyarmor.man')
            return

    check_call([sys.executable, '-m', 'pyarmor.man.shell'])


def main_parser(cmd=None):
    parser = argparse.ArgumentParser(
        prog='pyarmor',
        fromfile_prefix_chars='@',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-v', '--version', action='store_true',
        help='show version information and exit'
    )
    parser.add_argument(
        '-q', '--silent', action='store_true',
        help='suppress all normal output'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='generate debug file "pyarmor.debug.log"'
    )
    parser.add_argument(
        '-i', dest='interactive', action='store_true',
        help=argparse.SUPPRESS,
    )
    parser.add_argument('--home', help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers(
        title='The most commonly used pyarmor commands are',
    )

    gen_parser(subparsers)
    reg_parser(subparsers)

    if cmd:
        cmd.env_parser(subparsers)
        cmd.init_parser(subparsers)
        cmd.build_parser(subparsers)

    cfg_parser(subparsers)
    man_parser(subparsers)

    return parser


def gen_parser(subparsers):
    '''generate obfuscated scripts and all required runtime files
    pyarmor gen <options> <scripts>

generate runtime key only
    pyarmor gen key <options>

generate runtime package only
    pyarmor gen runtime <options>

Refer to
https://pyarmor.readthedocs.io/en/stable/reference/man.html#pyarmor-gen
'''
    cparser = subparsers.add_parser(
        'gen',
        aliases=['generate', 'g'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=gen_parser.__doc__,
        help='generate obfuscated scripts and required runtime files'
    )

    cparser.add_argument('-O', '--output', metavar='PATH', help='output path')

    group = cparser.add_argument_group(
        'action arguments'
    ).add_mutually_exclusive_group()
    group.add_argument(
        '--pack', metavar='MODE',
        help='specify pack mode, onefile or onedir'
    )
    group.add_argument(
        '--no-runtime', action='store_true', help=argparse.SUPPRESS
        # help='do not generate runtime package (only used with --outer)'
    )
    group.add_argument(
        '--use-runtime', metavar='PATH',
        help='use shared runtime package'
    )

    group = cparser.add_argument_group('obfuscation arguments')
    group.add_argument(
        '-r', '--recursive', action='store_true', default=None,
        help='search scripts in recursive mode'
    )
    group.add_argument(
        '-a', '--all', dest='findall', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--include', dest='includes', metavar='PATTERN', action='append',
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--exclude', dest='excludes', metavar='PATTERN', action='append',
        help='Exclude scripts and paths'
    )

    group.add_argument(
        '--obf-module', type=int, default=None, choices=(0, 1),
        help='obfuscate whole module (default is 1)'
    )
    group.add_argument(
        '--obf-code', type=int, default=None, choices=(0, 1, 2),
        help='obfuscate each function (default is 1)'
    )
    group.add_argument(
        '--no-wrap', action='store_true', default=None,
        help='disable wrap mode',
    )

    group.add_argument(
        '--mix-str', action='store_true', default=None,
        help='protect string constant',
    )
    group.add_argument(
        '--enable-bcc', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--enable-rft', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--enable-jit', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--enable-themida', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--assert-call', action='store_true', default=None,
        help='assert function is obfuscated'
    )
    group.add_argument(
        '--assert-import', action='store_true', default=None,
        help='assert module is obfuscated'
    )
    group.add_argument(
        '--enable', action='append', dest='enables',
        choices=('jit', 'bcc', 'rft', 'themida'),
        help='enable different obfuscation features',
    )

    restrict = group.add_mutually_exclusive_group()
    restrict.add_argument(
        '--private', action="store_const", default=None, const=2,
        dest='restrict_module', help='enable private mode for script'
    )
    restrict.add_argument(
        '--restrict', action="store_const", default=None, const=3,
        dest='restrict_module', help='enable restrict mode for package'
    )

    group = cparser.add_argument_group('runtime package arguments')
    group.add_argument(
        '-i', dest='import_prefix', action='store_const',
        default=None, const=1,
        help='store runtime files inside package'
    )
    group.add_argument(
        '--prefix', metavar='PREFIX',
        help='import runtime package with PREFIX'
    )
    group.add_argument(
        '--platform', dest='platforms', metavar='NAME', action='append',
        help='cross platform obfuscation'
    )

    group = cparser.add_argument_group('runtime key arguments')
    group.add_argument(
        '--outer', action='store_true', default=None,
        help='enable outer runtime key'
    )
    group.add_argument(
        '-e', '--expired', metavar='DATE',
        help='set expired date'
    )
    group.add_argument(
        '--period', metavar='N', dest='period',
        help='check runtime key periodically'
    )
    group.add_argument(
        '-b', '--bind-device', dest='devices', metavar='DEV', action='append',
        help='bind obfuscated scripts to device'
    )
    group.add_argument(
        '--bind-data', metavar='STRING or @FILENAME',
        help='store user data to runtime key'
    )

    cparser.add_argument(
        'inputs', metavar='ARG', nargs='+', help='scripts or packages'
    )

    cparser.set_defaults(func=cmd_gen)


def cfg_parser(subparsers):
    '''show all options:
    pyarmor cfg

show option `OPT` value:
    pyarmor cfg OPT

change option value:
    pyarmor cfg OPT=VALUE

Refer to
https://pyarmor.readthedocs.io/en/stable/reference/man.html#pyarmor-cfg
    '''

    cparser = subparsers.add_parser(
        'cfg',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=cfg_parser.__doc__,
        help='show and config Pyarmor environments',
    )

    cparser.add_argument(
        '-p', dest='name',
        help='private settings for special module or package'
    )
    cparser.add_argument(
        '-g', '--global', dest='scope', action='store_true',
        help='do everything in global settings, otherwise local settings'
    )
    cparser.add_argument(
        '-s', '--section', help=argparse.SUPPRESS
    )
    cparser.add_argument(
        '-r', '--reset', action='store_true',
        help='reset option to default value'
    )
    cparser.add_argument(
        '--encoding',
        help='specify encoding to read configuration file'
    )

    cparser.add_argument(
        'options', nargs='*', metavar='option',
        help='option name or "name=value"'
    )

    cparser.set_defaults(func=cmd_cfg)


def reg_parser(subparsers):
    '''register Pyarmor or upgrade Pyarmor license

At the first time to register Pyarmor, `-p` (product name) should be
set. For non-commercial use, set it to "non-profits". The product name
can't be changed after initial registration.

Refer to
https://pyarmor.readthedocs.io/en/stable/reference/man.html#pyarmor-reg
    '''
    cparser = subparsers.add_parser(
        'reg',
        aliases=['register', 'r'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=reg_parser.__doc__,
        help='register Pyarmor or upgrade old Pyarmor license'
    )

    cparser.add_argument(
        '-r', '--regname', metavar='NAME',
        help=argparse.SUPPRESS
    )
    cparser.add_argument(
        '-p', '--product', metavar='NAME',
        help='bind license to this product'
    )
    cparser.add_argument(
        '-u', '--upgrade', action='store_true',
        help='upgrade old Pyarmor license'
    )
    cparser.add_argument(
        '-g', '--device', metavar='ID', type=int, choices=range(1, 101),
        help='device id (1-100) in group license'
    )
    cparser.add_argument(
        '--buy', action='store_true',
        help='open buy link in default web browser'
    )
    cparser.add_argument(
        '-y', '--confirm', action='store_true',
        help=argparse.SUPPRESS
    )
    cparser.add_argument(
        '-C', '--CI', action='store_true', dest='ci',
        help='request license regfile for CI pipeline'
    )

    cparser.add_argument(
        'regfile', nargs='?', metavar='FILE',
        help='pyarmor-regcode-xxx.txt or pyarmor-regfile-xxxx.zip'
    )
    cparser.set_defaults(func=cmd_reg)


def man_parser(subparsers):
    '''Start Pyarmor Man shell

    Pyarmor Man is designed to help Pyarmor users to learn and use
    Pyarmor, to find solution quickly when something is wrong, to
    report bug by template in order to save both Pyarmor team's
    and users' time.
    '''
    cparser = subparsers.add_parser(
        'man',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=man_parser.__doc__,
        help='start Pyarmor Man shell'
    )

    cparser.set_defaults(func=cmd_man)
    return cparser


def log_settings(ctx, args):
    import logging.config
    logging.config.fileConfig(ctx.default_config)

    if args.silent:
        logger.setLevel(logging.ERROR)

    elif args.debug:
        logger.setLevel(logging.DEBUG)
        logger.handlers[1].setLevel(logging.DEBUG)

    if ctx.cfg.getboolean('builder', 'enable_trace'):
        level = logging.DEBUG if args.debug else logging.INFO
        logging.getLogger('trace').setLevel(level)


def log_bug(e):
    parser = main_parser(cmd=Commander())
    args = parser.parse_args(sys.argv[1:])
    ctx = Context(*get_home_paths(args))
    cmdline = ' '.join(sys.argv)
    buglog = logging.getLogger('cli.bug')

    buglog.info('[BUG]: %s\n', e)
    buglog.info('## Command Line\n%s\n', cmdline)
    buglog.info('## Environments', )
    buglog.info('Python %d.%d.%d', *sys.version_info[:3])
    buglog.info('Pyarmor %s', ctx.version_info())
    buglog.info('Platform %s', ctx.pyarmor_platform)
    buglog.info('Native %s', ctx.native_platform)
    buglog.info('Home %s', ctx.home_path)
    buglog.info('')

    if not isinstance(e, CliError):
        from traceback import format_exc
        buglog.info('## Traceback\n%s\n', format_exc())

    # reference/errors.html
    # reference/solutions.html
    # questions.html


def print_version(ctx):
    reg = Register(ctx)
    info = 'Pyarmor %s' % ctx.version_info(), '', str(reg)
    print('\n'.join(info))

    reg.check_group_license()
    check_license_version(ctx, silent=True)


def get_home_paths(args):
    home = args.home if args.home else os.getenv('PYARMOR_HOME')
    if not home:
        home = os.path.join('~', '.pyarmor')
    elif home.startswith(','):
        home = os.path.join('~', '.pyarmor') + home
    home = os.path.abspath(os.path.expandvars(os.path.expanduser(home)))
    return (home + ',,,').split(',')[:4]


def main_entry(argv):
    cmd = Commander()
    parser = main_parser(cmd)
    args = parser.parse_args(argv)

    ctx = cmd.ctx = Context(*get_home_paths(args))
    log_settings(ctx, args)

    x, y = sys.version_info[:2]
    if not (x == 3 and y > 6 and y < 16):
        raise CliError('Python %s.%s is not supported' % (x, y))

    if args.version:
        print_version(ctx)
        parser.exit()

    if args.interactive:
        return PyarmorShell(ctx).cmdloop()

    logger.info('Python %d.%d.%d', *sys.version_info[:3])
    logger.info('Pyarmor %s', ctx.version_info())
    logger.info('Platform %s', ctx.pyarmor_platform)

    logger.debug('native platform %s', ctx.native_platform)
    logger.debug('home path: %s', ctx.home_path)
    logger.debug('args: %s', argv)

    if hasattr(args, 'func'):
        return args.func(ctx, args)
    else:
        parser.print_help()


def main():
    try:
        main_entry(sys.argv[1:])
    except Exception as e:
        logger.error(e)
        log_bug(e)
        sys.exit(1 if isinstance(e, CliError) else 2)


if __name__ == '__main__':
    main()
