import argparse
import logging
import os
import socketserver
import struct
import sys

import docker

from .context import Context
from .generate import Builder
from .register import Register

PORT = 29092


def get_docker_gateway(client):
    filters = {
        'driver': 'bridge',
        'type': 'builtin'
    }
    networks = client.networks.list(filters=filters)
    return networks[0].attrs['IPAM']['Config'][0]['Gateway']


class DockerAuthHandler(socketserver.BaseRequestHandler):

    WORKPATH = os.path.expanduser(os.path.join('~', '.pyarmor', 'docker'))
    CTX = None
    CLIENT = None

    def handle(self):
        data = self.request.recv(64)
        logging.info('receive request from %s', self.client_address)
        try:
            logging.debug('data (%d): %s', len(data), data)
            self.process(data)
            logging.info('send auth result to %s', self.client_address)
        except Exception as e:
            logging.error('%s', str(e))
            msg = 'failed to verify docker, please check host console'.encode()
            msg += b'\00'
            self.request.send(struct.pack('!HH', 1, len(msg)) + msg)

    def copy_file_into_docker(self, containerid, filename):
        from subprocess import check_call
        check_call(['docker', 'cp', filename, '%s:/' % containerid])

    def get_container_info(self, client, shortid):
        try:
            container = client.container.get(shortid)
            return container.attrs
        except docker.errors.NotFound:
            pass
        except docker.errors.APIError:
            pass

    def process(self, packet):
        container = self.get_container(self.client_request[0])
        state = container.attrs['State']
        if state.get('Status') == 'running' and state.get('Running') == 'True':
            # 2023-06-15T23:51:03.287483366Z
            # state.get('StartedAt')
            # bridge = container.attrs['NetworkSettings']['Networks']['bridge']
            # bridge['MacAddress']
            # bridge['Gateway'] and bridge['IPAddress']
            # bridge['IPv6Gateway'] and bridge['GlobalIPv6Address']
            userdata = self.parse_packet(packet)
            keydata = self.generate_runtime_key(userdata)
            self.request.send(struct.pack('!HH', 0, len(keydata)) + keydata)

    def parse_packet(self, packet):
        if len(packet) == 32 and packet[:4] == b'PADK':
            return packet[12:]
        raise RuntimeError('invalid auth request')

    def generate_runtime_key(self, userdata):
        ctx = self.CTX
        ctx.cmd_options['user_data'] = userdata
        return Builder(ctx).generate_runtime_key()

    def get_container(self, ipaddr):
        filters = {
            'driver': 'bridge',
            'type': 'builtin'
        }
        networks = self.CLIENT.networks.list(filters=filters, greedy=True)
        containers = networks[0].attrs.get('Containers')
        if containers:
            marker = ipaddr + '/'
            for dockid, netattr in containers.items():
                if netattr.get('IPv4Address').startswith(marker):
                    return self.CLIENT.containers.get(dockid)
        raise RuntimeError('no found countainer with IPv4 %s' % ipaddr)


def register_pyarmor(ctx, regfile):
    reg = Register(ctx)
    logging.info('register "%s"', regfile)
    reg.register_regfile(regfile)
    if reg.license_info['features'] < 15:
        raise RuntimeError('this feature is only for group license')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=PORT)
    parser.add_argument('-s', '--sock', default='/var/run/docker.sock')
    parser.add_argument('--home')
    parser.add_argument('regfile', required=True)
    args = parser.parse_args(sys.argv[1:])

    home = DockerAuthHandler.WORKPATH
    if args.home:
        DockerAuthHandler.WORKPATH = args.home
        home = args.home
    logging.info('work path: %s', home)

    ctx = Context(home=os.path.expanduser(home))
    register_pyarmor(ctx, args.regfile)
    DockerAuthHandler.CTX = ctx

    client = docker.from_env()
    host, port = get_docker_gateway(client), args.port
    DockerAuthHandler.CLIENT = client

    with socketserver.TCPServer((host, port), DockerAuthHandler) as server:
        logging.info('listen docker auth request on %s:%s', host, args.port)
        server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s: %(message)s',
    )
    main()
