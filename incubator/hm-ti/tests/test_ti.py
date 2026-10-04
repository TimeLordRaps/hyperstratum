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


def test_fundamental_sequences_descent_into_naturals():
    r = subprocess.run([sys.executable, str(HERE / "fundamental.py")], capture_output=True, text=True, timeout=300)
    print(r.stdout, r.stderr)
    assert r.returncode == 0
    assert "closed forms H_ω=2n, H_ω·2=4n, H_ω²=n·2^n verified" in r.stdout
    assert "H_ω^3(2) = 2048" in r.stdout and "exceeds 10^7 steps" in r.stdout


@pytest.mark.skipif(not LEAN, reason="no lean (set HM_LEAN)")
def test_omegas_rank_order_kernel_checked_and_a_weak_order_is_rejected(tmp_path):
    code, out = lean(HERE / "RankOrder.lean")
    print(out)
    assert code == 0 and not re.search(r"\berror\b", out) and "sorry" not in out
    assert "∨ True" not in (HERE / "RankOrder.lean").read_text(encoding="utf-8")  # no vacuous disjunct
    assert sum("axioms" in ln for ln in out.splitlines()) == 5
    bad = (HERE / "RankOrder.lean").read_text(encoding="utf-8").replace(
        "| k + 1, (a, x), (b, y) => a < b ∨ (a = b ∧ lt k x y)",
        "| k + 1, (a, x), (b, y) => a ≤ b ∨ (a = b ∧ lt k x y)")
    p = tmp_path / "Bad.lean"
    p.write_text(bad, encoding="utf-8")
    code, out = lean(p)
    assert code != 0 and "error" in out


def test_exponent_axis_classes_by_phase_and_one_dimensional_spiral():
    r = subprocess.run([sys.executable, str(HERE / "exponent_axis.py")], capture_output=True, text=True, timeout=900)
    print(r.stdout, r.stderr)
    assert r.returncode == 0, r.stderr[-800:]
    for tag in ("1. ", "2. ", "3. ", "4. "):
        assert any(ln.startswith(tag) for ln in r.stdout.splitlines()), tag


def test_exponent_axis_check_rejects_a_map_without_the_imaginary_branch(tmp_path):
    src = (HERE / "exponent_axis.py").read_text(encoding="utf-8").replace(
        "W = -sp.log(2) + sp.I * sp.pi", "W = -sp.log(2)")
    p = tmp_path / "bad.py"
    p.write_text(src, encoding="utf-8")
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=900)
    assert r.returncode != 0
