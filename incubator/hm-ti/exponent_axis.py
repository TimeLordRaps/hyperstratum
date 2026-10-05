"""The exponent axis under ordinatics' value map, and what it does and does not separate.

Map used (copied from fields/ordinatics `rational_power_image`): W(ω^r) = exp(r·(−log 2 + iπ)), i.e. ω ↦ −1/2
with one fixed logarithm.  Modulus |W(ω^r)| = 2^(−r); phase = π·r (mod 2π).

Checked exactly (sympy) and by argument:
  1. composable: W(ω^a·ω^b) = W(ω^a)·W(ω^b) for rational a, b (exponents add, values multiply);
  2. rank survives, reversed, in the modulus: r < s  ⇒  |W(ω^r)| > |W(ω^s)|, so the map is injective on exponents;
  3. the classes by phase e^{iπr}:  r integer → phase of order 1 or 2 (real axis);  r half-odd → order 4
     (imaginary axis);  r rational p/q → phase of finite order 2q/gcd (periodic under repeated multiplication);
     r irrational → phase of infinite order (never returns to 1);
  4. the image of ordinatics' exponent is ONE-dimensional (a logarithmic spiral): modulus and phase are both
     functions of the single parameter r, so no independent 'surreal component × imaginary component'
     product exists until the exponent itself is complex, ω^(a+bi) with a, b independent.
"""
import cmath
import math
from fractions import Fraction as Fr
from math import gcd

import sympy as sp

W = -sp.log(2) + sp.I * sp.pi


def img(r):
    return sp.exp(sp.Rational(r.numerator, r.denominator) * W)


grid = sorted({Fr(p, q) for q in range(1, 7) for p in range(-12, 13)})

# 1. composability, exactly
for a in grid[::7]:
    for b in grid[::11]:
        lhs = sp.simplify(img(a + b))
        rhs = sp.simplify(img(a) * img(b))
        assert sp.simplify(lhs - rhs) == 0, (a, b)
print("1. W(ω^a·ω^b) = W(ω^a)·W(ω^b) verified exactly on", len(grid[::7]) * len(grid[::11]), "rational pairs")

# 2. modulus strictly decreasing in r (injective on the exponent axis), exact: |W(ω^r)| = 2^(-r)
for r in grid:
    assert sp.simplify(sp.Abs(img(r)) - sp.Integer(2) ** (-sp.Rational(r.numerator, r.denominator))) == 0
mods = [2.0 ** float(-r) for r in grid]
assert all(m1 > m2 for m1, m2 in zip(mods, mods[1:]))
print("2. |W(ω^r)| = 2^(-r) exactly on the grid and strictly decreasing: order survives, reversed, in the modulus")

# 3. phase classes
def order_of_phase(r):
    """Order of e^{iπr} = e^{2πi·p/(2q)} in the circle group, for r = p/q in lowest terms."""
    p, q = r.numerator, r.denominator
    return 2 * q // gcd(2 * q, abs(p)) if p else 1


for r in grid:
    n = order_of_phase(r)
    z = sp.exp(sp.I * sp.pi * sp.Rational(r.numerator, r.denominator))
    assert sp.simplify(z ** n - 1) == 0 and all(sp.simplify(z ** k - 1) != 0 for k in range(1, n))
    if r.denominator == 1:
        assert n in (1, 2)                      # real axis
    elif r.denominator == 2:
        assert n == 4                           # imaginary axis
cls = {"real axis (integer r)": 0, "imaginary axis (half-odd r)": 0, "other rational (finite order)": 0}
for r in grid:
    if r.denominator == 1:
        cls["real axis (integer r)"] += 1
    elif r.denominator == 2:
        cls["imaginary axis (half-odd r)"] += 1
    else:
        cls["other rational (finite order)"] += 1
print("3. phase order verified exactly for", len(grid), "rationals:", cls)
print("   irrational r: e^{iπr} has no finite order (e^{iπr n} = 1 would force n·r an even integer, so r rational)")

# 4. one parameter only: modulus and phase are both read off r (numeric check of the phase, tolerance 1e-12)
for r in grid[::9]:
    z = complex(sp.N(img(r), 30))
    assert abs(abs(z) - 2.0 ** float(-r)) < 1e-12
    d = (cmath.phase(z) - math.pi * float(r)) / (2 * math.pi)
    assert abs(d - round(d)) < 1e-9, (r, d)
print("4. modulus and phase are both determined by r: a one-dimensional spiral, not a product of two axes")
