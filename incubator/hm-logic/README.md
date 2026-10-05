# hm-logic: unfalsifiability and unprovability as computed statuses

`status.py` is a finite propositional frame (observation atoms Test, Null; theory atom Psi) that computes, by enumeration,
whether a postulate P is provable, refutable or independent of a background theory T, and whether it is falsifiable
(forbids some observation T allows) or unfalsifiable (observationally conservative over T). It then evaluates three readings
of the owner's remark "trying to prove it disproves it always": R1 tests always return null (falsifiable; a null result has
likelihood ratio 1, so nulls neither disprove nor support), R2 testing falsifies it (equivalent to "Psi and no test is ever
run"), R3 tests are uninterpretable (unfalsifiable and unprovable). Also checked: independence is not unfalsifiability.

Run: `python -m pytest tests -vv -s`. Hyperlogic (fields/hyperlogic) states it has no connective, quantifier or inference rule
at its L0, so this lives in the incubator as a proposed derivation-status layer, not as a change to hyperlogic.
