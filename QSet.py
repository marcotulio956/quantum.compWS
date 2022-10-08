from ket import *

class QSet:
    def __init__(self):
        self.authors = ["Gabriel Siqueira :D ", "Marco Tulio xD "]

    @staticmethod
    def gcd(a : int, b : int) -> int: #euclides
        if(a==b):
            return b
        else:
            if a > b:
                return QSet.gcd(a-b,b)
            else:
                return QSet.gcd(b-a,a)

    @staticmethod
    def pown():
        pass
    @staticmethod
    def qft(q):
        lambd = lambda k : pi*k/2
        for i in range(len(q)):
            for j in range(i):
                ctrl(q(i), u1, lambd(i-j), q(j))
            H(q(i))
    @staticmethod
    def shors_quantum_subroutine(N, x) -> int:
        from functools import reduce

        n = N.bit_length()

        def subroutine():
            reg1 = H(quant(n))
            reg2 = QSet.pown(x, reg1, n)
            measure(reg2)
            adj(QSet.qft, reg1)
            return measure(reg1).value
        
        r = reduce(QSet.gcd, [subroutine() for _ in range(n)])
        return 2**n//r

