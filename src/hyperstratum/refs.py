"""Live references into the hyperfields.

Grammar, in any authored page:

    [[hypermath:docs/x.md#L10-L14]]   transclude those lines, with a permalink
    [[hypermath:docs/x.md]]           link to the file (existence is checked)
    [[Hyperfield]]                    link to a term of the lexicon
    [[hypermath]]                     link to a field's page

A reference is a *path inside a pinned checkout*, never a URL typed by hand, so
it is relative by construction: bump the pin and the quoted text changes with
it. Three things can then happen to a reference whose target moved:

* the passage now sits at the same path -- it is simply re-read (DRIFTED when
  its text differs from what `wiki.lock.json` last recorded);
* the file was moved to another field -- found by the SHA-256 of the locked
  passage across every field (MOVED);
* the move was recorded by hand in `registry/moves.json` (REDIRECTED), for the
  case where content changed as well as place.

Anything else is MISSING_*, which `check` fails on.
"""

from __future__ import annotations

import hashlib
import html
import json
import pathlib
import re
from dataclasses import dataclass
from typing import Callable

from . import lexicon
from .registry import Registry

REF_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
# Code is quoted, never evaluated: a page documenting the grammar must be able
# to show `[[field:path]]` without it being resolved.
CODE_RE = re.compile(r"```.*?```|~~~.*?~~~|`[^`\n]*`", re.DOTALL)
RANGE_RE = re.compile(r"^L(\d+)(?:-L?(\d+))?$")
LOCK_SCHEMA = "hyperstratum-ref-lock/1"


@dataclass(frozen=True)
class Ref:
    raw: str
    field: str | None = None
    path: str | None = None
    span: tuple[int, int] | None = None
    name: str | None = None
    bad: str | None = None  # a malformed range, kept so it is reported, not guessed at


@dataclass
class Resolved:
    ref: Ref
    status: str
    detail: str = ""
    moved_to: tuple[str, str, tuple[int, int] | None] | None = None
    text: str | None = None
    digest: str | None = None
    pin: str | None = None
    url: str | None = None

    @property
    def key(self) -> str:
        r = self.ref
        if r.field is None:
            return f"term:{r.name}"
        rng = f"#L{r.span[0]}-L{r.span[1]}" if r.span else ""
        return f"{r.field}:{r.path}{rng}"

    def problem(self) -> dict | None:
        if self.status == "OK":
            return None
        severity = "warning" if self.status in ("MOVED", "REDIRECTED", "DRIFTED") else "error"
        return {"code": self.status, "severity": severity, "subject": self.key,
                "detail": self.detail}


def find_refs(text: str) -> list[Ref]:
    out = []
    for m in REF_RE.finditer(text):
        body = m.group(1).strip()
        if ":" not in body:
            out.append(Ref(raw=m.group(0), name=body))
            continue
        fld, _, rest = body.partition(":")
        path, _, frag = rest.partition("#")
        span, bad = None, None
        if frag:
            rm = RANGE_RE.match(frag)
            if rm:
                lo = int(rm.group(1))
                span = (lo, int(rm.group(2) or lo))
            else:
                bad = frag
        out.append(Ref(raw=m.group(0), field=fld.strip(), path=path.strip(), span=span, bad=bad))
    return out


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_lock(resolved: list[Resolved]) -> dict:
    refs = {}
    for r in resolved:
        if r.ref.field is not None and r.status in ("OK", "DRIFTED", "MOVED", "REDIRECTED") and r.digest:
            where = r.moved_to
            refs[r.key] = {"sha256": r.digest, "pin": r.pin,
                           "at": f"{where[0]}:{where[1]}" if where else f"{r.ref.field}:{r.ref.path}"}
    return {"schema": LOCK_SCHEMA, "refs": dict(sorted(refs.items()))}


def dump_lock(lock: dict) -> str:
    return json.dumps(lock, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def load_lock(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {"schema": LOCK_SCHEMA, "refs": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != LOCK_SCHEMA:
        raise ValueError(f"{path}: unsupported lock schema {data.get('schema')!r}")
    return data


class Resolver:
    def __init__(self, reg: Registry, terms: list[lexicon.Term], root: pathlib.Path,
                 lock: dict | None = None, moves: dict[str, str] | None = None):
        self.reg = reg
        self.fields = reg.by_name
        self.terms = {t.slug: t for t in terms}
        self.root = pathlib.Path(root)
        self.lock = (lock or {}).get("refs", {})
        if moves is None:
            mf = self.root / "registry" / "moves.json"
            moves = json.loads(mf.read_text(encoding="utf-8")) if mf.is_file() else {}
        self.moves = moves
        self._lines: dict[tuple[str, str], list[str] | None] = {}

    # -- reading ---------------------------------------------------------
    def _read(self, fld: str, path: str) -> list[str] | None:
        key = (fld, path)
        if key not in self._lines:
            f = self.fields.get(fld)
            target = (f.path / path) if f else None
            ok = (target is not None and f.path.resolve() in target.resolve().parents
                  and target.is_file())
            self._lines[key] = (target.read_text(encoding="utf-8", errors="replace").splitlines()
                                if ok else None)
        return self._lines[key]

    @staticmethod
    def _slice(lines: list[str], span: tuple[int, int] | None) -> str:
        return "\n".join(lines[span[0] - 1: span[1]] if span else lines)

    def _find_moved(self, digest: str, span, basename: str) -> tuple[str, str] | None:
        """Search every field for a file containing the locked passage."""
        for f in sorted(self.fields.values(), key=lambda x: x.name):
            if f.pin is None or not f.path.is_dir():
                continue
            for p in sorted(f.path.rglob(basename)):
                rel = p.relative_to(f.path).as_posix()
                if ".git/" in rel or not p.is_file():
                    continue
                lines = self._read(f.name, rel)
                if lines and (span is None or span[1] <= len(lines)) \
                        and _sha(self._slice(lines, span)) == digest:
                    return f.name, rel
        return None

    # -- resolving -------------------------------------------------------
    def resolve(self, ref: Ref) -> Resolved:
        if ref.field is None:
            return self._resolve_name(ref)
        res = Resolved(ref=ref, status="OK")
        if ref.bad is not None:
            return Resolved(ref, "BAD_RANGE", f"'#{ref.bad}' is not L<n> or L<n>-L<m>")
        fld = self.fields.get(ref.field)
        if fld is None:
            return Resolved(ref, "MISSING_FIELD", f"no hyperfield named '{ref.field}' is registered")
        if fld.pin is None:
            return Resolved(ref, "MISSING_FIELD", f"'{ref.field}' has no pinned commit yet")
        fname, path, status, detail = ref.field, ref.path or "", "OK", ""
        lines = self._read(fname, path)
        locked = self.lock.get(res.key)

        if lines is None:
            redirect = self.moves.get(f"{ref.field}:{path}")
            if redirect:
                fname, _, path = redirect.partition(":")
                lines = self._read(fname, path)
                if lines is not None:
                    status, detail = "REDIRECTED", f"moved to {fname}:{path} (registry/moves.json)"
            if lines is None and locked:
                hit = self._find_moved(locked["sha256"], ref.span, pathlib.PurePosixPath(path).name)
                if hit:
                    fname, path = hit
                    lines = self._read(fname, path)
                    status, detail = "MOVED", f"same passage found at {fname}:{path}"
            if lines is None:
                return Resolved(ref, "MISSING_FILE",
                                f"{ref.field}:{path} does not exist at pin {fld.pin[:10]}"
                                + ("" if locked else "; no lock entry, so no move can be traced"))
        span = ref.span
        if span and (span[0] < 1 or span[1] < span[0] or span[1] > len(lines)):
            return Resolved(ref, "BAD_RANGE",
                            f"lines {span[0]}-{span[1]} are outside {fname}:{path} ({len(lines)} lines)")
        text = self._slice(lines, span)
        digest = _sha(text)
        if status == "OK" and locked and locked["sha256"] != digest:
            status, detail = "DRIFTED", "passage text differs from wiki.lock.json"
        target_field = self.fields[fname]
        frag = f"L{span[0]}-L{span[1]}" if span else None
        return Resolved(ref, status, detail,
                        moved_to=(fname, path, span) if status in ("MOVED", "REDIRECTED") else None,
                        text=text if span else None, digest=digest, pin=target_field.pin,
                        url=target_field.permalink(path, frag))

    def _resolve_name(self, ref: Ref) -> Resolved:
        slug = lexicon.slugify(ref.name or "")
        is_term, is_field = slug in self.terms, (ref.name in self.fields)
        if is_term and is_field:
            return Resolved(ref, "AMBIGUOUS", f"'{ref.name}' is both a term and a field; write field:<path>")
        if is_term:
            return Resolved(ref, "OK", url=f"term:{slug}")
        if is_field:
            return Resolved(ref, "OK", url=f"field:{ref.name}")
        return Resolved(ref, "MISSING_TERM", f"'{ref.name}' is neither a term nor a registered field")

    def expand(self, text: str, link_term: Callable[[str], str],
               link_field: Callable[[str], str] | None = None) -> tuple[str, list[Resolved]]:
        """Replace every `[[ref]]` with markdown, returning what each resolved to."""
        resolved: list[Resolved] = []

        def sub(m: re.Match) -> str:
            ref = find_refs(m.group(0))[0]
            r = self.resolve(ref)
            resolved.append(r)
            return _render(r, link_term, link_field or (lambda n: n))

        out, last = [], 0
        for m in CODE_RE.finditer(text):
            out.append(REF_RE.sub(sub, text[last:m.start()]))
            out.append(m.group(0))
            last = m.end()
        out.append(REF_RE.sub(sub, text[last:]))
        return "".join(out), resolved


def _render(r: Resolved, link_term, link_field) -> str:
    ref = r.ref
    if r.status not in ("OK", "MOVED", "REDIRECTED", "DRIFTED"):
        return f"**[unresolved {ref.raw[2:-2]}: {r.status}]**"
    if ref.field is None:
        if (r.url or "").startswith("term:"):
            return f"[{ref.name}]({link_term(r.url[5:])})"
        return f"[{ref.name}]({link_field(r.url[6:])})"
    where = r.moved_to or (ref.field, ref.path, ref.span)
    label = f"{where[0]}:{where[1]}" + (f"#L{where[2][0]}-L{where[2][1]}" if where[2] else "")
    note = {"MOVED": " — moved", "REDIRECTED": " — redirected", "DRIFTED": " — changed since last lock"}.get(r.status, "")
    if r.text is None:
        return f"[{label}]({r.url}) @ `{(r.pin or '')[:10]}`{note}"
    body = html.escape(r.text)
    return (f'\n\n<blockquote class="transclusion"><pre>{body}</pre>'
            f'<p>&mdash; <a href="{html.escape(r.url)}">{html.escape(label)}</a> @ '
            f'<code>{html.escape((r.pin or "")[:10])}</code>{html.escape(note)}</p></blockquote>\n\n')
