"""Gates for the conatural top (Lean) and the GL procedure (Python)."""
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parents[1]
LEAN = os.environ.get("HM_LEAN") or shutil.which("lean")
sys.path.insert(0, str(HERE))


def test_gl_check_runs_and_matches_literature():
    r = subprocess.run([sys.executable, "gl_check.py"], cwd=HERE, capture_output=True, text=True, timeout=600)
    print(r.stdout, r.stderr)
    assert r.returncode == 0
    assert "FairBot      vs FairBot     : C C" in r.stdout
    assert "agree on 300/300" in r.stdout


def test_weakening_the_gl_rule_to_k_loses_loeb_and_4(tmp_path):
    src = (HERE / "gl.py").read_text(encoding="utf-8").replace(
        "frozenset(boxed_left | unboxed | {f})", "frozenset(unboxed)")
    (tmp_path / "gl.py").write_text(src, encoding="utf-8")
    code = ("from gl import *\np=var('p')\n"
            "print(prove(imp(box(imp(box(p), p)), box(p))), prove(imp(box(p), box(box(p)))))")
    r = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert r.stdout.split() == ["False", "False"], r.stdout + r.stderr  # plain K: Löb and 4 both lost


def test_letterless_truth_and_agents():
    import gl
    assert gl.true_in_arithmetic(gl.CON) and not gl.true_in_arithmetic(gl.box(gl.BOT))
    assert gl.play(gl.FairBot, gl.DefectBot) == (False, False)


@pytest.mark.skipif(not LEAN, reason="no lean (set HM_LEAN)")
def test_conatural_top_kernel_checked():
    r = subprocess.run([LEAN, str(HERE / "ConatTop.lean")], capture_output=True, text=True, timeout=300)
    out = r.stdout + r.stderr
    print(out)
    assert r.returncode == 0 and not re.search(r"\berror\b", out)
    deps = {ln.split("'")[1].split(".")[-1]: ln for ln in out.splitlines() if "depends on axioms" in ln}
    assert len(deps) == 4 and not any("sorryAx" in v for v in deps.values())
    # only the finite-or-top dichotomy needs classical choice: that is the LPO residue
    assert "Classical.choice" in deps["finite_or_top"]
    assert all("Classical.choice" not in v for k, v in deps.items() if k != "finite_or_top")


def test_reality_class_mapping_against_the_hyperreality_registry():
    r = subprocess.run([sys.executable, "reality_classes.py"], cwd=HERE, capture_output=True, text=True, timeout=120)
    print(r.stdout, r.stderr)
    assert r.returncode == 0, r.stderr[-600:]
    for tag in ("1. ", "2. ", "3a. ", "3b. ", "3c. ", "3d. "):
        assert any(ln.startswith(tag) for ln in r.stdout.splitlines()), tag


def test_a_one_sided_loop_is_not_bisimilar_to_the_self_containing_top(tmp_path):
    bad = (HERE / "reality_classes.py").read_text(encoding="utf-8").replace(
        'hr.Containment("U2", "S"), hr.Containment("U2", "U1")),\n)\nassert not', 'hr.Containment("U2", "U1")),\n)\nassert not', 1)
    assert bad != (HERE / "reality_classes.py").read_text(encoding="utf-8")
    p = tmp_path / "bad.py"
    p.write_text(bad.replace('ROOT = pathlib.Path(__file__).resolve().parents[2]', f'ROOT = pathlib.Path({str(HERE.parents[1])!r})'),
                 encoding="utf-8")
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and "AssertionError" in r.stderr


def test_sempiternality_vs_container_bisimulation_table():
    r = subprocess.run([sys.executable, "sempiternality_bisim.py"], cwd=HERE, capture_output=True, text=True, timeout=120)
    print(r.stdout, r.stderr)
    assert r.returncode == 0, r.stderr[-600:]
    assert "4 of 16 are bisimilar" in r.stdout and "B. " in r.stdout


def test_a_wrong_predicate_is_rejected_by_the_enumeration(tmp_path):
    src = (HERE / "sempiternality_bisim.py").read_text(encoding="utf-8").replace(
        "expected = u_real and (s_self == (u_self or u_has_s))", "expected = u_real and s_self and (u_self or u_has_s)")
    p = tmp_path / "bad.py"
    p.write_text(src, encoding="utf-8")
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and "AssertionError" in r.stderr
