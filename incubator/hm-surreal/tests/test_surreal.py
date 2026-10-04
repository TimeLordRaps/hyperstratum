"""Gates: the fold check (always) and the Lean filtration model (skips without HM_LEAN/lean)."""
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parents[1]
LEAN = os.environ.get("HM_LEAN") or shutil.which("lean")


def run_fold(path):
    return subprocess.run([sys.executable, str(path)], capture_output=True, text=True, timeout=300)


def test_average_fold_is_conway_birth_and_is_self_similar():
    r = run_fold(HERE / "fold_check.py")
    print(r.stdout, r.stderr)
    assert r.returncode == 0
    for tag in ("A ", "B ", "C ", "D "):
        assert any(line.startswith(tag) for line in r.stdout.splitlines()), tag


def test_a_non_average_fold_is_rejected(tmp_path):
    bad = (HERE / "fold_check.py").read_text(encoding="utf-8").replace(
        "new = [(a + b) / 2 for", "new = [(2 * a + b) / 3 for")
    p = tmp_path / "bad.py"
    p.write_text(bad, encoding="utf-8")
    r = run_fold(p)
    assert r.returncode != 0 and "failed" in r.stderr


@pytest.mark.skipif(not LEAN, reason="no lean (set HM_LEAN)")
def test_filtration_model_is_kernel_checked_without_sorry():
    r = subprocess.run([LEAN, str(HERE / "SurrealFiltration.lean")], capture_output=True, text=True, timeout=300)
    out = r.stdout + r.stderr
    print(out)
    assert r.returncode == 0 and not re.search(r"\berror\b", out)
    deps = [ln for ln in out.splitlines() if "depends on axioms" in ln]
    assert len(deps) == 4 and not any("sorryAx" in ln for ln in deps)
