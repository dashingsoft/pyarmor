import multiprocessing as mp

import pub_foo


def hello(q):
    print('module name: %s' % __name__)
    q.put('hello')


if __name__ == '__main__':
    try:
        ctx = mp.get_context('spawn')
    except Exception:
        ctx = mp
    q = ctx.Queue()
    p = ctx.Process(target=pub_foo.proxy_hello, args=(q,))
    p.start()
    print(q.get())
    p.join()
