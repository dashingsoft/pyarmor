#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2024 Dashingsoft corp.                   #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 9.1.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor/cli/commander.py
#
#  @Author: Jondy Zhao(pyarmor@163.com)
#
#  @Create Date: Tue Nov 12 16:38:51 CST 2024
#
import argparse
import configparser
import shlex

from os import makedirs
from os.path import abspath, exists, join as joinpath, relpath

from . import logger, CliError
from .project import Project
from .shell import PyarmorShell


class Commander:

    def init_parser(self, subparsers):
        parser = subparsers.add_parser(
            'init',
            aliases=['i'],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='init project in current path',
            help='init project in current path'
        )

        parser.add_argument(
            '-s', '--src', metavar='PATH', default='',
            help='where to find scripts, modules and packages'
        )
        parser.add_argument(
            '-e', '--entry', dest='scripts', metavar='FILE',
            action='append',
            help='project entry scripts'
        )
        parser.add_argument(
            '-m', '--module', metavar='FILE',
            dest='modules', action='append',
            help='append extra module'
        )
        parser.add_argument(
            '-p', '--package', metavar='PATH',
            dest='packages', action='append',
            help='append extra package'
        )

        parser.add_argument(
            '-x', '--exclude', metavar='PATTERN',
            dest='excludes', action='append',
            help='exclude file or path from src'
        )

        parser.add_argument(
            '-r', '--recursive', action='store_true',
            help='search modules and packages recursively'
        )
        parser.add_argument(
            '-C', '--clean', action='store_true',
            help='remove old project information before init'
        )

        parser.set_defaults(func=self.cmd_init)

    def env_parser(self, subparsers):
        parser = subparsers.add_parser(
            'env',
            aliases=['environ', 'e'],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='check and set Pyarmor environments',
            help='check and set Pyarmor environments'
        )

        # parser.add_argument(
        #     '-i', '--interactive', action='store_true',
        #     help='enable interactive mode'
        # )

        group = parser.add_argument_group(
            'select domain (default: project)'
        ).add_mutually_exclusive_group()
        group.add_argument(
            '-l', '--local', dest='domain', default='local',
            action="store_const", const='local',
            help='enter local domain'
        )
        group.add_argument(
            '-g', '--global', dest='domain', default='local',
            action="store_const", const='global',
            help='enter global domain'
        )
        group.add_argument(
            '-p', '--project', dest='domain', default='local',
            action="store_const", const='project',
            help='enter project domain'
        )

        parser.add_argument(
            'exprs', metavar='VERB', nargs='*',
            help='change option by info/ls/set/reset/push/pop'
        )

        parser.set_defaults(func=self.cmd_env)

    def build_parser(self, subparsers):
        parser = subparsers.add_parser(
            'build',
            aliases=['b'],
            formatter_class=argparse.RawTextHelpFormatter,
            help='obfuscate all the scripts in the project'
        )

        group = parser.add_argument_group(
            'select build target'
        ).add_mutually_exclusive_group()
        # group.add_argument(
        #     '--std', dest='target', default='std',
        #     action="store_const", const='std',
        #     help='genetate standard obfuscated scripts'
        # )
        # group.add_argument(
        #     '--ecc', dest='target', default='std',
        #     action="store_const", const='ecc',
        #     help='genetate scripts with embedded C code'
        # )
        # group.add_argument(
        #     '--vmc', dest='target', default='std',
        #     action="store_const", const='vmc',
        #     help='genetate scripts with vm C code'
        # )
        group.add_argument(
            '--rft', dest='target', default='std',
            action="store_const", const='rft',
            help='only refactor scripts'
        )
        group.add_argument(
            '--mini', dest='target', default='std',
            action="store_const", const='mini',
            help='genetate high performance scripts'
        )
        group.add_argument(
            '--mini-rft', dest='target', default='std',
            action="store_const", const='mini-rft',
            help='genetate high performance refactor scripts'
        )
        group.add_argument(
            '--list', dest='target', default='std',
            action="store_const", const='list',
            help='list project scripts, modules and packages'
        )
        group.add_argument(
            '--types', dest='target', default='std',
            action="store_const", const='types',
            help=argparse.SUPPRESS
        )
        group.add_argument(
            '--randname', type=int, metavar='{0,1}',
            help='Build random name pool'
        )
        group.add_argument(
            '--autofix', type=int, choices=(0, 1, 2, 3),
            help='Generate refactor rules by autofix mode'
        )

        # parser.add_argument(
        #     '--pack', metavar='MODE',
        #     help='specify pack mode, onefile or onedir'
        # )

        # sgroup = parser.add_argument_group(
        #     title='these options only for --std target',
        # )
        # sgroup.add_argument(
        #     '--restrict',
        #     default=1, choices=(0, 1, 2),
        #     help='set restrict mode (default: 1)'
        # )
        # sgroup.add_argument(
        #     '--assert-import', action="store_true",
        #     help='check imported module is obfuscated'
        # )
        # sgroup.add_argument(
        #     '--assert-call', action="store_true",
        #     help='check function is obfuscated before call'
        # )

        parser.add_argument(
            '-O', '--output', metavar='PATH',
            help='output path, default is "dist"'
        )

        # parser.add_argument(
        #     'project', metavar='PATH', nargs='?',
        #     help='project path (default: current path)'
        # )

        parser.set_defaults(func=self.cmd_build)

    def main_parser(self):
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

        subparsers = parser.add_subparsers(
            title='The most commonly used pyarmor commands are',
        )

        self.env_parser(subparsers)
        self.init_parser(subparsers)
        self.build_parser(subparsers)

        return parser

    def run(self, ctx, argv):
        parser = self.main_parser()
        args = parser.parse_args(argv)
        if hasattr(args, 'func'):
            args.func(ctx, args)
        else:
            parser.print_help()

    def cmd_init(self, ctx, args):
        logger.debug('init %s', args)

        sep = ','
        cfgsep = ' '
        data = {}

        cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation(),
        )
        cfg.read([ctx.local_config], encoding=ctx.encoding)

        sectname = 'project'
        if args.clean:
            logger.info('clean old project')
            if cfg.has_section(sectname):
                cfg.remove_section(sectname)

        if cfg.has_section(sectname):
            logger.info('change project settings')
        else:
            cfg.add_section(sectname)

        sect = cfg[sectname]
        if args.src:
            src = abspath(args.src)
            if not sect.get('src'):
                sect['src'] = src
            elif src != sect['src']:
                raise CliError(
                    'project has another src, '
                    'use option "-C" to fix this issue'
                )
        else:
            src = sect.get('src')
            if not src:
                src = abspath('.')
                sect['src'] = src

        if not exists(src):
            raise CliError('no found src "%s"' % src)

        def format_path(plist, raw=False):
            r = []
            for x in sep.join(plist).split(sep):
                x = x.strip()
                r.append(x if raw else relpath(abspath(x), src))
            return r

        if args.scripts:
            data['scripts'] = format_path(args.scripts)

        if args.excludes:
            data['excludes'] = format_path(args.excludes, raw=1)

        if args.modules:
            data['modules'] = format_path(args.modules)

        if args.packages:
            data['packages'] = format_path(args.packages)

        if args.recursive:
            data['recursive'] = 1

        for key, value in data.items():
            old = sect.get(key)
            if old is not None:
                logger.info('overwrite %s: %s', key, old)
            if isinstance(value, (tuple, list)):
                value = cfgsep.join([
                    x.replace(' ', '%20%') for x in value
                ])
            sect[key] = value

        logger.info('project information')
        for key, value in cfg.items(sectname):
            if key in ('src',):
                value = relpath(value)
            logger.info('%-20s: %s', key, value)

        makedirs(ctx.local_path, exist_ok=True)
        with open(ctx.local_config, 'w') as f:
            cfg.write(f)
        logger.info('project saved')

    def cmd_build(self, ctx, args):
        """Obfuscate all scripts, modules and packages in project

        Show project information:

            pyarmor i

        Generate plain scripts which no extra extension, the final
        scripts could be taken as input for Nuitka, Cython etc.:

            pyarmor build --rft

        Generate high performance scripts:

            pyarmor build --mini

        """
        logger.debug('build %s', args)
        cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation(),
        )
        cfg.read([ctx.local_config], encoding=ctx.encoding)

        sectname = 'project'
        if not cfg.has_section(sectname):
            raise CliError('no project information')

        cfgdata = dict(cfg.items(sectname))
        logger.debug('project: %s', cfgdata)

        project = Project(ctx)
        logger.info('load project ...')
        project.load(cfgdata)
        logger.info('load project end')

        if args.target == 'list':
            logger.info('project src: %s', relpath(project.src))
            logger.info('project scripts:')
            for x in project.scripts:
                logger.info('  %s', project.relsrc(x.abspath))
            logger.info('project modules:')
            for x in project.modules:
                logger.info('  %s', project.relsrc(x.abspath))
            logger.info('project packages:')
            for x in project.packages:
                logger.info('  %s', x.name)
                mlist = [m.abspath for m in project.iter_module()]
                mlist.sort()
                for s in mlist:
                    logger.info('    %s', project.relsrc(s))
            return

        if args.autofix is not None:
            value = args.autofix
            logger.info('build auto-fix-table:%s ...', value)
            output = args.output if args.output else 'dist'
            self._build(project, 'autofix', output, value)
            logger.info('build auto-fix-table:%s end', value)
        elif args.randname is not None:
            value = args.randname
            logger.info('build rand-pool:%s ...', value)
            output = args.output if args.output else 'dist'
            self._build(project, 'namepool', output, value)
            logger.info('build rand-pool:%s end', value)
        else:
            logger.info('build target %s ...', args.target)
            output = args.output if args.output else 'dist'
            self._build(project, args.target, output)
            logger.info('build target %s end', args.target)

    def _build(self, project, target, output, value=None):
        from .core import Pytransform3
        args = [self.ctx, target, project, output, value]
        m = Pytransform3.init(self.ctx)
        m.pre_build(args)

    def cmd_env(self, ctx, args):
        """Check and change pyarmor settings

        Enter interactive mode:

            pyarmor env

        Show project src

           pyarmor env -p get src

        Change project src

           pyarmor env -p set src ../src

        Append project excludes

           pyarmor env -p push excludes "test*"

        Remove project excludes

           pyarmor env -p pop excludes "test*"

        Clear project excludes

           pyarmor env -p reset excludes

        """
        logger.debug('env %s', args)
        logger.info('enter domain: %s', args.domain)
        shell = PyarmorShell(ctx, domain=args.domain)

        if args.exprs:
            exprs = args.exprs
            n = len(exprs)
            if n < 2:
                logger.error('missing parameters')
                return

            verb = exprs[0]
            opt = exprs[1]

            i = opt.find(':')
            if i > 0:
                section, opt = opt[:i], opt[i+1:]
                shell.do_cd(section)

            if verb == 'reset':
                shell.do_reset(opt)
            elif verb == 'get':
                shell.do_get(opt)
            elif verb == 'info':
                shell.do_info(opt)
            elif n < 3:
                logger.error('missing parameters')
                return
            else:
                arg = shlex.join([opt] + exprs[2:])
                if verb == 'pop':
                    shell.do_pop(arg)
                elif verb == 'push':
                    shell.do_push(arg)
                elif verb == 'set':
                    shell.do_set(arg)
                else:
                    logger.error('unknown verb "%s"', verb)
                    return

            shell.save()

        else:
            shell.cmdloop()


def test_main(args, target='rft', log=False):
    import logging.config
    from os.path import expanduser

    from .context import Context
    from .rftbuild import rft_build_project

    home = joinpath('~', '.pyarmor')
    home = abspath(expanduser(home))

    ctx = Context(home)
    if log:
        logging.config.fileConfig(ctx.default_config)
    cmd = Commander()
    cmd._build = rft_build_project
    cmd.run(ctx, args)


if __name__ == '__main__':
    import sys
    test_main(sys.argv[1:], log=True)
