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
#      Version: 8.4.6 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/hdinfo.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Fri Dec 15 09:27:30 CST 2023
#
import argparse
import sys

from pyarmor.cli.core import Pytransform3


GROUP_LICENSE_MACHINE_FLAG = 22
HT_HARDDISK, HT_IFMAC, HT_IPV4, HT_IPV6, HT_DOMAIN = range(5)


def get_hd_info(hdtype, name=None):
    try:
        return repr(Pytransform3.get_hd_info(hdtype, name))
    except Exception as e:
        return str(e)


def get_all_ifmac():
    try:
        buf = Pytransform3.get_hd_info(HT_IFMAC, name='*')
        i = 0
        n = len(buf)
        rlist = []
        while i < n and buf[i]:
            j = i + 1 + buf[i]
            rlist.append(':'.join(['%02x' % x for x in buf[i+1:j]]))
            i = j
    except Exception as e:
        return str(e)

    return '<%s>' % ','.join(set(rlist))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('devname', nargs='*', help=(
        'In Linux get netcard name like "eth0" '
        'or harddisk name like "/dev/sda"'))
    args = parser.parse_args(argv)

    print('Machine ID: %s' % get_hd_info(GROUP_LICENSE_MACHINE_FLAG)[1:])

    if not args.devname:
        print('Default Harddisk Serial Number: %s' % get_hd_info(HT_HARDDISK))
        print('Default Mac address: %s' % get_hd_info(HT_IFMAC))
        print('Default IPv4 address: %s' % get_hd_info(HT_IPV4))
        print('Multiple Mac addresses: %s' % get_all_ifmac())
        print('Domain: %s' % get_hd_info(HT_DOMAIN))

    for name in args.devname:
        if name.startswith('/'):
            print('Query Harddisk "%s" Serial Number: %s' %
                  (name, get_hd_info(HT_HARDDISK, name=name)))
        else:
            print('Query Netcard "/dev/%s" Mac Address: %s' %
                  (name, get_hd_info(HT_IFMAC, name=name)))


if __name__ == '__main__':
    main(sys.argv[1:])
