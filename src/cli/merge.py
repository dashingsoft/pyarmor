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
#      Version: 8.2.3 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/merge.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Tue May 30 19:35:02 CST 2023
#
import argparse
import logging
import os
import shutil
import struct
import sys

logger = logging.getLogger('merge')


def is_pyscript(filename):
    return os.path.splitext(filename)[-1].lower() in ('.py', '.pyw')


def makedirs(path, exist_ok=False):
    if not (exist_ok and os.path.exists(path)):
        if path:
            os.makedirs(path)


def parse_script(filename):
    with open(filename) as f:
        for line in f:
            if line.startswith('__pyarmor__('):
                i = line.find('(')
                j = line.find(')')
                return line[i+1:j].split(',')


def parse_header(code):
    left_size = len(code)
    offset = 0
    infos = []
    valid = False

    while left_size > 0:
        pymajor, pyminor = struct.unpack("BB", code[offset+9:offset+11])
        size, = struct.unpack("i", code[offset+56:offset+60])
        if not size:
            valid = True
            size = left_size
        left_size -= size
        infos.append([offset, size, (pymajor, pyminor)])
        offset += size

    if not valid:
        raise RuntimeError('invalid header in this script')

    return infos


def merge_script(name, paths, dest):
    scripts = [os.path.join(p, name) for p in paths]

    refscript = scripts.pop(0)
    refitem = parse_script(refscript, reflines)

    if refitem is None:
        logger.info('copy script, it is not obfuscated')
        shutil.copy2(refscript, dest)
        return

    refmark = 'xxxxxx'
    refcode = eval(refcode[-1])
    with open(refscript) as f:
        refdata = f.read().replace(refitem[-1], refmark)

    merged_vers = set()
    pieces = []

    for script in reversed(scripts):
        item = parse_script(script)
        if not item:
            raise RuntimeError('"%s" is not an obfuscated script' % script)
        code = eval(item[-1])
        pieces.extend([code[:56], struct.pack("i", len(code)), code[60:]])

    refinfos = parse_header(refcode)
    for offset, size, ver in refinfos:
        pieces.append(refcode[offset:offset+size])

    with open(dest, 'w') as f:
        f.write(refdata.replace(refmark, repr(b''.join(pieces)))


def merge_scripts(paths, output, runtime_name=None):
    refpath = os.path.normpath(paths[-1])
    rpath = os.path.join(refpath, runtime_name) if runtime_name else None

    n = len(refpath) + 1
    for root, dirs, files in os.walk(refpath):
        for x in files:
            if rpath and root.startswith(rpath):
                continue

            name = root[n:]
            destpath = os.path.join(output, name)
            if not os.path.exists(destpath):
                os.makedirs(destpath)

            dest = os.path.join(destpath, x)
            logger.info('handle "%s"', dest)
            if is_pyscript(x):
                merge_script(os.path.join(name, x), paths, dest)
            else:
                shutil.copy2(os.path.join(root, x), dest)


def merge_runtimes(paths, rname, output):
    dest = os.path.join(output, rname)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)

    shutil.copy2(os.path.join(paths[0], rname, '__init__.py'), dest)

    for p in paths:
        logger.info('handle runtime package at "%s"', p)
        rpath = os.path.join(p, rname)
        if not os.path.exists(rpath):
            raise RuntimeError('no runtime package found')
        for x in os.scandir(rpath):
            if x.is_dir():
                logger.info('copy runtime files "%s"', x.name)
                shutil.copytree(x.path, dest)


def scan_runtime(paths):
    refpath = os.path.normpath(paths[-1])
    logger.info('scan runtime package in the path: %s', refpath)

    n = len(refpath) + 1
    for root, dirs, files in os.walk(refpath):
        for x in files:
            if x == '__init__.py':
                filename = os.path.join(root, x)
                with open(filename) as f:
                    for line in f:
                        if line.startswith('from sys import version_info'):
                            return filename[n:-12]

    raise RuntimeError('no runtime package found')


def excepthook(type, exc, traceback):
    try:
        msg = exc.args[0] % exc.args[1:]
    except Exception:
        msg = str(exc)
    logging.error(msg)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='pyarmor-merge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='merge Pyarmor 8 obfuscated scripts')

    parser.add_argument('-O', '--output',
                        default='merged_dist',
                        help='Default output path: %(default)s)')
    parser.add_argument('-d', '--debug',
                        default=False,
                        action='store_true',
                        dest='debug',
                        help='print debug log (default: %(default)s)')
    group = parser.add_argument_group().add_mutually_exclusive_group()
    group.add_argument('-n', '--no-runtime', action='store_true',
                       help='Ignore runtime files')
    group.add_argument('--runtime-name', help='Runtime package name')
    parser.add_argument('path', nargs='+',
                        help="Paths or obfuscated scripts")

    args = parser.parse_args(sys.argv[1:])
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        sys.excepthook = excepthook

    logger.info('start to merge %s...', str(args.path)[1:-1])
    output = args.output

    runtime_name = args.runtime_name

    if not args.no_runtime:
        if not runtime_name:
            runtime_name = scan_runtime(args.path)
        logger.info('runtime package at "%s"', runtime_name)

        logging.info('merging runtime files...')
        merge_runtimes(args.path, runtime_name, output)
        logging.info('merging runtime files OK')

    logging.info('merging obfuscated scripts...')
    merge_scripts(args.path, runtime_name, output)
    logging.info('merging obfuscated scripts OK')

    logger.info('merge all the scripts to %s successfully', output)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main()
