"""The owner's reality-class mapping, built as a hyperreality Registry and checked against its rules.

Owner (USER-STATED 2026-10-04): base:normal, surreality:surreal, areality:imaginary, rational and irrational both
in base-reality; sempiternality encompasses them as ω^ω; universempiternality closes over sempiternality as the
self-containing superclass.

hyperreality's registry (fields/hyperreality/hyperreality.py, imported read-only) has two relations that are never
inferred from each other (Classification is-a, Containment is-in), unordered kinds, and `well_founded` reported not
enforced. Checks:
  1. the mapping is expressible: kinds are classes of number-representations, sempiternality is a Whole that contains
     the realities and classifies nothing;
  2. kinds stay unordered even though the number classes they are mapped to nest (ordinals ⊂ surreals ⊂ surcomplex):
     the mapping must not be read as inclusion between kinds;
  3. universempiternality as a one-node loop is NOT expressible (direct self-containment raises); the two-node loop is,
     is not well-founded, and is bisimilar to the one-node loop (partition refinement), the same fact as '== is
     bisimilarity' and as the conatural top with succ(top) = top.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "fields" / "hyperreality"))

import hyperreality as hr  # noqa: E402

base = hr.Kind("base-reality", "normal, rational and irrational representations", "USER-STATED 2026-10-04")
sur = hr.Kind("surreality", "surreal representations", "USER-STATED 2026-10-04")
are = hr.Kind("areality", "imaginary representations", "USER-STATED 2026-10-04")

# 2. kinds are unordered
for a, b in ((base, sur), (sur, are), (base, are)):
    try:
        a < b
    except TypeError:
        pass
    else:
        raise AssertionError("kinds must be unordered")
print("2. kinds are unordered (comparison raises), although the number classes they map to nest")

realities = (
    hr.Presentation("r-normal", "base-reality"),
    hr.Presentation("r-rational", "base-reality"),
    hr.Presentation("r-irrational", "base-reality"),
    hr.Presentation("r-surreal", "surreality"),
    hr.Presentation("r-imaginary", "areality"),
)
S = hr.Whole("S", "sempiternality")
base_reg = hr.Registry(
    kinds=(base, sur, are),
    presentations=realities,
    wholes=(S,),
    containments=tuple(hr.Containment("S", p.reality_id) for p in realities),
)
assert hr.well_founded(base_reg)
assert hr.members_of(base_reg, "S") == frozenset(p.reality_id for p in realities)
assert hr.classes_of(base_reg, "S") == frozenset()  # sempiternality contains; containment never classifies
print("1. sempiternality S contains the five realities, classifies nothing, containment well-founded")

# 3. universempiternality
U = hr.Whole("U", "universempiternality")
try:
    hr.Containment("U", "U")
except ValueError:
    print("3a. one-node loop U ∋ U is refused by the registry (direct self-containment)")
else:
    raise AssertionError("expected refusal")

U1, U2 = hr.Whole("U1", "universempiternality"), hr.Whole("U2", "universempiternality")
loop_reg = hr.Registry(
    kinds=(base, sur, are),
    presentations=realities,
    wholes=(S, U1, U2),
    containments=tuple(hr.Containment("S", p.reality_id) for p in realities)
    + (hr.Containment("U1", "S"), hr.Containment("U1", "U2"),
       hr.Containment("U2", "S"), hr.Containment("U2", "U1")),
)
assert not hr.well_founded(loop_reg)
print("3b. the two-node loop (each contains S and the other) is representable and reported NOT well-founded")


def bisimulation_classes(nodes, edges):
    """Coarsest partition such that bisimilar nodes have the same set of successor blocks."""
    block = {n: 0 for n in nodes}
    while True:
        sig = {n: (block[n], frozenset(block[m] for (a, m) in edges if a == n)) for n in nodes}
        ids = {}
        new = {n: ids.setdefault(sig[n], len(ids)) for n in nodes}
        if new == block or len(set(new.values())) == len(set(block.values())):
            return new
        block = new


def graph(reg):
    nodes = sorted({p.reality_id for p in reg.presentations} | {w.whole_id for w in reg.wholes})
    return nodes, [(c.container_id, c.member_id) for c in reg.containments]


nodes, edges = graph(loop_reg)
part = bisimulation_classes(nodes, edges)
assert part["U1"] == part["U2"], part
print("3c. U1 and U2 are bisimilar: the two-node loop is the one-node loop up to ==")

# negative control: a 2-cycle that is not symmetric is not collapsed
asym = hr.Registry(
    kinds=(base, sur, are), presentations=realities, wholes=(S, U1, U2),
    containments=tuple(hr.Containment("S", p.reality_id) for p in realities)
    + (hr.Containment("U1", "S"), hr.Containment("U1", "U2"),
       hr.Containment("U2", "S"), hr.Containment("U2", "U1"),
       hr.Containment("U2", "r-normal")),
)
n2, e2 = graph(asym)
p2 = bisimulation_classes(n2, e2)
assert p2["U1"] != p2["U2"]
print("3d. control: giving U2 an extra member breaks the bisimilarity, so the quotient is not trivial")
