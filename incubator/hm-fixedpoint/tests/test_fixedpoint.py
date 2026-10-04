"""Gates for the fixed-point experiment. Lean gates skip without a toolchain (set HM_LEAN);
the rescue gate also needs a built copy of hypermath's lean4/ (set HM_HYPERMATH_LAKE)."""
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
COUNTERMODEL = ROOT / "fields" / "hypermath" / "lean4" / "FiniteActionCountermodel.lean"
LEAN = os.environ.get("HM_LEAN") or shutil.which("lean")
LAKE_DIR = os.environ.get("HM_HYPERMATH_LAKE")


def test_search_finds_computation_laws_on_the_countermodel():
    r = subprocess.run([sys.executable, str(HERE / "search_countermodel.py")], capture_output=True, text=True,
                       timeout=120)
    print(r.stdout)
    assert r.returncode == 0
    assert "zero+succ+path simultaneously satisfiable: True" in r.stdout


@pytest.mark.skipif(not LEAN, reason="no lean (set HM_LEAN)")
def test_transfinite_model_compiles_without_axioms():
    r = subprocess.run([LEAN, str(HERE / "TransfiniteForm.lean")], capture_output=True, text=True, timeout=300)
    print(r.stdout, r.stderr)
    assert r.returncode == 0 and "error" not in r.stdout
    assert "sorryAx" not in r.stdout
    assert r.stdout.count("does not depend on any axioms") == 3


@pytest.mark.skipif(not (LAKE_DIR and COUNTERMODEL.exists()), reason="set HM_HYPERMATH_LAKE to a built hypermath lean4 copy")
def test_rescue_is_kernel_checked_against_the_pinned_countermodel_and_rejects_a_wrong_table():
    lake = shutil.which("lake") or str(pathlib.Path(LEAN).with_name("lake"))
    part = (HERE / "RecursionRescue.lean.part").read_text(encoding="utf-8")
    good = COUNTERMODEL.read_text(encoding="utf-8") + part
    for name, text, expect_ok in [("Rescue.lean", good, True),
                                  ("Bad.lean", good.replace("| .a1, .a1 => .a2 |", "| .a1, .a1 => .a1 |"), False)]:
        f = pathlib.Path(LAKE_DIR) / name
        f.write_text(text, encoding="utf-8")
        r = subprocess.run([lake, "env", "lean", name], cwd=LAKE_DIR, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        if expect_ok:
            assert r.returncode == 0, out[-2000:]
            line = [ln for ln in out.splitlines() if "clauses_and_computation_laws_consistent' depends" in ln][0]
            assert "sorryAx" not in line
        else:
            assert r.returncode != 0
