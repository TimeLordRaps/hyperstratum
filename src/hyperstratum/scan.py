"""Read a hyperfield checkout and report what it says, without interpreting it.

Everything here is derived from file bytes at the pinned commit. Nothing is
cached between runs, so the output is a function of (pin, ontology) alone.
"""

from __future__ import annotations

import ast
import json
import os
import pathlib
import re
from collections import Counter
from dataclasses import dataclass, field

from . import lexicon
from .registry import OWNER, Field, Registry

SKIP_DIRS = frozenset({".git", ".lake", "node_modules", ".venv", "venv", "__pycache__",
                       ".pytest_cache", ".mypy_cache", ".tox", "site-packages", "_site"})
TEXT_SUFFIXES = frozenset({".md", ".py", ".lean", ".hm", ".tex", ".txt", ".rst"})
MAX_BYTES = 2_000_000
MAX_LOCATIONS = 12
TAGS = ("FORM", "FRAME", "OPEN", "HYPER")

# Original case, not IGNORECASE: `HypermathFullAxiomModel` is an identifier, not a word.
HYPER_WORD_RE = re.compile(r"(?<![\w-])[Hh]yper[a-z]{2,}(?![\w-])")
TAG_RE = re.compile(r"\[(FORM|FRAME|OPEN|HYPER)\]")
URL_RE = re.compile(r"https?://\S+")
CITATION_RE = re.compile(
    rf"github\.com/{OWNER}/([\w.-]+)/blob/([0-9a-f]{{40}})/([^\s)#\"'\]>]+)")
CITED_REPO_RE = re.compile(rf"github\.com/{OWNER}/([\w.-]+)")
LEAN_DECL = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|unsafe|partial)\s+)*"
    r"(theorem|lemma|def|structure|inductive|class|axiom|instance|abbrev)\s+([A-Za-z_][\w.'?!]*)")


@dataclass
class Mentions:
    count: int = 0
    locations: list[tuple[str, int]] = field(default_factory=list)


@dataclass(frozen=True)
class Symbol:
    kind: str
    name: str
    path: str
    line: int
    doc: str = ""


@dataclass(frozen=True)
class Citation:
    source: str
    file: str
    line: int
    target: str
    sha: str
    path: str


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    kind: str  # "url" (links to the repo) | "name" (mentions its name in prose)
    count: int
    evidence: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class Audit:
    citation: Citation
    status: str  # CURRENT | BEHIND | DRIFTED | UNRESOLVABLE | EXTERNAL
    detail: str


@dataclass
class FieldScan:
    name: str
    files: dict[str, int] = field(default_factory=dict)
    mentions: dict[str, Mentions] = field(default_factory=dict)
    symbols: list[Symbol] = field(default_factory=list)
    tags: dict[str, int] = field(default_factory=dict)
    open_items: list[tuple[str, int, str]] = field(default_factory=list)
    sorry_count: int = 0
    contract: dict | None = None
    contract_error: str | None = None
    excerpt: str = ""
    citations: list[Citation] = field(default_factory=list)
    hyper_words: dict[str, Mentions] = field(default_factory=dict)
    raw_edges: dict[tuple[str, str], Mentions] = field(default_factory=dict)


def iter_files(root: pathlib.Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            p = pathlib.Path(dirpath, name)
            if p.suffix.lower() in TEXT_SUFFIXES and p.is_file() and p.stat().st_size <= MAX_BYTES:
                yield p


def _py_symbols(rel: str, text: str) -> list[Symbol]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    out = []
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) \
                and not node.name.startswith("_"):
            doc = (ast.get_docstring(node) or "").strip().splitlines()
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            out.append(Symbol(kind, node.name, rel, node.lineno, doc[0] if doc else ""))
    return out


def _lean_symbols(rel: str, lines: list[str]) -> tuple[list[Symbol], int]:
    out, sorries, block = [], 0, False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if block:
            block = "-/" not in stripped
            continue
        if stripped.startswith("/-"):
            block = "-/" not in stripped
            continue
        if stripped.startswith("--"):
            continue
        m = LEAN_DECL.match(line)
        if m:
            out.append(Symbol(m.group(1), m.group(2), rel, i))
        sorries += len(re.findall(r"\bsorry\b", line.split("--", 1)[0]))
    return out, sorries


def _excerpt(readme: pathlib.Path) -> str:
    if not readme.is_file():
        return ""
    para: list[str] = []
    fenced = False
    for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            continue
        if fenced or s.startswith(("#", "![", "[![", "<", ">", "|")) or not s:
            if para:
                break
            continue
        para.append(s)
    return " ".join(para)[:500]


def scan_field(f: Field, terms: list[lexicon.Term], sibling_names: set[str] | None = None) -> FieldScan:
    s = FieldScan(name=f.name)
    patterns = [(t, lexicon.pattern(t)) for t in terms if t.scannable]
    for t, _ in patterns:
        s.mentions[t.slug] = Mentions()
    tags: Counter = Counter()
    files: Counter = Counter()
    siblings = {n for n in (sibling_names or set()) if n != f.name}
    sib_re = {n: re.compile(rf"(?<![\w-]){re.escape(n)}(?![\w-]|\.\w)", re.IGNORECASE) for n in siblings}

    for path in iter_files(f.path):
        rel = path.relative_to(f.path).as_posix()
        files[path.suffix.lower()] += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        if path.suffix == ".py":
            s.symbols.extend(_py_symbols(rel, text))
        elif path.suffix == ".lean":
            syms, sorries = _lean_symbols(rel, lines)
            s.symbols.extend(syms)
            s.sorry_count += sorries
        for i, line in enumerate(lines, 1):
            for term, pat in patterns:
                hits = len(pat.findall(line))
                if hits:
                    m = s.mentions[term.slug]
                    m.count += hits
                    if len(m.locations) < MAX_LOCATIONS:
                        m.locations.append((rel, i))
            for w in HYPER_WORD_RE.findall(line):
                _bump_word(s.hyper_words, w.lower(), rel, i)
            for tag in TAG_RE.findall(line):
                tags[tag] += 1
            if "[OPEN]" in line:
                s.open_items.append((rel, i, line.strip()[:240]))
            for cm in CITATION_RE.finditer(line):
                s.citations.append(Citation(f.name, rel, i, cm.group(1).removesuffix(".git"),
                                            cm.group(2), cm.group(3)))
            for repo in {r.removesuffix(".git") for r in CITED_REPO_RE.findall(line)}:
                if repo in siblings:
                    _bump(s.raw_edges, (repo, "url"), rel, i)
            bare = URL_RE.sub(" ", line)
            for name, rx in sib_re.items():
                if rx.search(bare):
                    _bump(s.raw_edges, (name, "name"), rel, i)

    s.files = dict(sorted(files.items()))
    s.tags = {k: tags[k] for k in TAGS if tags[k]}
    contract = f.path / "FIELD.json"
    if contract.is_file():
        try:
            s.contract = json.loads(contract.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            s.contract_error = str(exc)
    s.excerpt = _excerpt(f.path / "README.md")
    return s


def _bump_word(words: dict, word: str, rel: str, line: int) -> None:
    m = words.setdefault(word, Mentions())
    m.count += 1
    if len(m.locations) < MAX_LOCATIONS:
        m.locations.append((rel, line))


def _bump(raw: dict, key: tuple[str, str], rel: str, line: int) -> None:
    m = raw.setdefault(key, Mentions())
    m.count += 1
    if len(m.locations) < MAX_LOCATIONS:
        m.locations.append((rel, line))


def build_edges(scans: dict[str, FieldScan], reg: Registry) -> list[Edge]:
    edges = []
    for src in sorted(scans):
        for (target, kind), m in sorted(scans[src].raw_edges.items()):
            edges.append(Edge(src, target, kind, m.count, tuple(m.locations[:5])))
    return edges


def sibling_names(reg: Registry) -> set[str]:
    return {f.name for f in reg.fields} | {"hyperstratum"}


def audit_citations(citations: list[Citation], reg: Registry, blob_lookup) -> list[Audit]:
    """Compare what each commit-pinned citation points at with what is current.

    * into a sibling:  CURRENT iff the cited commit is the wiki's pin of it.
      Otherwise BEHIND -- and whether the cited *file* changed is UNKNOWN,
      because pinned checkouts are shallow and hold no history to compare.
    * into hyperstratum: the blob at the cited commit is compared with the blob
      at HEAD, so DRIFTED means the definition itself changed under the citer.
    """
    pins = {f.name: f.pin for f in reg.fields}
    out = []
    for c in citations:
        if c.target == "hyperstratum":
            then, now = blob_lookup(c.sha, c.path), blob_lookup("HEAD", c.path)
            if then is None or now is None:
                out.append(Audit(c, "UNRESOLVABLE",
                                 "cited commit or path is not in this repository's history"))
            elif then == now:
                out.append(Audit(c, "CURRENT", "cited file is byte-identical at HEAD"))
            else:
                out.append(Audit(c, "DRIFTED",
                                 f"{c.path} has changed since {c.sha[:10]}; the citing text may be stale"))
        elif c.target in pins and pins[c.target]:
            if c.sha == pins[c.target]:
                out.append(Audit(c, "CURRENT", "cited commit is this wiki's pin"))
            else:
                out.append(Audit(c, "BEHIND",
                                 f"cites {c.sha[:10]} but the wiki pins {pins[c.target][:10]}; "
                                 "whether the cited file changed between them is UNKNOWN"))
        else:
            out.append(Audit(c, "EXTERNAL", f"{c.target} is not a pinned hyperfield"))
    return out


# Technical words that begin with "hyper" in their ordinary, established senses.
# They are not coinages of this ecosystem, so listing them as candidate terms
# would bury the real ones. Edit freely: a word added here only disappears from
# the candidates page, nothing else.
STANDARD_HYPER_WORDS = frozenset({
    "hyperlink", "hypertext", "hyperparameter", "hypervisor", "hyperbolic", "hyperbola",
    "hyperbole", "hypergraph", "hyperset", "hyperreal", "hypercube", "hyperplane",
    "hypersphere", "hyperoperation", "hyperfine", "hypergeometric", "hyperthreading",
    "hypertension", "hyperactive", "hyperlinked", "hyperscale", "hyperscaler",
    "hyperconverged", "hyperfocus", "hyperventilate", "hyperinflation", "hyperloop",
    "hypermedia", "hypersonic", "hyperspectral", "hypercalcemia", "hyperref", "hypersetup",
})


def _fold(word: str, seen: set[str]) -> str:
    """Merge a plural into its singular only if the singular was itself seen."""
    if word.endswith("s") and not word.endswith(("ss", "us", "is")) and word[:-1] in seen:
        return word[:-1]
    return word


def candidate_terms(scans: dict[str, FieldScan], terms: list[lexicon.Term], reg: Registry) -> list[dict]:
    """`hyper*` words the fields use that the lexicon does not define.

    Only the hyper- family is detected; a coinage in another shape (the owner's
    "universempiternality") is invisible here, and the page says so.
    """
    known = {t.slug for t in terms} | {f.name for f in reg.fields} | {"hyperstratum"}
    known |= {t.slug.replace("-", "") for t in terms}
    merged: dict[str, dict] = {}
    seen = {w for sc in scans.values() for w in sc.hyper_words}
    for name in sorted(scans):
        for raw, m in scans[name].hyper_words.items():
            w = _fold(raw, seen)
            if w in known or raw in known or w in STANDARD_HYPER_WORDS or raw in STANDARD_HYPER_WORDS:
                continue
            e = merged.setdefault(w, {"word": w, "total": 0, "fields": {}, "places": []})
            e["total"] += m.count
            e["fields"][name] = e["fields"].get(name, 0) + m.count
            for path, line in m.locations[:2]:
                if len(e["places"]) < 6:
                    e["places"].append([name, path, line])
    out = sorted(merged.values(), key=lambda e: (-len(e["fields"]), -e["total"], e["word"]))
    for e in out:
        e["fields"] = dict(sorted(e["fields"].items()))
    return out
