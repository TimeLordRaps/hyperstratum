# Limit labels

**Status, 2026-10-03.** `[FRAME]` for the method and its tests; `[HYPER]` for the application to spacetime; `[OPEN]` where stated. The code is pushed to hyperphysics as commit `d34561d` on the unmerged branch `claude/order-of-limits`, and a finite companion witness to hyperchemistry as `9adb266` on the unmerged branch `claude/projection-order-witness`. No pull request is open for either. This wiki pins the hyperfields at earlier commits, so the quoted passages below do not yet include that work.

## The problem

A statement such as "spacetime is the continuum limit of the spin foam" is incomplete until it says which limits, in which order, along which schedule. Limits taken in a different order can give different answers, so the order is part of the claim.

## The method

A limit procedure is written as a **word**: an ordered list of stages, innermost first, each stage a parameter, a target (`∞` or `0⁺`) and an explicit schedule. Two things are read off a word.

* **Label.** `n` nested stages have label `ω^n`; parameters sent together along one schedule (a diagonal limit) form one stage and have label `ω`.
* **Notation.** The order, outermost first: `lim[h→0⁺] lim[N→∞]`.

The label alone does **not** tell two orders apart: `lim_x lim_y` and `lim_y lim_x` both have label `ω²`. What a citation must carry is the word, which is why the check compares words.

## What the check refuses to do

It reads a finite schedule, and it will not say more than that schedule supports:

* a limit is certified only if the last steps contract by a fixed factor and the tail error bound falls under a stated tolerance; slow or drifting convergence is `UNSETTLED`;
* an outer limit of an unsettled inner one is unsettled;
* two words **commute** only if their answers agree and each is known to within the tolerance; they **do not commute** only if they differ by more than their combined uncertainty; anything else is `UNKNOWN`.

## A physical case that was checked

The Curie–Weiss ferromagnet below its critical temperature (`β = 2`), exact finite-`N` sums:

| Word | Result |
|---|---|
| `lim[h→0⁺] lim[N→∞]` (thermodynamic limit first) | `0.95773`, certified to about `8×10⁻⁴`; the mean-field fixed point `m = tanh(2m)` is `0.9575` |
| `lim[N→∞] lim[h→0⁺]` (zero field first) | about `4×10⁻¹⁵`, that is, zero |

The two orders disagree by `0.9577`. Above the critical temperature (`β = 0.5`) they agree. A schedule that does not satisfy `N·h·β·m ≫ 1` at its smallest `h` is reported unsettled and not decided.

## Where it was meant to go

The instance this was built for is quantum gravity's two limits, large spin on a fixed graph and refinement of the graph ([[Reality]] seam, and the loop-quantum-gravity discussion of the hypersphere page). That instance is **not implemented**; Curie–Weiss is the verified analogue and nothing more. `[OPEN]` Does the order matter there? Only a model can say.

## Placement

The declaration of the field stack:

[[hyperphysics:FIELD_STACK.md#L11-L15]]

hyperphysics states a law once with its validity conditions and failure modes; a limit with its schedule and refusal conditions is that shape, so the method and the worked case fit there. hyperchemistry asks the neighbouring question about composition:

[[hyperchemistry:README.md#L16-L17]]

Words of limits in different orders are an instance of it, with limits as the operations. See [[hyperphysics]] and [[hyperchemistry]].

## The finite counterpart, in hyperchemistry

The contract there can state this exactly for finite relations, where limits cannot be stated at all. Adding the universal quantifier to the existential projection its composition already uses, two projections applied to one relation in different orders give different results. Over all sixteen relations on `B x B`, with `B = {0, 1}`, `exists y, forall x` always implies `forall x, exists y`, and the converse fails for **exactly two** relations: the identity and the negation that the repository's own witnesses already use. An exchange of limits is an exchange of quantifiers (`epsilon`, `N`), so this is the shape of the failure in a setting small enough to enumerate. It is not a model of limits, and the map from a word of limits to a quantifier prefix is `[OPEN]` there (HC-004).

## Open

* `[OPEN]` The estimator's error bound assumes contraction continues past the sampled range.
* `[OPEN]` Whether `ω^n` buys anything beyond naming the depth. By Shoenfield's limit lemma (recalled, not retrieved), a function is `Δ⁰₂` exactly when it is a limit of a computable function, and `n`-fold limits reach the next levels; the code does not use this.
* `[HYPER]` Representing spacetime as the `ω²`-limit "large spin, then refine".
