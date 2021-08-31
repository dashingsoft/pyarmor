'''This tool is used to merge the scripts obfuscated by different
Python versions into one obfuscated script.

For example,

1. First obfuscate the scripts by Python 2.7

    python2.7 pyarmor.py obfuscate -O py27 foo.py

2. Then obfuscate the scripts by Python 3.8

    python3.8 pyarmor.py obfuscate -O py38 foo.py

3. Run this tool to merge all of them to path `merged_dist`

    python merge.py py38/ py27/

If also possible to merge one script, for example:

    python merge.py py27/foo.py py36/foo.py py35/foo.py

'''
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
    n = 0
    with open(filename) as f:
        for s in f.readlines():
            if s.startswith('__pyarmor') or s.startswith('pyarmor('):
                fs = s[s.find('__file__'):s.rfind(')')].split(', ')
                code = eval(fs[-2])
                flag = int(fs[-1])
                break
            n += 1
        else:
            return None, None, None, None

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


def merge_scripts(scripts, output):
    refscript = scripts.pop(0)
    logger.info('Parse reference script %s', refscript)
    refn, reflag, refcode, refinfos = parse_script(refscript)

    if refcode is None:
        logger.info('Ignore this script, it is not obfuscated')
        return

    merged_vers = []
    pieces = []

    for script in reversed(scripts):
        logger.info('Parse script %s', script)
        n, flag, code, pyinfos = parse_script(script)
        if code is None:
            raise RuntimeError('This script is not an obfuscated script')
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


def merge_runtimes(paths, output):
    runtimes = []
    pyvers = []
    refpath = os.path.normpath(paths[-1])

    n = len(refpath) + 1
    for root, dirs, files in os.walk(refpath):
        if os.path.basename(root).startswith('pytransform'):
            runtimes.append(root[n:])

        for x in files:
            if x.startswith('pytransform'):
                runtimes.append(os.path.join(root, x)[n:])
            elif is_pyscript(x) and not pyvers:
                name = os.path.join(root, x)[n:]
                for p in paths:
                    pyinfos = parse_script(os.path.join(p, name))[-1]
                    if pyinfos is None:
                        pyvers = []
                        break
                    if len(pyinfos) > 1:
                        raise RuntimeError('The runtime file in %s is merged'
                                           % p)
                    pyvers.append(pyinfos[0][-1])

    logger.debug('Found runtimes: %s', runtimes)
    if not runtimes:
        raise RuntimeError('No runtime files found')
    elif len(runtimes) > 1:
        raise RuntimeError('Too many runtime files')

    logger.debug('Found python versions: %s', pyvers)
    if not pyvers:
        raise RuntimeError('Could not get python version of runtime files')

    r = os.path.join(refpath, runtimes[0])
    if os.path.isdir(r):
        logger.info('Copy non-super mode runtime package %s', r)
        dst = os.path.join(output, runtimes[0])
        logger.info('To %s', dst)
        makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(r, dst)
        return

    pkgname = os.path.basename(r).rsplit('.', 1)[0]
    pkgpath = os.path.join(output, pkgname)
    makedirs(pkgpath, exist_ok=True)

    src = os.path.join(pkgpath, '__init__.py')
    logger.info('Create super runtime package: %s', src)
    with open(src, 'w') as f:
        f.write(
            "import sys\n"
            "sys.modules[__name__].__dict__.update("
            "__import__('.'.join("
            "[__name__, 'py%s%s' % sys.version_info[:2], __name__]),"
            " globals(), locals(), ['*']).__dict__)"
        )

    for p, (major, minor) in zip(paths, pyvers):
        src = os.path.join(p, runtimes[0])
        dst = os.path.join(pkgpath,  'py%s%s' % (major, minor))
        logger.info('Copy %s to %s', src, dst)
        makedirs(dst, exist_ok=True)
        shutil.copy2(src, dst)

        logger.debug('Create package file "%s/__init__.py"', dst)
        with open(os.path.join(dst, '__init__.py'), 'w') as f:
            f.write('')


def find_scripts(paths):
    names = []

    refpath = os.path.normpath(paths[-1])
    logger.info('Find scripts in the path %s', refpath)

    n = len(refpath) + 1
    for root, dirs, files in os.walk(refpath):
        for x in files:
            if not is_pyscript(x):
                continue

            scripts = [os.path.join(root, x)]
            names.append(scripts[0][n:])

    return names


def excepthook(type, exc, traceback):
    try:
        msg = exc.args[0] % exc.args[1:]
    except Exception:
        msg = str(exc)
    logging.error(msg)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='pyarmor merge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)

    parser.add_argument('-O', '--output',
                        default='merged_dist',
                        help='Default output path: %(default)s)')
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

    logger.info('Merge %s...', str(args.path)[1:-1])
    output = args.output

    if os.path.isfile(args.path[0]):
        output = output if is_pyscript(output) \
            else os.path.join(output, os.path.basename(args.path[0]))

        merge_scripts(args.path, output)

    else:
        if output and is_pyscript(output):
            raise RuntimeError('--output must be a path when mergeing path')

        logging.info('Merging obfuscated scripts...')
        for name in find_scripts(args.path):
            merge_scripts([os.path.join(p, name) for p in args.path],
                          os.path.join(output, name))
        logging.info('Merging obfuscated scripts OK')

        logging.info('Merging runtime files...')
        merge_runtimes(args.path, output)
        logging.info('Merging runtime files OK')

    logger.info('Merge all the scripts to %s successfully', output)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main()
