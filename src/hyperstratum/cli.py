"""`hyperstratum build | check | lock | pins`."""

from __future__ import annotations

import argparse
import pathlib
import sys

from . import build, diff, refs, registry

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hyperstratum", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, help_ in [("build", "render the wiki site and wiki.json"),
                        ("check", "verify registry, references and citations"),
                        ("lock", "record the text of every live reference in wiki.lock.json"),
                        ("pins", "list each hyperfield and the commit it is pinned at")]:
        s = sub.add_parser(name, help=help_)
        s.add_argument("--root", default=".", help="hyperstratum checkout (default: .)")
        s.add_argument("--no-git", action="store_true",
                       help="do not call git for the HEAD sha (tests, exported trees)")
        if name == "build":
            s.add_argument("--out", default="_site/wiki")
            s.add_argument("--source-ref", default="")
            s.add_argument("--previous", default="",
                           help="wiki.json (path or https URL) of the last build, to report what changed")
            s.add_argument("--landing", default="",
                           help="a landing index.html to receive one link to the wiki")
        if name == "check":
            s.add_argument("--strict", action="store_true", help="warnings fail too")
            s.add_argument("--verdict", default="",
                           help="write a machine-readable clean/attention verdict to this path")
    return p


def main(argv: list[str] | None = None, pins=None, blob_lookup=None) -> int:
    args = _parser().parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    kw = dict(pins=pins, blob_lookup=blob_lookup)

    if args.cmd == "pins":
        reg = registry.load_registry(root, pins=pins)
        for f in reg.fields:
            print(f"{f.name:34s} {f.pin or '-':40s} {f.role}")
        return 0

    if args.cmd == "lock":
        c = build.collect(root, lock={}, **kw)  # a fresh lock records, it never compares
        text = refs.dump_lock(refs.make_lock(c.resolved))
        (root / build.LOCK_FILE).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {build.LOCK_FILE}: {len(refs.make_lock(c.resolved)['refs'])} reference(s)")
        return 0

    source_ref = "" if args.no_git else build.head_sha(root)
    if args.cmd == "build":
        source_ref = args.source_ref or source_ref
        previous, why = (diff.load_previous(args.previous) if args.previous else (None, ""))
        if args.previous and previous is None:
            print(f"note: no previous build to compare with ({why})")
        c = build.collect(root, source_ref=source_ref, previous=previous, **kw)
        if why:
            c.model["previous_unavailable"] = why
        site = build.render(c, pathlib.Path(args.out))
        errors = sum(1 for p in c.model["problems"] if p["severity"] == "error")
        print(f"built {len(site.written)} file(s) into {args.out} "
              f"({len(c.terms)} terms, {len(c.scans)} fields, {errors} error(s))")
        if args.landing:
            href = pathlib.PurePosixPath(
                pathlib.Path(args.out).resolve().relative_to(pathlib.Path(args.landing).resolve().parent)
            ).as_posix() + "/index.html"
            print("landing link:", "added" if build.link_landing(pathlib.Path(args.landing), href) else "unchanged")
        return 0

    c = build.collect(root, source_ref=source_ref, **kw)
    problems = sorted(c.model["problems"], key=lambda p: (SEVERITY_ORDER[p["severity"]], p["code"], p["subject"]))
    for p in problems:
        print(f"{p['severity'].upper():7s} {p['code']:24s} {p['subject']}  {p['detail']}")
    n = {k: sum(1 for p in problems if p["severity"] == k) for k in SEVERITY_ORDER}
    print(f"\n{n['error']} error(s), {n['warning']} warning(s), {n['info']} info; "
          f"{len(c.scans)} field(s) scanned, {len(c.resolved)} reference(s) resolved")
    if args.verdict:
        _write_verdict(pathlib.Path(args.verdict), c.model["problems"], n)
    return 1 if n["error"] or (args.strict and n["warning"]) else 0


# What a person must look at before a pin move is merged. A stale sibling
# citation (`CITATION_BEHIND`) is deliberately absent: it is the normal state of
# a fast-moving family and says nothing about whether *this* move is safe.
ATTENTION = ("DRIFTED", "MOVED", "REDIRECTED", "MISSING_FIELD", "MISSING_FILE", "BAD_RANGE",
             "MISSING_TERM", "AMBIGUOUS", "CITATION_DRIFTED", "CITATION_UNRESOLVABLE")


def _write_verdict(path: pathlib.Path, problems: list[dict], n: dict) -> None:
    import json

    items = [p for p in problems if p["severity"] == "error" or p["code"] in ATTENTION]
    verdict = {"schema": "hyperstratum-verdict/1", "clean": not items, "errors": n["error"],
               "warnings": n["warning"], "attention": [
                   {"code": p["code"], "subject": p["subject"], "detail": p["detail"]} for p in items]}
    path.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def console() -> None:
    sys.exit(main())
