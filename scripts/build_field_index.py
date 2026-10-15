#!/usr/bin/env python3
"""Write the hyperfields index: one static HTML page, no network.

    python scripts/build_field_index.py --output _site/fields

The page is read from the checkouts under `fields/`, the registry and the family graph. What is
read and what is not is described in `src/hyperstratum/fieldindex.py`.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hyperstratum import fieldindex


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the hyperfields index page.")
    parser.add_argument("--output", type=pathlib.Path, default=ROOT / "_site" / "fields",
                        help="directory to write index.html into (created if missing)")
    args = parser.parse_args(argv)
    index = fieldindex.build_index(ROOT)
    page = fieldindex.render(index)
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / "index.html"
    target.write_text(page, encoding="utf-8")
    checked = sum(1 for entry in index.entries if entry.checked_out)
    print(f"wrote {target}: {len(index.entries)} fields, {checked} checked out, {len(page)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
