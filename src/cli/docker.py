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
import sys

from .context import Context
from .generate import Pytransform3
from .register import Register, MACHFLAGS


CONFIG = {
    'host': '0.0.0.0',
    'port': 29092,
    'home': os.path.expanduser(os.path.join('~', '.pyarmor', 'docker')),
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
            rtkey = self.generate_runtime_key(userdata)
            response = struct.pack('!HH', 0, len(rtkey)) + rtkey
            self.request.send(response)
        else:
            raise RuntimeError('unknown packet %r' % packet)
        return response

    def parse_packet(self, packet):
        if len(packet) == 32 and packet[:4] == b'PADK':
            return packet[12:]
        raise RuntimeError('invalid auth request: %r' % packet)

    def generate_runtime_key(self, userdata):
        ctx = CONFIG['ctx']
        ctx.cmd_options['user_data'] = userdata
        ctx.cmd_options['expired'] = '.3'
        ctx.cmd_options['outer'] = 0
        Pytransform3._pytransform3.init_ctx(ctx)
        return Pytransform3.generate_runtime_key(ctx)

    def generate_outer_key(self, userdata, outer=True):
        ctx = CONFIG['ctx']
        ctx.cmd_options['user_data'] = userdata
        ctx.cmd_options['expired'] = '.3'
        ctx.cmd_options['outer'] = 1
        Pytransform3._pytransform3.init_ctx(ctx)
        return Pytransform3.generate_runtime_key(ctx, outer=outer)


def register_pyarmor(ctx, regfile):
    reg = Register(ctx)
    logging.info('register "%s"', regfile)
    reg.register_regfile(regfile)
    if reg.license_info['features'] < 15:
        raise RuntimeError('this feature is only for group license')
    Pytransform3.init(ctx)


def main_entry():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--host', type=str, default=CONFIG['host'])
    parser.add_argument('-p', '--port', type=int, default=CONFIG['port'],
                        help=argparse.SUPPRESS)
    parser.add_argument('-s', '--sock', default='/var/run/docker.sock',
                        help=argparse.SUPPRESS)
    parser.add_argument('--home', help=argparse.SUPPRESS)
    parser.add_argument('regfile', nargs=1,
                        help='group device registration file for this machine')
    args = parser.parse_args(sys.argv[1:])

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.home:
        CONFIG['home'] = os.path.expandvars(os.path.expanduser(args.home))
    home = CONFIG['home']
    logging.info('work path: %s', home)

    # lpath should be non-existent or empty
    ctx = Context(home=home, lpath=os.path.join(home, 'non-existent'))
    register_pyarmor(ctx, args.regfile[0])
    CONFIG['ctx'] = ctx

    CONFIG['machid'] = [Pytransform3.get_hd_info(x) for x in MACHFLAGS]
    logging.debug('machine id: %s', CONFIG['machid'])

    host, port = args.host, args.port
    with socketserver.TCPServer((host, port), DockerAuthHandler) as server:
        logging.info('listen container auth request on %s:%s', host, port)
        server.serve_forever()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s: %(message)s',
    )
    main_entry()


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
    from subprocess import check_call
    check_call(['docker', 'cp', filename, '%s:/' % containerid])


def get_container_info(client, shortid):
    container = client.container.get(shortid)
    return container.attrs


if __name__ == '__main__':
    main()
