# Handoff: order-of-limits labels for hyperphysics

**Status, 2026-10-03.** Written and tested inside hyperstratum in hyperphysics' own shape, then promoted on the owner's go-ahead: pushed to `TimeLordRaps/hyperphysics` as commit `d34561d` on branch `claude/order-of-limits` (**no pull request opened, not merged**). This copy stays until that branch is merged, and should then be deleted. hyperphysics' full suite passes there (73 tests: its 55 plus these 18), ruff is clean, and no byte of a manifest-tracked file changed.

## What is here

| File | Role |
|---|---|
| `src/hyperphysics/limits.py` | the method: `Stage`, `Word`, ordinal label, notation, estimator, `commutation`, and the Curie–Weiss worked example with `CURIE_WEISS_FAILS_WHEN` |
| `tests/test_limits.py` | 18 tests: labels, estimator refusals, toy and physical cases, the decision rule |

Standard library only; Python 3.10+; tests run in about 1.5 s against hyperphysics' own `--timeout=30`.

## Why hyperphysics, and what is left for hyperchemistry

* hyperphysics is declared as the mechanics, dynamics and static features of operations, and it states a law once with its validity conditions and failure modes. A limit is an operation on a sequence of operations; `limits.py` states it with its schedule, its refusal conditions (`UNSETTLED`, `UNKNOWN`) and one worked physical case, in the same shape as `electrical.py`.
* hyperchemistry already asks the neighbouring question about composition: *when the same operations are wired differently, can their composite states differ?* Limits in different orders are an instance of the shape. The exact finite counterpart now exists there: adding the universal quantifier beside the existential projection `compose` uses, the order of two projections is observable for exactly two relations on `B x B`, the identity and the negation the contract already uses. That model does not model limits (infinite domains are outside its envelope); the relation is recorded there as `[OPEN]`, HC-004.

## What was done on promotion (for the record)

1. Copied the two files into `hyperphysics`; ruff's import sorting changed one line of the test, and the same fix is applied here so the copies stay identical.
2. Added a README section and a dated addendum to `VALIDATION.md` (the existing receipt was not edited). `__init__.py` does not re-export the module, so the manifest digest still describes the bytes it names; the new files are explicitly outside it.
3. Ran hyperphysics' full suite and ruff.
4. hyperchemistry's side is separate: `claude/projection-order-witness`, commit `9adb266`, a finite witness that the order of mixed projections matters (see the wiki page). **No pull request opened there either.**

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
