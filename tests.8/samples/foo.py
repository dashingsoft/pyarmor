import sys

data = 'abcxyz'

def hello(msg):
    print('hello world')
    print(msg)

def sum2(a, b):
    return a + b

def main(msg):
    a = 2
    b = 6
    hello(msg)
    print('%s + %s = %d' % (a, b, sum2(a, b)))

if __name__ == '__main__':
    main('pass: %s' % data)
