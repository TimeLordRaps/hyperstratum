import os, pathlib, re, shutil, subprocess, sys
import pytest

HERE = pathlib.Path(__file__).resolve().parents[1]
LEAN = os.environ.get("HM_LEAN") or shutil.which("lean")


def lean(path):
    r = subprocess.run([LEAN, str(path)], capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def test_descent_to_naturals_runs():
    r = subprocess.run([sys.executable, str(HERE / "descent_to_naturals.py")], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert "every run reached (0,0)" in r.stdout


@pytest.mark.skipif(not LEAN, reason="no lean (set HM_LEAN)")
def test_ladder_induction_kernel_checked_with_no_axioms():
    code, out = lean(HERE / "LadderInduction.lean")
    print(out)
    assert code == 0 and not re.search(r"\berror\b", out)
    deps = [ln for ln in out.splitlines() if "axioms" in ln]
    assert len(deps) == 3 and all("does not depend on any axioms" in ln for ln in deps)


@pytest.mark.skipif(not LEAN, reason="no lean (set HM_LEAN)")
def test_a_non_wellfounded_order_is_rejected(tmp_path):
    bad = (HERE / "LadderInduction.lean").read_text(encoding="utf-8").replace(
        "| k + 1, (a, x), (b, y) => a < b ∨ (a = b ∧ lt k x y)",
        "| k + 1, (a, x), (b, y) => a ≤ b ∨ (a = b ∧ lt k x y)")
    p = tmp_path / "Bad.lean"
    p.write_text(bad, encoding="utf-8")
    code, out = lean(p)
    assert code != 0 and "error" in out
