"""`hmtrans FILE.hm… --out DIR [--lean BIN] [--mmverify PATH]`: files must be given in dependency order."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import lean, metamath, project, receipt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="hmtrans", description=__doc__)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lean", help="path to a `lean` binary; enables kernel checking")
    ap.add_argument("--mmverify", help="path to mmverify.py; enables Metamath output")
    ap.add_argument("--namespace", default="Hypermath")
    a = ap.parse_args(argv)
    proj = project.analyze([(f.name, f.read_text(encoding="utf-8")) for f in a.files])
    a.out.mkdir(parents=True, exist_ok=True)
    lean_text, log, ver = None, [], None
    if a.lean:
        out, log = lean.kernel_check(proj, a.lean, a.namespace)
        lean_text = out.text
        (a.out / "Out.lean").write_text(lean_text, encoding="utf-8")
        ver = subprocess.run([a.lean, "--version"], capture_output=True, text=True).stdout.strip()
    else:
        print("note: no --lean given; nothing was kernel-checked and no Lean file was written", file=sys.stderr)
    mm_text, mm_status = None, None
    if a.mmverify:
        mm_text, mm_status = metamath.emit_checked(proj, a.mmverify)
        (a.out / "out.mm").write_text(mm_text, encoding="utf-8")
    rec = receipt.build(proj, lean_text, log, mm_text, mm_status, ver, a.mmverify)
    (a.out / "receipt.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    for k, n in rec["counts"].items():
        print(f"{n:4d}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
