"""Assemble the wiki: model first, pages second.

`collect` computes everything as plain data from (ontology, pinned fields).
`render` turns that data into a static site. Keeping them apart is what makes
`wiki.json` -- the same facts, machine-readable -- a by-product rather than a
second implementation that could disagree with the pages.
"""

from __future__ import annotations

import html
import json
import pathlib
import posixpath
import re
import subprocess
import urllib.parse
from dataclasses import dataclass

from . import __version__, lexicon, refs, registry, scan

SCHEMA = "hyperstratum-wiki/1"
PRIMER_DIRS = ("docs", "specs", "examples")
LOCK_FILE = "wiki.lock.json"
SYMBOL_LIMIT = 300
OPEN_LIMIT = 60

STYLE = """
:root{--ink:#16181d;--muted:#5b6270;--rule:#d9dde5;--bg:#fff;--accent:#2f5fd0;--code:#f4f6fa;
--ok:#1a7f4b;--warn:#a15c00;--bad:#b3261e}
@media(prefers-color-scheme:dark){:root{--ink:#e6e8ee;--muted:#9aa3b4;--rule:#2b3140;--bg:#14161b;
--accent:#7aa2f7;--code:#1c2029;--ok:#5fd39a;--warn:#e0a84a;--bad:#ff8a80}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:62rem;margin:0 auto;padding:1.5rem 1rem 5rem}
nav.top{display:flex;gap:1.1rem;flex-wrap:wrap;font-size:.9rem;border-bottom:1px solid var(--rule);
padding-bottom:.7rem;margin-bottom:1.6rem}nav.top a{color:var(--muted);text-decoration:none}
nav.top a:hover{color:var(--accent)}a{color:var(--accent)}
h1{font-size:1.8rem;line-height:1.2;margin:.2rem 0 .8rem}h2{font-size:1.2rem;margin:2rem 0 .6rem;
border-bottom:1px solid var(--rule);padding-bottom:.25rem}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88em}
code{background:var(--code);padding:.12em .32em;border-radius:3px}
pre{background:var(--code);padding:.8rem 1rem;overflow-x:auto;border-radius:6px;white-space:pre-wrap}
table{border-collapse:collapse;width:100%;margin:.8rem 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--rule);padding:.35rem .6rem;text-align:left;vertical-align:top;font-size:.92rem}
th{background:var(--code)}.muted{color:var(--muted)}.def{border-left:3px solid var(--accent);
padding:.2rem 1rem;margin:1rem 0;font-size:1.05rem}
blockquote.transclusion{margin:1rem 0;padding:.2rem 1rem;border-left:3px solid var(--rule)}
blockquote.transclusion pre{background:none;padding:0}
.tag{display:inline-block;font-size:.75rem;border:1px solid var(--rule);border-radius:99px;
padding:0 .55rem;color:var(--muted);margin-right:.3rem}
.ok{color:var(--ok)}.warning,.BEHIND,.DRIFTED,.UNRESOLVABLE{color:var(--warn)}.error{color:var(--bad)}
.CURRENT{color:var(--ok)}input.q{width:100%;padding:.5rem .7rem;font:inherit;margin:.5rem 0 1rem;
border:1px solid var(--rule);border-radius:6px;background:var(--bg);color:var(--ink)}
ul.cols{columns:3 14rem;list-style:none;padding:0}footer{margin-top:3rem;font-size:.8rem;
color:var(--muted);border-top:1px solid var(--rule);padding-top:.8rem}
"""


# --------------------------------------------------------------------- git


class GitBlobs:
    """`blob_lookup(sha, path)`: the git blob id of `path` at `sha`, else None."""

    def __init__(self, root: pathlib.Path):
        self.root = root

    def __call__(self, sha: str, path: str) -> str | None:
        done = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--verify", "-q",
                               f"{sha}:{path}"], capture_output=True, text=True)
        return done.stdout.strip() if done.returncode == 0 else None


def head_sha(root: pathlib.Path) -> str:
    done = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


# ------------------------------------------------------------------- model


@dataclass
class Collected:
    model: dict
    reg: registry.Registry
    terms: list[lexicon.Term]
    statements: list[lexicon.Statement]
    levels: list[list[str]]
    scans: dict[str, scan.FieldScan]
    audits: list[scan.Audit]
    edges: list[scan.Edge]
    resolver: refs.Resolver
    resolved: list[refs.Resolved]
    documents: dict[str, str]  # source path -> rendered markdown (refs expanded) kept for render


def _authored_sources(root: pathlib.Path) -> dict[str, str]:
    """source path -> published path, for every authored markdown document."""
    found: dict[str, str] = {}
    readme = root / "README.md"
    if readme.is_file():
        found["README.md"] = "primer/README.html"
    for d in PRIMER_DIRS:
        for p in sorted((root / d).rglob("*.md")) if (root / d).is_dir() else []:
            rel = p.relative_to(root).as_posix()
            if rel.startswith("docs/family/"):
                continue
            found[rel] = "primer/" + rel[:-3] + ".html"
    wiki = root / "wiki"
    for p in sorted(wiki.glob("*.md")) if wiki.is_dir() else []:
        found[f"wiki/{p.name}"] = f"pages/{p.stem}.html"
    return found


def _rel(src: str, dst: str) -> str:
    return posixpath.relpath(dst, posixpath.dirname(src) or ".")


def collect(root, pins=None, blob_lookup=None, lock: dict | None = None,
            source_ref: str = "") -> Collected:
    root = pathlib.Path(root)
    reg = registry.load_registry(root, pins=pins)
    blob_lookup = blob_lookup or GitBlobs(root)

    canon = root / "specs" / "canonical-definitions.md"
    chain = root / "specs" / "dependency-graph.md"
    terms, statements = lexicon.parse_canonical(canon.read_text(encoding="utf-8")) if canon.is_file() else ([], [])
    levels = lexicon.parse_construction(chain.read_text(encoding="utf-8")) if chain.is_file() else []
    terms = lexicon.assign_strata(terms, levels)

    names = scan.sibling_names(reg)
    scans = {f.name: scan.scan_field(f, terms, names)
             for f in reg.fields if f.pin and f.path.is_dir()}
    edges = scan.build_edges(scans, reg)
    citations = [c for n in sorted(scans) for c in scans[n].citations]
    audits = scan.audit_citations(citations, reg, blob_lookup)

    if lock is None:
        lock = refs.load_lock(root / LOCK_FILE)
    resolver = refs.Resolver(reg, terms, root, lock=lock)

    sources = _authored_sources(root)
    resolved: list[refs.Resolved] = []
    documents: dict[str, str] = {}
    for src in sources:
        text = (root / src).read_text(encoding="utf-8", errors="replace")
        here = sources[src]
        expanded, got = resolver.expand(
            text,
            link_term=lambda slug, here=here: _rel(here, f"terms/{slug}.html"),
            link_field=lambda name, here=here: _rel(here, f"fields/{name}.html"))
        resolved.extend(got)
        documents[src] = expanded

    problems = [p.as_dict() for p in reg.problems()]
    problems += [p for p in (r.problem() for r in resolved) if p]
    for a in audits:
        if a.status in ("DRIFTED", "BEHIND", "UNRESOLVABLE"):
            problems.append({"code": f"CITATION_{a.status}", "severity": "warning",
                             "subject": f"{a.citation.source}:{a.citation.file}#L{a.citation.line}",
                             "detail": f"-> {a.citation.target}:{a.citation.path}: {a.detail}"})
    for n, s in sorted(scans.items()):
        if s.contract_error:
            problems.append({"code": "BAD_CONTRACT", "severity": "warning", "subject": n,
                             "detail": f"FIELD.json: {s.contract_error}"})
    problems.sort(key=lambda p: (p["severity"] != "error", p["severity"] != "warning", p["code"], p["subject"]))

    model = {
        "schema": SCHEMA,
        "generator": f"hyperstratum {__version__}",
        "source_ref": source_ref,
        "ontology": {
            "terms": [{"name": t.name, "slug": t.slug, "definition": t.definition,
                       "stratum": t.stratum, "scannable": t.scannable} for t in terms],
            "statements": [{"name": s.name, "text": s.text} for s in statements],
            "levels": levels,
        },
        "fields": [_field_row(f, scans.get(f.name), terms) for f in reg.fields],
        "edges": [{"source": e.source, "target": e.target, "kind": e.kind, "count": e.count,
                   "evidence": [list(x) for x in e.evidence]} for e in edges],
        "citations": [{"source": a.citation.source, "file": a.citation.file, "line": a.citation.line,
                       "target": a.citation.target, "sha": a.citation.sha, "path": a.citation.path,
                       "status": a.status, "detail": a.detail} for a in audits],
        "refs": [{"key": r.key, "status": r.status, "detail": r.detail} for r in resolved],
        "problems": problems,
    }
    return Collected(model, reg, terms, statements, levels, scans, audits, edges, resolver,
                     resolved, documents)


def _field_row(f: registry.Field, s: scan.FieldScan | None, terms: list[lexicon.Term]) -> dict:
    row = {"name": f.name, "role": f.role, "tagline": f.tagline, "repo": f.repo_url,
           "pin": f.pin, "pending": f.pending}
    if s is not None:
        row.update({
            "files": s.files, "tags": s.tags, "lean_sorry_occurrences": s.sorry_count,
            "contract": s.contract, "symbols": len(s.symbols), "open_items": len(s.open_items),
            "mentions": {slug: m.count for slug, m in sorted(s.mentions.items()) if m.count},
        })
    return row


# ------------------------------------------------------------------ render


def _e(x) -> str:
    return html.escape(str(x), quote=True)


def _q(path: str) -> str:
    return urllib.parse.quote(path, safe="/")


class Site:
    def __init__(self, c: Collected, out: pathlib.Path):
        self.c, self.out = c, out
        self.fields = c.reg.by_name
        self.written: list[str] = []

    def write(self, rel: str, text: str) -> None:
        path = self.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        self.written.append(rel)

    def link(self, here: str, to: str, label: str | None = None) -> str:
        return f'<a href="{_e(_rel(here, to))}">{_e(label if label is not None else to)}</a>'

    def page(self, here: str, title: str, body: str) -> str:
        nav = " ".join(self.link(here, to, label) for to, label in [
            ("index.html", "Wiki"), ("index.html#terms", "Terms"), ("index.html#fields", "Fields"),
            ("open.html", "Open questions"), ("audit.html", "Audit")])
        css = _rel(here, "style.css")
        ref = f" &middot; built from <code>{_e(self.c.model['source_ref'][:12])}</code>" if self.c.model["source_ref"] else ""
        return (f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{_e(title)} &middot; Hyperstratum</title>'
                f'<link rel="stylesheet" href="{_e(css)}"></head><body><div class="wrap">'
                f'<nav class="top">{nav}</nav>\n{body}\n'
                f'<footer>hyperstratum {_e(__version__)}{ref} &middot; pinned references, not live HEADs</footer>'
                f'</div></body></html>\n')

    # -- pieces ----------------------------------------------------------
    def loc_links(self, f: registry.Field, locs, limit: int = 4) -> str:
        shown = [f'<a href="{_e(f.permalink(p, f"L{n}"))}">{_e(p)}:{n}</a>' for p, n in locs[:limit]]
        return ", ".join(shown) + (f' <span class="muted">+{len(locs) - limit} more</span>' if len(locs) > limit else "")

    def field_link(self, here: str, name: str) -> str:
        if name in self.fields:
            return self.link(here, f"fields/{name}.html", name)
        return f'<a href="https://github.com/{registry.OWNER}/{_e(name)}">{_e(name)}</a>'

    # -- pages -----------------------------------------------------------
    def term_page(self, t: lexicon.Term) -> None:
        here = f"terms/{t.slug}.html"
        c = self.c
        b = [f"<h1>{_e(t.name)}</h1>"]
        if t.stratum is not None:
            peers = [x for x in c.levels[t.stratum] if x != t.slug]
            tag = f'<span class="tag">construction level {t.stratum + 1} of {len(c.levels)}</span>'
            b.append(tag + (" alongside " + ", ".join(self.term_ref(here, s) for s in peers) if peers else ""))
            nav = []
            if t.stratum > 0:
                nav.append("built from: " + ", ".join(self.term_ref(here, s) for s in c.levels[t.stratum - 1]))
            if t.stratum + 1 < len(c.levels):
                nav.append("builds: " + ", ".join(self.term_ref(here, s) for s in c.levels[t.stratum + 1]))
            if nav:
                b.append(f'<p class="muted">{" &middot; ".join(nav)}</p>')
        else:
            b.append('<span class="tag">compound / derived term</span>')
        b.append(f'<div class="def">{_e(t.definition)}</div>')
        b.append(f'<p class="muted">Defined in {self.link(here, "primer/specs/canonical-definitions.html", "specs/canonical-definitions.md")}.</p>')
        parts = [x for x in c.terms if x.slug != t.slug and t.slug in x.slug.split("-")]
        inside = [x for x in c.terms if x.slug != t.slug and x.slug in t.slug.split("-")]
        if parts or inside:
            rel = [("contains", inside), ("appears inside", parts)]
            b.append("<h2>Related terms</h2><ul>" + "".join(
                f"<li>{label}: {', '.join(self.term_ref(here, x.slug) for x in xs)}</li>"
                for label, xs in rel if xs) + "</ul>")
        b.append("<h2>Where it lives</h2>")
        if not t.scannable:
            b.append('<p class="muted">An ordinary English word as well as a term. Occurrences in other '
                     'repositories are not counted: the count would measure the language, not the ontology.</p>')
        else:
            rows = []
            for name, s in sorted(c.scans.items(), key=lambda kv: (-kv[1].mentions[t.slug].count, kv[0])):
                m = s.mentions[t.slug]
                if m.count:
                    rows.append(f"<tr><td>{self.field_link(here, name)}</td><td>{m.count}</td>"
                                f"<td>{self.loc_links(self.fields[name], m.locations)}</td></tr>")
            b.append("<table><tr><th>Hyperfield</th><th>Mentions</th><th>First places (at the pinned commit)</th></tr>"
                     + "".join(rows) + "</table>" if rows else
                     '<p class="muted">Not mentioned in any pinned hyperfield.</p>')
        self.write(here, self.page(here, t.name, "\n".join(b)))

    def term_ref(self, here: str, slug: str) -> str:
        t = next((x for x in self.c.terms if x.slug == slug), None)
        return self.link(here, f"terms/{slug}.html", t.name if t else slug) if t else _e(slug)

    def field_page(self, f: registry.Field) -> None:
        here = f"fields/{f.name}.html"
        c, s = self.c, self.c.scans.get(f.name)
        b = [f"<h1>{_e(f.name)}</h1>",
             f'<span class="tag">{_e(f.role)}</span> <a href="{_e(f.repo_url)}">{_e(f.repo_url)}</a>',
             f"<p>{_e(f.tagline)}</p>"]
        if f.pin:
            b.append(f'<p class="muted">Pinned at <a href="{_e(f.permalink())}"><code>{_e(f.pin[:12])}</code></a>. '
                     "Everything below is read from that commit.</p>")
        else:
            b.append(f'<p><strong>No pinned commit (pending).</strong> {_e(f.pending or "")}</p>')
        if s is None:
            self.write(here, self.page(here, f.name, "\n".join(b)))
            return
        if s.excerpt:
            b.append(f'<div class="def">{_e(s.excerpt)}</div>')
        if s.contract:
            rows = "".join(f"<tr><th>{_e(k)}</th><td>{self._json_cell(v)}</td></tr>"
                           for k, v in s.contract.items() if k in
                           ("scope", "classification", "exclusions", "exports", "verifier_status", "contract_version"))
            b.append(f"<h2>Contract (<code>FIELD.json</code>)</h2><table>{rows}</table>")
        facts = [f"{n} {suffix} file(s)" for suffix, n in s.files.items()]
        if s.tags:
            facts.append("tags: " + " ".join(f"[{k}]&times;{v}" for k, v in s.tags.items()))
        if s.sorry_count:
            facts.append(f"{s.sorry_count} textual <code>sorry</code> occurrence(s) in Lean (open proof obligations, approximate)")
        b.append("<h2>Shape</h2><p>" + " &middot; ".join(_e(x) if "<code>" not in x and "&times;" not in x else x for x in facts) + "</p>")
        used = [(t, s.mentions[t.slug]) for t in c.terms if t.scannable and s.mentions[t.slug].count]
        if used:
            b.append("<h2>Vocabulary from the lexicon</h2><table><tr><th>Term</th><th>Mentions</th><th>First places</th></tr>"
                     + "".join(f"<tr><td>{self.link(here, f'terms/{t.slug}.html', t.name)}</td><td>{m.count}</td>"
                               f"<td>{self.loc_links(f, m.locations, 3)}</td></tr>"
                               for t, m in sorted(used, key=lambda x: -x[1].count)) + "</table>")
        out_e = [e for e in c.edges if e.source == f.name]
        in_e = [e for e in c.edges if e.target == f.name]
        if out_e or in_e:
            b.append("<h2>Connections to other repositories</h2>")
            for title, rows, col in (("Refers to", out_e, "target"), ("Referred to by", in_e, "source")):
                if rows:
                    b.append(f"<h3>{title}</h3><table><tr><th>Repository</th><th>How</th><th>Count</th><th>Evidence</th></tr>"
                             + "".join(f"<tr><td>{self.field_link(here, getattr(e, col))}</td>"
                                       f"<td>{'link' if e.kind == 'url' else 'named in prose'}</td><td>{e.count}</td>"
                                       f"<td>{self._evidence(e)}</td></tr>" for e in rows) + "</table>")
        cites = [a for a in c.audits if a.citation.source == f.name]
        if cites:
            b.append("<h2>Commit-pinned citations</h2><table><tr><th>Where</th><th>Cites</th><th>Status</th></tr>"
                     + "".join(self._citation_row(here, a) for a in cites) + "</table>")
        if s.open_items:
            b.append(f'<h2 id="open">[OPEN] items ({len(s.open_items)})</h2><ul>'
                     + "".join(f'<li><a href="{_e(f.permalink(p, f"L{n}"))}">{_e(p)}:{n}</a> {_e(t)}</li>'
                               for p, n, t in s.open_items[:OPEN_LIMIT]) + "</ul>")
        if s.symbols:
            shown = s.symbols[:SYMBOL_LIMIT]
            b.append(f"<h2>Symbols ({len(s.symbols)})</h2><table><tr><th>Kind</th><th>Name</th><th>Where</th><th>Doc</th></tr>"
                     + "".join(f'<tr><td>{_e(x.kind)}</td><td><code>{_e(x.name)}</code></td>'
                               f'<td><a href="{_e(f.permalink(x.path, f"L{x.line}"))}">{_e(x.path)}:{x.line}</a></td>'
                               f"<td>{_e(x.doc)}</td></tr>" for x in shown) + "</table>"
                     + (f'<p class="muted">{len(s.symbols) - SYMBOL_LIMIT} more not shown.</p>' if len(s.symbols) > SYMBOL_LIMIT else ""))
        self.write(here, self.page(here, f.name, "\n".join(b)))

    def _json_cell(self, v) -> str:
        if isinstance(v, list):
            return ", ".join(f"<code>{_e(x)}</code>" if len(str(x)) < 40 else _e(x) for x in v)
        return _e(v)

    def _evidence(self, e: scan.Edge) -> str:
        f = self.fields.get(e.source)
        return self.loc_links(f, list(e.evidence), 2) if f else ""

    def _citation_row(self, here: str, a: scan.Audit) -> str:
        c = a.citation
        f = self.fields.get(c.source)
        where = (f'<a href="{_e(f.permalink(c.file, f"L{c.line}"))}">{_e(c.source)}:{_e(c.file)}:{c.line}</a>'
                 if f else _e(c.source))
        return (f"<tr><td>{where}</td><td>{self.field_link(here, c.target)}:<code>{_e(c.path)}</code> "
                f"@ <code>{_e(c.sha[:10])}</code></td><td class=\"{_e(a.status)}\">{_e(a.status)} "
                f'<span class="muted">{_e(a.detail)}</span></td></tr>')

    def open_page(self) -> None:
        here, b = "open.html", ["<h1>Open questions across the hyperfields</h1>",
                                 '<p class="muted">Every line tagged <code>[OPEN]</code> in a pinned hyperfield, '
                                 "gathered live. Each is the author's own marker of an unresolved claim.</p>"]
        total = 0
        for name, s in sorted(self.c.scans.items()):
            if not s.open_items:
                continue
            f = self.fields[name]
            total += len(s.open_items)
            b.append(f'<h2>{self.field_link(here, name)} <span class="muted">({len(s.open_items)})</span></h2><ul>'
                     + "".join(f'<li><a href="{_e(f.permalink(p, f"L{n}"))}">{_e(p)}:{n}</a> {_e(t)}</li>'
                               for p, n, t in s.open_items[:OPEN_LIMIT]) + "</ul>")
        if not total:
            b.append("<p>No <code>[OPEN]</code> markers found.</p>")
        self.write(here, self.page(here, "Open questions", "\n".join(b)))

    def audit_page(self) -> None:
        here, c = "audit.html", self.c
        b = ["<h1>Audit</h1>", '<p class="muted">What the wiki cannot vouch for, stated plainly.</p>',
             "<h2>Problems</h2>"]
        if c.model["problems"]:
            b.append("<table><tr><th>Severity</th><th>Code</th><th>Subject</th><th>Detail</th></tr>"
                     + "".join(f'<tr><td class="{_e(p["severity"])}">{_e(p["severity"])}</td><td>{_e(p["code"])}</td>'
                               f'<td>{_e(p["subject"])}</td><td>{_e(p["detail"])}</td></tr>'
                               for p in c.model["problems"]) + "</table>")
        else:
            b.append("<p>None.</p>")
        b.append("<h2>Citations pinned to a commit</h2>")
        b.append("<table><tr><th>Where</th><th>Cites</th><th>Status</th></tr>"
                 + "".join(self._citation_row(here, a) for a in c.audits) + "</table>" if c.audits else "<p>None found.</p>")
        b.append("<h2>Reference status in authored pages</h2>")
        rs = [r for r in c.resolved]
        b.append("<table><tr><th>Reference</th><th>Status</th><th>Detail</th></tr>" + "".join(
            f'<tr><td><code>{_e(r.key)}</code></td><td class="{"ok" if r.status == "OK" else "warning"}">{_e(r.status)}</td>'
            f"<td>{_e(r.detail)}</td></tr>" for r in rs) + "</table>" if rs else "<p>No authored page uses a live reference yet.</p>")
        self.write(here, self.page(here, "Audit", "\n".join(b)))

    def index_page(self) -> None:
        here, c = "index.html", self.c
        pinned = [f for f in c.reg.fields if f.pin]
        b = ["<h1>Hyperstratum</h1>",
             "<p>The dictionary, encyclopedia and wiki of the hyperfields. Terms are authored here; "
             "every statement about a hyperfield is read from that repository at a pinned commit.</p>",
             f'<p class="muted">{len(c.terms)} terms &middot; {len(pinned)} pinned hyperfields &middot; '
             f"{sum(len(s.symbols) for s in c.scans.values())} symbols &middot; "
             f"{sum(len(s.open_items) for s in c.scans.values())} [OPEN] items &middot; "
             f'{sum(1 for p in c.model["problems"] if p["severity"] == "error")} error(s), '
             f'{sum(1 for p in c.model["problems"] if p["severity"] == "warning")} warning(s) — '
             f'{self.link(here, "audit.html", "audit")}</p>',
             '<input class="q" id="q" placeholder="filter terms and fields" aria-label="filter">',
             '<h2 id="terms">Terms</h2><ul class="cols" id="terms-list">']
        for t in sorted(c.terms, key=lambda x: x.name.lower()):
            b.append(f'<li data-q="{_e(t.name.lower())} {_e(t.definition.lower())}">'
                     f'{self.link(here, f"terms/{t.slug}.html", t.name)}</li>')
        b.append("</ul>")
        if c.statements:
            b.append("<h2>Statements</h2>" + "".join(
                f"<h3>{_e(s.name)}</h3><div class=\"def\">{_e(s.text)}</div>" for s in c.statements))
        b.append('<h2 id="fields">Hyperfields</h2><table id="fields-table"><tr><th>Field</th><th>Role</th><th>What it is</th>'
                 "<th>Pin</th><th>Symbols</th><th>[OPEN]</th></tr>")
        for f in c.reg.fields:
            s = c.scans.get(f.name)
            pin = (f'<a href="{_e(f.permalink())}"><code>{_e(f.pin[:10])}</code></a>' if f.pin
                   else f"<em>pending</em> — {_e(f.pending or '')}")
            b.append(f'<tr data-q="{_e(f.name.lower())} {_e(f.tagline.lower())} {_e(f.role)}">'
                     f"<td>{self.link(here, f'fields/{f.name}.html', f.name)}</td><td>{_e(f.role)}</td>"
                     f"<td>{_e(f.tagline)}</td><td>{pin}</td>"
                     f"<td>{len(s.symbols) if s else '—'}</td><td>{len(s.open_items) if s else '—'}</td></tr>")
        b.append("</table>")
        docs = sorted(((src, pub) for src, pub in _authored_sources(c.reg.root).items()), key=lambda x: x[1])
        if docs:
            b.append("<h2>Primer and authored pages</h2><ul>" + "".join(
                f"<li>{self.link(here, pub, src)}</li>" for src, pub in docs) + "</ul>")
        b.append("<script>document.getElementById('q').addEventListener('input',function(e){"
                 "var v=e.target.value.toLowerCase();document.querySelectorAll('[data-q]').forEach(function(n){"
                 "n.style.display=n.getAttribute('data-q').indexOf(v)<0?'none':''})})</script>")
        self.write(here, self.page(here, "Hyperstratum", "\n".join(b)))

    def document_pages(self) -> None:
        import markdown

        sources = _authored_sources(self.c.reg.root)
        for src, pub in sources.items():
            text = rewrite_links(self.c.documents[src], src, pub, sources)
            body = markdown.markdown(text, extensions=["extra", "sane_lists", "toc"], output_format="html5")
            title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), src)
            self.write(pub, self.page(pub, title, body))


def rewrite_links(text: str, src: str, pub: str, sources: dict[str, str]) -> str:
    """Point relative markdown links at where their targets are published."""
    def fix(m: re.Match) -> str:
        target = m.group(2)
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            return m.group(0)
        path, _, frag = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src), urllib.parse.unquote(path)))
        if resolved not in sources:
            return m.group(0)
        return f"{m.group(1)}({_rel(pub, sources[resolved])}{'#' + frag if frag else ''})"
    return re.sub(r"(\[[^\]]*\])\(\s*([^)\s]+)\s*\)", fix, text)


def render(c: Collected, out: pathlib.Path) -> Site:
    site = Site(c, pathlib.Path(out))
    site.write("style.css", STYLE)
    site.index_page()
    for t in c.terms:
        site.term_page(t)
    for f in c.reg.fields:
        site.field_page(f)
    site.open_page()
    site.audit_page()
    site.document_pages()
    site.write("wiki.json", json.dumps(c.model, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return site


def build_site(root, out, pins=None, blob_lookup=None, lock=None, source_ref: str = "") -> dict:
    c = collect(root, pins=pins, blob_lookup=blob_lookup, lock=lock, source_ref=source_ref)
    render(c, pathlib.Path(out))
    return c.model


def link_landing(landing: pathlib.Path, href: str, label: str = "Browse the hyperfield wiki") -> bool:
    """Add one idempotent link to the wiki into a landing page another builder owns."""
    marker = "<!-- hyperstratum-wiki-link -->"
    try:
        text = landing.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    if marker in text or "</body>" not in text:
        return False
    block = (f'{marker}\n<p style="max-width:46rem;margin:2rem auto;padding:0 1rem;font:16px/1.65 sans-serif">'
             f'<a href="{_e(href)}">{_e(label)} &#8594;</a></p>\n')
    landing.write_text(text.replace("</body>", block + "</body>", 1), encoding="utf-8")
    return True
