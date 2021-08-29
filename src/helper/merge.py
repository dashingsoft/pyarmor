'''This tool is used to merge the scripts obfuscated by different
Python versions into one obfuscated script.

For example,

1. First obfuscate the scripts by Python 2.7

    python2.7 pyarmor.py obfuscate --output dist/py27 foo.py

2. Then obfuscate the scripts by Python 3.8

    python3.8 pyarmor.py obfuscate --output dist/py38 foo.py

3. Run this tool to merge all of them

    python merge.py -O dist dist/py38/ dist/py27/

If no option `--output`, the obfuscated scripts in first path will be
updated to save the final merged scripts. For example, this command
will overwrite all the obfuscated scripts in the `dist/py38`:

    python merge.py dist/py38/ dist/py27 dist/py39

If also possible to merge one script, for example:

    python merge.py dist/foo.py dist/py36/foo.py dist/py35/foo.py

'''
import argparse
import logging
import os
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
    n = 0
    with open(filename) as f:
        for s in f.readlines():
            if s.startswith('__pyarmor__(') or s.startswith('pyarmor('):
                fs = s[s.find('__file__'):s.rfind(')')].split(', ')
                code = eval(fs[-2])
                flag = int(fs[-1])
                break
            n += 1
        else:
            raise RuntimeError('This script is not an obfuscated script')

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
        raise RuntimeError('Invalid header in this script')

    return n, flag, code, infos


def merge_scripts(refscript, scripts, output):
    logger.info('Parse reference script %s', refscript)
    refn, reflag, refcode, refinfos = parse_script(refscript)

    merged_vers = []
    pieces = []

    for script in reversed(scripts):
        logger.info('Parse script %s', script)
        n, flag, code, pyinfos = parse_script(script)
        if reflag != flag:
            raise RuntimeError('The script "%s" is obfuscated with '
                               'different way' % script)
        if len(pyinfos) > 1:
            raise RuntimeError('The script "%s" is merged script' % script)

        ver = pyinfos[0][-1]
        logger.debug('\tFound Python %d.%d', *ver)

        if ver in merged_vers:
            logging.warning('\tIngore this Python %d.%d', *ver)
            continue

        logger.debug('\tMerge this Python %d.%d', *ver)
        merged_vers.append(ver)
        pieces.extend([code[:56], struct.pack("i", len(code)), code[60:]])

    logger.debug('Handle reference script %s', refscript)
    for offset, size, ver in refinfos:
        logger.debug('\tFound Python %d.%d', *ver)
        if ver in merged_vers:
            logger.debug('\tIgnore this Python %d.%d', *ver)
            continue
        logger.debug('\tMerge this Python %d.%d', *ver)
        merged_vers.append(ver)
        pieces.append(refcode[offset:offset+size])

    scode = '\\x' + '\\x'.join(['%02x' % c
                                for c in bytearray(b''.join(pieces))])

    with open(scripts[0]) as f:
        lines = f.readlines()

    s = lines[refn]
    i = s.find(', b')
    j = s.rfind(',')
    lines[refn] = s[:i+4] + scode + s[j-1:]

    logger.info('Write merged script: %s', output)
    for ver in merged_vers:
        logger.info('\t* Python %d.%d', *ver)
    makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, 'w') as f:
        f.write(''.join(lines))


def walk_scripts(paths, output=None):
    results = []
    refpath = os.path.normpath(paths[0])

    if os.path.isfile(refpath):
        return [[paths, refpath if output is None else
                 output if is_pyscript(output) else
                 os.path.join(output, os.path.basename(refpath))]]

    if output and is_pyscript(output):
        raise RuntimeError('--output must be a path when mergeing path')

    n = len(refpath) + 1
    for root, dirs, files in os.walk(refpath):
        for x in files:
            if not is_pyscript(x):
                continue

            scripts = [os.path.join(root, x)]
            relname = scripts[0][n:]
            for p in paths[1:]:
                scripts.append(os.path.join(p, relname))
            results.append([scripts, os.path.join(output, relname) if output
                            else scripts[0]])
    return results


def excepthook(type, exc, traceback):
    if hasattr(exc, 'args'):
        try:
            logging.error(exc.args[0], *exc.args[1:])
        except Exception:
            logging.error(", ".join(['%s'] * len(exc.args)), *exc.args)
    else:
        logging.error('%s', exc)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='pyarmor merge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)

    parser.add_argument('-O', '--output',
                        help='Where to save merged script')
    parser.add_argument('-d', '--debug',
                        default=False,
                        action='store_true',
                        dest='debug',
                        help='print debug log (default: %(default)s)')
    parser.add_argument('path', nargs='+',
                        help="Path or obfuscated script")

    args = parser.parse_args(sys.argv[1:])
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        sys.excepthook = excepthook

    for scripts, output in walk_scripts(args.path, args.output):
        merge_scripts(scripts[0], scripts[1:], output)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main()
