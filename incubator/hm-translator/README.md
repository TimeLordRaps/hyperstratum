# hmtrans — `.hm` → Lean 4 / Metamath

Translator for the semi-formal `.hm` language of `hypermath`. Fail-closed: every
declaration ends as `translated`, `admitted`, `untranslated` (with a reason and a
line) or `builtin`; nothing is dropped silently.

```
PYTHONPATH=src python -m hmtrans L0_ground.hm L1_relations.hm L2_operations.hm L3_ordinatics.hm \
    --out out/ --lean $(which lean) --mmverify /path/to/mmverify.py
```

Files go in dependency order (relation symbols, arities and infix words are inherited).
Outputs: `Out.lean`, `out.mm`, `receipt.json` (counts, per-entry status, digests).

## What the checkers certify (and what they do not)

| Target | Oracle | Certifies | Does not certify |
|---|---|---|---|
| Lean 4.14.0 (hypermath's `lean-toolchain`) | `lean` kernel | the output type-checks; `sorry` marks admitted obligations | that the Lean statement means what the `.hm` statement means |
| Metamath | `mmverify.py` | vocabulary is sort/arity-consistent; bare-instantiation derives have a real substitution proof | any logic: the database has no logical axioms |

Derives are proved only when they are a bare single-step instantiation of one axiom whose
result equals `close:`; all others are `theorem … := by sorry` in Lean and omitted from
Metamath. Statements with nested quantifiers are omitted from Metamath, with a reason.

## Measured coverage on hypermath L0–L3 (pin in `fields/hypermath`, 2026-10-04)

axioms 20 translated / 6 untranslated; derives 5 admitted (3 proved by instantiation in Lean and
Metamath) / 32 untranslated; closes 12 and graduations 4 untranslated (prose or comment-only);
relations 3, opaques 17, primitives 9 (+`Prop` builtin) translated. Untranslated axioms include
real source defects: undeclared `additionally`, `congruent-path-part-of`, `plus`.
Lean compiles the generated file with exit 0 and no errors.

## Tests

`HM_LEAN=… HM_MMVERIFY=… python -m pytest` (48 tests). Kernel/Metamath tests skip when the tool
is absent; set the variables in any run that is meant to be a gate. Includes a differential test
against the hand-written `L0Ground.lean` (vocabulary and the four axioms match exactly) and
negative tests (kernel and mmverify reject tampered output).
