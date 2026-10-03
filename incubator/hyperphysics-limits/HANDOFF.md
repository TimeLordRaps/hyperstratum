# Handoff: order-of-limits labels for hyperphysics

**Status, 2026-10-03.** Written and tested inside hyperstratum, deliberately in hyperphysics' own shape, so that promotion is a copy. **Not applied to hyperphysics.** This session's repository access is limited to hyperstratum, and writing into another repository needs the owner's explicit go-ahead.

## What is here

| File | Role |
|---|---|
| `src/hyperphysics/limits.py` | the method: `Stage`, `Word`, ordinal label, notation, estimator, `commutation`, and the Curie–Weiss worked example with `CURIE_WEISS_FAILS_WHEN` |
| `tests/test_limits.py` | 18 tests: labels, estimator refusals, toy and physical cases, the decision rule |

Standard library only; Python 3.10+; tests run in about 1.5 s against hyperphysics' own `--timeout=30`.

## Why hyperphysics, and what is left for hyperchemistry

* hyperphysics is declared as the mechanics, dynamics and static features of operations, and it states a law once with its validity conditions and failure modes. A limit is an operation on a sequence of operations; `limits.py` states it with its schedule, its refusal conditions (`UNSETTLED`, `UNKNOWN`) and one worked physical case, in the same shape as `electrical.py`.
* hyperchemistry already asks the neighbouring question about composition: *when the same operations are wired differently, can their composite states differ?* Words of limits in different orders are an instance of exactly that, with limits as the operations. A later step could cite `limits.py` from `hyperchemistry/COMPOSITION_CONTRACT.md` as a second example beside the Boolean negations. That is hyperchemistry's call and is not proposed as part of this copy.

## To promote (needs your go-ahead to touch hyperphysics)

1. Copy `src/hyperphysics/limits.py` to `hyperphysics/src/hyperphysics/limits.py` and `tests/test_limits.py` to `hyperphysics/tests/test_limits.py`.
2. Add the module to hyperphysics' README and an entry for it to `VALIDATION.md`, with the open obligations listed below.
3. Run hyperphysics' full suite: `python -m pytest tests`.
4. Re-run the mutation checks listed below on the promoted copy.

## Evidence at this coordinate (hyperstratum `incubator/`, 18 tests, Python 3.11 and 3.10)

* Curie–Weiss ferromagnet, `β = 2` (below the critical temperature): taking `N → ∞` first and `h → 0⁺` second gives `0.95773` (certified to about `8e-4`); taking them the other way gives about `4e-15`. The mean-field oracle `m = tanh(2m)` gives `0.9575`. The verdict is DO_NOT_COMMUTE with gap `0.9577`.
* The same two words at `β = 0.5` (above it) agree: COMMUTE.
* A schedule that does not satisfy `N·h·β·m ≫ 1` at its smallest `h` is reported UNSETTLED, not decided.
* Mutation checks, each of which made at least one test fail: contraction test accepting anything, a decision rule that always says COMMUTE, ignoring unsettled inner limits, swapping inner and outer, and disabling divergence detection.

## Open obligations

* `[OPEN]` The estimator certifies a limit only under the *assumption* that contraction continues beyond the sampled range. It is not a convergence proof.
* `[OPEN]` The loop-quantum-gravity instance the method was invented for (large spin on a fixed graph, then graph refinement) is **not implemented**. The Curie–Weiss case is the verified analogue, nothing more.
* `[OPEN]` Unit handling is the caller's: every quantity is dimensionless here.
* `[HYPER]` Whether the ordinal label `ω^n` buys anything beyond naming depth. The link to the arithmetical hierarchy (Shoenfield's limit lemma) is recalled and not used by the code.
