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

from base64 import b64decode, b64encode, urlsafe_b64encode
from json import loads as json_loads
from string import Template

from . import logger, CliError


# All supported machine flags for group license: [11, 26)
MACHFLAGS = 22, 21, 18, 20, 16, 11

# Upgrade notes for Pyarmor 9
URL_UPGRADE_V9 = 'https://github.com/dashingsoft/pyarmor/issues/1958'

# Template for license info
LICENSE_INFO_TEMPLATE = '''$advanced

$notes
'''


def parse_token(data):
    from struct import unpack

    if data and data.find(b' ') > 0:
        try:
            buf = b64decode(data.split()[0])

            token, value = unpack('II', buf[:8])
            rev, features = value & 0xff, value >> 8
            licno = buf[16:34].decode('utf-8')

            pstr = []
            i = 64
            for k in range(4):
                n = buf[i]
                i += 1
                pstr.append(buf[i:i+n].decode('utf-8') if n
                            else '')
                i += n

            product = ('non-profits(TBD)' if pstr[2] in ('', 'TBD')
                       else pstr[2])
            return {
                'token': token,
                'rev': rev,
                'features': features,
                'licno': licno,
                'machine': pstr[0],
                'regname': pstr[1],
                'product': product,
                'note': pstr[3],
            }
        except Exception as e:
            logger.warning('bad token: %s', str(e))

    return {
        'token': 0,
        'rev': 0,
        'features': 0,
        'licno': 'pyarmor-vax-000000',
        'regname': '',
        'product': 'non-profits',
        'note': 'This is trial license'
    }


def show_help_page(prompt, url):
    choice = input('\n'.join(prompt)).lower()[:1]
    if choice in ('h', 'y'):
        import webbrowser
        webbrowser.open(url)
    return choice


def check_license_version(ctx, silent=False):
    licinfo = ctx.license_info
    rev = licinfo.get('rev', 0)
    token = licinfo.get('token', 0)
    features = licinfo.get('features', 0)
    if rev == 1 and features > 0 and token > 0:
        logger.warning('this license is not ready for Pyarmor 9')
        if silent:
            return False

        # Group License
        if features == 15:
            prompt = (
                '',
                'Pyarmor 9 has some changes on license policy',
                'This group license is still available',
                'But it need request new device regfile as before',
                'Press "h" to check Pyarmor 9 Upgrade Notes',
                '',
                'Help (h), Quit (q): '
            )
            show_help_page(prompt, URL_UPGRADE_V9)
            raise SystemExit('Quit')

        prompt = (
            '',
            'Pyarmor 9 has big change on CI/CD pipeline',
            'If not using Pyarmor License in CI/CD pipeline',
            'Press "c" to continue',
            'Otherwise press "h" to check Pyarmor 9.0 Upgrade Notes',
            '',
            'Continue (c), Help (h), Quit (q): '
        )
        if not show_help_page(prompt, URL_UPGRADE_V9) == 'c':
            raise SystemExit('Quit')


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
            if len(product) > 60:
                raise CliError('too long product name (length > 60)')
            url += '&product=' + \
                urlsafe_b64encode(product.encode('utf-8')).decode()
        if rcode:
            url += '&rcode=' + rcode
        if prepare:
            url += '&prepare=1'
        return url

    def update_token(self):
        from .core import Pytransform3
        assert Pytransform3._pytransform3 is None
        with open(self.ctx.license_token, 'wb') as f:
            f.close()
        Pytransform3.init(self.ctx)

    @property
    def license_info(self):
        return parse_token(self.ctx.read_token())

    def _license_type(self, info):
        return 'basic' if info['features'] in (1, 17) else \
            'pro' if info['features'] == 7 else \
            'group' if info['features'] == 15 else \
            'ci' if info['features'] == 23 else \
            'trial' if info['token'] == 0 else 'unknown'

    def _license_to(self, info):
        name = info['regname']
        product = info['product']
        return '%s (%s)' % (product, name) if name and product else \
            'non-profits' if not name else 'non-profits (%s)' % name

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

        raise CliError('invalid activation file "%s"' % filename)

    def _register_offline_license(self, fzip, namelist):
        logger.info('machine id in group license: %s', ', '.join(
            [x[7:] for x in namelist if x.startswith('tokens')]))
        for idver in MACHFLAGS:
            machid = self._get_machine_id(idver).decode('utf-8')
            logger.debug('got machine id: %s', machid)
            name = '/'.join(['tokens', machid])
            if name in namelist:
                logger.info('this machine id matchs group license')
                break
        else:
            logger.info('no machine id matchs this group license')
            logger.info('take this machine as docker container, and '
                        'connect to docker host for authentication...')
            mlist = self._get_docker_hostname()
            if not mlist:
                logger.info(
                    'could not get docker host machine id\n%s',
                    '\n'.join([
                        '',
                        'if this machine is docker container, please '
                        'run command `pyarmor-auth` in docker host, '
                        'and try it again', '',
                        'otherwise please generate new group '
                        'device license for this machine', '',
                        'more information please check section '
                        '"using group license" in documentation '
                        '"how-to register" guide', ''
                    ]))
                raise CliError('this group device license is not for '
                               'this machine')
            for machid in mlist:
                hostname = '/'.join(['tokens', machid])
                if hostname in namelist:
                    name = hostname
                    break
            else:
                logger.debug('docker host machine ids: %s', mlist)
                raise CliError('this group device license is not for '
                               'this docker host')

        logger.debug('extracting %s', name)
        self.ctx.save_group_token(fzip.read(name))

    def _init_token(self, reginfo):
        from struct import pack
        rev, licno, lictp, regname, product = (
            reginfo['rev'], reginfo['rcode'], reginfo['type'],
            reginfo['name'], reginfo['product']
        )

        token = 0
        old_license = self.license_info
        if old_license['licno'] == licno:
            token = old_license['token']

        features = (1 if lictp == 'J' else 7 if lictp == 'Z' else
                    15 if lictp == 'G' else 23 if lictp == 'C' else
                    0)
        notes = (
            '* Do not use this file in CI/CD pipeline directly\n'
            '* Only use it to request CI regfile '
            '"pyarmor-ci-%s.zip"' % licno[:6].lstrip('0')
            if lictp == 'C' else ''
        )

        regname = regname.encode('utf-8')
        product = product.encode('utf-8')
        notes = notes.encode('utf-8')
        sizes = len(regname), len(product), len(notes)
        data = pack('<II8x20s28xBB{0}sB{1}sB{2}s'.format(*sizes),
                    token,
                    rev | features << 8,
                    licno.encode('utf-8'),
                    0,
                    sizes[0], regname,
                    sizes[1], product,
                    sizes[2], notes)
        return b64encode(data) + b' *=='

    def register_regfile(self, regfile, clean=True):
        from zipfile import ZipFile

        if os.path.exists(self.ctx.license_group_token):
            os.remove(self.ctx.license_group_token)

        path = self.ctx.reg_path
        with ZipFile(regfile, 'r') as f:
            for item in ('license.lic', '.pyarmor_capsule.zip'):
                logger.debug('extracting %s', item)
                f.extract(item, path=path)
            namelist = f.namelist()
            if 'group.tokens' in namelist:
                self._register_offline_license(f, namelist)
            elif 'ci.token' in namelist:
                name = 'ci.token'
                logger.debug('extracting %s', name)
                self.ctx.save_token(f.read(name))
            elif 'group.info' in namelist:
                logger.info('this file is only used to '
                            'request device regfile:\n\n'
                            '\tpyarmor reg -g 1 %s\n', regfile)
                raise CliError('wrong usage for Group License')
            elif 'reg.info' in namelist:
                data = f.read('reg.info')
                info = json_loads(data)
                if info.get('type', '') == 'C':
                    logger.info('this file is only used to '
                                'request ci regfile:\n\n'
                                '\tpyarmor reg -C %s\n', regfile)
                    raise CliError('wrong usage for CI License')
                self.ctx.save_token(self._init_token(info))
            else:
                logger.error('this license is not ready for Pyarmor 9')
                prompt = (
                    '',
                    'Pyarmor 9 has big change on CI/CD pipeline',
                    'Press "h" to check Pyarmor 9.0 Upgrade Notes',
                    '',
                    'Help (h), Quit (q): '
                )
                show_help_page(prompt, URL_UPGRADE_V9)
                raise SystemExit()

    def _get_docker_hostname(self):
        try:
            from socket import socket, AF_INET, SOCK_STREAM
            host = os.getenv('PYARMOR_DOCKER_HOST', 'host.docker.internal')
            port = 29092
            rlist = []
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect((host, port))
                logger.info('socket addr: %s', str(s.getsockname()))
                logger.info('remote addr: %s', str(s.getpeername()))
                s.sendall(b'PADH' + b'x' * 60)
                while True:
                    flag = s.recv(1)
                    if ord(flag) - 87 in MACHFLAGS:
                        data = s.recv(32)
                    machid = (flag + data).decode('utf-8')
                    logger.info('got docker host machine id: %s', machid)
                    rlist.append(machid)
                    if s.recv(1) == b'\x00':
                        break
            return rlist
        except Exception as e:
            logger.debug('%s:%d:%s', host, port, str(e))

    def _get_machine_id(self, devflag=11):
        from .core import Pytransform3
        try:
            return Pytransform3.get_hd_info(devflag)
        except SystemError:
            from time import time
            return b'u-machine-id:%020.6f' % time()

    def generate_group_device(self, devid):
        from datetime import datetime
        from platform import uname
        path = self.ctx.group_device_file(devid)
        logger.info('generating device file "%s"', path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        uinfo = uname()
        devflag = self.ctx.cfg['builder'].getint('group_device_flag', 21)
        machid = self._get_machine_id(devflag).decode('utf-8')
        logger.info('current machine id is "%s"', machid)
        tpl = Template('\n'.join([
            '# Generated by Pyarmor $rev, $timestamp',
            'host: $node',
            'system: $host ($version)',
            'machine: $machine'
        ])).substitute(
            rev='.'.join(self.ctx.version),
            node=uinfo.node,
            host=uinfo.system,
            version=uinfo.version,
            timestamp=datetime.now().isoformat(),
            machine=machid,
        )
        with open(path, "wb") as f:
            f.write(tpl.encode('utf-8'))
        return path

    def check_group_license(self, silent=False):
        licinfo = self.license_info
        if licinfo['features'] & 8:
            licmach = licinfo.get('machine', '')
            if not licmach:
                raise RuntimeError('no token machine')

            idver = ord(licmach[0]) - 87
            # This can't be called in "cmd_gen", otherwise crash
            machid = self._get_machine_id(idver).decode('utf-8')
            if machid == licmach:
                return

            mlist = self._get_docker_hostname()
            if mlist and licmach in mlist:
                return

            logger.info('this license is for machine: %s', licmach)

            if mlist:
                logger.info('but docker host machine ids: %s',
                            ', '.join(mlist))
                raise RuntimeError(
                    'this group license is not for this docker host')
            else:
                logger.info('but this machine id: %s', machid)
                raise RuntimeError(
                    'this group license is not for this machine')

    def __str__(self):
        info = self.license_info
        lictype = self._license_type(info)

        fmt = '%-16s: %s'
        lines = [
            fmt % ('License Type', 'pyarmor-' + lictype),
            fmt % ('License No.', info['licno']),
            fmt % ('License To', info['regname']),
            fmt % ('License Product', info['product']),
            '',
        ]

        bccmode = info['features'] & 2
        rftmode = info['features'] & 4
        cidmode = info.get('machine', '').startswith('CITK')
        advanced = [
            fmt % ('BCC Mode', 'Yes' if bccmode else 'No'),
            fmt % ('RFT Mode', 'Yes' if rftmode else 'No'),
            fmt % ('CI/CD Mode', 'Yes' if cidmode else 'No'),
        ]
        if lictype == 'trial':
            self.notes.append('* Can\'t obfuscate big script and mix str')
        elif lictype in ('basic', 'pro'):
            self.notes.append('* Need verify license online '
                              'when obfuscating scripts')
        elif lictype == 'group':
            self.notes.append('* Offline obfuscation')

        if info['note']:
            self.notes.extend(info['note'].splitlines())

        if self.notes:
            self.notes.insert(0, 'Notes')

        lines.append(Template(LICENSE_INFO_TEMPLATE).substitute(
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

    # Before v9.0:  1
    # Pyarmor v9.0: 2
    # Pyarmor v9.2: 3
    LICENSE_REVSION = 3

    # Before v9.0: no CI License
    # Pyarmor v9.0: 1
    # Pyarmor v9.2: 2
    CI_LICENSE_REVSION = 2

    def _request(self, url):
        from http.client import HTTPSConnection
        n = len('https://')
        k = url.find('/', n)
        conn = HTTPSConnection(url[n:k])
        conn.request("GET", url[k:])
        return conn.getresponse()

    def check_request_interval(self, delta=30.0):
        """Make sure no more than 2 requests in 1 minute"""
        tspath = os.path.join(self.ctx.reg_path, 'last_register')
        try:
            st = os.stat(tspath)
        except FileNotFoundError:
            os.makedirs(tspath)
        else:
            from time import sleep, time
            d = delta - (time() - st.st_mtime)
            if d > 0:
                logger.warning('caution: this activation file can only '
                               'be used no more than 10 times')
                logger.info('waiting for %d seconds', d)
            while time() - st.st_mtime < delta:
                logger.info('waiting ...')
                sleep(3.0)
            os.utime(tspath)

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

    def _check_product_name(self, name):
        name = name.lower()
        if name.count(name[0]) == len(name) or name.find('pyarmor') >= 0:
            raise RuntimeError('invalid product name "%s"' % name)

    def prepare(self, keyfile, product, upgrade=False):
        reginfo = self.parse_keyfile(keyfile)
        logger.info('prepare "%s"', keyfile)

        if product:
            self._check_product_name(product)

        rcode = self._get_old_rcode() if upgrade else None
        if upgrade and not rcode and keyfile.endswith('regcode-to-pro.txt'):
            logger.error('please use `pyarmor-7 -v` to check old license')
            logger.error('this code is used to upgrade old license')
            raise CliError('no found old license in this machine')
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
            logger.warning('this license has bound to product "%s"', pname)
            logger.warning('it can not be changed to "%s"', product)

        lines = []
        if upgrade:
            if rcode and not rcode.startswith('pyarmor-vax-'):
                raise CliError('old license "%s" can not be upgraded' % rcode)
            if info['upgrade']:
                lines.append(upgrade_to_pro_info.substitute(rcode=rcode))
            else:
                lines.append(upgrade_to_basic_info.substitute())
        else:
            if info['lictype'] == 'OLD':
                raise CliError('old license only works for Pyarmor <= 7.7.4')
            if info['lictype'] not in ('BASIC', 'PRO', 'GROUP', 'CI'):
                raise CliError('unknown license type %s' % info['lictype'])
            lines.append('This license registration information will be')

        if info['product'] in ('', 'TBD') and info['lictype'] == 'GROUP':
            raise CliError('"TBD" is invalid product name for group license')

        fmt = '%-16s: %s'
        lines.extend([
            '',
            fmt % ('License Type', 'pyarmor-' + info['lictype'].lower()),
            fmt % ('License To', info['regname']),
            fmt % ('License Product', info['product']),
            '',
        ])
        if info['product'] == 'non-profits':
            lines.append('This license is about to be used for non-profits')
        if info['product'] in ('', 'TBD'):
            lines.append('This license is bind to non-profits(TBD) '
                         'for the time being')
            lines.append('If not change "TBD" to product name in 6 months, '
                         'it will be set to "non-profits" automatically')
        else:
            lines.append('This license is about to be used for product "%s"'
                         % info['product'])
        if info['product'] not in ('', 'TBD'):
            lines.append('')
            lines.append('IMPORTANT: PRODUCT NAME CAN NOT BE CHANGED '
                         'AFTER INITIAL REGISTRATION')

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
        regfile, lictype = self._handle_response(res)

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
        url += '&rev=' + str(self.LICENSE_REVSION)
        if upgrade:
            url += '&upgrade_to_basic=1'
        logger.debug('url: %s', url)

        logger.info('send request to server')
        res = self._send_request(url)
        regfile, lictype = self._handle_response(res)

        logger.info('')
        logger.info('the registration file "%s" has been generated', regfile)
        logger.info('this license has been activated sucessfully')

        notes = [
            '* Please backup "%s", but do not use it to '
            'register Pyarmor' % os.path.basename(keyfile),
            '* Please backup regfile "%s", and '
            'use this file for next any registration' % regfile,
            '* Do not use this file in docker and CI/CD pipeline',
            '',
        ]
        logger.info('\n\nImport Notes:\n%s\n', '\n'.join(notes))

        input('Type Enter to continue ...')
        LicenseHelper(self).run(lictype, regfile)

    def _handle_response(self, res):
        if res and res.code == 200:
            lictype = None
            dis = res.headers.get('Content-Disposition')
            filename = dis.split('"')[1] if dis else 'pyarmor-regfile.zip'
            logger.info('write registration file "%s"', filename)
            data = res.read()
            if data.startswith(b'{"group":'):
                lictype = 'G'
                n = data.find(b'}') + 1
                with open(filename, 'wb') as f:
                    f.write(data[n:])
                self._write_group_info(filename, data[:n])
            elif data.startswith(b'REGINFO:'):
                i = len(b'REGINFO:')
                n = data[i] + (data[i+1] << 8)
                i += 2
                n += i
                with open(filename, 'wb') as f:
                    f.write(data[n:])
                reginfo = data[i:n]
                lictype = json_loads(reginfo).get('type', None)
                self._write_reg_info(filename, reginfo)
            else:
                # Only for request group token
                logger.debug('no REGINFO found')
                with open(filename, 'wb') as f:
                    f.write(data)
            return filename, lictype

        elif res:
            data = res.read()
            logger.debug('server return(%d): %s', res.code, data)
            try:
                msg = data.decode('utf-8')
            except Exception as e:
                logger.debug('decode server data error "%s"', e)
                msg = data
            raise CliError(msg)

        raise CliError('no response from license server')

    def _write_reg_info(self, filename, data):
        from zipfile import ZipFile
        logger.info('write reg information')
        with ZipFile(filename, 'a') as f:
            f.writestr('reg.info', data)

    def _write_group_info(self, filename, data):
        from zipfile import ZipFile
        logger.info('write group information')
        with ZipFile(filename, 'a') as f:
            f.writestr('group.info', data)

    def request_device_regfile(self, regfile, devid):
        from zipfile import ZipFile
        devfile = self.ctx.group_device_file(devid)
        rev = self.LICENSE_REVSION
        logger.info('request device regfile "%s" (v%d)', devfile, rev)
        logger.info('use group license "%s"', regfile)
        if not os.path.exists(devfile):
            logger.error('please generate device file in offline device by')
            logger.error('    pyarmor reg -g %s', devid)
            logger.error('and copy generated device file to this machine')
            raise CliError('no group device file "%s"' % devfile)

        with open(devfile) as f:
            prefix = 'machine:'
            for line in f:
                if line.startswith(prefix):
                    machid = line[len(prefix):].strip()
                    break
            else:
                logger.error('no machid information in device file')
                raise CliError('invalid device file "%s"' % devfile)

        with ZipFile(regfile, 'r') as f:
            if 'group.info' not in f.namelist():
                logger.error('no group information in group license file')
                raise CliError('invalid group license file "%s"' % regfile)
            group = json_loads(f.read('group.info'))
            licdata = f.read('license.lic')
            capsule = f.read('.pyarmor_capsule.zip')

        # Ignore token cache
        tokencache = os.path.join(os.path.dirname(devfile), 'tokens', machid)
        if False and os.path.exists(tokencache):
            logger.info('read cached "%s"', tokencache)
            with open(tokencache, 'rb') as f:
                data = f.read()
            filename = regfile.replace('pyarmor-', 'pyarmor-device-').replace(
                '.zip', '.%s.zip' % devid)
            logger.info('write registeration file "%s"', filename)
        else:
            logger.info('send request to server')
            url = self.regurl('/'.join(['group', group['ucode']]))
            paras = ('rev', str(rev)), ('group', str(group['group'])), \
                ('source', machid), ('devid', str(devid))
            url += '&'.join(['='.join(x) for x in paras])
            logger.debug('url: %s', url)

            res = self._send_request(url)
            filename, lictype = self._handle_response(res)
            with open(filename, 'rb') as f:
                data = f.read()
            os.makedirs(os.path.dirname(tokencache), exist_ok=True)
            with open(tokencache, 'wb') as f:
                f.write(data)

        with ZipFile(filename, 'w') as f:
            f.writestr('license.lic', licdata)
            f.writestr('.pyarmor_capsule.zip', capsule)
            f.writestr('group.tokens', b'')
            f.writestr('tokens/' + machid, data)

        logger.info('please copy deivce regfile to offline device and run')
        logger.info('    pyarmor reg %s', filename)

    register_group_device = request_device_regfile

    def _write_ci_info(self, filename, data):
        from zipfile import ZipFile
        logger.info('write ci information')
        with ZipFile(filename, 'a') as f:
            f.writestr('ci.token', data)

    def request_ci_regfile(self, regfile):
        rev = self.LICENSE_REVSION
        cirev = self.CI_LICENSE_REVSION
        logger.info('request ci regfile (v%d) by "%s"', cirev, regfile)
        from zipfile import ZipFile

        with ZipFile(regfile, 'r') as f:
            if 'reg.info' not in f.namelist():
                logger.error('missing reg.info in regfile, '
                             'this license may be out of date, '
                             'please check Pyarmor upgrade notes')
                raise CliError('can not request CI license')
            reginfo = json_loads(f.read('reg.info'))

        ucode = reginfo['ucode']
        rcode = reginfo['rcode']
        if len(ucode) != 192:
            raise CliError('invalid registration file "%s"', regfile)

        url = self.regurl('ci/%s' % ucode)
        paras = ('rev', str(rev)), ('cirev', str(cirev))
        url += '&'.join(['='.join(x) for x in paras])
        logger.debug('url: %s', url)

        logger.info('send request to server')
        res = self._send_request(url)

        logger.info('handle response')
        if res is None:
            raise CliError('no response from license server')

        elif res.code != 200:
            raise CliError(res.read().decode('utf-8'))

        data = res.read()
        if not data.startswith(b'CITOKEN:'):
            raise CliError('wrong server data: "%s"' % data)

        i = len(b'CITOKEN:') + 2
        n = data[i-2] + (data[i-1] << 8)
        token = data[i:i+n]

        rn = rcode[-6:].lstrip('0')
        cifile = 'pyarmor-ci-%s.zip' % rn

        with ZipFile(regfile, 'r') as src:
            with ZipFile(cifile, 'w') as dst:
                for x in src.namelist():
                    dst.writestr(x, src.read(x))
                dst.writestr('ci.token', token)

        logger.info('generate CI regfile "%s" successfully', cifile)

        ver = '.'.join([str(x) for x in self.ctx.version])
        logger.info('\n\nCheck CI license in local machine by:\n'
                    '\n\tpyarmor reg %s\n\n'
                    'Register Pyarmor in CI/CD pipeline by:\n'
                    '\n\tpip install pyarmor==%s\n'
                    '\tpyarmor reg %s\n',
                    cifile, ver, cifile)


BASIC_LICENSE_HELP_INFO = Template('''
Using Basic license in CI/CD pipeline or docker container need extra steps, please check this page

$docurl/how-to/ci.html

More usage about Basic License, check this page

$docurl/how-to/register.html

If need register Pyarmor in build device, run this command:

    pyarmor reg $regfile

''')

PRO_LICENSE_HELP_INFO = Template('''
Pro license can't be used in CI/CD pipeline or docker container direclty.

A few times for debug purpose, about 60 runs per month, may work.

But there is one workaroud for Pro licnese in CI/CD pipeline, please check this page

$docurl/how-to/ci.html

More usage about Pro License, check this page

$docurl/how-to/register.html

If need register Pyarmor in build device, run this command:

    pyarmor reg $regfile

''')

GROUP_LICENSE_HELP_INFO = Template('''
Group License file `$regfile` is only used to request device regfile

In order to register Pyarmor in offline device:

1. In the build device (may be offline), generate device info by this command

   pyarmor reg -g 1

2. In any online device, copy device file generated by first step, then request device regfile for this device

   cp pyarmor-group-device.1 .pyarmor/group/
   pyarmor reg -g 1 $regfile

3. In the build device, register Pyarmor by device regfile

   pyarmor reg pyarmor-device-regfile-xxxx.1.zip

More usage about CI License, check section `Using group licnese`

$docurl/how-to/register.html
''')

CI_LICENSE_HELP_INFO = Template('''
CI license file `$regfile` is only used to request CI regfile

CI regfile is used to register Pyarmor in the CI/CD pipeline

If need request CI regfile, run this command:

    pyarmor reg -C $regfile

Note that CI regfile can NOT be used in physical machine, and there is rate limits to register CI regfile in CI/CD pipeline and docker container.

It may need request new CI regfile after Pyarmor is upgraded, please check section `When need to request new CI regfile` in this page

$docurl/how-to/ci.html

More usage about CI License, check these pages

$docurl/how-to/register.html
$docurl/how-to/ci.html
''')


class LicenseHelper(object):
    """Only used for first activate license.

    Help the beginner to understand how to use different licenses.

    """

    def __init__(self, parent):
        self.parent = parent
        self.docurl = parent.ctx.cfg.get(
            'pyarmor', 'docurl').rstrip('/').replace('{lang}', 'en')
        self.print = print

    def run(self, lictype, regfile):
        if lictype == 'G':
            self._group_license_helper(regfile)

        elif lictype == 'C':
            self._ci_license_helper(regfile)

        elif lictype == 'Z':
            self._pro_license_helper(regfile)

        elif lictype in ('J', 'B', 'P'):
            self._basic_license_helper(regfile)

        else:
            raise CliError('unknown license type "%s"' % lictype)

    def _basic_license_helper(self, regfile):
        self.print(BASIC_LICENSE_HELP_INFO.substitute(
            docurl=self.docurl, regfile=regfile))

        prompt = 'Yes (y), No (n), Quit (q): '
        self.print('Show basic license usage in webbrowser? (n)')
        choice = show_help_page([prompt], self.docurl + '/how-to/register.html')
        if choice == 'q':
            return

        self.print('Show basic license for CI/CD pipeline or docker? (n)')
        choice = show_help_page([prompt], self.docurl + '/how-to/ci.html')
        if choice == 'q':
            return

        self.print('Do you want register Pyarmor in this machine? (y)')
        choice = input(prompt).lower()[:1]
        if choice == 'q':
            return

        if choice in ('y', ''):
            self.print('register "%s"' % regfile)
            self.parent.register_regfile(regfile)
            self.print('This license registration information:\n\n'
                       '%s' % self.parent)

    def _pro_license_helper(self, regfile):
        self.print(PRO_LICENSE_HELP_INFO.substitute(
            docurl=self.docurl, regfile=regfile))

        prompt = 'Yes (y), No (n), Quit (q): '
        self.print('Show pro license usage in webbrowser? (n)')
        choice = show_help_page([prompt], self.docurl + '/how-to/register.html')
        if choice == 'q':
            return

        self.print('Show pro license for CI/CD pipeline or docker? (n)')
        choice = show_help_page([prompt], self.docurl + '/how-to/ci.html')
        if choice == 'q':
            return

        self.print('Do you want register Pyarmor in this machine? (y)')
        choice = input(prompt).lower()[:1]
        if choice == 'q':
            return

        if choice in ('y', ''):
            self.print('register "%s"' % regfile)
            self.parent.register_regfile(regfile)
            self.print('This license registration information:\n\n'
                       '%s' % self.parent)

    def _group_license_helper(self, regfile):
        self.print(GROUP_LICENSE_HELP_INFO.substitute(
            docurl=self.docurl, regfile=regfile))

        prompt = 'Yes (y), No (n), Quit (q): '
        self.print('Show group license usage in webbrowser? (n)')
        choice = show_help_page([prompt], self.docurl + '/how-to/register.html')
        if choice == 'q':
            return

        self.print('Do you want register Pyarmor in this machine? (n)')
        choice = input(prompt).lower()[:1]
        if choice == 'q':
            return

        if choice != 'y':
            return

        self.print('Please assign one unused device no. to this device, '
                   'starts from 1')
        devid = None
        while devid is None:
            a = input('Type device no. (default is 1): ')
            if a == '':
                devid = 1
            elif (not a.isdigit()) or int(a) < 1 or int(a) > 100:
                self.print('invalid input')
            else:
                devid = int(a)

        if devid:
            sep = '-' * 16
            devinfo = self.parent.ctx.group_device_file(devid)
            self.print('%s 1. generate device info' % sep)
            if os.path.exists(devinfo):
                logger.warning('old device file has been exists')
            else:
                self.parent.generate_group_device(devid)
            self.print('%s 2. request device regfile' % sep)
            self.parent.request_device_regfile(regfile, devid)
            self.print('%s 3. register Pyarmor with device regfile' % sep)
            self.parent.register(regfile.
                                 replace('.zip', '.%d.zip' % devid).
                                 replace('-regfile', '-device-regfile'))

    def _ci_license_helper(self, regfile):
        self.print(CI_LICENSE_HELP_INFO.substitute(
            docurl=self.docurl, regfile=regfile))

        prompt = 'Yes (y), No (n), Quit (q): '
        self.print('Show ci license usage in webbrowser? (n)')
        choice = show_help_page([prompt], self.docurl + '/how-to/ci.html')
        if choice == 'q':
            return

        self.print('Do you want request one CI Regfile now? (y)')
        choice = input(prompt).lower()[:1]
        if choice == 'q':
            return

        if choice in ('y', ''):
            self.parent.request_ci_regfile(regfile)
