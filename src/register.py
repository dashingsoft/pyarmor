#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2022 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 7.4.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: register.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2022/02/02
#
#  @Description:
#
#  The registration functions of pyarmor.
#
import logging
import os

from zipfile import ZipFile
from json import loads as json_loads

from config import key_url, reg_url
from utils import PYARMOR_PATH, HOME_PATH, _urlopen, decode_license_key


def query_keyinfo(key):
    try:
        from urllib.parse import urlencode
    except ImportError:
        from urllib import urlencode

    licfile = os.path.join(HOME_PATH, 'license.lic')
    if not os.path.exists(licfile):
        licfile = os.path.join(HOME_PATH, 'license.lic')
    logging.debug('Got license data from %s', licfile)
    with open(licfile) as f:
        licdata = urlencode({'rcode': f.read()}).encode('utf-8')

    try:
        logging.debug('Query url: %s', key_url % key)
        res = _urlopen(key_url % key, licdata, timeout=6.0)
        data = json_loads(res.read().decode())
    except Exception as e:
        note = 'Note: sometimes remote server is busy, please try it later'
        return '\nError: %s\n%s' % (str(e), note)

    name = data['name']
    email = data['email']
    if name and email:
        return 'License to: "%s <%s>"' % (name, email)

    if 'error' in data:
        return '\nError: %s' % data['error']

    return '\nError: this code may NOT be issued by PyArmor officially.' \
        '\nPlease contact <pyarmor@163.com>'


def activate_regcode(ucode):
    res = _urlopen(reg_url % ucode, timeout=6.0)
    if res is None:
        raise RuntimeError('Activate registration code failed, '
                           'got nothing from server')

    if res.code != 200:
        data = res.read().decode()
        raise RuntimeError('Activate registration code failed: %s' % data)

    data = res.read()
    dis = res.headers.get('Content-Disposition')
    filename = dis.split('"')[1] if dis else 'pyarmor-regfile-1.zip'
    with open(filename, 'wb') as f:
        f.write(data)

    return filename


def upgrade_license(filename):
    logging.info('Start to upgrade license with keyfile: %s', filename)
    path = HOME_PATH
    if not os.path.exists(path):
        logging.info('Create path: %s', path)
        os.makedirs(path)
    path = os.path.join(path, '.key')
    logging.info('Save registration data to: %s', path)
    f = ZipFile(filename, 'r')
    try:
        for item in ('license.lic', '.pyarmor_capsule.zip'):
            logging.info('Extracting %s' % item)
            f.extract(item, path=path)
    finally:
        f.close()
    logging.info('The old license has been upgraded successfully.')


def register_keyfile(filename, upgrade=False, legency=False):
    if upgrade:
        return upgrade_license(filename)

    logging.info('Start to register keyfile: %s', filename)
    if (not legency) and \
       not os.getenv('PYARMOR_HOME',
                     os.getenv('HOME', os.getenv('USERPROFILE'))):
        logging.debug('Force traditional way because no HOME set')
        legency = True
    old_license = os.path.join(PYARMOR_PATH, 'license.lic')
    if os.path.exists(old_license):
        logging.info('Remove old license file `%s`', old_license)
        os.remove(old_license)

    path = PYARMOR_PATH if legency else HOME_PATH
    if not os.path.exists(path):
        logging.info('Create path: %s', path)
        os.makedirs(path)
    logging.info('Save registration data to: %s', path)
    f = ZipFile(filename, 'r')
    try:
        for item in ('license.lic', '.pyarmor_capsule.zip'):
            logging.info('Extracting %s' % item)
            f.extract(item, path=path)
    finally:
        f.close()
    logging.info('This keyfile has been registered successfully.')


def get_keylist():
    '''List all the register the keys, print id and registration code'''
    licfile = os.path.join(HOME_PATH, 'license.lic')
    if not os.path.exists(licfile):
        return []

    with open(licfile, 'r') as f:
        current = decode_license_key(f.read())

    result = []
    keyfile = os.path.join(HOME_PATH, '.pyarmor.key')
    if os.path.exists(keyfile):
        myzip = ZipFile(keyfile, 'r')
        try:
            for name in myzip.namelist():
                if name.endswith('/'):
                    result.append((name, current == name))
        finally:
            myzip.close()
    elif current:
        result.append((current, True))

    return result


def list_key():
    '''Print all the available license keys'''
    klist = get_keylist()
    if not klist:
        logging.warning('There is no activate license key')
        return

    result = ['All the available license keys:',
              'ID.\tKey']
    for i in range(1, len(klist) + 1):
        result.append('%s %-2s\t%s' % ('*' if klist[1] else ' ', i, klist[0]))

    print('\n'.join(result))


def select_key(rcode):
    '''Activate the specify license by index or key code.'''
    if rcode.isdigit():
        klist = get_keylist()
        if not klist:
            logging.warning('There is no available license key')
            return
        rcode = klist[int(rcode)][0]

    path = HOME_PATH
    if not os.path.exists(path):
        logging.info('Create path: %s', path)
        os.makedirs(path)
    logging.info('Save registration data to: %s', path)

    keyfile = os.path.join(HOME_PATH, '.pyarmor.key')
    f = ZipFile(keyfile, 'r')
    try:
        for item in ('license.lic', '.pyarmor_capsule.zip'):
            logging.info('Extracting %s' % item)
            f.extract('/'.join(rcode, item), path=path)
        logging.info('The registration code %s has been activated.', rcode)
    except Exception:
        logging.error('No keyfile found for this code: %s' % rcode)
    finally:
        f.close()


def append_key(licfile, capsule):
    '''Append license to keyfile, ignore if license already exists'''
    with open(licfile, 'rb') as f:
        old_code = decode_license_key(f.read())
        if not old_code:
            return

    if old_code in [x[0] for x in get_keylist()]:
        return

    keyfile = os.path.join(HOME_PATH, '.pyarmor.key')
    myzip = ZipFile(keyfile, 'a')
    try:
        myzip.write(licfile, '/'.join(old_code, 'license.lic'))
        myzip.write(capsule, '/'.join(old_code, '.pyarmor_capsule.zip'))
    finally:
        myzip.close()
