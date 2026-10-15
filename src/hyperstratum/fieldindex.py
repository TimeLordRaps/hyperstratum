"""A navigable index of the hyperfields, read from the checkouts this repository pins.

One static page, one entry per registered field: what the field is (role and tagline, from
`registry/fields.json`), where it lives (its repository, its public site if the family graph
records one, and the commit this repository pins), what its checkout contains (files, `.hm`
declarations, Lean files, test functions, and decisions and debt where the repository keeps
them), what the family graph says it is connected to, and what is missing.

What it reads, and what it does not:

* It reads text only. It never runs Lean, never evaluates an `.hm` statement, and never fetches
  anything, so the page makes no requests when it is opened.
* A declaration is a top-level line (no indentation, not in a `--` or `/- -/` comment) whose first
  word is one of `DECLARATION_KEYWORDS`, the keywords the fields' `.hm` files use. It is a keyword
  match, not a check.
* A decision is a heading `D<number>`; a debt row is a table row whose first cell is an identifier
  such as `HS-039`. A repository that keeps these in another shape shows none, and its entry says
  which files it has.
* A connection comes from the family graph. A citation is a cross-reference between two
  repositories, not a proof, a derivation, or an implemented interface.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import subprocess
from dataclasses import dataclass

from . import registry

DECLARATION_KEYWORDS = (
    "non-derive", "axiom", "derive", "open", "opaque", "primitive",
    "law", "relation", "close", "termformer", "graduation",
)
ROLE_ORDER = ("foundation", "companion", "applied", "language", "combination", "substrate", "declared", "unplaced")
SUMMARY_LIMIT = 360
GRAPH = pathlib.PurePosixPath("docs/family/family-graph.json")

_KEYWORD_ALTERNATION = "|".join(DECLARATION_KEYWORDS)
_DECLARATION = re.compile(rf"(?P<kind>{_KEYWORD_ALTERNATION})\s+(?P<name>[A-Za-z][\w'-]*)")
_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_EMPHASIS = re.compile(r"[*_`]+")
_SKIP_LINE = ("#", "![", "[!", "<", "|", "```", "> ", "- ", "* ", "+ ", "1. ")
_DEBT_ROW = re.compile(r"^\|\s*(?P<id>[A-Z]{1,4}-\d{3})\s*\|\s*(?P<where>[^|]*)\|")
_DECISION_HEAD = re.compile(r"^#{1,6}\s*\**(?P<id>D\d{1,3})\b\**[\s:.\-—–]*(?P<title>.*)$")
_TEST_DEF = re.compile(r"^[ \t]*def (test_\w+)", re.MULTILINE)


@dataclass(frozen=True)
class Declaration:
    kind: str
    name: str
    file: str
    line: int


@dataclass(frozen=True)
class DebtRow:
    id: str
    where: str
    line: int


@dataclass(frozen=True)
class Scan:
    files: int
    top: tuple[tuple[str, int], ...]
    hm: tuple[str, ...]
    lean: tuple[str, ...]
    test_functions: int


@dataclass
class FieldEntry:
    name: str
    role: str
    tagline: str
    repo_url: str
    pages_url: str | None
    pin: str | None
    checked_out: bool
    pending: str | None
    field: registry.Field
    title: str | None
    summary: str | None
    scan: Scan | None
    declarations: tuple[Declaration, ...]
    decisions: tuple[tuple[str, str], ...]
    decisions_file: bool
    debt: tuple[DebtRow, ...]
    debt_file: bool
    validation_file: bool
    connections: tuple[tuple[str, str, str, int], ...]
    notes: tuple[str, ...]


@dataclass
class Index:
    entries: tuple[FieldEntry, ...]
    digest: str | None
    head: str | None
    problems: tuple[str, ...]


def _plain(text: str) -> str:
    return " ".join(_EMPHASIS.sub("", _LINK.sub(r"\1", text)).split())


def readme_summary(text: str) -> tuple[str | None, str | None]:
    """The title (first `# ` heading) and the first prose paragraph, as plain text."""
    lines = text.splitlines()
    title = None
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("# "):
        title = lines[i].lstrip()[2:].strip() or None
        i += 1
    paragraph: list[str] = []
    for line in lines[i:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(_SKIP_LINE):
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    if not paragraph:
        return title, None
    summary = _plain(" ".join(paragraph))
    if len(summary) > SUMMARY_LIMIT:
        summary = summary[:SUMMARY_LIMIT].rsplit(" ", 1)[0] + "…"
    return title, summary


def parse_declarations(text: str, file: str) -> list[Declaration]:
    found: list[Declaration] = []
    in_block = False
    for number, line in enumerate(text.splitlines(), 1):
        if in_block:
            in_block = "-/" not in line
            continue
        if line.startswith("/-") and "-/" not in line:
            in_block = True
            continue
        if not line or line[0].isspace() or line.startswith("--"):
            continue
        match = _DECLARATION.match(line)
        if match:
            found.append(Declaration(match["kind"], match["name"], file, number))
    return found


def parse_debt(text: str) -> list[DebtRow]:
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        match = _DEBT_ROW.match(line)
        if match:
            rows.append(DebtRow(match["id"], _plain(match["where"])[:120], number))
    return rows


def parse_decisions(text: str) -> list[tuple[str, str]]:
    found = []
    for line in text.splitlines():
        match = _DECISION_HEAD.match(line)
        if match:
            found.append((match["id"], _plain(match["title"])[:140]))
    return found


def scan_checkout(path: pathlib.Path) -> Scan:
    rels = []
    for candidate in path.rglob("*"):
        rel = candidate.relative_to(path)
        if ".git" in rel.parts or not candidate.is_file():
            continue
        rels.append(rel)
    counts: dict[str, int] = {}
    for rel in rels:
        key = rel.parts[0] if len(rel.parts) > 1 else "."
        counts[key] = counts.get(key, 0) + 1
    functions = 0
    for rel in rels:
        if rel.suffix == ".py" and rel.name.startswith("test_"):
            functions += len(_TEST_DEF.findall(_read(path / rel) or ""))
    return Scan(
        files=len(rels),
        top=tuple(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:10]),
        hm=tuple(sorted(rel.as_posix() for rel in rels if rel.suffix == ".hm")),
        lean=tuple(sorted(rel.as_posix() for rel in rels if rel.suffix == ".lean")),
        test_functions=functions,
    )


def _read(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _role_rank(role: str) -> int:
    return ROLE_ORDER.index(role) if role in ROLE_ORDER else len(ROLE_ORDER)


def _graph(root: pathlib.Path) -> dict:
    path = root / GRAPH
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _connections(graph: dict, name: str) -> tuple[tuple[str, str, str, int], ...]:
    out = []
    for edge in graph.get("edges", []):
        weight = int(edge.get("weight", 1))
        if edge.get("source") == name:
            out.append(("out", edge["target"], edge.get("kind", "?"), weight))
        elif edge.get("target") == name:
            out.append(("in", edge["source"], edge.get("kind", "?"), weight))
    return tuple(sorted(out))


def _head(root: pathlib.Path) -> str | None:
    done = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True, check=False)
    return done.stdout.strip() if done.returncode == 0 else None


def _entry(fld: registry.Field, nodes: dict, graph: dict) -> FieldEntry:
    path = fld.path
    checked_out = path.is_dir() and any(child.name != ".git" for child in path.iterdir())
    readme = _read(path / "README.md") if checked_out else None
    title, summary = readme_summary(readme) if readme else (None, None)
    scan = scan_checkout(path) if checked_out else None
    declarations: list[Declaration] = []
    if scan:
        for rel in scan.hm:
            declarations.extend(parse_declarations(_read(path / rel) or "", rel))
    decisions_text = _read(path / "DECISIONS.md") if checked_out else None
    debt_text = _read(path / "TECHNICAL_DEBT.md") if checked_out else None
    notes = []
    if fld.pin is None:
        notes.append("not pinned in the index")
    if fld.pending:
        notes.append(f"pending: {fld.pending}")
    if not checked_out:
        notes.append("checkout is empty (run `git submodule update --init` for this field)")
    elif readme is None:
        notes.append("no README.md")
    if scan and scan.test_functions == 0:
        notes.append("no test functions found")
    if scan and not scan.hm and not scan.lean:
        notes.append("no `.hm` or Lean specification files")
    node = nodes.get(fld.name, {})
    return FieldEntry(
        name=fld.name, role=fld.role, tagline=fld.tagline or "", repo_url=fld.repo_url,
        pages_url=node.get("pages_url"), pin=fld.pin, checked_out=checked_out,
        pending=fld.pending, field=fld, title=title, summary=summary, scan=scan,
        declarations=tuple(declarations),
        decisions=tuple(parse_decisions(decisions_text)) if decisions_text else (),
        decisions_file=decisions_text is not None,
        debt=tuple(parse_debt(debt_text)) if debt_text else (),
        debt_file=debt_text is not None,
        validation_file=checked_out and (path / "VALIDATION.md").is_file(),
        connections=_connections(graph, fld.name), notes=tuple(notes),
    )


def build_index(root: pathlib.Path, pins: dict[str, str] | None = None) -> Index:
    root = pathlib.Path(root)
    reg = registry.load_registry(root, pins=pins)
    graph = _graph(root)
    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    entries = tuple(_entry(fld, nodes, graph)
                    for fld in sorted(reg.fields, key=lambda f: (_role_rank(f.role), f.name)))
    problems = tuple(f"{p.code} ({p.severity}): {p.subject}, {p.detail}" for p in reg.problems())
    return Index(entries=entries, digest=graph.get("digest"), head=_head(root), problems=problems)


# --- the page ---------------------------------------------------------------------------------------------------

def _e(text: object) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def _search_text(entry: FieldEntry) -> str:
    parts = [entry.name, entry.tagline, entry.summary or "", *(d.name for d in entry.declarations),
             *(title for _id, title in entry.decisions), *(row.where for row in entry.debt)]
    if entry.scan:
        parts.extend(entry.scan.hm)
        parts.extend(entry.scan.lean)
    return " ".join(parts).lower()


def _chips(entry: FieldEntry) -> str:
    chips = []
    chips.append("README" if entry.summary or entry.title else "no README")
    if entry.scan:
        chips.append(f"{entry.scan.files} files")
        chips.append(f"{len(entry.declarations)} `.hm` declarations" if entry.declarations else "no `.hm`")
        if entry.scan.lean:
            chips.append(f"{len(entry.scan.lean)} Lean files")
        chips.append(f"{entry.scan.test_functions} tests")
    if entry.decisions_file:
        chips.append(f"{len(entry.decisions)} decisions")
    if entry.debt_file:
        chips.append(f"{len(entry.debt)} debt rows")
    if entry.validation_file:
        chips.append("validation receipt")
    return "".join(f'<span class="chip">{_e(c)}</span>' for c in chips)


def _declarations_html(entry: FieldEntry) -> str:
    if not entry.declarations:
        return "<p class=\"muted\">No declarations.</p>"
    rows = []
    for decl in entry.declarations:
        link = entry.field.permalink(decl.file, f"L{decl.line}")
        rows.append(f'<tr><td>{_e(decl.kind)}</td><td><code>{_e(decl.name)}</code></td>'
                    f'<td><a href="{_e(link)}">{_e(decl.file)}:{decl.line}</a></td></tr>')
    return ('<table><thead><tr><th>kind</th><th>name</th><th>where (pinned commit)</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def _entry_html(entry: FieldEntry) -> str:
    links = [f'<a href="{_e(entry.repo_url)}">repository</a>']
    if entry.pages_url:
        links.append(f'<a href="{_e(entry.pages_url)}">public site</a>')
    if entry.pin:
        links.append(f'pinned <code>{_e(entry.pin[:12])}</code>')
    separator = " · "
    body = [f'<p class="links">{separator.join(links)}</p>']
    if entry.summary:
        readme_link = entry.field.permalink("README.md")
        body.append(f'<p class="summary">{_e(entry.summary)} <a href="{_e(readme_link)}">README</a></p>')
    if entry.scan:
        contents = " · ".join(f"{_e(name)} ({count})" for name, count in entry.scan.top)
        body.append(f'<h3>Contents</h3><p class="muted">{contents}</p>')
        body.append(f'<h3>Declarations</h3>{_declarations_html(entry)}')
        if entry.scan.lean:
            names = ", ".join(_e(name) for name in entry.scan.lean[:40])
            more = f" and {len(entry.scan.lean) - 40} more" if len(entry.scan.lean) > 40 else ""
            body.append('<h3>Lean</h3><p class="muted">Lean sources are listed here and not rendered: '
                        f'lean4-explainer is a separate step.</p><p class="files">{names}{more}</p>')
    if entry.decisions:
        items = "".join(f"<li><code>{_e(did)}</code> {_e(title)}</li>" for did, title in entry.decisions)
        body.append(f'<h3>Decisions</h3><ul>{items}</ul>')
    elif entry.decisions_file:
        body.append('<h3>Decisions</h3><p class="muted">DECISIONS.md has no `D<number>` headings.</p>')
    if entry.debt:
        items = "".join(f"<li><code>{_e(row.id)}</code> {_e(row.where)}</li>" for row in entry.debt)
        body.append(f'<h3>Debt</h3><ul>{items}</ul>')
    if entry.connections:
        items = []
        for direction, other, kind, weight in entry.connections:
            arrow = "→" if direction == "out" else "←"
            items.append(f'<li>{arrow} <a href="#f-{_e(other)}">{_e(other)}</a> '
                         f'<span class="muted">({_e(kind)}, weight {weight})</span></li>')
        body.append('<h3>Connections</h3><ul>' + "".join(items) + '</ul>'
                    '<p class="muted">From the family graph. A citation is a cross-reference, not a proof.</p>')
    if entry.notes:
        body.append('<h3>Missing or unusual</h3><ul>' + "".join(f"<li>{_e(n)}</li>" for n in entry.notes) + "</ul>")
    return (f'<article class="field" id="f-{_e(entry.name)}" data-text="{_e(_search_text(entry))}">'
            f'<details><summary><span class="name">{_e(entry.name)}</span> '
            f'<span class="tagline">{_e(entry.tagline)}</span> <span class="chips">{_chips(entry)}</span>'
            f'</summary><div class="body">{"".join(body)}</div></details></article>')


_CSS = """
:root{--bg:#fbfaf7;--fg:#1d1c1a;--muted:#6b6862;--line:#dcd8cf;--accent:#2d5b8c;--chip:#eeeae2}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17161a;--fg:#ece9e2;--muted:#9c978d;--line:#33312f;--accent:#8fb6e0;--chip:#25232a}}
:root[data-theme="dark"]{--bg:#17161a;--fg:#ece9e2;--muted:#9c978d;--line:#33312f;--accent:#8fb6e0;--chip:#25232a}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header,main,footer{max-width:58rem;margin:0 auto;padding:0 16px}
h1{font-size:2rem;margin:1.5rem 0 .25rem}
h2{font-size:1.05rem;margin:2rem 0 .5rem;color:var(--muted);font-weight:600}
h3{font-size:.95rem;margin:1rem 0 .25rem}
a{color:var(--accent)}
code{font-size:.9em;overflow-wrap:anywhere}
.lede{color:var(--muted);margin:.25rem 0 1rem}
.muted{color:var(--muted);font-size:.9rem}
.stats{display:flex;flex-wrap:wrap;gap:.4rem;margin:.75rem 0}
.stats .chip{font-size:.85rem}
input[type=search]{width:100%;box-sizing:border-box;font:inherit;padding:.5rem .65rem;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);margin-top:.5rem}
.chip{display:inline-block;background:var(--chip);border-radius:999px;padding:.05rem .55rem;margin:.1rem .15rem .1rem 0;font-size:.78rem;color:var(--muted);white-space:nowrap}
article.field{border-top:1px solid var(--line);padding:.6rem 0}
article.field summary{cursor:pointer;list-style:revert}
article.field .name{font-weight:600}
article.field .tagline{color:var(--muted)}
article.field .body{padding:.25rem 0 .5rem 1.1rem}
article.field .summary{margin:.25rem 0}
table{border-collapse:collapse;width:100%;font-size:.9rem;overflow-wrap:anywhere}
th,td{text-align:left;padding:.2rem .4rem;border-bottom:1px solid var(--line);vertical-align:top}
ul{padding-left:1.2rem;margin:.25rem 0}
.files{font-size:.85rem;color:var(--muted);overflow-wrap:anywhere}
footer{color:var(--muted);font-size:.85rem;margin-top:2rem;padding-bottom:2rem}
[hidden]{display:none !important}
"""

_SCRIPT = """
(function(){
  var q=document.getElementById('q'), out=document.getElementById('count');
  var items=[].slice.call(document.querySelectorAll('article.field'));
  function apply(){
    var t=q.value.trim().toLowerCase(), shown=0;
    items.forEach(function(a){
      var hit=!t || a.getAttribute('data-text').indexOf(t)!==-1;
      a.hidden=!hit; if(hit) shown++;
    });
    document.querySelectorAll('section.role').forEach(function(s){
      s.hidden=!s.querySelector('article.field:not([hidden])');
    });
    out.textContent=shown+' of '+items.length+' fields shown';
  }
  q.addEventListener('input',apply); apply();
})();
"""


def render(index: Index) -> str:
    entries = index.entries
    checked = [e for e in entries if e.checked_out]
    stats = [
        f"{len(entries)} fields",
        f"{sum(1 for e in entries if e.pin)} pinned",
        f"{len(checked)} checked out",
        f"{sum(len(e.declarations) for e in entries)} `.hm` declarations",
        f"{sum(len(e.scan.lean) for e in checked if e.scan)} Lean files",
        f"{sum(e.scan.test_functions for e in checked if e.scan)} test functions",
    ]
    sections = []
    for role in ROLE_ORDER + tuple(sorted({e.role for e in entries} - set(ROLE_ORDER))):
        members = [e for e in entries if e.role == role]
        if not members:
            continue
        cards = "".join(_entry_html(e) for e in members)
        sections.append(f'<section class="role" id="role-{_e(role)}"><h2>{_e(role)} ({len(members)})</h2>{cards}</section>')
    problems = "".join(f"<li>{_e(p)}</li>" for p in index.problems)
    problem_block = (f'<h2>Registry problems</h2><ul class="muted">{problems}</ul>' if index.problems else "")
    stat_html = "".join(f'<span class="chip">{_e(s)}</span>' for s in stats)
    section_html = "".join(sections)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hyperfields</title>
<meta name="description" content="One entry per hyperfield: what it is, where it lives, what its checkout contains, and what is missing.">
<style>{_CSS}</style>
</head>
<body>
<header>
<h1>Hyperfields</h1>
<p class="lede">One entry per field pinned by hyperstratum. Every fact here is read from the pinned checkout or the family graph; nothing is fetched when the page is opened. Declarations are keyword matches, not checks, and decisions and debt are read only where the repository keeps them.</p>
<p class="muted">Family graph digest <code>{_e((index.digest or "")[:16])}</code> · hyperstratum <code>{_e(index.head or "unknown")}</code> · <a href="../family/">family explorer</a></p>
<div class="stats">{stat_html}</div>
<label for="q" class="muted">Filter the fields</label>
<input id="q" type="search" autocomplete="off" placeholder="name, tagline, file, declaration, decision, debt">
<p id="count" class="muted"></p>
</header>
<main>
{section_html}
{problem_block}
</main>
<footer>Generated by <code>scripts/build_field_index.py</code> from the hyperstratum checkout. Field repositories keep their own licences.</footer>
<script>{_SCRIPT}</script>
</body>
</html>
"""
