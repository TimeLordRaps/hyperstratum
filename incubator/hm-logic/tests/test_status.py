import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parents[1]


def run(path):
    return subprocess.run([sys.executable, str(path)], capture_output=True, text=True, timeout=120)


def test_status_checks_pass_and_all_six_findings_print():
    r = run(HERE / "status.py")
    print(r.stdout, r.stderr)
    assert r.returncode == 0, r.stderr[-600:]
    for tag in ("0. ", "1. ", "2. ", "3. ", "4. ", "5. "):
        assert any(ln.startswith(tag) for ln in r.stdout.splitlines()), tag


def test_dropping_the_null_prediction_makes_r1_unfalsifiable_and_the_check_notices(tmp_path):
    src = (HERE / "status.py").read_text(encoding="utf-8").replace(
        'lambda m: m["Psi"] and ((not m["Test"]) or m["Null"])', 'lambda m: m["Psi"]', 1)
    p = tmp_path / "bad.py"
    p.write_text(src, encoding="utf-8")
    r = run(p)
    assert r.returncode != 0 and "AssertionError" in r.stderr


def test_a_wrong_likelihood_ratio_is_noticed(tmp_path):
    src = (HERE / "status.py").read_text(encoding="utf-8").replace(
        "lr = likelihood_ratio_of_null(1, 1)", "lr = likelihood_ratio_of_null(1, Fraction(1, 2))", 1)
    p = tmp_path / "bad.py"
    p.write_text(src, encoding="utf-8")
    r = run(p)
    assert r.returncode != 0 and "AssertionError" in r.stderr
