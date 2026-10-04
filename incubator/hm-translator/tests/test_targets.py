import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

from hmtrans import lean, metamath, project, receipt
from conftest import HYPERMATH

L0 = """\
primitive Form :: Type
primitive ground :: Form
primitive apply :: Form -> Form
opaque struct-distinct :: Form -> Form -> Prop
relation Similar :: Form -> Form -> Prop   -- (~~)

axiom ax-diff:
    for-all x :: Form:
        struct-distinct(apply(x), ground)

axiom ax-guarded:
    for-all x :: Form where struct-distinct(x, ground):
        x ~~ x

axiom ax-nested:
    for-all x :: Form:
        exists y :: Form: struct-distinct(x, y)

derive d-inst as FORM:
    step 1: ax-diff with x := ground
            -> struct-distinct(apply(ground), ground)
    close: struct-distinct(apply(ground), ground)

derive d-unproved as FORM:
    step 1: ax-diff with x := ground
            -> struct-distinct(apply(ground), ground)
    step 2: ax-diff with x := apply(ground)
            -> struct-distinct(apply(apply(ground)), ground)
    close: struct-distinct(apply(ground), ground)
"""


def lean_bin():
    return os.environ.get("HM_LEAN") or shutil.which("lean")


def mm_tool():
    return os.environ.get("HM_MMVERIFY")


def proj():
    return project.analyze([("l0.hm", L0)])


def test_lean_text_follows_hypermath_conventions():
    t = lean.emit(proj()).text
    assert "axiom Form : Type" in t and "axiom f2f : Form → Form" in t  # apply -> f2f
    assert "axiom structDistinct : Form → Form → Prop" in t
    assert 'scoped notation:50 a " ~~ " b => Similar a b' in t
    assert "axiom axDiff : ∀ (x : Form), structDistinct (f2f x) ground" in t
    assert "theorem dInst : structDistinct (f2f ground) ground :=\n  axDiff ground" in t
    assert "theorem dUnproved" in t and "by sorry" in t  # two steps: admitted, not proved


def test_vocabulary_is_emitted_before_statements_that_use_it():
    src = "axiom a1:\n    for-all x :: Form:\n        later(x)\nprimitive Form :: Type\nopaque later :: Form -> Prop\n"
    t = lean.emit(project.analyze([("f.hm", src)])).text
    assert t.index("axiom later") < t.index("axiom a1")


def test_rendering_is_precedence_correct():
    src = ("primitive Form :: Type\nopaque p :: Form -> Prop\nopaque q :: Form -> Prop\n"
           "axiom a:\n    for-all x :: Form:\n        (p(x) or q(x)) and not p(x)\n")
    t = lean.emit(project.analyze([("f.hm", src)])).text
    assert "(p x ∨ q x) ∧ ¬ (p x)" in t


@pytest.mark.lean
@pytest.mark.skipif(not lean_bin(), reason="no lean binary (set HM_LEAN); gate required with HM_REQUIRE_LEAN=1")
def test_kernel_accepts_fixture_output_and_rejects_a_broken_one():
    p = proj()
    out, log = lean.kernel_check(p, lean_bin())
    code, errs, _ = lean.run_lean(out.text, lean_bin())
    assert code == 0 and not errs
    broken = out.text.replace("structDistinct (f2f x) ground", "structDistinct (f2f x) nonsense")
    code, errs, _ = lean.run_lean(broken, lean_bin())
    assert code != 0 and errs  # the oracle can say no


@pytest.mark.lean
@pytest.mark.skipif(not lean_bin(), reason="no lean binary")
def test_bad_instance_proof_falls_back_to_sorry_not_to_silent_acceptance():
    p = proj()
    e = next(e for e in p.entries if e.name == "d-inst")
    e.proof = ("ax-diff", (("x", "apply(ground)"),))  # wrong instance for the stated close
    out, log = lean.kernel_check(p, lean_bin())
    assert ("proof->sorry", p.entries.index(e), log[0][2]) in log
    assert "theorem dInst : structDistinct (f2f ground) ground :=\n  by sorry" in out.text


@pytest.mark.metamath
@pytest.mark.skipif(not mm_tool(), reason="no mmverify (set HM_MMVERIFY)")
def test_metamath_subset_is_verified_and_honest_about_omissions():
    text, st = metamath.emit_checked(proj(), mm_tool())
    names = {proj().entries[i].name: s for i, s in st.items()}
    assert names["d-inst"] == "proved"
    assert names["ax-nested"].startswith("omitted: nested quantifier")
    assert names["d-unproved"].startswith("omitted")
    assert "th.d-inst $p" in text and "th.d-unproved" not in text


@pytest.mark.metamath
@pytest.mark.skipif(not mm_tool(), reason="no mmverify")
def test_mmverify_rejects_a_wrong_theorem():
    text, _ = metamath.emit_checked(proj(), mm_tool())
    bad = text.replace("th.d-inst $p |- ( struct-distinct ( apply ground ) ground )",
                       "th.d-inst $p |- ( struct-distinct ground ground )")
    ok, _ = metamath.verify(bad, mm_tool())
    assert not ok


def test_receipt_is_deterministic_and_self_hashed():
    p = proj()
    a = receipt.build(p, None, [], None, None, None, None)
    b = receipt.build(proj(), None, [], None, None, None, None)
    assert a == b and len(a["receipt_sha256"]) == 64
    assert a["counts"]["axiom/translated"] == 3 and a["counts"]["derive/admitted"] == 2
    assert any("fidelity" in g for g in a["guarantees"])


# -- differential against the hand-written mechanization (L0 only) -------------------

HAND = HYPERMATH / "lean4" / "Hypermath" / "L0Ground.lean"


@pytest.mark.skipif(not HAND.exists(), reason="hypermath submodule not checked out")
def test_l0_vocabulary_and_axioms_match_the_hand_written_lean():
    src = (HYPERMATH / "L0_ground.hm").read_text(encoding="utf-8")
    t = lean.emit(project.analyze([("L0_ground.hm", src)])).text
    sig = lambda s: dict(re.findall(r"^axiom (\w+) : (.+)$", s, re.M))  # noqa: E731
    ours, hand = sig(t), sig(HAND.read_text(encoding="utf-8"))
    # every vocabulary declaration we generate for L0 exists in the hand-written file
    # with the identical type (the hand file adds §VIII+ material we do not generate).
    for name in ("Form", "ground", "f2f", "structDistinct", "structContinues", "structOrbits",
                 "Similar", "Congruent", "Simulation"):
        assert ours[name] == hand[name], name
    for name in ("axDiff", "axSim", "axBox", "axGroundSelf"):
        assert ours[name].replace("∀ (x : Form),", "∀ x : Form,") == hand[name], name
