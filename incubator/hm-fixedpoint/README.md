# hm-fixedpoint: is "form" a least fixed point, and what rescues the L3 arithmetic?

| File | What it establishes |
|---|---|
| `search_countermodel.py` | Exhaustive search on hypermath's own six-element countermodel: an `ordinalApply` exists satisfying all three refuted L3 claims. |
| `RecursionRescue.lean.part` | Appended to the pinned `FiniteActionCountermodel.lean` and kernel-checked: `FullAxioms` plus the three claims hold in one model (`propext`, `Quot.sound` only). |
| `TransfiniteForm.lean` | Standalone: finite reachability contradicts `ax-limit-not-finite`; forms as the least collection closed under `ground`, `f2f` and ω-limits make all three claims hold with equality (no axioms). |

Run: `HM_LEAN=… HM_HYPERMATH_LAKE=<built copy of fields/hypermath/lean4> python -m pytest tests -vv -s`.
The rescue test writes `Rescue.lean`/`Bad.lean` into `HM_HYPERMATH_LAKE`, so point it at a scratch copy, never at the submodule.
Write-up: `wiki/hypermath-program.md`. Not done: showing the transfinite model satisfies every `FullAxioms` clause.
