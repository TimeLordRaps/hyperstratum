"""Runs the GL checks and prints the results that the program page cites."""
import random

from gl import (BOT, CON, AGENTS, box, conj, countermodel, diamond, disj, iff, imp, neg, play, prove,
                true_in_arithmetic, var)

p, q = var("p"), var("q")
cases = {
    "K: □(p→q)→(□p→□q)": (imp(box(imp(p, q)), imp(box(p), box(q))), True),
    "4: □p→□□p": (imp(box(p), box(box(p))), True),
    "Löb: □(□p→p)→□p": (imp(box(imp(box(p), p)), box(p)), True),
    "T: □p→p (reflection)": (imp(box(p), p), False),
    "Con is not provable: ¬□⊥": (CON, False),
    "G2: Con → ¬□Con": (imp(CON, neg(box(CON))), True),
    "proving own consistency ⇒ inconsistent: □Con→□⊥": (imp(box(CON), box(BOT)), True),
    "self-assertion closes (Henkin): ⊞(p↔□p) → p": (imp(conj(iff(p, box(p)), box(iff(p, box(p)))), p), True),
    "self-denial = consistency (Gödel): ⊞(p↔¬□p) → (p↔Con)":
        (imp(conj(iff(p, neg(box(p))), box(iff(p, neg(box(p))))), iff(p, CON)), True),
}
for name, (f, expected) in cases.items():
    got = prove(f)
    cm = None if got else countermodel(f, 4)
    assert got == expected, (name, got)
    assert got or cm is not None, ("no countermodel found for unprovable", name)
    print(f"{'⊢' if got else '⊬'}  {name}" + ("" if got else f"   (countermodel on {cm[0]} nodes)"))

print("\narithmetic truth of letterless sentences:")
for name, f in {"Con": CON, "□⊥": box(BOT), "¬□Con": neg(box(CON)), "◇⊤ (= Con)": diamond(neg(BOT))}.items():
    print(f"  {name}: {true_in_arithmetic(f)}")

# differential test: prover vs countermodel oracle on random formulas
random.seed(20261004)


def rand(d):
    if d == 0:
        return random.choice([p, q, BOT])
    k = random.choice(["not", "imp", "and", "or", "box", "box"])
    if k == "not":
        return neg(rand(d - 1))
    if k == "box":
        return box(rand(d - 1))
    return {"imp": imp, "and": conj, "or": disj}[k](rand(d - 1), rand(d - 1))


agree = 0
for _ in range(300):
    f = rand(3)
    proved = prove(f)
    cm = countermodel(f, 4)
    assert not (proved and cm is not None), ("unsound", f)
    assert proved or cm is not None, ("prover failed but no small countermodel", f)
    agree += 1
print(f"\ndifferential: prover and countermodel oracle agree on {agree}/300 random formulas")

print("\nmodal agents (outcome = arithmetic truth of the fixed point):")
for a in AGENTS:
    for b in AGENTS:
        ra, rb = play(AGENTS[a], AGENTS[b])
        print(f"  {a:12s} vs {b:12s}: {'C' if ra else 'D'} {'C' if rb else 'D'}")
