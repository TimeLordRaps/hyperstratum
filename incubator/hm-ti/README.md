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

## Added: rank order of the omegas, and descent into the naturals by fundamental sequences

* `RankOrder.lean` (kernel-checked, `propext`/`Quot.sound` at most, a weakened order is rejected): the order on every
  `Tower k` is a strict total order (irreflexive, transitive, trichotomous); `omegaPow_strictMono` ω^j < ω^j' for
  j < j'; `band_upper`/`band_lower` an element is below ω^k exactly when its leading coefficient at rank k is zero,
  so every element lies in exactly one band [ω^k, ω^(k+1)); `lift` preserves the order and fixes the omega powers;
  `omega_cofinal` every element is below some ω^j, so ω^ω is the supremum of the omegas and none of them.
* `fundamental.py`: ω^ω[n] = ω^n, ω^k[n] = ω^(k-1)·n, … down to the naturals (Hardy hierarchy). Verified H_ω = 2n,
  H_ω·2 = 4n, H_ω² = n·2^n; H_ω³(2) = 2048; H_ω⁴(2) exceeds 10^7 steps (terminates by ladder induction, length explodes).
