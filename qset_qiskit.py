# qset.py

from math import gcd
from fractions import Fraction

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.circuit.library import UnitaryGate
from qiskit_aer import AerSimulator


def _modular_multiplication_matrix(a, N, n):
    """
    Matrix for

        |y> -> |a*y mod N>

    for y < N.

    States y >= N are left unchanged.

    This is only practical for small N.
    """
    dim = 2 ** n

    U = [[0j for _ in range(dim)] for _ in range(dim)]

    for y in range(dim):
        if y < N:
            z = (a * y) % N
        else:
            z = y

        U[z][y] = 1.0

    return U


def _controlled_modular_multiplication(a, N, n):
    """
    Controlled modular multiplication:

        |0>|y> -> |0>|y>
        |1>|y> -> |1>|a*y mod N>

    for y < N.
    """

    dim = 2 ** n

    U = [[0j for _ in range(2 * dim)] for _ in range(2 * dim)]

    for y in range(dim):

        # control = 0
        U[y][y] = 1.0

        # control = 1
        if y < N:
            z = (a * y) % N
        else:
            z = y

        U[dim + z][dim + y] = 1.0

    return U


def _controlled_modular_power(x, power, N, n):
    """
    Controlled operation

        |c>|y> -> |c>|x^power * y mod N>

    when c = 1.

    Used for the controlled-U^(2^j) operations
    in quantum phase estimation.
    """

    a = pow(x, power, N)

    U = _controlled_modular_multiplication(a, N, n)

    return UnitaryGate(
        U,
        label=f"x^{power} mod {N}"
    )


def _continued_fraction_denominator(value, Q, N):
    """
    Recover a candidate order r from a measured phase

        value / Q ≈ s / r

    using continued fractions.
    """

    phase = value / Q

    frac = Fraction(phase).limit_denominator(N)

    return frac.denominator


def shors_quantum_subroutine(N, x):
    """
    Qiskit quantum order-finding subroutine.

    Signature is compatible with:

        shor(N, quantum_subroutine=...)

    Returns:
        A candidate order r of x modulo N.

    NOTE:
        This implementation constructs explicit unitary matrices and
        is therefore intended for small demonstration instances.
    """

    if gcd(x, N) != 1:
        raise ValueError(
            f"x={x} is not coprime with N={N}"
        )

    # Number of qubits needed to represent N.
    n = N.bit_length()

    # Number of phase-estimation qubits.
    #
    # 2n is the usual choice for Shor's order finding.
    t = 2 * n

    # ------------------------------------------------------------
    # Registers
    # ------------------------------------------------------------

    phase = QuantumRegister(t, "phase")
    work = QuantumRegister(n, "work")

    classical = ClassicalRegister(t, "c")

    qc = QuantumCircuit(
        phase,
        work,
        classical
    )

    # ------------------------------------------------------------
    # |phase> = |+>^t
    # ------------------------------------------------------------

    qc.h(phase)

    # ------------------------------------------------------------
    # Initialize work register to |1>
    # ------------------------------------------------------------

    qc.x(work[0])

    # ------------------------------------------------------------
    # Controlled modular exponentiation
    #
    # U_x:
    #
    #     |y> -> |x y mod N>
    #
    # Therefore
    #
    #     U_x^(2^j)
    #
    # performs multiplication by
    #
    #     x^(2^j) mod N.
    # ------------------------------------------------------------

    for j in range(t):

        power = 2 ** j

        U = _controlled_modular_power(
            x,
            power,
            N,
            n
        )

        # The matrix has control as the first qubit.
        #
        # Qiskit therefore receives the control followed by
        # all work qubits.
        # gate = U.to_gate()

        qc.append(
            U,
            [phase[j]] + list(work)
        )

    # ------------------------------------------------------------
    # Inverse QFT
    # ------------------------------------------------------------

    iqft = QFT(
        num_qubits=t,
        inverse=True,
        do_swaps=True
    ).inverse().decompose()

    qc.compose(
        iqft,
        qubits=phase,
        inplace=True
    )

    # ------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------

    qc.measure(
        phase,
        classical
    )

    # ------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------

    simulator = AerSimulator()

    result = simulator.run(
        qc,
        shots=1
    ).result()

    counts = result.get_counts()

    measured = next(iter(counts))

    # Qiskit classical strings are printed MSB -> LSB.
    y = int(measured, 2)

    Q = 2 ** t

    # ------------------------------------------------------------
    # Classical continued fraction step
    # ------------------------------------------------------------

    r = _continued_fraction_denominator(
        y,
        Q,
        N
    )

    # ------------------------------------------------------------
    # Continued fractions only give a candidate denominator.
    #
    # It may be a divisor of the actual order.
    # Search small multiples until we find the order.
    # ------------------------------------------------------------

    if r == 0:
        return None

    for k in range(1, N + 1):

        candidate = k * r

        if candidate >= N:
            break

        if pow(x, candidate, N) == 1:
            return candidate

    return r


class QSet:
    """
    Namespace matching your desired API.
    """

    shors_quantum_subroutine = staticmethod(
        shors_quantum_subroutine
    )