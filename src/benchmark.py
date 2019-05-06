#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2013 - 2017 Dashingsoft corp.            #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 1.7.0 - 3.4.0                               #
#                                                           #
#############################################################
#
#
#  @File: benchmark.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2017/11/21
#
#  @Description:
#
#   Check performance of pyarmor.
#
import logging
import os
import shutil
import sys
import subprocess
import time

from ctypes import c_int, c_void_p, py_object, pythonapi, PYFUNCTYPE

import pytransform

OBF_MODULE_MODE = 'none', 'des'
OBF_CODE_MODE = 'none', 'des', 'fast', 'wrap'

PYARMOR_PATH = os.path.dirname(__file__)
PYARMOR = 'pyarmor.py'


def make_test_script(filename):
    lines = [
        'def empty():',
        '  return 0',
        '',
        'def one_thousand():',
        '  if False:',
        '    i = 0',
    ]
    lines.extend(['    i += 1'] * 100)
    lines.append('\n  return 1000\n')
    lines.extend(['def ten_thousand():',
                  '  if False:',
                  '    i = 0'])
    lines.extend(['    i += 1'] * 1000)
    lines.append('\n  return 10000\n')

    with open(filename, 'wb') as f:
        f.write('\n'.join(lines).encode())


def call_pyarmor(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()


def obffuscate_scripts(output, filename, module_mode, code_mode, wrap_mode):
    project = os.path.join(output, 'project')
    if os.path.exists(project):
        shutil.rmtree(project)

    args = [sys.executable, PYARMOR, 'init', '--src', output,
            '--entry', filename, project]
    call_pyarmor(args)

    args = [sys.executable, PYARMOR, 'config',
            '--manifest', 'include %s' % filename,
            '--obf-mod', module_mode,
            '--obf-code', code_mode,
            '--wrap-mode', wrap_mode,
            project]
    call_pyarmor(args)

    args = [sys.executable, PYARMOR, 'build', project]
    call_pyarmor(args)

    for s in os.listdir(os.path.join(project, 'dist')):
        shutil.copy(os.path.join(project, 'dist', s), output)


def metricmethod(func):
    if not hasattr(time, 'process_time'):
        time.process_time = time.clock

    def wrap(*args, **kwargs):
        t1 = time.process_time()
        result = func(*args, **kwargs)
        t2 = time.process_time()
        logging.info('%s: %s ms', func.__name__, (t2 - t1) * 1000)
        return result
    return wrap


@metricmethod
def verify_license(m):
    try:
        prototype = PYFUNCTYPE(py_object)
        dlfunc = prototype(('get_registration_code', m))
        code = dlfunc()
    except Exception:
        logging.warning('Verify license failed')
        code = ''
    return code


@metricmethod
def init_pytransform(m):
    major, minor = sys.version_info[0:2]
    # Python2.5 no sys.maxsize but sys.maxint
    # bitness = 64 if sys.maxsize > 2**32 else 32
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_void_p)
    init_module = prototype(('init_module', m))
    init_module(major, minor, pythonapi._handle)

    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_int)
    init_runtime = prototype(('init_runtime', m))
    init_runtime(0, 0, 0, 0)


@metricmethod
def load_pytransform():
    return pytransform._load_library(PYARMOR_PATH)


@metricmethod
def total_extra_init_time():
    m = load_pytransform()
    init_pytransform(m)
    verify_license(m)


@metricmethod
def import_no_obfuscated_module(name):
    return __import__(name)


@metricmethod
def import_obfuscated_module(name):
    return __import__(name)


@metricmethod
def re_import_no_obfuscated_module(name):
    return __import__(name)


@metricmethod
def re_import_obfuscated_module(name):
    return __import__(name)


@metricmethod
def run_empty_obfuscated_code_object(foo):
    return foo.empty()


@metricmethod
def run_one_thousand_obfuscated_bytecode(foo):
    return foo.one_thousand()


@metricmethod
def run_ten_thousand_obfuscated_bytecode(foo):
    return foo.ten_thousand()


@metricmethod
def run_empty_no_obfuscated_code_object(foo):
    return foo.empty()


@metricmethod
def run_one_thousand_no_obfuscated_bytecode(foo):
    return foo.one_thousand()


@metricmethod
def run_ten_thousand_no_obfuscated_bytecode(foo):
    return foo.ten_thousand()


def main():
    if not os.path.exists('benchmark.py'):
        logging.warning('Please change current path to %s', PYARMOR_PATH)
        return

    output = '.benchtest'
    name = 'bfoo'
    filename = os.path.join(output, name + '.py')

    obname = 'obfoo'
    obfilename = os.path.join(output, obname + '.py')

    if len(sys.argv) > 1 and 'bootstrap'.startswith(sys.argv[1]):
        if len(sys.argv) < 5:
            sys.argv.extend(['1', '1', '1'])
        obf_mod, obf_code, wrap_mode = sys.argv[2:5]

        if not os.path.exists(output):
            logging.info('Create output path: %s', output)
            os.makedirs(output)
        else:
            logging.info('Output path: %s', output)

        logging.info('Generate test script %s ...', filename)
        make_test_script(filename)

        logging.info('Obffuscate test script ...')
        shutil.copy(filename, obfilename)
        obffuscate_scripts(output, os.path.basename(obfilename),
                           obf_mod, obf_code, wrap_mode)
        if not os.path.exists(obfilename):
            logging.info('Something is wrong to obsfucate the script')
            return
        logging.info('Generate obffuscated script %s', obfilename)

        logging.info('Copy benchmark.py to %s', output)
        shutil.copy('benchmark.py', output)

        logging.info('')
        logging.info('Now change to "%s"', output)
        logging.info('Run "%s benchmark.py".', sys.executable)
        return

    filename = os.path.basename(filename)
    if os.path.exists(filename):
        logging.info('Test script: %s', filename)
    else:
        logging.warning('Test script: %s not found', filename)
        logging.info('Run "%s benchmark.py bootstrap" first.', sys.executable)
        return

    obfilename = os.path.basename(obfilename)
    if os.path.exists(obfilename):
        logging.info('Obfuscated script: %s', obfilename)
    else:
        logging.warning('Obfuscated script: %s not found', obfilename)
        logging.info('Run "%s benchmark.py bootstrap" first.', sys.executable)
        return

    logging.info('--------------------------------------')

    logging.info('')
    total_extra_init_time()

    logging.info('')
    foo = import_no_obfuscated_module(name)
    obfoo = import_obfuscated_module(obname)

    logging.info('')
    foo = re_import_no_obfuscated_module(name)
    obfoo = re_import_obfuscated_module(obname)

    logging.info('')
    run_empty_no_obfuscated_code_object(foo)
    run_empty_obfuscated_code_object(obfoo)

    logging.info('')
    run_one_thousand_no_obfuscated_bytecode(foo)
    run_one_thousand_obfuscated_bytecode(obfoo)

    logging.info('')
    run_ten_thousand_no_obfuscated_bytecode(foo)
    run_ten_thousand_obfuscated_bytecode(obfoo)

    logging.info('')
    logging.info('--------------------------------------')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
    )
    main()
