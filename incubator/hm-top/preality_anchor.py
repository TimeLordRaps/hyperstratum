"""A finite toy for 'anchor preality at the big bang and at now, run it in infinite time in finite space'.

System: Arnold's cat map on the n x n torus of integer states, (x, y) -> (2x + y, x + y) mod n. It is a bijection
(reversible, chaotic), so its state space is finite and every state has exactly one past and one future.
Macrostates are b x b blocks (coarse-graining = what an observer can fix).

Checked:
  1. infinite time in finite space is a loop: C^P = identity for a finite period P, so the forward run visits at most
     P states from any start and adds no information after one lap; an exhaustive run is exact enumeration of a finite set;
  2. the past is unique for a microstate (running backwards from the full present state is well-defined and exact),
     but the *timelines converging on a macro-moment* are one per compatible microstate (b*b of them here);
  3. anchoring both ends (macrostate at t=0 and macrostate at t=T) partitions those timelines: summed over all final
     macrostates the consistent timelines are exactly b*b, and for T past the mixing time each final macrostate keeps
     about b*b / (number of macrostates): the second anchor 'locks' the landmark by that factor, a two-boundary problem.
"""
n, b = 60, 10
STATES = [(x, y) for x in range(n) for y in range(n)]


def fwd(s):
    x, y = s
    return ((2 * x + y) % n, (x + y) % n)


def bwd(s):
    x, y = s
    return ((x - y) % n, (-x + 2 * y) % n)


def block(s):
    return (s[0] // b, s[1] // b)


# 0. reversibility: bijection with the stated inverse
assert sorted(map(fwd, STATES)) == sorted(STATES)
assert all(bwd(fwd(s)) == s and fwd(bwd(s)) == s for s in STATES)
print("0. the cat map on", len(STATES), "states is a bijection with an exact inverse: every state has one past and one future")


# 1. a finite loop
def matmul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) % n for j in range(2)) for i in range(2))


M, IDENT = ((2, 1), (1, 1)), ((1, 0), (0, 1))
P, A = 1, M
while A != IDENT:
    A, P = matmul(A, M), P + 1
s = (7, 13)
t = s
orbit = {s}
for _ in range(P):
    t = fwd(t)
    orbit.add(t)
assert t == s and len(orbit) <= P
print(f"1. period P = {P}: the infinite forward run from {s} visits {len(orbit)} states and then repeats exactly")

# 2. one past per microstate, many per macrostate
M0 = (2, 3)
micro_in_M0 = [s for s in STATES if block(s) == M0]
assert len(micro_in_M0) == b * b
T = 200
past = {s: s for s in micro_in_M0}
for _ in range(T):
    past = {s: bwd(p) for s, p in past.items()}
assert len(set(past.values())) == b * b  # distinct microstates keep distinct pasts
print(f"2. macro-moment {M0}: {b * b} microstates, hence {b * b} distinct timelines, each with a unique exact past")

# 3. second anchor
T = 100
counts = {}
for s in micro_in_M0:
    t = s
    for _ in range(T):
        t = fwd(t)
    counts[block(t)] = counts.get(block(t), 0) + 1
assert sum(counts.values()) == b * b
nblocks = (n // b) ** 2
mean = (b * b) / nblocks
worst = max(counts.values())
assert worst <= 12 * mean, (worst, mean)
print(f"3. anchoring a second macro-moment at T={T} keeps {min(counts.values())}..{worst} of the {b * b} timelines "
      f"(mean {mean:.1f} over {nblocks} possible end-macrostates): the landmark locks by about a factor {nblocks}")
