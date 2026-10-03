"""What changed between two builds of the wiki.

Pure function of two `wiki.json` models. The previous one is whatever was last
deployed, so a pin-moving pull request can say what the new pin *did* -- not
just that a SHA moved.

A category the previous build did not record is reported under `unknown`, never
as "everything is new": absence of a record is not evidence of absence.
"""

from __future__ import annotations

import json
import urllib.request

EXAMPLES = 5


def load_previous(source: str) -> tuple[dict | None, str]:
    """(model, "") on success, (None, reason) otherwise. Never raises."""
    try:
        if source.startswith(("http://", "https://")):
            req = urllib.request.Request(source, headers={"User-Agent": "hyperstratum-diff"})
            with urllib.request.urlopen(req, timeout=20) as r:  # noqa: S310 (https only, caller-supplied)
                return json.loads(r.read().decode("utf-8")), ""
        with open(source, encoding="utf-8") as fh:
            return json.load(fh), ""
    except Exception as exc:  # any failure means "no previous", with the reason kept
        return None, f"{source}: {type(exc).__name__}: {exc}"


def _by_name(model: dict) -> dict[str, dict]:
    return {f["name"]: f for f in model.get("fields", [])}


def _term_totals(model: dict) -> dict[str, int]:
    totals: dict[str, int] = {}
    for f in model.get("fields", []):
        for slug, n in (f.get("mentions") or {}).items():
            totals[slug] = totals.get(slug, 0) + n
    return totals


def diff_models(old: dict | None, new: dict) -> dict | None:
    if old is None:
        return None
    of, nf = _by_name(old), _by_name(new)
    unknown: list[str] = []
    out: dict = {"previous_source_ref": old.get("source_ref", "")}

    out["fields"] = {
        "added": sorted(set(nf) - set(of)),
        "removed": sorted(set(of) - set(nf)),
        "pin_changed": [{"name": n, "old": of[n].get("pin"), "new": nf[n].get("pin")}
                        for n in sorted(set(of) & set(nf)) if of[n].get("pin") != nf[n].get("pin")],
    }

    added_open, removed_open = [], []
    if all("open" in f for f in of.values() if f.get("pin")):
        for n in sorted(nf):
            before = set(of.get(n, {}).get("open", []))
            after = set(nf[n].get("open", []))
            added_open += [{"field": n, "text": t} for t in sorted(after - before)]
            removed_open += [{"field": n, "text": t} for t in sorted(before - after)]
    else:
        unknown.append("open_items")
    out["open_items"] = {"added": added_open, "removed": removed_open}

    symbols: dict[str, dict] = {}
    if all("symbol_names" in f for f in of.values() if f.get("pin")):
        for n in sorted(nf):
            before = set(of.get(n, {}).get("symbol_names", []))
            after = set(nf[n].get("symbol_names", []))
            if before != after:
                symbols[n] = {"added": len(after - before), "removed": len(before - after),
                              "examples_added": sorted(after - before)[:EXAMPLES],
                              "examples_removed": sorted(before - after)[:EXAMPLES]}
    else:
        unknown.append("symbols")
    out["symbols"] = symbols

    ot, nt = _term_totals(old), _term_totals(new)
    out["terms"] = [{"slug": s, "old": ot.get(s, 0), "new": nt.get(s, 0)}
                    for s in sorted(set(ot) | set(nt)) if ot.get(s, 0) != nt.get(s, 0)]

    orf = {r["key"]: r["status"] for r in old.get("refs", [])}
    nrf = {r["key"]: r["status"] for r in new.get("refs", [])}
    out["refs"] = [{"key": k, "old": orf.get(k), "new": nrf.get(k)}
                   for k in sorted(set(orf) | set(nrf)) if orf.get(k) != nrf.get(k)]

    op = {(p["code"], p["subject"]): p for p in old.get("problems", [])}
    np_ = {(p["code"], p["subject"]): p for p in new.get("problems", [])}
    out["problems"] = {"new": [np_[k] for k in sorted(set(np_) - set(op))],
                       "resolved": [op[k] for k in sorted(set(op) - set(np_))]}

    out["unknown"] = unknown
    out["empty"] = not (out["fields"]["added"] or out["fields"]["removed"] or out["fields"]["pin_changed"]
                        or added_open or removed_open or symbols or out["terms"] or out["refs"]
                        or out["problems"]["new"] or out["problems"]["resolved"])
    return out


def _short(x) -> str:
    return (x or "none")[:10]


def changes_markdown(c: dict) -> str:
    prev = _short(c.get("previous_source_ref"))
    if c["empty"]:
        return f"# Changes\n\nNo change since the previous build (`{prev}`).\n"
    L = [f"# Changes since `{prev}`", ""]
    f = c["fields"]
    if f["added"] or f["removed"] or f["pin_changed"]:
        L.append("## Hyperfields")
        L += [f"- added: **{n}**" for n in f["added"]]
        L += [f"- removed: **{n}**" for n in f["removed"]]
        L += [f"- **{p['name']}** `{_short(p['old'])}` → `{_short(p['new'])}`" for p in f["pin_changed"]]
        L.append("")
    o = c["open_items"]
    if o["added"] or o["removed"]:
        L.append("## [OPEN] items")
        L += [f"- new in **{x['field']}**: {x['text']}" for x in o["added"]]
        L += [f"- gone from **{x['field']}**: {x['text']}" for x in o["removed"]]
        L.append("")
    if c["symbols"]:
        L.append("## Symbols")
        for n, s in c["symbols"].items():
            L.append(f"- **{n}**: +{s['added']} / −{s['removed']}"
                     + (f" (e.g. +`{s['examples_added'][0]}`)" if s["examples_added"] else "")
                     + (f" (e.g. −`{s['examples_removed'][0]}`)" if s["examples_removed"] else ""))
        L.append("")
    if c["terms"]:
        L.append("## Vocabulary use (total mentions)")
        L += [f"- `{t['slug']}`: {t['old']} → {t['new']}" for t in c["terms"]]
        L.append("")
    if c["refs"]:
        L.append("## Live references")
        L += [f"- `{r['key']}`: {r['old'] or 'new'} → {r['new'] or 'removed'}" for r in c["refs"]]
        L.append("")
    p = c["problems"]
    if p["new"] or p["resolved"]:
        L.append("## Problems")
        L += [f"- new {x['severity']} `{x['code']}` {x['subject']}" for x in p["new"]]
        L += [f"- resolved `{x['code']}` {x['subject']}" for x in p["resolved"]]
        L.append("")
    if c["unknown"]:
        L.append("_Not comparable (previous build did not record): " + ", ".join(c["unknown"]) + "._")
    return "\n".join(L).rstrip() + "\n"
