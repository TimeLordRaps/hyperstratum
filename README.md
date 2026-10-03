# Hyperstratum

The dictionary, encyclopedia and wiki of the hyperfields.

Hyperstratum authors the vocabulary — form, frame, base, meta, hyper, and everything built on them (`specs/canonical-definitions.md`). It does **not** author anything about the hyperfield repositories themselves. Each hyperfield is pinned here as a git submodule under `fields/`, and every statement the wiki makes about one — what it contains, which terms it uses, what it leaves `[OPEN]`, which other repositories it cites — is read from that repository at the pinned commit.

```bash
git clone --recurse-submodules https://github.com/TimeLordRaps/hyperstratum
cd hyperstratum
pip install -e .
hyperstratum build --out _site/wiki   # the site + wiki.json
hyperstratum check                    # registry, references, citations
```

## What the wiki contains

| Page | Source of truth |
|---|---|
| Term entries (definition, construction level, where the term lives in every field) | `specs/` here; usage scanned from `fields/` |
| Field entries (role, pin, `FIELD.json` contract, vocabulary, symbols, `[OPEN]` items, links in and out) | the field's own repository at its pin |
| Open questions (every `[OPEN]` across the fields) | the fields |
| Audit (what cannot be vouched for: stale citations, unresolved references, pending pins) | computed |
| Authored pages in `wiki/` with live `[[references]]` | here, quoting the fields |
| `wiki.json` | the same facts, machine-readable |

## How it stays live

```txt
hyperfield repo changes
   -> dependency edge fields/<name> has a newer commit
   -> Dependabot (gitsubmodule), or sync-fields.yml on a dispatch from the field
   -> pull request that moves the pin
   -> wiki.yml rebuilds the site from the new pin, re-resolves every [[reference]],
      re-audits every commit-pinned citation
   -> merge -> pages.yml publishes
```

A reference is a **path inside a pinned checkout**, never a hand-typed URL, so it is relative by construction. If a passage moves to another hyperfield, the reference follows it by content hash; if it changes, the audit says so; if it disappears, the check fails. Details, the reference grammar and the limits of the guarantee: `docs/04-wiki-architecture.md`.

In this framework, `hyper-` does not merely mean larger, higher-dimensional, or more abstract. It means recursive meta-connective structure across base forms, meta-forms, meta-meta-forms, and the whole-form closure they participate in.

## Canonical stack

```txt
Universe = whole containing order.
Reality = situated slice of the universe.

Form = identifiable structure.
Frame = opening for interpretation, derivation, or transformation.
Base = local appearance or object-level form.
Meta = representation, interpretation, constraint, transformation, or condition of the base.
Hyper = recursive meta-connective structure across base/meta/whole-form levels.

Hypertopology = nearness-law across recursive form-levels.
Hypermanifold = recursive space of derivation and navigation.
Hyperfield = distributed potential/substance across recursive form-levels.
Hypernode = local recursive form-point.
Hyperconnection = cross-level connective path.
Hyperrelation = rule-governed cross-level relation.
Hyperemergent = emerging cross-level coherence before stabilization.
Recursive-graph = graph representation of recursive form-structure.
Self-graph = graph whose subject is represented in relation to itself.
Mira-graph = reflective graph from an interpretive position.
Hyperstructure = whole recursive object.
Hyperform = closed or closing identity of that object.
Hyperrepresentation = recursive representation across base, meta, path, frame, receiver, self-reflection, ambiguity, and whole-form context.
```

## Graph-prefix grammar

Graph terms are compositional. Prefixes modify the graph object without collapsing into one another.

```txt
graph = structured representation of nodes and connections
recursive-graph = graph of recursive form-structure
self-graph = graph of self-relation
mira-graph = graph of reflective appearance from an interpretive position
```

These can compose:

```txt
self-mira-recursive-graph
```

Meaning:

```txt
A recursive graph by which a subject reflectively represents itself to itself across base/meta/whole-form levels.
```

This keeps `self`, `mira`, and `recursive` distinct:

```txt
self- = subject/object self-relation
mira- = reflective appearance from an interpretive position
recursive- = base/meta/whole-form recursion
```

## Why not `hypergraph`?

`Hypergraph` already has a standard mathematical meaning. Hyperstratum therefore uses `recursive-graph` as the canonical term for graphs of recursive form-structure.

`R-graph` may be used as shorthand in notes, but `recursive-graph` is the canonical repo term.

## Repository map

```txt
.
├── README.md
├── specs/                  authored vocabulary (the lexicon the wiki is built on)
├── docs/                   authored primer chapters; docs/family/ is the older static explorer
├── examples/               authored worked bridges
├── wiki/                   authored pages with live [[references]] into the fields
├── registry/fields.json    what each hyperfield is (role, tagline); pins come from git
├── registry/moves.json     hand-recorded moves for passages whose text changed as well
├── wiki.lock.json          last-recorded text hash of every live reference
├── fields/                 one git submodule per hyperfield (the dependency edges)
├── src/hyperstratum/       registry, lexicon, scanner, reference resolver, builder, CLI
├── tests/
├── templates/              notify-hyperstratum.yml, for a field to announce its changes
└── .github/                dependabot.yml, wiki.yml, sync-fields.yml + the shared conformance gate
```

## Status

The vocabulary is an initial scaffold: definitions are canonical enough to reference, but notation and formal tests remain open. The wiki machinery is new (2026-10-03); see `TECHNICAL_DEBT.md` for what it does not yet do.
