# Wiki Architecture

## Two kinds of statement

Hyperstratum separates what it **authors** from what it **reports**.

* Authored: the lexicon in `specs/`, the primer in `docs/`, the pages in `wiki/`.
* Reported: everything about a hyperfield. It is never typed into this repository; it is read from the repository's own files at the commit pinned in `fields/<name>`.

A claim of the second kind is therefore a function of `(pinned commit, lexicon)` and nothing else. `wiki.json` is deterministic for that reason: building twice yields the same bytes.

## One dependency edge per hyperfield

Each hyperfield is a git submodule. The pin is the gitlink commit in the index; `.gitmodules` says where it comes from; `registry/fields.json` says what it is. `hyperstratum check` fails if these disagree: a registered repository that is not pinned (and not marked `pending`), or a checkout that is missing. A pinned repository with no registry entry is a warning, not silence.

Pending: a repository with no commit on its default branch cannot be a submodule. It stays in the registry with a `pending` reason and is listed on the index page, so the wiki never quietly covers fewer repositories than it claims.

## Reference grammar

Written in `wiki/*.md` (and permitted in `docs/`, `specs/`, `examples/`):

| Form | Meaning |
|---|---|
| `[[hypermath:docs/x.md#L10-L14]]` | quote those lines from the pinned checkout, with a permalink at the pinned commit |
| `[[hypermath:docs/x.md]]` | link to the file; existence is checked |
| `[[Hyperfield]]` | link to a lexicon term |
| `[[hypermath]]` | link to a field's page |

Code spans and fenced blocks are never evaluated, so this page can show the grammar. Quoted field text is HTML-escaped and shown verbatim; it is data, not markup.

Statuses: `OK`; `DRIFTED` (text differs from `wiki.lock.json`); `MOVED` (the file left that field; the same passage, by SHA-256, was found in another); `REDIRECTED` (recorded in `registry/moves.json`, for when the text changed as well as the place); `MISSING_FIELD`, `MISSING_FILE`, `BAD_RANGE`, `MISSING_TERM`, `AMBIGUOUS` (errors).

`hyperstratum lock` records the current text hash of every reference. Run it when you have read a drift report and accept the new text.

## Three lanes for a change to arrive

1. **Dependabot** (`.github/dependabot.yml`, ecosystem `gitsubmodule`): daily, no secret needed. The floor.
2. **Dispatch** (`.github/workflows/sync-fields.yml`): a field copies `templates/notify-hyperstratum.yml`, and a push there opens the pin-moving pull request within minutes.
3. **Schedule**: the same workflow every six hours, covering a lost dispatch.

All three end in a pull request, so `wiki.yml` reviews the change. Nothing publishes without the existing `pages.yml` gate.

## Audits that need no reference

* **Commit-pinned citations.** Fields cite each other with absolute `blob/<sha>/<path>` URLs. For a citation of this repository the blob at the cited commit is compared with the blob at `HEAD`; `DRIFTED` means a definition changed under its citer. For a citation of a sibling, `CURRENT` means the cited commit is the wiki's pin; otherwise `BEHIND`, and whether the file changed in between is **unknown** (pinned checkouts are shallow).
* **Open questions.** Every `[OPEN]` line, gathered by field.
* **Vocabulary use.** Mentions of each term per field, with permalinks. The seven ordinary English words among the terms (`universe`, `reality`, `form`, `frame`, `base`, `meta`, `hyper`) are defined but not counted.

## What this does not establish

* Mention counts are lexical. A term used under another name is not counted; a term used in a different sense is.
* Edges of kind `named in prose` are weaker than links, and neither is a dependency.
* `[OPEN]` items are the authors' own markers; the wiki does not judge them.
* Whether Dependabot resolves these submodule URLs and opens the pull requests as configured is UNKNOWN until it has run once on GitHub.
* The site shows the pin, not the field's HEAD. A field can be ahead of the wiki until its pin-moving pull request merges; the pin is shown on every field page for that reason.
