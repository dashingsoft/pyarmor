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


#############################################################
#                                                           #
# Deprecated since Pyarmor 9, use `pyarmor man` instead     #
#                                                           #
#############################################################

import logging

from string import Template

BUG_FILE, LOG_FILE = 'pyarmor.report.bug', '.pyarmor/pyarmor.debug.log'

BUG_TEMPLATE = Template('''[Bug] $title

### Full command options and console output
$cmdline

$tracelog

### Traceback
$tb
''')

UNUSED_ENABLE_DEBUG_HINTS = '''something is wrong
*=============================================================*
*  Please enable debug option `-d` to run it again            *
*    pyarmor -d gen options ...                               *
*                                                             *
*  Then check console log to find more information            *
*                                                             *
*  Please also check                                          *
*    https://pyarmor.readthedocs.io/en/latest/questions.html  *
*=============================================================*
'''

UNUSED_SOLUTION_HINTS = Template('''something is wrong
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

ENABLE_DEBUG_HINTS = 'please enable debug option `-d` to run it again'

SOLUTION_HINTS = Template('''
*=============================================================*
*  Please check console log to find out what's wrong          *
*                                                             *
*  If still not solved, please find solutions by              *
*    https://pyarmor.readthedocs.io/en/latest/questions.html  *
*=============================================================*
''')


def generate_bug_report(e, logfile=LOG_FILE, output=BUG_FILE):
    'Generate file `pyarmor.report.bug` in current path'
    from os.path import exists
    from sys import argv
    from traceback import format_exc

    if exists(logfile):
        with open(logfile, 'r') as f:
            lines = f.readlines()
            n = len(lines)
            if n > 128:
                tracelog = ''.join(lines[:100] + ['...\n'] + lines[n-20:n])
            else:
                tracelog = ''.join(lines[:n])
    else:
        tracelog = Template(
            'TODO: no found logfile "$logfile", please paste console log '
            'here manually').substitute(logfile=logfile)

    title = '%s: %s' % (type(e).__name__, str(e))
    with open(output, 'w') as f:
        f.write(BUG_TEMPLATE.substitute(
            title=title,
            cmdline=' '.join(argv),
            tracelog=tracelog,
            tb=format_exc()
        ))


def find_solutions(e):
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
    logger = logging.getLogger()
    if logger.getEffectiveLevel() > logging.DEBUG:
        return

    print('\nDebug Information:')
    logger.info('generate bug file "%s"', BUG_FILE)
    generate_bug_report(e)
    logger.info(SOLUTION_HINTS.substitute(bugfile=BUG_FILE))


if __name__ == '__main__':
    pass
