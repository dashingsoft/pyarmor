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

from .errors import CliError
from .context import Context
from .generate import Builder
from .register import LocalRegister, RealRegister
from .config import Configer, PyarmorShell

logger = logging.getLogger('Pyarmor')


def _cmd_gen_key(ctx, options):
    if len(options['inputs']) > 1:
        raise CliError('too many args %s' % options['inputs'][1:])

    name = ctx.outer_name
    if not name:
        raise CliError('missing outer key name')

    logger.info('start to generate outer runtime key OK')
    data = Builder(ctx).generate_runtime_key(outer=True)
    output = options.get('output', 'dist')
    os.makedirs(output, exist_ok=True)

    target = os.path.join(output, name)
    logger.info('write %s', target)
    with open(target, 'wb') as f:
        f.write(data)
    logger.info('generate outer runtime key OK')


def _cmd_gen_runtime(ctx, options):
    if len(options['inputs']) > 1:
        raise CliError('too many args %s' % options['inputs'][1:])

    output = options.get('output', 'dist')

    logger.info('start to generate runtime files')
    Builder(ctx).generate_runtime(output)
    logger.info('generate runtime files OK')


def cmd_gen(ctx, args):
    options = {}
    for x in ('recursive', 'findall', 'inputs', 'output', 'prebuilt_runtime',
              'enable_bcc', 'enable_jit', 'enable_refactor', 'enable_themida',
              'mix_name', 'mix_str', 'relative_import', 'restrict_module',
              'platforms', 'outer_name', 'check_period', 'expired'):
        v = getattr(args, x)
        if v is not None:
            options[x] = v

    if args.relative:
        options['relative_import'] = args.relative

    if args.mode:
        pass

    machine = ''
    if args.disk:
        machine += '*HARDDISK:' + args.disk
    if args.net:
        machine += '*IFMAC:' + args.net
    if args.ipv4:
        machine += '*IFIPV4:' + args.ipv4
    if machine:
        options['machines'] = machine

    logger.debug('command options: %s', options)
    ctx.push(options)

    if args.inputs[0].lower() in ('key', 'k'):
        _cmd_gen_key(ctx, options)
    elif args.inputs[0].lower() in ('runtime', 'run', 'r'):
        _cmd_gen_runtime(ctx, options)
    else:
        Builder(ctx).build(options, pack=args.pack, no_runtime=args.no_runtime)


def cmd_env(ctx, args):
    if args.interactive:
        return PyarmorShell(ctx).cmdloop()

    cfg = Configer(ctx)
    cfg.run(args.section, args.option, args.value, args.local)


def cmd_reg(ctx, args):
    regfile = args.regfile
    regname = args.regname if args.regname else ''
    product = args.product if args.product else 'non-profits'

    reg = LocalRegister(ctx) if args.dry else RealRegister(ctx)
    reg.check_args(args)

    meth = 'upgrade' if args.upgrade else 'register'
    getattr(reg, meth)(regfile, regname, product)

    logger.info('\n%s', reg)


def main_parser():
    parser = argparse.ArgumentParser(
        prog='pyarmor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-v', '--version', action='store_true',
                        help='show program\'s version number and exit')
    parser.add_argument('-q', '--silent', action='store_true',
                        help=argparse.SUPPRESS)
    parser.add_argument('-d', '--debug', action='store_true',
                        help=argparse.SUPPRESS)
    parser.add_argument('-C', '--encoding', help=argparse.SUPPRESS)
    parser.add_argument('--home', help=argparse.SUPPRESS)
    parser.add_argument('--boot', help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers(
        title='The most commonly used pyarmor commands are',
        metavar=''
    )

    gen_parser(subparsers)
    env_parser(subparsers)
    reg_parser(subparsers)

    return parser


def gen_parser(subparsers):
    '''generate obfuscated scripts and all required runtime files
    pyarmor gen <options> <scripts>

generate runtime key only
    pyarmor gen key <options>

generate runtime package only
    pyarmor gen runtime <options>'''
    cparser = subparsers.add_parser(
        'generate',
        aliases=['gen', 'g'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=gen_parser.__doc__,
        help='obfuscate scripts and generate runtime files'
    )

    cparser.add_argument('-O', '--output', metavar='PATH', help='output path')

    group = cparser.add_argument_group(
        'action arguments'
    ).add_mutually_exclusive_group()
    group.add_argument(
        '--pack', action='store_true', help='pack the obfuscated scripts'
    )
    group.add_argument(
        '--no-runtime', action='store_true',
        help='do not generate runtime package'
    )

    group = cparser.add_argument_group('obfuscation arguments')
    group.add_argument(
        '-r', '--recursive', action='store_true', default=None,
        help='search scripts in recursive mode'
    )
    group.add_argument(
        '-a', '--all', dest='findall', action='store_true', default=None,
        help='find all dependent modules and packages'
    )

    group.add_argument(
        '-m', '--mode', type=int, choices=(-2, -1, 1, 2),
        help='from the fastest mode -2 to the safest mode 2'
    )

    group.add_argument(
        '--mix-str', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--mix-name', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--enable-bcc', action='store_true', default=None,
        help=argparse.SUPPRESS
    )
    group.add_argument(
        '--enable-refactor', action='store_true', default=None,
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
        '--restrict', type=int, default=1, choices=(0, 1, 2, 3),
        dest='restrict_module',
        help='restrict obfuscated script'
    )

    group = cparser.add_argument_group('runtime package arguments')
    group.add_argument(
        '-i', dest='relative_import', action='store_const',
        default=None, const=1,
        help='import runtime package by relative way'
    )
    group.add_argument(
        '--relative', metavar='PREFIX',
        help='import runtime package with PREFIX'
    )
    group.add_argument(
        '--platform', dest='platforms', metavar='NAME', action='append',
        help='target platform to run obfuscated scripts, '
        'use this option multiple times for more platforms'
    )
    group.add_argument(
        '--with-runtime', dest='prebuilt_runtime', help=argparse.SUPPRESS
    )

    group = cparser.add_argument_group('runtime key arguments')
    group.add_argument(
        '--outer', metavar='NAME', dest='outer_name',
        help='using outer runtime key'
    )
    group.add_argument(
        '--expired', metavar='YYYY-MM-DD',
        help='expired date for runtime key'
    )
    group.add_argument(
        '--disk', metavar='xxxx',
        help='bind script to harddisk serial number'
    )
    group.add_argument(
        '--ipv4', metavar='a.b.c.d',
        help='bind script to ipv4 addr'
    )
    group.add_argument(
        '--net', metavar='x:x:x:x',
        help='Bind script to mac addr'
    )
    group.add_argument(
        '--period', type=int, metavar='N', dest='check_period',
        help='check runtime key in hours periodically'
    )

    cparser.add_argument(
        'inputs', metavar='ARG', nargs='+',
        help='scripts or keyword "key", "runtime"'
    )

    cparser.set_defaults(func=cmd_gen)


def env_parser(subparsers):
    '''get or set option's value
    if no section, show all the available sections
    if no option, show all the options in this section
    if no value, show option value, otherwise change option to value'''

    cparser = subparsers.add_parser(
        'environ',
        aliases=['env', 'e'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=env_parser.__doc__,
        help='show and config Pyarmor environments',
    )

    cparser.add_argument(
        '-i', dest='interactive', action='store_true',
        help='interactive mode'
    )
    cparser.add_argument(
        '-L', '--local', action='store_true',
        help='do everything in local settings'
    )

    cparser.add_argument('section', nargs='?', help='section name')
    cparser.add_argument('option', nargs='?', help='option name')
    cparser.add_argument('value', nargs='?', help='change option to value')

    cparser.set_defaults(func=cmd_env)


def reg_parser(subparsers):
    '''register or upgrade Pyarmor license

it's better to use option `-T` to check registration information
make sure everything is fine, then remove `-T` to register really

once register successfully, regname and product can't be changed
    '''
    cparser = subparsers.add_parser(
        'register',
        aliases=['reg', 'r'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=reg_parser.__doc__,
        help='register or upgrade Pyarmor license'
    )

    cparser.add_argument(
        '-r', '--regname', metavar='NAME',
        help='owner of this license'
    )
    cparser.add_argument(
        '-p', '--product', metavar='Name',
        help='license to this product'
    )
    cparser.add_argument(
        '-u', '--upgrade', action='store_true',
        help='upgrade license to pyarmor-pro'
    )
    cparser.add_argument(
        '-T', '--dry', action='store_true',
        help='dry run, not really register'
    )

    cparser.add_argument(
        'regfile', nargs=1, metavar='FILE',
        help='pyarmor-regcode-xxx.txt or pyarmor-regfile-xxxx.zip'
    )
    cparser.set_defaults(func=cmd_reg)


def log_settings(ctx, args):
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        handler = logging.FileHandler(ctx.debug_logfile, mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(handler)

    if args.silent:
        logging.getLogger().setLevel(100)


def log_exception(e):
    logger.critical('unknown error, please check pyarmor.error.log')
    handler = logging.FileHandler('pyarmor.error.log', mode='w')
    fmt = '%(process)d %(processName)s %(asctime)s'
    handler.setFormatter(logging.Formatter(fmt))
    log = logging.getLogger('Pyarmor.Error')
    log.propagate = False
    log.addHandler(logging.NullHandler())
    log.addHandler(handler)
    log.exception(e)


def print_version(ctx):
    info = 'Pyarmor %s' % ctx.version_info(), '', str(LocalRegister(ctx))
    print('\n'.join(info))


def main_entry(argv):
    home = os.getenv('PYARMOR_HOME')
    if not home:
        home = os.path.expanduser(os.path.join('~', '.pyarmor'))
    home = os.path.abspath(home)

    parser = main_parser()
    args = parser.parse_args(argv)

    if sys.version_info[0] == 2 or sys.version_info[1] < 7:
        raise CliError('only Python 3.7+ is supported now')

    if args.home:
        home = args.home
    ctx = Context(home, encoding=args.encoding)

    log_settings(ctx, args)

    if args.version:
        print_version(ctx)
        parser.exit()

    logger.info('Python %d.%d.%d', *sys.version_info[:3])
    logger.info('%s', ctx.version_info())

    logger.debug('native platform %s', ctx.native_platform)
    logger.debug('home path: %s', home)
    if args.boot:
        logger.info('change platform %s', args.boot)
        os.environ['PYARMOR_PLATFORM'] = args.boot

    if hasattr(args, 'func'):
        args.func(ctx, args)
    else:
        parser.print_help()


def call_old_pyarmor():
    from pyarmor.pyarmor import main_entry
    main_entry()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(name)-8s %(message)s',
    )

    try:
        main_entry(sys.argv[1:])
    # TBD: comment for debug
    # except (CliError, RuntimeError) as e:
    #     logger.error(e)
    #     sys.exit(1)
    except argparse.ArgumentError:
        call_old_pyarmor()
    except Exception as e:
        log_exception(e)
        logger.error(e)
        sys.exit(2)


if __name__ == '__main__':
    main()
