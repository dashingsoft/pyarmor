from .foo import hello


title = 'PyArmor Test Case'


def open_hello(msg):
    print('This is public hello: %s' % msg)


def proxy_hello(msg):
    print('This is proxy hello: %s' % msg)
    hello(msg)
