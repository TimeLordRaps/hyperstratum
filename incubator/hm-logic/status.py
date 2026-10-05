"""Statuses of a postulate P over a background theory T: provable, refutable, independent, falsifiable, unfalsifiable.

Finite propositional frame. Atoms are split into OBSERVATION atoms (what a test can read) and THEORY atoms (what it
cannot). A model is a truth assignment to all atoms. For a theory T (a predicate on assignments):
    models(T)          the satisfying assignments
    observable(T)      the set of observation-patterns realisable by models(T)     (projection onto O)
Statuses of P relative to T, all computed by enumeration:
    provable      T entails P                      refutable      T entails not P
    independent   neither (some model of T satisfies P and some satisfies not P): *unprovable* and *unrefutable*
    falsifiable   observable(T and P) is a proper subset of observable(T): P forbids some observation T allows
    unfalsifiable observable(T and P) == observable(T): P is observationally conservative over T
Facts checked in `check()` (not assumed): provable/refutable/independent partition the cases; falsifiable implies not
conservative; an independent P can be falsifiable (independence is not unfalsifiability).

The owner's remark "trying to prove it disproves it always" (2026-10-05) has three readings, computed separately:
    R1  tests always return null:          Psi and (Test -> Null)
    R2  testing falsifies the postulate:   Psi and (Test -> not Psi)       (equivalent to Psi and not Test)
    R3  tests are uninterpretable:         Psi, with Null unconstrained     (adds no observational constraint)
and, for R1, the likelihood ratio of a null result under H = Psi versus not-H when both predict nulls.
"""
from fractions import Fraction
from itertools import product

ATOMS = ("Test", "Null", "Psi")
OBS = ("Test", "Null")


def assignments():
    for vals in product([False, True], repeat=len(ATOMS)):
        yield dict(zip(ATOMS, vals))


def models(pred):
    return [m for m in assignments() if pred(m)]


def observable(pred):
    return {tuple(m[a] for a in OBS) for m in models(pred)}


def entails(t, p):
    return all(p(m) for m in models(t))


def status(t, p):
    prov, ref = entails(t, p), entails(t, lambda m: not p(m))
    assert not (prov and ref) or not models(t)  # a consistent theory cannot prove and refute
    both = lambda m: t(m) and p(m)  # noqa: E731
    obs_t, obs_tp = observable(t), observable(both)
    return {
        "provable": prov,
        "refutable": ref,
        "independent": not prov and not ref,
        "falsifiable": obs_tp < obs_t,
        "unfalsifiable": obs_tp == obs_t,
        "observable_with_P": sorted(obs_tp),
    }


def T0(m):  # background theory with no link between tests and the postulate
    return True


Psi = lambda m: m["Psi"]  # noqa: E731
READINGS = {
    "R1 tests always return null": lambda m: m["Psi"] and ((not m["Test"]) or m["Null"]),
    "R2 testing falsifies the postulate": lambda m: m["Psi"] and ((not m["Test"]) or (not m["Psi"])),
    "R3 tests are uninterpretable": lambda m: m["Psi"],
}


def likelihood_ratio_of_null(p_null_given_h, p_null_given_not_h):
    return Fraction(p_null_given_h) / Fraction(p_null_given_not_h)


def posterior(prior, lr):
    odds = Fraction(prior) / (1 - Fraction(prior)) * lr
    return odds / (1 + odds)


def check():
    base = status(T0, Psi)
    assert base["independent"] and base["unfalsifiable"] and not base["falsifiable"]
    print("0. Psi alone: unprovable and unrefutable (independent) and unfalsifiable: no observation pattern is excluded")

    neg = status(T0, lambda m: not m["Psi"])
    assert neg["independent"] and neg["unfalsifiable"]
    print("1. not Psi has the same status, so no observation distinguishes Psi from not Psi on T0 (observational underdetermination)")

    r1 = status(T0, READINGS["R1 tests always return null"])
    assert r1["falsifiable"] and (True, False) not in r1["observable_with_P"]
    print("2. R1 (tests always return null) is falsifiable: one Test with a non-null result refutes it")
    lr = likelihood_ratio_of_null(1, 1)
    assert lr == 1 and posterior(Fraction(1, 10), lr) == Fraction(1, 10)
    print("   and a null result, predicted by Psi and by not-Psi alike, has likelihood ratio 1: posterior = prior (no disproof, no support)")

    r2 = status(T0, READINGS["R2 testing falsifies the postulate"])
    assert r2["falsifiable"] and all(not test for (test, _null) in r2["observable_with_P"])
    assert not entails(T0, lambda m: not m["Test"])
    print("3. R2 (testing falsifies it) is equivalent to 'Psi and no test is ever run': it survives only untested, so any run test refutes it by definition")

    r3 = status(T0, READINGS["R3 tests are uninterpretable"])
    assert r3["unfalsifiable"] and r3["independent"]
    print("4. R3 (tests uninterpretable) adds no observational constraint: unfalsifiable and unprovable; evidence cannot touch it")

    # independence is not unfalsifiability: a theory that links Psi to a prediction makes an independent claim falsifiable
    T1 = lambda m: (not m["Psi"]) or (not m["Test"]) or m["Null"]  # noqa: E731  (T1: Psi and Test imply Null)
    s1 = status(T1, Psi)
    assert s1["independent"] and s1["falsifiable"] and not s1["unfalsifiable"]
    s2 = status(lambda m: T1(m), lambda m: m["Psi"] and m["Test"] and not m["Null"])
    assert s2["refutable"]
    print("5. independence is not unfalsifiability: with a bridge law (Psi and Test imply Null) Psi is independent of T1 yet falsifiable "
          "(it forbids Test with a non-null result); its 'positive-result' strengthening is refuted outright")
    return True


if __name__ == "__main__":
    check()
