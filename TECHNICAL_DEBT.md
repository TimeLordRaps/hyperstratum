# Technical debt

Single tracker. Status: OPEN | SUSPECTED | VERIFIED_RESOLVED. Dates are YYYY-MM-DD.

| ID | Location | Hypothesis / mechanism | Evidence | Consequence | Remedy | Revisit |
|---|---|---|---|---|---|---|
| HS-001 | `.github/dependabot.yml` | Dependabot's `gitsubmodule` ecosystem may not open PRs as configured (URL form, branch tracking, PR volume at 24 repos). | UNKNOWN: not yet run on GitHub. | The daily lane is the floor; if it fails the wiki still moves via sync-fields.yml. | After first merge, read the Dependabot tab; consider `groups`. | first Dependabot run |
| HS-002 | `docs/family/` + `scripts/build_pages.py` | Two graph sources: the static `family-graph.json` explorer (template-generated) and the live edges computed from `fields/`. | Observed: both exist; the explorer lists 21 repos, the wiki 24. | The older explorer can disagree with the wiki. | Regenerate or retire the explorer from `wiki.json` edges, upstream in the family template. | next template refresh |
| HS-003 | `.github/workflows/pages.yml` | Shared template edited locally (`submodules`, `fetch-depth`, one build step). | Observed in `git diff`. | A template refresh will silently drop the wiki from the published site. | Move the three lines into the template, or give the template a hook. | next template refresh |
| HS-004 | `scan.py` | Mention counting is lexical; sibling-name edges count prose mentions of common words (e.g. `verifier`, `hyperspace`). | Cross-checked: `hypernode` 8 and `hyperfield` 0 match an independent `grep -w`. Edge precision not measured. | `named in prose` edges may overstate coupling. | Sample-label 50 edges, measure precision, decide whether to keep the kind. | before edges are relied on |
| HS-005 | `scan.py` BEHIND citations | Shallow submodules cannot say whether a behind-pinned cited file changed. | By construction. | 13 BEHIND warnings carry no content verdict. | Fetch the cited commit per citation on demand in CI, compare blobs. | when the warning count is noisy |
| HS-006 | `hyperbiology` | No commit on `main` as of 2026-10-03, so unpinnable. | `git ls-remote` returned nothing. | Wiki lists it as pending with no content. | `git submodule add` once it has a commit, delete `pending`. | each sync |
| HS-007 | `registry/fields.json` | Roles for `verifier` and four companions are assigned here, not inherited; other roles are copied from the family graph's tiers. | `role_source` records which. | Roles are classification, not fact. | Owner confirms or edits. | owner review |
