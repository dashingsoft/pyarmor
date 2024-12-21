from threading import Thread


def info(title):
    print(title)
    print('module name:', __name__)


def f(name):
    info('function f')
    print('hello', name)


if __name__ == '__main__':
    tlist = []
    for i in range(10):
        p = Thread(target=f, args=('bob',))
        p.start()
        tlist.append(p)
    for p in tlist:
        p.join()
