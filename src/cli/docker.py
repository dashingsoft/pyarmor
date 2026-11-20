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
#      Version: 8.3.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: cli/docker.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Tue Aug 1 09:18:12 CST 2023
#
import argparse
import logging
import os
import socketserver
import struct
import subprocess
import sys

from .context import Context
from .generate import Pytransform3
from .register import Register, MACHFLAGS


CONFIG = {
    'host': '0.0.0.0',
    'port': 29092,
    'home': os.path.expanduser(os.path.join('~', '.pyarmor')),
    'machid': None,
    'ctx': None,
}


class DockerAuthHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(64)
        logging.info('receive request from %s', self.client_address)
        try:
            logging.debug('request data (%d): %s', len(data), data)
            response = self.process(data)
            logging.info('send auth result to %s', self.client_address)
            logging.debug('response data (%d): %s', len(response), response)
        except Exception as e:
            logging.error('%s', str(e))
            msg = 'verification failed, please check host console'.encode()
            msg += b'\00'
            self.request.send(struct.pack('!HH', 1, len(msg)) + msg)

    def process(self, packet):
        cmd = packet[:4]
        if cmd == b'PADH':
            response = b'\n'.join(CONFIG['machid']) + b'\x00'
            self.request.send(response)
        elif cmd == b'PADI':
            userdata = packet[4:].decode('utf-8')
            rtkey = self.generate_outer_key(userdata, outer=False)
            magic = b'DockerRuntimeKey'
            response = magic + struct.pack('!HH', 0, len(rtkey)) + rtkey
            self.request.send(response)
        elif cmd == b'PADK':
            userdata = self.parse_packet(packet).decode('utf-8')
            rtkey = generate_runtime_key(userdata)
            response = struct.pack('!HH', 0, len(rtkey)) + rtkey
            self.request.send(response)
        elif cmd == b'PADC':
            ctx = CONFIG['ctx']
            key = ctx.read_license()
            token = ctx.read_token()
            response = struct.pack('!HH', len(token), len(key)) + token + key
            self.request.send(response)
        else:
            raise RuntimeError('unknown packet %r' % packet)
        return response

    def parse_packet(self, packet):
        n = len(packet)
        if n >= 32 and packet[:4] == b'PADK' and packet[32:34] in (b'DK', b''):
            return packet[12:]
        raise RuntimeError('invalid auth request: %r' % packet)

    def generate_outer_key(self, userdata, outer=True):
        ctx = CONFIG['ctx']
        ctx.cmd_options['user_data'] = userdata
        ctx.cmd_options['expired'] = '.3'
        ctx.cmd_options['outer'] = 1
        Pytransform3._pytransform3.init_ctx(ctx)
        return Pytransform3.generate_runtime_key(ctx, outer=outer)


def generate_runtime_key(userdata):
    ctx = CONFIG['ctx']
    ctx.cmd_options['user_data'] = userdata
    ctx.cmd_options['expired'] = '.3'
    ctx.cmd_options['outer'] = 0
    Pytransform3._pytransform3.init_ctx(ctx)
    return Pytransform3.generate_runtime_key(ctx, outer=False)


def register_pyarmor(ctx, regfile):
    reg = Register(ctx)
    if regfile:
        logging.info('register "%s"', regfile)
        reg.register_regfile(regfile)
    else:
        master = Context(home=CONFIG['home'])
        if not os.path.exists(master.license_group_token):
            raise RuntimeError('this device is not registerred as group license')

        def copy_files(src, dest):
            import shutil
            with open(src.license_group_token, 'rb') as f:
                data = f.read()
            dest.save_group_token(data)
            shutil.copy(src.license_file, dest.reg_path)

        copy_files(master, ctx)

    logging.debug(reg.license_info)
    if reg.license_info['features'] < 15:
        raise RuntimeError('this feature is only for group license')
    Pytransform3.init(ctx)


def prepare(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--host', type=str, default=CONFIG['host'])
    parser.add_argument('-p', '--port', type=int, default=CONFIG['port'],
                        help=argparse.SUPPRESS)
    parser.add_argument('-s', '--sock', default='/var/run/docker.sock',
                        help=argparse.SUPPRESS)
    parser.add_argument('--home', help=argparse.SUPPRESS)
    parser.add_argument('-b', '--background', action='store_true',
                        help='Enable daemon mode')
    parser.add_argument('regfile', nargs='?',
                        help='group device registration file for this machine')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.home:
        CONFIG['home'] = os.path.expandvars(os.path.expanduser(args.home))

    home = os.path.join(CONFIG['home'], 'docker')

    if args.regfile in ('s', 'stop'):
        stop_daemon_proc(home)
        return

    logging.info('work path: %s', home)
    if not os.path.exists(home):
        os.makedirs(home)

    # lpath should be non-existent or empty
    ctx = Context(home=home, lpath=os.path.join(home, 'non-existent'))
    register_pyarmor(ctx, args.regfile)
    CONFIG['ctx'] = ctx

    CONFIG['machid'] = [Pytransform3.get_hd_info(x) for x in MACHFLAGS]
    logging.debug('machine id: %s', CONFIG['machid'])

    logging.info('check command `docker`')
    subprocess.check_call(['docker', '-v'])

    logging.info('check group license')
    generate_runtime_key('test group license')

    return args.host, args.port, args.background


def start_daemon_proc(args):
    command = [sys.executable, '-m', 'pyarmor.cli.docker']
    command.extend([x for x in args if x not in ('-b', '--background')])
    ctx = CONFIG['ctx']

    pidfile = os.path.join(ctx.home_path, 'auth.pid')
    logfile = os.path.join(ctx.home_path, 'auth.log')

    logging.info('log file: %s', logfile)
    with open(logfile, 'w') as f:
        if sys.platform == "win32":
            p = subprocess.Popen(
                command,
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP
                               | subprocess.CREATE_NO_WINDOW),
                stdin=subprocess.DEVNULL,
                stdout=f.fileno(),
                stderr=subprocess.STDOUT,
                close_fds=True,
            )
        else:
            p = subprocess.Popen(
                command,
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=f.fileno(),
                stderr=subprocess.STDOUT,
                close_fds=True,
            )
    with open(pidfile, 'w') as f:
        f.write('%s' % p.pid)

    try:
        logging.info('starting pyarmor-auth in background')
        p.wait(3.0)
    except Exception as e:
        logging.debug('%s', e)

    if p.returncode is not None:
        raise RuntimeError('something is wrong, please check "%s"', logfile)

    return p.pid


def stop_daemon_proc(home):
    from signal import SIGINT, SIGTERM
    pidfile = os.path.join(Context(home=home).home_path, 'auth.pid')
    try:
        with open(pidfile) as f:
            pid = f.read()

        logging.info('kill pyarmor-auth (pid: %s)', pid)
        os.kill(int(pid), SIGINT)

        logging.info('pyarmor-auth now is stopped')
        sys.exit(0)
    except FileNotFoundError:
        logging.error('no pid file "%s" found', pidfile)
    except Exception as e:
        logging.error('failed to stop pyarmor-auth: %s', e)
    sys.exit(1)


def main_entry(args):
    try:
        host, port, background = prepare(args)
    except Exception as e:
        logging.error('%s', e)
        return

    if background:
        try:
            pid = start_daemon_proc(args)
            logging.info('pyarmor-auth is running in background (%s)', pid)
            logging.info('run command `pyarmor-auth stop` to quit')
        except Exception as e:
            logging.error('%s', e)
        return

    logging.info('listen container auth request on %s:%s', host, port)
    with socketserver.TCPServer((host, port), DockerAuthHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info('bye bye')
        except Exception as e:
            logging.error('unknown error: %s', e)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s: %(message)s',
    )
    main_entry(sys.argv[1:])


#
# Deprecrated functions
#
def get_docker_gateway(client):
    filters = {
        'driver': 'bridge',
        'type': 'builtin'
    }
    networks = client.networks.list(filters=filters)
    return networks[0].attrs['IPAM']['Config'][0]['Gateway']


def get_container(client, ipaddr):
    filters = {
        'driver': 'bridge',
        'type': 'builtin'
    }
    networks = client.networks.list(filters=filters, greedy=True)
    containers = networks[0].attrs.get('Containers')
    if containers:
        marker = ipaddr + '/'
        for dockid, netattr in containers.items():
            if netattr.get('IPv4Address').startswith(marker):
                return client.containers.get(dockid)
    raise RuntimeError('no found countainer with IPv4 %s' % ipaddr)


def copy_file_into_docker(containerid, filename):
    subprocess.check_call(['docker', 'cp', filename, '%s:/' % containerid])


def get_container_info(client, shortid):
    container = client.container.get(shortid)
    return container.attrs


if __name__ == '__main__':
    main()
