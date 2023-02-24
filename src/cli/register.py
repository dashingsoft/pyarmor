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
#      Version: 8.0.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/register.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Mon Jan  2 15:39:08 CST 2023
#
import logging

from string import Template


logger = logging.getLogger('Pyarmor')


def parse_token(data):
    from base64 import b64decode
    from struct import unpack

    if not data or data.find(' ') == -1:
        return {
            'token': 0,
            'rev': 0,
            'features': 0,
            'licno': 'pyarmor-vax-000000',
            'regname': '',
            'product': '',
            'note': 'This is trial license'
        }

    buf = b64decode(data.split()[0])

    token, value = unpack('II', buf[:8])
    rev, features = value & 0xff, value >> 8
    licno = unpack('20s', buf[16:36]).decode('utf-8')

    pstr = []
    i = 64
    for k in range(4):
        n = buf[i]
        i += 1
        pstr.append(buf[i:i+n].decode('utf-8'))
        i += n

    return {
        'token': token,
        'rev': rev,
        'features': features,
        'licno': licno,
        'machine': pstr[0],
        'regname': pstr[1],
        'product': pstr[2],
        'note': pstr[3],
    }


class Register(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def check_args(self, args):
        if args.upgrade and args.keyfile.endswith('.zip'):
            raise RuntimeError('use .txt file to upgrade, not .zip file')

    def regurl(self, ucode, upgrade=False):
        url = self.ctx.cfg['pyarmor']['regurl'] % ucode
        if upgrade:
            url += '&upgrade=1'
        return url

    @property
    def license_info(self):
        return parse_token(self.ctx.read_token())

    def _license_type(self, info):
        return 'basic' if info['features'] == 1 else \
            'pro' if info['features'] == 7 else \
            'trial' if info['token'] == 0 else 'unknown'

    def _license_to(self, info):
        name = info['regname']
        product = info['product']
        return '%s - %s' % (name, product) if name and product else \
            '' if not name else '%s - %s' % (name, 'non-profits')

    def parse_keyfile(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                marker = 'Dear '
                if line.startswith(marker):
                    regname = line[len(marker):].strip(' ,')
                    break

            for line in f:
                line = line.strip()
                if len(line) == 192 and line.find(' ') == -1:
                    return regname, line

        raise RuntimeError('no registration code found in %s' % filename)

    def __str__(self):
        '''$advanced

Notes
* Internet connection is required to verify Pyarmor license
$limitations
'''

        info = self.license_info
        lictype = self._license_type(info)

        fmt = '%-16s: %s'
        lines = [
            fmt % ('License Type', 'pyarmor-' + lictype),
            fmt % ('License No.', info['licno']),
            fmt % ('License To', self._license_to(info)),
            '',
        ]

        bccmode = info['features'] & 2
        rftmode = info['features'] & 4
        advanced = [
            fmt % ('BCC Mode', 'Yes' if bccmode else 'No'),
            fmt % ('RFT Mode', 'Yes' if rftmode else 'No'),
        ]
        limitations = []
        if lictype == 'trial':
            limitations.append('* Trial license can\'t obfuscate big script')

        lines.append(Template(self.__str__.__doc__).substitute(
            advanced='\n'.join(advanced),
            limitations='\n'.join(limitations),
        ))

        return '\n'.join(lines)


class LocalRegister(Register):

    def upgrade(self, keyfile, regname, product):
        pass

    def register(self, keyfile, regname, product):
        pass


class RealRegister(Register):

    def _request_license_info(self):
        from .core import Pytransform3
        return Pytransform3.get_license_info(self.ctx)

    def _send_request(self, url, timeout=6.0):
        from urllib.request import urlopen
        from ssl import _create_unverified_context
        context = _create_unverified_context()
        return urlopen(url, None, timeout, context=context)

    def _register_regfile(self, regfile):
        from zipfile import ZipFile
        path = self.ctx.home_path
        with ZipFile(regfile, 'r') as f:
            for item in ('license.lic', '.pyarmor_capsule.zip'):
                logger.debug('extracting %s' % item)
                f.extract(item, path=path)

    def upgrade(self, keyfile, regname, product):
        reginfo = self.parse_keyfile(keyfile)
        url = self.regurl(reginfo[1])
        res = self._request_license_info(url)
        if res and res.code == 200:
            self._request_license_info()
        elif res:
            raise RuntimeError(res.read().decode())

        raise RuntimeError('no response from license server')

    def register(self, keyfile, regname, product):
        if keyfile.endswith('.zip'):
            self._register_regfile(keyfile)
            return

        reginfo = self.parse_keyfile(keyfile)
        url = self.regurl(reginfo[1])
        res = self._request_license_info(url)
        regfile = self._handle_response(res)
        self._register_regfile(regfile)
        self._request_license_info()

    def _handle_response(self, res):
        if res and res.code == 200:
            dis = res.headers.get('Content-Disposition')
            filename = dis.split('"')[1] if dis else 'pyarmor-regfile.zip'
            with open(filename, 'wb') as f:
                f.write(res.read())
            return filename

        elif res:
            raise RuntimeError(res.read().decode())

        raise RuntimeError('no response from license server')
