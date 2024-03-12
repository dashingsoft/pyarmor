#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2024 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      Pyarmor                                              #
#                                                           #
#      Version: 8.5.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/bug.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Tue Mar 12 15:19:41 CST 2024
#
from string import Template

BUG_TEMPLATE = Template('''
### Command options and console output
$cmdline

$tracelog

### Traceback
$tb
''')


def generate_bug_report(e):
    'Generate file `pyarmor.report.bug` in current path'
    from os.path import exists
    from sys import argv
    from traceback import format_exc

    logfile = '.pyarmor/pyarmor.debug.log'
    if exists(logfile):
        with open('.pyarmor/pyarmor.debug.log', 'r') as f:
            tracelog = f.read()

    with open('pyarmor.report.bug', 'w') as f:
        f.write(BUG_TEMPLATE.substitute(
            cmdline=' '.join(argv),
            tracelog=tracelog,
            tb=format_exc()
        ))


def find_solutions(logger, e):
    '''Print quick solutions according to exception

    If not enable debug, tell user try `pyarmor -d cmd...`

    If it raises CliError, print possible solutions

    For unknown error, print FAQ page link and `pyarmor man`

    Pyarmor Man is designed to help Pyarmor users to learn
    and use Pyarmor by web-ui, to find solution quickly when
    something is wrong, to report bugs and ask questions in
    standard form in order to save both Pyarmor team's and
    Pyarmor users' time.
    '''
    generate_bug_report(e)

    # debug = logging.getLogger().getEffectiveLevel()
    # clierr = isinstance(e, CliError)
    logger.error('''somthing is wrong
*=============================================================*
*  Please check                                               *
*    https://pyarmor.readthedocs.io/en/latest/questions.html  *
*  or run `pyarmor man` to find solutions quickly             *
*                                                             *
*  It's recommand to report issue by `pyarmor man` in order   *
*  to provide necessary information, and avoid dupcliated     *
*  issues or unclear question.                                *
*=============================================================*
''')


if __name__ == '__main__':
    pass
