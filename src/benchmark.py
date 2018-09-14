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
import tempfile
import time

from ctypes import cdll, c_int, c_void_p, py_object, pythonapi, PYFUNCTYPE
from ctypes.util import find_library

PYARMOR = 'pyarmor-deprecated.py'

def metricmethod(func):
    def wrap(*args, **kwargs):
        t1 = time.clock()
        result = func(*args, **kwargs)
        t2 = time.clock()
        logging.info('%s: %s ms', func.__name__, (t2 - t1) * 1000)
        return result
    return wrap

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

@metricmethod
def verify_license(pytransform):
    try:
        prototype = PYFUNCTYPE(py_object)
        dlfunc = prototype(('get_registration_code', pytransform))
        code = dlfunc()
    except Exception:
        logging.warning('Verify license failed')
        code = ''
    return code

@metricmethod
def init_pytransform(pytransform):
    major, minor = sys.version_info[0:2]
    # Python2.5 no sys.maxsize but sys.maxint
    # bitness = 64 if sys.maxsize > 2**32 else 32
    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_void_p)
    init_module = prototype(('init_module', pytransform))
    init_module(major, minor, pythonapi._handle)

    prototype = PYFUNCTYPE(c_int, c_int, c_int, c_int)
    init_runtime = prototype(('init_runtime', pytransform))
    init_runtime(0, 0, 0, 0)

@metricmethod
def load_pytransform():
    try:
        if sys.platform.startswith('linux'):
            m = cdll.LoadLibrary(os.path.abspath('_pytransform.so'))
            m.set_option('libc'.encode(), find_library('c').encode())
        elif sys.platform.startswith('darwin'):
            m = cdll.LoadLibrary('_pytransform.dylib')
        else:
            m = cdll.LoadLibrary('_pytransform.dll')
    except Exception:
        raise RuntimeError('Could not load library _pytransform.')
    return m

@metricmethod
def import_no_obfuscated_module(name):
    return __import__(name)

@metricmethod
def import_obfuscated_module(name):
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

def check_output(output):
    if not os.path.exists(output):
        logging.info('Create output path: %s', output)
        os.makedirs(output)
    else:
        logging.info('Output path: %s', output)

def obffuscate_python_scripts(output, filename, mode=None):
    args = [sys.executable, PYARMOR, 'encrypt']
    if mode is not None:
        args.extend(['--mode', mode])
    args.extend(['-O', output, filename])
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

    # Generate license with no restrict mode
    licfile = os.path.join(output, 'license.lic')
    args = [sys.executable, PYARMOR, 'license',
            '-O', licfile, '*FLAGS:A*CODE:Benchmark' ]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

def check_default_capsule():
    if not os.path.exists(PYARMOR):
        return
    capsule = 'project.zip'
    if os.path.exists(capsule):
        logging.info('Use capsule: %s', capsule)
        return

    p = subprocess.Popen([sys.executable, PYARMOR, 'capsule'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

def main():
    check_default_capsule()

    time.clock()
    pytransform = load_pytransform()
    init_pytransform(pytransform)
    verify_license(pytransform)

    logging.info('')

    output = '.benchtest'
    name = 'bfoo'
    filename = os.path.join(output, name + '.py')

    mode = sys.argv[2] if len(sys.argv) > 2 else '8'
    ext = '' if mode in ('7', '8', '9', '10', '11', '12', '13', '14') else 'e'

    obname = 'obfoo'
    obfilename = os.path.join(output, obname + '.py' + ext)

    if len(sys.argv) > 1 and 'bootstrap'.startswith(sys.argv[1]):
        check_output(output)
        logging.info('Generate test script %s ...', filename)
        make_test_script(filename)
        logging.info('Test script %s has been generated.', filename)
        if mode not in ('3', '5', '6', '7', '8',
                        '9', '10', '11', '12', '13', '14'):
            logging.warning('Unsupport mode %s, use default mode 8', mode)
            mode = '8'
        logging.info('Obffuscate test script with mode %s...', mode)
        obffuscate_python_scripts(output, filename, mode)
        if not os.path.exists(os.path.join(output, filename + ext)):
            logging.info('Something is wrong to obsfucate %s.', filename)
            return
        shutil.move(os.path.join(output, filename + ext), obfilename)
        logging.info('Generate obffuscated script %s', obfilename)

        logging.info('Copy benchmark.py to %s', output)
        with open('benchmark.py') as f:
            lines = f.read()
        with open(os.path.join(output, 'benchmark.py'), 'w') as f:
            f.write(lines.replace("else '8'", "else '%s'" % mode))
        # shutil.copy('benchmark.py', output)
        logging.info('')
        logging.info('Now change to "%s"', output)
        logging.info('Run "%s benchmark.py".', sys.executable)
        return

    if os.path.exists(os.path.basename(filename)):
        logging.info('Test script: %s', os.path.basename(filename))
    else:
        logging.warning('Test script: %s not found', os.path.basename(filename))
        logging.info('Run "%s benchmark.py bootstrap" first.', sys.executable)
        return

    if os.path.exists(os.path.basename(obfilename)):
        logging.info('Obfuscated script: %s', os.path.basename(obfilename))
    else:
        logging.warning('Obfuscated script: %s not found', os.path.basename(obfilename))
        logging.info('Run "%s benchmark.py bootstrap" first.', sys.executable)
        return

    logging.info('Start test with mode %s', mode)
    logging.info('--------------------------------------')

    logging.info('')
    foo = import_no_obfuscated_module(name)
    obfoo = import_obfuscated_module(obname)

    logging.info('')
    run_empty_no_obfuscated_code_object(foo)
    run_empty_obfuscated_code_object(obfoo)

    logging.info('')
    run_one_thousand_no_obfuscated_bytecode(foo)
    run_one_thousand_obfuscated_bytecode(obfoo)

    logging.info('')
    run_ten_thousand_no_obfuscated_bytecode(foo)
    run_ten_thousand_obfuscated_bytecode(obfoo)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
    )
    main()
