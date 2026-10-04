"""The average as a fold, occurring fractally up the tower: checks on surreal birthdays.

Construction (the fold): day 0 = {0}; on day n+1 every gap between consecutive numbers
born so far is folded at its average (midpoint), and the two ends extend by one.

Independent oracle: Conway's rule that a new number is the *simplest* (earliest-born)
number strictly between its neighbours, with the closed-form birthday of a dyadic
m/2^k in lowest terms (k >= 1): floor(|x|) + 1 + k; of an integer n: |n|.

Checks:
  A. every number the fold produces has the oracle birthday of the day it appears;
  B. in every gap, the simplest number strictly between is exactly the average;
  C. fractal: inside each gap of day k, the numbers born over the next d days are an
     affine copy of those born inside (0, 1) over its next d days;
  D. limits: the fold path toward 1/3 (a sign expansion) converges at rate 2^-n, so the
     fold run transfinitely reaches non-dyadic reals, while omega itself = {0,1,2,...|}
     is reached by the ends, not by any average.
"""
from fractions import Fraction as Q
from math import floor

DAYS = 9


def birthday(x: Q) -> int:
    if x.denominator == 1:
        return abs(x.numerator)
    k = x.denominator.bit_length() - 1
    return floor(abs(x)) + 1 + k


def fold_days(n):
    born = {Q(0): 0}
    for day in range(1, n + 1):
        xs = sorted(born)
        new = [(a + b) / 2 for a, b in zip(xs, xs[1:])] + [xs[-1] + 1, xs[0] - 1]
        for v in new:
            born[v] = day
    return born


def simplest_between(a: Q, b: Q, born: dict) -> Q:
    inside = [x for x in born if a < x < b]
    return min(inside, key=lambda x: (birthday(x), abs(x)))


born = fold_days(DAYS)
assert all(birthday(x) == d for x, d in born.items()), "A failed"
print(f"A  {len(born)} numbers over {DAYS} days: fold day == Conway birthday for all")

for day in range(DAYS - 1):
    xs = sorted(x for x, d in born.items() if d <= day)
    for a, b in zip(xs, xs[1:]):
        assert simplest_between(a, b, born) == (a + b) / 2, ("B failed", a, b)
print(f"B  in every gap of days 0..{DAYS - 2}, simplest-between == average")

d = 4
ref = sorted(x for x, t in born.items() if 0 < x < 1 and t <= 1 + d)
for day in range(1, DAYS - d):
    xs = sorted(x for x, t in born.items() if t <= day)
    for a, b in zip(xs, xs[1:]):
        if a >= 0 and b <= 1 or a >= 1:  # inner gaps (the end gaps grow by +1, not by folding)
            inner = sorted((x - a) / (b - a) for x, t in born.items() if a < x < b and t <= day + d)
            assert inner == ref, ("C failed", a, b)
print(f"C  every inner gap reproduces the (0,1) fold pattern over the next {d} days")

target, lo, hi, x, path = Q(1, 3), None, None, Q(0), []
for n in range(1, 40):
    sign = "+" if target > x else "-"
    path.append(sign)
    if sign == "+":
        lo = x
        x = x + 1 if hi is None else (x + hi) / 2
    else:
        hi = x
        x = x - 1 if lo is None else (lo + x) / 2
    if n >= 3:
        assert abs(x - target) <= Q(1, 2 ** (n - 2)), ("D failed", n, x)
print("D  fold path to 1/3:", "".join(path[:16]), "... converges at rate 2^-n")
