from ket import *

class QSet:
    def __init__(self):
        self.authors = ["Gabriel Siqueira", "Marco Tulio"]

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
    def apjmodN(a, p, j, N):
        import numpy as np
        for i in range(j):
            a = np.mod(a**p, N)
        return a

    @staticmethod
    def unitary_op():
        pass

    @staticmethod
    def mod_exp():
        c = quant()
        # with control(c):
        
    @staticmethod
    def shors_quantum_subroutine(N, x) -> int:
        from functools import reduce
        from ket.lib import qft

        n = N.bit_length()

        def subroutine():
            reg1 = H(quant(n))
            reg3 = measure(reg1)
            reg2 = 1
            for i in range(n):
                reg2 = reg2 * reg3
            reg2 = reg2 - (reg2//N * N)
            adj(qft, reg1)
            return measure(reg1).value
        
        from math import gcd
        r = reduce(gcd, [subroutine() for _ in range(n)])
        return 2**n//r

