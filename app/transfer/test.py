

class A:
    def __init__(self, a: str):
        print(a)


class B:
    def __init__(self, c: str):
        print(c)


class C:
    def __init__(self, c: str):
        print(c)


class SUB(A, B, C):
    def __init__(self, a, b, c):
        A.__init__(self, a)
        B.__init__(self, b)
        C.__init__(self, c)

sub = SUB('a', 'b', 'c')