"""The authored vocabulary: terms, statements, and where terms sit in the stack."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

# Ordinary English words that are also terms. Counting their occurrences in
# other repositories would measure the English language, not the ontology, so
# they are defined and linked but their mentions are not scanned -- and the
# wiki says so on the term's page rather than showing a misleading zero.
COMMON_WORDS = frozenset({"universe", "reality", "form", "frame", "base", "meta", "hyper"})


@dataclass(frozen=True)
class Term:
    name: str
    slug: str
    definition: str
    scannable: bool
    stratum: int | None = None


@dataclass(frozen=True)
class Statement:
    name: str
    text: str


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _sections(text: str):
    name, buf = None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if name is not None:
                yield name, buf
            name, buf = line[3:].strip(), []
        elif name is not None:
            buf.append(line)
    if name is not None:
        yield name, buf


def _first_fence(lines: list[str]) -> str | None:
    inside, got = False, []
    for line in lines:
        if line.startswith("```"):
            if inside:
                return "\n".join(got).strip()
            inside = True
        elif inside:
            got.append(line)
    return None


def parse_canonical(text: str) -> tuple[list[Term], list[Statement]]:
    terms: list[Term] = []
    statements: list[Statement] = []
    for name, lines in _sections(text):
        body = _first_fence(lines)
        if body is None:
            continue
        head, sep, rest = body.partition("=")
        if sep and head.strip().lower() == name.lower():
            slug = slugify(name)
            terms.append(Term(name=name, slug=slug,
                              definition=" ".join(rest.split()),
                              scannable=slug not in COMMON_WORDS))
        else:
            statements.append(Statement(name=name, text=" ".join(body.split())))
    return terms, statements


def parse_construction(text: str) -> list[list[str]]:
    """The 'Construction order' block: one list of slugs per level, arrows removed."""
    for name, lines in _sections(text):
        if name.lower().startswith("construction order"):
            body = _first_fence(lines) or ""
            levels = []
            for line in body.splitlines():
                line = line.strip()
                if not line or set(line) <= set("↓|v "):
                    continue
                levels.append([slugify(part) for part in line.split("/") if part.strip()])
            return levels
    return []


def assign_strata(terms: list[Term], levels: list[list[str]]) -> list[Term]:
    at = {slug: i for i, level in enumerate(levels) for slug in level}
    return [replace(t, stratum=at.get(t.slug)) for t in terms]


def pattern(term: Term) -> re.Pattern:
    """Whole-token match, plural-tolerant, and distinct from its compounds.

    `(?<![\\w-])` / `(?![\\w-])` keep `hypernode` from matching inside
    `person-hypernode`: compound terms are different terms, not mentions.
    """
    core = re.escape(term.name).replace(r"\-", "-")
    return re.compile(rf"(?<![\w-]){core}(?:s|es)?(?![\w-])", re.IGNORECASE)
