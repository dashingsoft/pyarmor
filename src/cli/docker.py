import argparse
import logging
import os
import socketserver
import struct
import sys

from .context import Context
from .generate import Builder, Pytransform3
from .register import Register


CONFIG = {
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
        if packet[:4] == b'PADH':
            response = b'\n'.join(CONFIG['machid']) + b'\x00'
            self.request.send(response)
        else:
            userdata = self.parse_packet(packet)
            keydata = self.generate_runtime_key(userdata.decode('utf-8'))
            response = struct.pack('!HH', 0, len(keydata)) + keydata
            self.request.send(response)
        return response

    def parse_packet(self, packet):
        if len(packet) == 32 and packet[:4] == b'PADK':
            return packet[12:]
        raise RuntimeError('invalid auth request')

    def generate_runtime_key(self, userdata):
        ctx = CONFIG['ctx']
        ctx.cmd_options['user_data'] = userdata
        return Builder(ctx).generate_runtime_key()


def register_pyarmor(ctx, regfile):
    reg = Register(ctx)
    logging.info('register "%s"', regfile)
    reg.register_regfile(regfile)
    if reg.license_info['features'] < 15:
        raise RuntimeError('this feature is only for group license')
    Pytransform3._update_token(ctx)


def main_entry():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
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

    ctx = Context(home=home)
    register_pyarmor(ctx, args.regfile[0])
    CONFIG['ctx'] = ctx

    mflags = 20, 18, 16, 11, 10
    CONFIG['machid'] = [Pytransform3.get_hd_info(x) for x in mflags]
    logging.debug('machine id: %s', CONFIG['machid'])

    host, port = '0.0.0.0', args.port
    with socketserver.TCPServer((host, port), DockerAuthHandler) as server:
        logging.info('listen container auth request on %s:%s', host, args.port)
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
