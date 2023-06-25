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
            logging.debug('data (%d): %s', len(data), data)
            self.process(data)
            logging.info('send auth result to %s', self.client_address)
        except Exception as e:
            logging.error('%s', str(e))
            msg = 'failed to verify docker, please check host console'.encode()
            msg += b'\00'
            self.request.send(struct.pack('!HH', 1, len(msg)) + msg)

    def process(self, packet):
        if packet[:4] == b'PADH':
            self.request.send(CONFIG['machid'])
        else:
            userdata = self.parse_packet(packet)
            keydata = self.generate_runtime_key(userdata.decode('utf-8'))
            self.request.send(struct.pack('!HH', 0, len(keydata)) + keydata)

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
    parser.add_argument('-p', '--port', type=int, default=CONFIG['port'],
                        help=argparse.SUPPRESS)
    parser.add_argument('-s', '--sock', default='/var/run/docker.sock',
                        help=argparse.SUPPRESS)
    parser.add_argument('--home', help=argparse.SUPPRESS)
    parser.add_argument('regfile', nargs=1,
                        help='group device registration file for this machine')
    args = parser.parse_args(sys.argv[1:])

    if args.home:
        CONFIG['home'] = os.path.expandvars(os.path.expanduser(args.home))
    home = CONFIG['home']
    logging.info('work path: %s', home)

    ctx = Context(home=home)
    register_pyarmor(ctx, args.regfile[0])
    CONFIG['ctx'] = ctx

    CONFIG['machid'] = Pytransform3.get_hd_info(11)
    logging.debug('machine id: %s', CONFIG['machid'])

    host, port = '0.0.0.0', args.port
    with socketserver.TCPServer((host, port), DockerAuthHandler) as server:
        logging.info('listen docker auth request on %s:%s', host, args.port)
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
