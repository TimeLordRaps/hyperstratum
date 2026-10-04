"""Exhaustive search: can ordinalApply be *defined* on hypermath's own 6-element countermodel
so that the three refuted L3 claims hold?

Model copied verbatim from fields/hypermath/lean4/FiniteActionCountermodel.lean (pinned):
f2f a0->a1->a2->a1, b0->b1->b2->b0; congruence classes a0:0 a1:1 a2:2 b0:3 b1:1 b2:2;
ground=a0; ordinalSucc=f2f; DerivationPath=Nat; compose=+; pathLength n = f2f^n ground.

Claims (exact types from that file):
  zero : forall x, Congruent (ordinalApply ground x) x
  succ : forall p x, Congruent (ordinalApply (ordinalSucc p) x) (f2f (ordinalApply p x))
  path : forall p q, Congruent (pathLength (p+q)) (ordinalApply (pathLength q) (pathLength p))

ordinalApply(p, x) = g_x(p). The claims decouple per x except `path`, which constrains
g_x for x in {pathLength p}. Search space per x: 6^6.
"""
from itertools import product

F = ["a0", "a1", "a2", "b0", "b1", "b2"]
f2f = {"a0": "a1", "a1": "a2", "a2": "a1", "b0": "b1", "b1": "b2", "b2": "b0"}
cls = {"a0": 0, "a1": 1, "a2": 2, "b0": 3, "b1": 1, "b2": 2}
ground = "a0"


def it(n, x):
    for _ in range(n):
        x = f2f[x]
    return x


def ok_zero_succ(x, g):
    if cls[g[ground]] != cls[x]:
        return False
    return all(cls[g[f2f[p]]] == cls[f2f[g[p]]] for p in F)


sols = {x: [dict(zip(F, vals)) for vals in product(F, repeat=6) if ok_zero_succ(x, dict(zip(F, vals)))] for x in F}
for x in F:
    print(f"x={x}: {len(sols[x])} choices of ordinalApply(-, x) satisfy zero+succ")

N = 12  # pathLength is periodic with period <= 3 after one step; 12 covers it
reach = sorted({it(p, ground) for p in range(N)})
found = None
for combo in product(*(sols[x] for x in reach)):
    g = dict(zip(reach, combo))
    if all(cls[it(p + q, ground)] == cls[g[it(p, ground)][it(q, ground)]] for p in range(N) for q in range(N)):
        found = g
        break
print("zero+succ+path simultaneously satisfiable:", found is not None and all(sols[x] for x in F))

if __name__ == "__main__" and found is not None:
    # complete the table for x outside the reachable chain with any zero+succ solution
    table = {x: (found[x] if x in found else sols[x][0]) for x in F}
    print("ordinalApply table, rows p, columns x:")
    for p in F:
        print(" ", p, [table[x][p] for x in F])
