from math import log2, gcd
from random import Random
from time import time
from datetime import datetime, timezone, timedelta


def is_prime(n: int) -> bool:
    """
    Primality test using 6k+-1 optimization.

    Font: https://en.wikipedia.org/wiki/Primality_test#Simple_methods
    """
    if n <= 3:
        return n > 1
    if not n % 2 or not n % 3:
        return False
    i = 5
    stop = int(n**0.5)
    while i <= stop:
        if not n % i or not n % (i + 2):
            return False
        i += 6
    return True


def _factor_pow_a_b(N):
    n = N.bit_length()
    y = int(log2(N))
    for b in range(2, n+1):
        x = y/b
        u1 = int(2**x)
        u2 = u1+1

        if u1**b == N:
            return u1
        elif u2**b == N:
            return u2


def _quantum_subroutine(N, x):
    from functools import reduce
    from ket import quant, H, measure, adj
    from ket.lib import qft
    from ket.plugins import pown

    n = N.bit_length()

    def subroutine():
        reg1 = H(quant(n))
        
        reg2 = pown(x, reg1, N)

        measure(reg2)
        adj(qft, reg1)
        return measure(reg1).value

    r = reduce(gcd, [subroutine() for _ in range(n)])
    return 2**n//r


def shor(N: int, quantum_subroutine=_quantum_subroutine, quantum: bool = False, seed=None, verbose=False, _timezone=-3) -> int:
    """
    Shor's factorization algorithm

    The `quantum_subroutine` must have the signature:

        def quantum_subroutine(N: int, x: int) -> int:
            ...

    Args:
        N: Number to factor.
        quantum_subroutine: Order-ﬁnding quantum subroutine to ﬁnd the order of f(j) = x^j % N.
        quantum: If True checks whether N is trivially factorable AND force use the quantum subroutine.
        seed: RNG seed. Not used in quantum simulation.
        verbose: If True print the result and execution time.

    Returns:
        A factor of the number N.

    Raises:
        ValueError: If quantum is True and N is trivially factorable OR N is prime.
        RuntimeError: If the algorithm fails to factor N.
    """

    if N < 4:
        raise ValueError(f"{N} is prime")

    if N % 2 == 0:
        if quantum:
            raise RuntimeError(f'{N} is trivially factorable')
        else:
            return 2

    factor = _factor_pow_a_b(N)
    if factor is not None:
        if quantum:
            raise RuntimeError(f'{N} is trivially factorable')
        else:
            return factor

    rng = Random(seed)

    factor = None

    begin = time()

    for _ in range(N.bit_length()):
        while True:
            x = rng.randint(2, N-1)
            gcd_x_N = gcd(x, N)
            if gcd_x_N > 1 and not quantum:
                return gcd_x_N
            elif gcd_x_N == 1:
                break

        r = quantum_subroutine(N, x)

        if r % 2 == 0 and pow(x, r//2) != -1 % N:
            p = gcd(x**(r//2)-1, N)
            if p != 1 and p != N and p*N//p == N:
                end = time()
                factor = p
                break

            q = gcd(x**(r//2)+1, N)
            if q != 1 and q != N and q*N//q == N:
                end = time()
                factor = q
                break

    if factor is not None:
        if verbose:
            total = end-begin
            min = int(total // 60)
            s = total % 60
            date = datetime.now(timezone(timedelta(hours=_timezone)))
            date = date.strftime('%d/%m/%Y %H:%M:%S')
            print(
                f"Shor's algorithm: {N}={factor}x{N//factor}\t({min}min {s:.2f}s; {date})")
        return factor
    elif is_prime(N):
        raise ValueError(f"{N} is prime")
    else:
        raise RuntimeError(f"fails to factor {N}")


if __name__ == '__main__':
    from itertools import combinations

    prime_list = [5, 11, 17, 23, 29, 41, 47, 53, 59, 71, 83, 89, 101, 107,
                  113, 131, 137, 149, 167, 173, 179, 191, 197, 227, 233, 239, 251, 257, 263]

    import sys
    if sys.argv[1]:
        try:
            f = shor(int(sys.argv[1]),  quantum=True, verbose=True)
        except Exception as e:
            print(e)
    else:
        for N in sorted([p*q for p, q in combinations(prime_list, 2)]):
            try:
                f = shor(N,  quantum=True, verbose=True)
            except Exception as e:
                print(e)
                continue

        assert (N == f*(N//f))
