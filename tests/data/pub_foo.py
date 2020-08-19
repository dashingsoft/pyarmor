def proxy_hello(q):
    from mfoo import hello
    return hello(q)


def proxy_say_hello(msg):
    from tfoo import say_hello
    return say_hello(msg)
