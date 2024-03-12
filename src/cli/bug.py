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

def generate_bug_report(e):
    'Generate file `pyarmor.report.bug` in current path'
    pass


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
