# hm-ti: ladder induction (transfinite induction from nested finite induction)

`LadderInduction.lean` defines `Tower k` (ordinals below ω^k as k rank-ordered coefficients) and proves
`ladder_induction`: transfinite induction below ω^k by k nested ordinary inductions, for every k at once
(ω^ω-induction). No `WellFounded`/`Acc` library: the proof is the nesting. Derived: no infinite descent,
the ℕ-indexed band ω·n below ω², and a termination proof for a rewrite game that a single-ℕ measure cannot
give. `descent_to_naturals.py` runs the game: every run from an infinite position is a finite descent whose
length is unbounded over adversaries. Kernel-checked with no axioms; a non-well-founded order (`≤` for `<`) is rejected.
Not done: towers of towers (ω^ω^ω, ε₀), where the outer induction on k must itself be nested (Gentzen's wall);
the reals direction (limits of dyadic approximants at birthday ω) is only checked numerically in `hm-surreal/fold_check.py`.
Run: `HM_LEAN=… python -m pytest tests -vv -s`.
