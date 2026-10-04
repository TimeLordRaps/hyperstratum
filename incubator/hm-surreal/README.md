# hm-surreal: a surreal-normal-form model of the filtration, and the average fold

Owner's decision (2026-10-04): ℕ is definable only at `==`.

| File | Establishes |
|---|---|
| `SurrealFiltration.lean` | On finite sums `Σ c·ω^k`: `==` equality, `=~` same leading term, `~~` same order of infinity satisfy hypermath's `filtrationSimCong`, `filtrationCongSim`, `traceLevels`; □ = doubling satisfies `axDiff`, is injective, is the identity at `~~` and never at `==` (off zero); the □-tower is one point at `~~` (no `~~`-invariant property can count it) and injective at `==`; each rung `ω^k` carries the same coefficient line and distinct rungs never meet at `~~`. Kernel-checked, `propext`/`Quot.sound` only. |
| `fold_check.py` | The average as a fold: iterated midpoints reproduce Conway birthdays exactly (1023 numbers, 9 days); the simplest number in every gap is its average; every inner gap repeats the (0,1) fold pattern (fractal); the fold path to 1/3 converges at 2^-n. A one-third fold is rejected. |

Run: `HM_LEAN=… python -m pytest tests -vv -s`.
Not shown: every `FullAxioms` clause in this model; rational/real coefficients (Lean core has no ℚ); the fold at limit stages beyond the convergence check.
