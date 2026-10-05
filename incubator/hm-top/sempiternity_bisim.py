"""Is sempiternity S bisimilar to its container universempiternity U?

Containment graph: an edge A -> B means "A contains B". Realities r1..r5 are leaves. Bisimilar = same block of the
coarsest partition in which equivalent nodes have the same set of successor blocks (partition refinement).

All 16 combinations of four yes/no clauses are enumerated:
  s_self  S contains S          u_self  U contains U
  u_has_s U contains S          u_real  U contains the realities directly (containment closed transitively)
Derivation (written before running the enumeration): S's successors always include the leaf block, so S ~ U needs
u_real. The non-leaf successor blocks are {[S]} if s_self else {} for S, and {[S]} if (u_self or u_has_s) else {} for U
(U's own block equals S's block under S ~ U). Equality of those sets gives
  S ~ U  iff  u_real  and  (s_self == (u_self or u_has_s)).
Reading: S and U are bisimilar exactly when they agree on whether each holds a copy of the whole, once U's containment is
closed over the realities. The owner's question, "only U contains S and itself, S contains neither", has s_self false
and u_has_s true, so it is NOT bisimilar; give S a self-containing copy and it is.
"""
import itertools

R = ["r1", "r2", "r3", "r4", "r5"]


def bisim(nodes, edges):
    block = {n: 0 for n in nodes}
    while True:
        sig = {n: (block[n], frozenset(block[m] for (a, m) in edges if a == n)) for n in nodes}
        ids = {}
        new = {n: ids.setdefault(sig[n], len(ids)) for n in nodes}
        if len(set(new.values())) == len(set(block.values())):
            return new
        block = new


def variant(s_self, u_self, u_has_s, u_real):
    nodes = ["S", "U"] + R
    edges = [("S", r) for r in R]
    if s_self:
        edges.append(("S", "S"))
    if u_self:
        edges.append(("U", "U"))
    if u_has_s:
        edges.append(("U", "S"))
    if u_real:
        edges += [("U", r) for r in R]
    return nodes, edges


print("s_self u_self u_has_s u_real | S ~ U")
count = 0
for s_self, u_self, u_has_s, u_real in itertools.product([False, True], repeat=4):
    n, e = variant(s_self, u_self, u_has_s, u_real)
    p = bisim(n, e)
    got = p["S"] == p["U"]
    expected = u_real and (s_self == (u_self or u_has_s))
    assert got == expected, (s_self, u_self, u_has_s, u_real, got)
    count += got
    print(f"{s_self!s:6} {u_self!s:6} {u_has_s!s:7} {u_real!s:6} | {got}")
print(f"A. all 16 variants match: S ~ U iff u_real and (s_self == (u_self or u_has_s)); {count} of 16 are bisimilar")

n, e = variant(False, True, True, True)  # U contains S, itself and the realities; S contains only the realities
assert bisim(n, e)["S"] != bisim(n, e)["U"]
print("B. 'U contains S, itself and the realities; S contains only the realities': NOT bisimilar (U holds a copy of the whole, S does not)")

# C. If S must NOT contain itself (owner, 2026-10-05: "if U contains U then S needs to contain S ... doesn't feel right"),
#    then S is bisimilar to NO self-containing U: the criterion forces s_self == (u_self or u_has_s).
for u_self, u_has_s, u_real in itertools.product([False, True], repeat=3):
    if u_self or u_has_s:
        n, e = variant(False, u_self, u_has_s, u_real)
        p = bisim(n, e)
        assert p["S"] != p["U"], (u_self, u_has_s, u_real)
print("C. with S not containing itself, S is bisimilar to no U that contains itself or S: they are different objects")

# D. U is still determined: every presentation of 'U contains S, itself and the realities' is bisimilar to every other
#    (one-node loop, two-node loop, three-node loop), so U is unique up to ==, as the solution of  U = {S, U, r1..r5}.
def presentation(k, tag):
    """k-node ring u0 -> u1 -> ... -> u_{k-1} -> u0, each also containing S and the realities."""
    nodes = [f"{tag}{i}" for i in range(k)]
    edges = [(nodes[i], nodes[(i + 1) % k]) for i in range(k)]
    edges += [(n, "S") for n in nodes] + [(n, r) for n in nodes for r in R]
    return nodes, edges


nodes, edges = ["S"] + R, [("S", r) for r in R]
rings = {}
for k in (1, 2, 3):
    ns, es = presentation(k, f"k{k}_")
    nodes, edges = nodes + ns, edges + es
    rings[k] = ns[0]
part = bisim(nodes, edges)
assert len({part[rings[k]] for k in (1, 2, 3)}) == 1
assert part[rings[1]] != part["S"]
print("D. the 1-, 2- and 3-node presentations of U are one object up to ==, and it is not S")
