def g(x):
    print('g--> x=', x)
    if x == 1:
        return 1
    if x == 2:
        return 2
    return 3


for i in range(1, 4):
    print(f'g({i})=', g(i))


if [g(i) for i in range(1, 4)] == [1, 2, 3]:
    print('All test passed')
