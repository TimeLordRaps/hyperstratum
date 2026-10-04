"""GL (Gödel-Löb provability logic): a decision procedure, an independent countermodel
oracle, fixed points of self-reference, and modal agents (program equilibrium).

Formulas: ("var", p) | ("bot",) | ("not", A) | ("imp", A, B) | ("and", A, B) | ("or", A, B) | ("box", A).
`prove(A)` is backward proof search in the sequent calculus GLS (propositional rules plus
the GL rule: from  B1..Bn, □B1..□Bn, □A ⇒ A  infer  □B1..□Bn ⇒ □A).  Each modal step adds □A to
the left, and □A can be the principal formula only while it is absent there, so search terminates.
`countermodel(A)` searches finite irreflexive transitive trees, an independent semantic oracle
(GL is sound and complete for them).
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product

BOT = ("bot",)


def var(p): return ("var", p)
def neg(a): return ("not", a)
def imp(a, b): return ("imp", a, b)
def conj(a, b): return ("and", a, b)
def disj(a, b): return ("or", a, b)
def box(a): return ("box", a)
def iff(a, b): return conj(imp(a, b), imp(b, a))
def diamond(a): return neg(box(neg(a)))


TOP = neg(BOT)
CON = neg(box(BOT))  # "the theory is consistent"


@lru_cache(maxsize=None)
def _prove(left: frozenset, right: frozenset) -> bool:
    if BOT in left or left & right:
        return True
    for f in left:
        k, rest = f[0], left - {f}
        if k == "not":
            return _prove(rest, right | {f[1]})
        if k == "and":
            return _prove(rest | {f[1], f[2]}, right)
        if k == "or":
            return _prove(rest | {f[1]}, right) and _prove(rest | {f[2]}, right)
        if k == "imp":
            return _prove(rest, right | {f[1]}) and _prove(rest | {f[2]}, right)
    for f in right:
        k, rest = f[0], right - {f}
        if k == "not":
            return _prove(left | {f[1]}, rest)
        if k == "and":
            return _prove(left, rest | {f[1]}) and _prove(left, rest | {f[2]})
        if k == "or":
            return _prove(left, rest | {f[1], f[2]})
        if k == "imp":
            return _prove(left | {f[1]}, rest | {f[2]})
    boxed_left = {f for f in left if f[0] == "box"}
    unboxed = {f[1] for f in boxed_left}
    for f in right:
        if f[0] == "box" and f not in left:
            if _prove(frozenset(boxed_left | unboxed | {f}), frozenset({f[1]})):
                return True
    return False


def prove(a) -> bool:
    return _prove(frozenset(), frozenset({a}))


def atoms(a, acc=None):
    acc = set() if acc is None else acc
    if a[0] == "var":
        acc.add(a[1])
    for sub in a[1:]:
        if isinstance(sub, tuple):
            atoms(sub, acc)
    return acc


def holds(a, w, R, V) -> bool:
    k = a[0]
    if k == "var":
        return V[(w, a[1])]
    if k == "bot":
        return False
    if k == "not":
        return not holds(a[1], w, R, V)
    if k == "imp":
        return (not holds(a[1], w, R, V)) or holds(a[2], w, R, V)
    if k == "and":
        return holds(a[1], w, R, V) and holds(a[2], w, R, V)
    if k == "or":
        return holds(a[1], w, R, V) or holds(a[2], w, R, V)
    if k == "box":
        return all(holds(a[1], v, R, V) for v in R[w])
    raise ValueError(k)


def trees(n):
    """Rooted trees on nodes 0..n-1 (parent index < child), as transitive-closure successor maps."""
    for parents in product(*[range(i) for i in range(1, n)]):
        children = {i: set() for i in range(n)}
        for c, p in enumerate(parents, start=1):
            children[p].add(c)

        def desc(w):
            out = set()
            for c in children[w]:
                out |= {c} | desc(c)
            return out
        yield {w: desc(w) for w in range(n)}


def countermodel(a, max_nodes=4):
    ps = sorted(atoms(a))
    for n in range(1, max_nodes + 1):
        for R in trees(n):
            for vals in product([False, True], repeat=n * len(ps)):
                V = {(w, p): vals[w * len(ps) + i] for w in range(n) for i, p in enumerate(ps)}
                if not holds(a, 0, R, V):
                    return n, R, V
    return None


# ---------------------------------------------------------------- arithmetic truth of letterless sentences

def true_in_arithmetic(a, height=64) -> bool:
    """A letterless sentence is true in ℕ iff it holds at the top of a long enough linear frame
    (□X at world k means X holds at every world below k). Exact for letterless GL sentences."""
    R = {k: set(range(k)) for k in range(height)}
    return holds(a, height - 1, R, {})


# ---------------------------------------------------------------- modal agents (program equilibrium)

def play(agent_a, agent_b, height=64):
    """Outcome of two modal agents. Each agent decides at world k from `Box(pred)`, which is true
    iff `pred` held at every world below k (provability, read on a linear frame bottom-up).
    The value at a high enough world is the arithmetic truth of the agents' fixed point."""
    ca, cb = [], []
    for k in range(height):
        def box_a(pred, k=k):  # □(pred) at world k
            return all(pred(j) for j in range(k))
        ca_k = agent_a(lambda j: cb[j], lambda j: ca[j], box_a)
        cb_k = agent_b(lambda j: ca[j], lambda j: cb[j], box_a)
        ca.append(ca_k)
        cb.append(cb_k)
    return ca[-1], cb[-1]


def FairBot(opp, me, Box):          # cooperate iff it is provable that the opponent cooperates
    return Box(opp)


def DefectBot(opp, me, Box):
    return False


def CooperateBot(opp, me, Box):
    return True


AGENTS = {"FairBot": FairBot, "DefectBot": DefectBot, "CooperateBot": CooperateBot}
