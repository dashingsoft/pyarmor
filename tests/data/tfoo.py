import threading

from pub_foo import proxy_say_hello


def say_hello(msg):
    print('Say hello from %s' % msg)


def test():
    threading.Thread(target=proxy_say_hello, args=('function',)).start()


if __name__ == '__main__':
    threading.Thread(target=proxy_say_hello, args=('module',)).start()
    test()
