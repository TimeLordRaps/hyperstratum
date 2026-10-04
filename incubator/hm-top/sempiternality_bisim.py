"""Is sempiternality S bisimilar to its container universempiternality U?

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
