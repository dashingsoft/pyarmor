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
import os

from base64 import b64decode, urlsafe_b64encode
from json import loads as json_loads
from string import Template

from . import logger, CliError


def parse_token(data):
    from struct import unpack

    if not data or data.find(b' ') == -1:
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
    licno = buf[16:34].decode('utf-8')

    pstr = []
    i = 64
    for k in range(4):
        n = buf[i]
        i += 1
        pstr.append(buf[i:i+n].decode('utf-8') if n else '')
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
        self.notes = []

    def check_args(self, args):
        if args.upgrade and args.keyfile.endswith('.zip'):
            raise CliError('use .txt file to upgrade, not .zip file')

    def _get_old_rcode(self):
        old_license = self.ctx.read_license()
        if not old_license:
            logger.debug('no license file found')
            return
        if len(old_license) == 256:
            logger.debug('no old purchased license')
            return

        data = b64decode(old_license)
        i = data.find(b'pyarmor-vax-')
        if i == -1:
            raise CliError('no valid old license')
        return data[i:i+18].decode()

    def regurl(self, ucode, product=None, rcode=None, prepare=False):
        url = self.ctx.cfg['pyarmor']['regurl'] % ucode
        if product:
            url += '&product=' + \
                urlsafe_b64encode(product.encode('utf-8')).decode()
        if rcode:
            url += '&rcode=' + rcode
        if prepare:
            url += '&prepare=1'
        return url

    def update_token(self):
        from .core import Pytransform3
        with open(self.ctx.license_token, 'wb') as f:
            f.close()
        Pytransform3._update_token(self.ctx)

    @property
    def license_info(self):
        return parse_token(self.ctx.read_token())

    def _license_type(self, info):
        return 'basic' if info['features'] == 1 else \
            'pro' if info['features'] == 7 else \
            'group' if info['features'] == 15 else \
            'trial' if info['token'] == 0 else 'unknown'

    def _license_to(self, info):
        name = info['regname']
        product = info['product']
        return '%s (%s)' % (product, name) if name and product else \
            '' if not name else 'non-profits (%s)' % name

    def parse_keyfile(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
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

        raise CliError('no registration code found in %s' % filename)

    def register_regfile(self, regfile, clean=True):
        from zipfile import ZipFile

        path = self.ctx.reg_path
        with ZipFile(regfile, 'r') as f:
            for item in ('license.lic', '.pyarmor_capsule.zip'):
                logger.debug('extracting %s', item)
                f.extract(item, path=path)
            token_name = os.path.basename(self.ctx.license_token)
            if token_name in f.namelist():
                logger.debug('extracting %s', token_name)
                f.extract(token_name, path=path)
                return
            if 'group.info' in f.namelist():
                raise CliError('wrong usage for group license, please '
                               'check `pyarmor reg` in Man page')

        logger.info('update license token')
        self.update_token()

    def generate_group_device(self, devid):
        from .core import Pytransform3
        machine = Pytransform3.get_hd_info(10)
        filename = os.path.basename(self.ctx.group_device_file(devid))
        with open(filename, "wb") as f:
            f.write(b'machine: ' + machine)
        return filename

    def __str__(self):
        '''$advanced

Notes
$notes
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
        if lictype == 'trial':
            self.notes.append(
                '* Trial license can\'t obfuscate big script and mix str'
            )
        if lictype != 'group':
            self.notes.append(
                '* Internet connection is required to verify Pyarmor license'
            )

        lines.append(Template(self.__str__.__doc__).substitute(
            advanced='\n'.join(advanced),
            notes='\n'.join(self.notes),
        ))

        return '\n'.join(lines)


upgrade_to_basic_info = Template('''
You are about to upgrade old Pyarmor license to Pyarmor Basic License

The upgraded license information will be''')

upgrade_to_pro_info = Template('''
You are about to upgrade old Pyarmor license to Pyarmor Pro License

The original license no: $rcode

The upgraded license information will be''')


class WebRegister(Register):

    def _request(self, url):
        from http.client import HTTPSConnection
        n = len('https://')
        k = url.find('/', n)
        conn = HTTPSConnection(url[n:k])
        conn.request("GET", url[k:])
        return conn.getresponse()

    def _send_request(self, url, timeout=6.0):
        try:
            return self._request(url)
        except Exception as e:
            logger.debug('direct request failed "%s"', str(e))

        from urllib.request import urlopen
        from ssl import _create_unverified_context
        context = _create_unverified_context()
        return urlopen(url, None, timeout, context=context)

    def _remove_token(self):
        if os.path.exists(self.ctx.license_token):
            logger.debug('remove old token')
            os.remove(self.ctx.license_token)

    def prepare(self, keyfile, product, upgrade=False):
        reginfo = self.parse_keyfile(keyfile)
        logger.info('prepare "%s"', keyfile)

        rcode = self._get_old_rcode() if upgrade else None
        url = self.regurl(reginfo[1], rcode=rcode, prepare=True)
        logger.debug('url: %s', url)

        logger.info('query key file from server')
        with self._send_request(url) as res:
            if not res:
                logger.error('please try it later')
                raise CliError('no response from license server')
            if res.code != 200:
                logger.error('HTTP Error %s', res.code)
                raise CliError(res.read().decode('utf-8'))
            info = json_loads(res.read())

        pname = info['product']
        if pname in ('', 'TBD'):
            info['product'] = product
        elif pname != product:
            logger.warning('old license is bind to product "%s"', pname)
            logger.warning('it can not be changed to "%s"', product)

        lines = []
        if upgrade:
            if not (rcode and rcode.startswith('pyarmor-vax-')):
                logger.error('please check Pyarmor 8.0 EULA')
                raise CliError('old code "%s" can not be upgraded' % rcode)
            if info['upgrade']:
                lines.append(upgrade_to_pro_info.substitute(rcode=rcode))
            else:
                lines.append(upgrade_to_basic_info.substitute())
        else:
            if info['lictype'] not in ('BASIC', 'PRO', 'GROUP'):
                logger.error('this license does not work in Pyarmor 8')
                logger.error('please check Pyarmor 8.0 EULA')
                raise CliError('unknown license type %s' % info['lictype'])
            lines.append('This license registration information will be')

        if info['product'] in ('', 'TBD') and info['lictype'] == 'GROUP':
            raise CliError('"TBD" is invalid product name for group license')

        fmt = '%-16s: %s'
        lines.extend([
            '',
            fmt % ('License Type', 'pyarmor-' + info['lictype'].lower()),
            fmt % ('License Owner', info['regname']),
            fmt % ('Bind Product', info['product']),
            '',
        ])
        if info['product'] in ('', 'TBD'):
            lines.append('This license is about to be used for non-profits')

        lines.extend(['', ''])
        return info, '\n'.join(lines)

    def upgrade_to_pro(self, keyfile, product):
        logger.info('process upgrading file "%s"', keyfile)
        reginfo = self.parse_keyfile(keyfile)

        rcode = self._get_old_rcode()
        logger.info('old license no: %s', rcode)

        url = self.regurl(reginfo[1], product=product, rcode=rcode)
        logger.debug('url: %s', url)

        logger.info('send upgrade request to server')
        res = self._send_request(url)
        regfile = self._handle_response(res)

        logger.info('update license token')
        self.update_token()
        logger.info('This license has been upgraded successfully')

        notes = '* Please backup regfile "%s" carefully, and ' \
            'use this file for subsequent registration' % regfile,
        logger.info('Import Notes:\n\n%s\n', notes)

    def register(self, keyfile, product, upgrade=False, group=False):
        if keyfile.endswith('.zip'):
            logger.info('register "%s"', keyfile)
            self.register_regfile(keyfile)
            return

        logger.info('process activation file "%s"', keyfile)
        reginfo = self.parse_keyfile(keyfile)

        url = self.regurl(reginfo[1], product=product)
        if upgrade:
            url += '&upgrade_to_basic=1'
        logger.debug('url: %s', url)

        logger.info('send request to server')
        res = self._send_request(url)
        regfile = self._handle_response(res)

        notes = [
            '* Please backup regfile "%s" carefully, and '
            'use this file for subsequent registration' % regfile,
            '* Do not use "%s" again' % os.path.basename(keyfile),
        ]

        if group:
            logger.info('This group license has been activated sucessfully')
            notes.append('* Please check `pyarmor reg` in Man page for '
                         'how to register Pyarmor on offline device')
        else:
            logger.info('register "%s"', regfile)
            self.register_regfile(regfile)
            logger.info('This license code has been %s successfully',
                        'upgraded' if upgrade else 'activated')

        logger.info('Import Notes:\n\n%s\n', '\n'.join(notes))

    def _handle_response(self, res):
        if res and res.code == 200:
            dis = res.headers.get('Content-Disposition')
            filename = dis.split('"')[1] if dis else 'pyarmor-regfile.zip'
            logger.info('write registration file "%s"', filename)
            data = res.read()
            if data.startswith(b'{"group":'):
                n = data.find(b'}') + 1
                with open(filename, 'wb') as f:
                    f.write(data[n:])
                self._write_group_info(filename, data[:n])
            else:
                with open(filename, 'wb') as f:
                    f.write(data)
            return filename

        elif res:
            raise CliError(res.read().decode('utf-8'))

        raise CliError('no response from license server')

    def _write_group_info(self, filename, data):
        from zipfile import ZipFile
        logger.info('write group information')
        with ZipFile(filename, 'a') as f:
            f.writestr('group.info', data)

    def register_group_device(self, regfile, devid):
        from zipfile import ZipFile
        devinfo = self.ctx.group_device_file(devid)
        logger.info('register device file "%s"', devinfo)
        logger.info('use group license "%s"', regfile)
        if not os.path.exists(devinfo):
            logger.error('please generate device file in offline device by')
            logger.error('    pyarmor reg -g %s', devid)
            logger.error('and copy generated device file to this machine')
            raise CliError('no group device file "%s"' % devinfo)

        with open(devinfo) as f:
            prefix = 'machine:'
            for line in f:
                if line.startswith(prefix):
                    machine = line[len(prefix):].strip()
                    break
            else:
                logger.error('no machine information in device file')
                raise CliError('invalid device file "%s"' % devinfo)

        with ZipFile(regfile, 'r') as f:
            if 'group.info' not in f.namelist():
                logger.error('no group information in group license file')
                raise CliError('invalid group license file "%s"' % regfile)
            group = json_loads(f.read('group.info'))
            licdata = f.read('license.lic')
            capsule = f.read('.pyarmor_capsule.zip')

        logger.info('send request to server')
        url = self.regurl('/'.join(['group', group['ucode']]))
        paras = ('rev', '1'), ('group', str(group['group'])), \
            ('source', machine), ('devid', str(devid))
        url += '&'.join(['='.join(x) for x in paras])
        logger.debug('url: %s', url)

        res = self._send_request(url)
        filename = self._handle_response(res)
        with open(filename, 'rb') as f:
            tokendata = f.read()

        token_name = os.path.basename(self.ctx.license_token)
        with ZipFile(filename, 'w') as f:
            f.writestr('license.lic', licdata)
            f.writestr('.pyarmor_capsule.zip', capsule)
            f.writestr(token_name, tokendata)

        logger.info('please copy deivce regfile to offline device and run')
        logger.info('    pyarmor reg %s', filename)
