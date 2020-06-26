#! /usr/bin/env python
'''This script could create a python module from data file, so that
the data file could be protected by PyArmor.

1. First create data module from date file by this script

    python build_data_module.py data.txt > data.py

    Or

    python -m pyarmor.helper.build_data_module data.txt > data.py

2. Next obfuscate this data module with restrict mode 4

    pyarmor obfuscate --exact --restrict 4 --no-runtime data.py

After that, use the data file in other obfuscated scripts. For example,

    import data

    # Here load the content of data file to memory variable "text"
    # And clear it from memory as exiting the context
    with data.Safestr() as text:
        ...

This script encodes the string data by a simple way (xor), DO NOT
generate data module by this script directly. It's recommend to write
your own script to generate data module base on it or not.

'''
import argparse
import logging
import random
import sys

from os import makedirs
from os.path import basename, exists, join as join_path, splitext

#
# The template of data module
#
# Do not yield key directly, because generator will not be obfuscated
#
template = '''
def index(n):
    rlist = range(n)
    while 1:
        for x in rlist:
            yield x


class Safestr(object):

    def __enter__(self):
        key = {key}
        i = index(len(key))
        data = bytearray([x ^ key[next(i)] for x in bytearray(b"\\x{data}")])
        self._value = data.decode({encoding})
        return self._value

    def __exit__(self, exc_type, exc_value, exc_tb):
        del self._value

'''


def key(xlist):
    while 1:
        for x in xlist:
            yield x


def build_module(filename, keylen=32, encoding=''):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())
    keylist = [random.randint(0, 255) for i in range(keylen)]

    k = key(keylist)
    s = r'\x'.join(['%02x' % (x ^ next(k)) for x in data])
    return template.format(data=s, key=str(keylist), encoding=encoding)


def main(argv):
    parser = argparse.ArgumentParser(
        prog='build-data-module',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Build data module from data file',
    )
    parser.add_argument('-n', '--key', default=32, type=int,
                        help='length of key list used to xor data')
    parser.add_argument('-c', '--encoding', help='encoding of data file')
    parser.add_argument('-f', '--force', action='store_true',
                        help='overwrite the exists module file')
    parser.add_argument('-O', '--output', metavar='PATH',
                        help='write data module here other than stdout')
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='data files')

    args = parser.parse_args(argv)
    encoding = repr(args.encoding) if args.encoding else ''

    if args.output:
        if not exists(args.output):
            logging.info('Make output path: %s', args.output)
            makedirs(args.output)

        def output(filename, code):
            name = splitext(basename(filename))[0] + '.py'
            target = join_path(args.output, name)
            if exists(target) and not args.force:
                raise RuntimeError('Data module "%s" exists' % target)
            logging.info('Write data module to "%s"', target)
            with open(target, 'w') as f:
                f.write(code)
    else:
        def output(filename, code):
            print(code)

    random.seed()
    for filename in args.files:
        code = build_module(filename, keylen=args.key, encoding=encoding)
        output(filename, code)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main(sys.argv[1:])
