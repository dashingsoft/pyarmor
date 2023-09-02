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
from .register import Register, WebRegister
from .config import Configer
from .shell import PyarmorShell
from .plugin import Plugin
from .generate import Builder
from .bootstrap import check_prebuilt_runtime_library


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
        dist_path = os.path.join(ctx.repack_path, 'dist')
        logger.info('implicitly set output to "%s"', dist_path)
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

    if ctx.cmd_options.get('no_runtime') and not ctx.runtime_outer:
        raise CliError('--outer is required if using --no_runtime')

    if ctx.use_runtime and not ctx.runtime_outer:
        if os.path.exists(ctx.use_runtime):
            keyname = os.path.join(ctx.use_runtime, ctx.runtime_keyfile)
            if not os.path.exists(keyname):
                raise CliError('no runtime key in "%s"', ctx.use_runtime)

    if ctx.runtime_outer and any(
            [ctx.runtime_devices, ctx.runtime_period, ctx.runtime_expired]):
        raise CliError('--outer conflicts with any -e, --period, -b')

    if args.pack:
        if not os.path.isfile(args.pack):
            raise CliError('--pack must be an executable file')
        if args.no_runtime:
            raise CliError('--pack conficts with --no-runtime, --use-runtime')
        if ctx.import_prefix:
            raise CliError('--pack conficts with -i, --prefix')


def cmd_gen(ctx, args):
    options = format_gen_args(ctx, args)
    logger.debug('command options: %s', options)
    ctx.push(options)
    check_gen_context(ctx, args)

    builder = Builder(ctx)

    Plugin.install(ctx)
    if args.inputs[0].lower() in ('key', 'k'):
        return _cmd_gen_key(builder, options)
    elif args.inputs[0].lower() in ('runtime', 'run', 'r'):
        _cmd_gen_runtime(builder, options)
    elif args.pack:
        from .repack import Repacker
        codesign = ctx.cfg['pack'].get('codesign_identify', None)
        packer = Repacker(args.pack, ctx.repack_path, codesign=codesign)
        builder.process(options, packer=packer)
        Plugin.post_build(ctx, pack=args.pack)
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
        regsvr.register_group_device(regfile, args.device)
        logger.info('The device regfile has been generated successfully')

    elif regfile.endswith('.zip'):
        reg = Register(ctx)
        logger.info('register "%s"', regfile)
        reg.register_regfile(regfile)
        logger.info('This license registration information:\n\n%s', str(reg))

    else:
        regsvr = WebRegister(ctx)
        info, msg = regsvr.prepare(regfile, args.product, upgrade=upgrade)
        prompt = 'Are you sure to continue? (yes/no) '
        if args.confirm:
            from time import sleep
            sleep(1.0)
        elif input(msg + prompt) not in ('y', 'yes'):
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


def main_parser():
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
        help='print debug informations in the console'
    )
    parser.add_argument(
        '-i', dest='interactive', action='store_true',
        help=argparse.SUPPRESS,
    )
    parser.add_argument('--home', help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers(
        title='The most commonly used pyarmor commands are',
        metavar=''
    )

    gen_parser(subparsers)
    reg_parser(subparsers)
    cfg_parser(subparsers)

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
        '--pack', metavar='BUNDLE',
        help='repack bundle with obfuscated scripts'
    )
    group.add_argument(
        '--no-runtime', action='store_true',
        help='do not generate runtime package'
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
        'regfile', nargs='?', metavar='FILE',
        help='pyarmor-regcode-xxx.txt or pyarmor-regfile-xxxx.zip'
    )
    cparser.set_defaults(func=cmd_reg)


def log_settings(ctx, args):
    if args.debug:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.FileHandler(ctx.debug_logfile, mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        handler.setLevel(logging.DEBUG)
        root.addHandler(handler)

    tracelog = logging.getLogger('trace')
    tracelog.propagate = False
    tracelog.addHandler(logging.NullHandler())
    if ctx.cfg.getboolean('builder', 'enable_trace'):
        handler = logging.FileHandler(ctx.trace_logfile, mode='w')
        handler.setFormatter(logging.Formatter('%(name)-20s %(message)s'))
        handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
        tracelog.addHandler(handler)

    if args.silent:
        logging.getLogger().setLevel(100)


def log_exception(e):
    logger.debug('unknown error, please check pyarmor.error.log')
    handler = logging.FileHandler('pyarmor.error.log', mode='w')
    fmt = '%(process)d %(processName)s %(asctime)s'
    handler.setFormatter(logging.Formatter(fmt))
    log = logging.getLogger('error')
    log.propagate = False
    log.addHandler(logging.NullHandler())
    log.addHandler(handler)
    log.exception(e)


def print_version(ctx):
    info = 'Pyarmor %s' % ctx.version_info(), '', str(Register(ctx))
    print('\n'.join(info))


def get_home_paths(args):
    home = args.home if args.home else os.getenv('PYARMOR_HOME')
    if not home:
        home = os.path.join('~', '.pyarmor')
    elif home.startswith(','):
        home = os.path.join('~', '.pyarmor') + home
    home = os.path.abspath(os.path.expandvars(os.path.expanduser(home)))
    return (home + ',,,').split(',')[:4]


def main_entry(argv):
    parser = main_parser()
    args = parser.parse_args(argv)

    if sys.version_info[0] == 2 or sys.version_info[1] < 7:
        raise CliError('only Python 3.7+ is supported now')

    ctx = Context(*get_home_paths(args))

    log_settings(ctx, args)

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

    if hasattr(args, 'func'):
        return args.func(ctx, args)
    else:
        parser.print_help()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )

    try:
        main_entry(sys.argv[1:])
    except CliError as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        log_exception(e)
        logger.error(e)
        sys.exit(2)


if __name__ == '__main__':
    main()
