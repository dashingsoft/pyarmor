import mfoo
import tfoo


def proxy_hello(q):
    return mfoo.hello(q)


def proxy_say_hello(msg):
    return tfoo.say_hello(msg)
