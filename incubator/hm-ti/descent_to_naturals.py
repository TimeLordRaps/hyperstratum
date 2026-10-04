"""Working backwards from an infinity into the naturals, concretely.

The rewrite of LadderInduction.lean (`step`) on pairs (a, b) = ω·a + b: dropping a leading coefficient
lets the adversary refill b with any natural m. The position ω·a + b is an infinite ordinal, yet every run
from it is a finite descent ending at (0,0). The run length is *not* bounded by any function of the
finite data (a, b) alone: it is bounded only by the ordinal (that is what ω² induction proves).
"""
import random


def run_length(a, b, adversary):
    n = 0
    while (a, b) != (0, 0):
        if a > 0:
            a, b = a - 1, adversary(n)
        else:
            b -= 1
        n += 1
    return n


# from ω (= (1,0)) the adversary picks m, run length is m + 1: unbounded over adversaries
for m in (0, 1, 10, 1000, 10**6):
    n = run_length(1, 0, lambda _: m)
    assert n == m + 1
print("ω: run lengths m+1 for m = 0, 1, 10, 1000, 10^6: finite each, unbounded over the choice")

# from ω·2: length depends on two successive choices
random.seed(1)
for _ in range(2000):
    a, b = random.randint(0, 4), random.randint(0, 6)
    ms = [random.randint(0, 9) for _ in range(64)]
    n = run_length(a, b, lambda i: ms[i % 64])
    assert n >= 0
print("2000 random starts and adversaries: every run reached (0,0)")
