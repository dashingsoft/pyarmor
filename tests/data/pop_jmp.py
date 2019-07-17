def jmp_simple(n):
    return 3 if n == 0 else 5


def jmp_short(n):
    if n == 0:
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
        n += 1
    return n


if __name__ == '__main__':
    print("jmp_simple return %s" % jmp_simple(0))
    print("jmp_short return %s" % jmp_short(0))
