from multiprocessing import Process
import os

def info(title):
    print(title)
    print('module name: %s' % __name__)
    if hasattr(os, 'getppid'):  # only available on Unix
        print('parent process: %s' % os.getppid())
    print('process id: %s' % os.getpid())

def f(name):
    info('function f')
    print('hello %s' % name)

def main():
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()

if __name__ == '__main__':
    main()
