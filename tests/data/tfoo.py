import threading

import pub_foo


def say_hello(msg):
    print('Say hello from %s' % msg)


def test():
    threading.Thread(target=pub_foo.proxy_say_hello, args=('function',)).start()


if __name__ == '__main__':
    threading.Thread(target=pub_foo.proxy_say_hello, args=('module',)).start()
    test()
