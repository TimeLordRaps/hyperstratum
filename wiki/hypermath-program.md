# The hypermath program

**Status, 2026-10-04.** The owner's account below is `USER-STATED`. The mathematical mapping is `[FORM]` where it cites a theorem and `[OPEN]` where marked. The experiment is kernel-checked in `incubator/hm-fixedpoint/` (hyperstratum branch only; nothing was written to hypermath).

## In the owner's words

> hypermath is the underlying complete structure that contains itself and allows the other hypers to exist, and ordinatics, it all stems from me doubting godelian completeness of arithmetic and designing transfinite arithmetic ordinatics so that I could define a self-closing system which is complete and explains arithmetic with yes a system outside of arithmetic ordinatics but ordinatics contains its own design within itself from hypermaths self-closure. So if we can derive arithmetic from transfinite representations like work backwards through the condition of being beyond infinite then we can complete arithmetic so to speak

Earlier the same day: "A form is a reachable closed derivation chain from the ground L0", and the purpose of `.hm` files is that "they are translatable to any language". Other answers from that exchange are not recorded here yet.

## How established mathematics meets the program

Gödel's incompleteness theorems bind theories that are consistent, effectively axiomatized and able to interpret basic arithmetic. Completing arithmetic through the transfinite has known exact forms (cited from memory, not re-verified this session):

* **ω-rule (Schütte).** Infer `∀n P(n)` from proofs of every `P(k)`; proofs become well-founded trees of ordinal height. Peano arithmetic with the ω-rule is complete for arithmetic truth. `[FORM]`
* **Gentzen (1936).** Peano arithmetic's consistency follows from transfinite induction to `ε₀`. `[FORM]`
* **Turing (1939), Feferman (1962).** Progressions of theories along ordinal notations, adding reflection at each step; some path proves every true arithmetic sentence. `[FORM]`

The constant price is that completeness stops being effectively checkable: the information moves into choosing a notation that really denotes a well-ordering. `[OPEN]` Whether hypermath's self-closure discharges that residue, or relocates it.

The unresolved architectural question for the owner: must the completed arithmetic be checkable by verifier (finite certificates only), in which case well-foundedness of the ordinal notation becomes the one trusted assumption, or may completeness be truth beyond any finite check (the ω-rule route)?

## What the experiment found (kernel-checked)

The pinned hypermath refutes three L3 derives that `.hm` tags `FORM` (`ordinal-zero-identity`, `ordinal-succ-applies`, `path-length-arithmetic`) with a finite model of all 38 axiom clauses. Its own comment gives the reason:

[[hypermath:lean4/FiniteActionCountermodel.lean#L66-L68]]

1. **The missing piece is the recursion equations, not injectivity.** The same six-element model, with `ordinalApply` defined by a table found through exhaustive search, satisfies every clause of `FullAxioms` and all three claims at once (`clauses_and_computation_laws_consistent`, depending only on `propext` and `Quot.sound`; a one-entry change to the table is rejected). So the countermodel shows the claims do not follow from the clauses. It does not show they conflict with them. The clauses declare `ordinal-apply` as an opaque with no laws:

   [[hypermath:L3_ordinatics.hm#L130]]

2. **"Reachable from ground" must be transfinite.** For any carrier, reachability by finitely many `f2f` steps contradicts the source's own limit axiom whenever `≡` is reflexive at the limit (`finite_reachability_contradicts_limit`, no axioms used):

   [[hypermath:lean4/Hypermath/L3Ordinatics.lean#L54]]

3. **The transfinite least fixed point works.** Take forms to be the least collection containing `ground` and closed under `f2f` and under limits of ω-sequences (Brouwer ordinal trees). Then minimality is the recursor, `f2f` is injective, `f2f x ≠ ground`, the limit is not finite, and `ordinalApply` defined by transfinite recursion makes all three claims hold with equality. ω+1 is reached as `ordinalApply (f2f ground) ordinalLimit`. Lean reports no axioms used.

Reading for the program: the owner's definition of form, taken transfinitely, plus ordinal iteration defined by transfinite recursion, is what rescues the arithmetic derives. That is the "work backwards through beyond-infinite" step stated as a type. `[FORM]` for the three Lean results. `[OPEN]`: that this model also satisfies every hypermath clause (not attempted), and whether to add the recursion equations to hypermath (an owner decision; hypermath's `AGENTS.md` fixes an 18-axiom inventory).

See also [Limit labels](limit-labels.md) for ordinal depth labels on physical limits.

## Later the same day: towers, collapse, and the average fold

**Owner's statements (USER-STATED, 2026-10-04).** A finite looping operation like □ "can be applied in place in infinitum", so the □-tower should give cyclic proofs of non-contradiction and compress transfinite representations "along compressible dimensions". The operations are "always identity", like 1×1×1×1, and ω-towers can be decomposed "into rank ordered omegas" with the smallest at the bottom. Infinities can be treated as pseudounits, "equatable in their continuation aspect, sort of like they are vectors". Decision: **ℕ is definable only at `==`.** Open question raised: the average as "a fold that is fractally occurring up the tower".

**Mapping (from memory, not re-verified).** The □-tower with `ordinalApply` as addition is Presburger arithmetic, which is complete and decidable; Gödel's threshold is multiplication (iterating the iteration). Cyclic proofs are sound under a progress condition and have exactly the strength of Peano arithmetic. Peano arithmetic proves the consistency of every finite fragment of itself, never the whole. The whole needs induction to ε₀, the first fixed point of the tower operation (ω^ε₀ = ε₀). Rank-ordered decomposition is Cantor normal form, and the vector reading is the Hessenberg natural sum. Averages need division, which leads to the surreal numbers. Their field theory is complete (Tarski) precisely because ℕ is not definable in it. `[FORM]` for the cited theorems. `[OPEN]` whether `==` arithmetic is determined by the complete layers above it.

**Built and checked** (`incubator/hm-surreal/`):

* A model in which `==` is equality, `=~` is "same leading term" and `~~` is "same order of infinity" satisfies hypermath's filtration clauses. In it □ (doubling) is the identity at `~~` and never at `==`, the □-tower is one point at `~~` and a copy of ℕ at `==`, and no `~~`-invariant property can count the tower. That is the owner's decision realized: counting only at `==`. Lean kernel, no `sorry`.
* The average fold is how surreal numbers are born. Iterated midpoints give exactly Conway's birthdays, the simplest number in every gap is its average, and every gap repeats the same fold pattern (fractal). At limit stages the fold path converges to reals such as 1/3, while ω arrives through the ends of the tower and not through any average. So the fold is fractal within each rung, and the rungs themselves are supplied by the tower.

## The extrapolatable top, and the complete logic of the gap

**Owner's statement (USER-STATED, 2026-10-04).** "The highest top is the extrapolatable top that would have to be the top given the descriptions of all of the runs below where you currently are." From a rung "you cant know how high you are or what determines that this run is this rung, you just know that the ordinals below you are smaller infinities than you and the ones above you are larger". Sometimes, from yourself and the neighbouring infinities, "can you determine a boundedness of your tower otherwise its undecidable".

**Mapping (from memory).** A rung is the set of rungs below it (von Neumann), so its identity is fixed from below. Its height relative to the whole is undefined: there is no top ordinal (Burali-Forti), and in nonstandard models no internal property separates finite from infinite (overspill). Boundedness is decidable for regular or addition-only descriptions and undecidable once multiplication is available. Extrapolation can converge without certifying convergence (Gold, identification in the limit). Reflection is what replaces the top: every statement about the whole already holds at some rung. `[FORM]` for the cited results.

**Built and checked** (`incubator/hm-top/`):

* **The top, as a greatest fixed point.** In the conatural numbers the top satisfies `□ top = top`, the ladder ℕ embeds below it, and *anything above every rung is the top*: the top is fully determined by the runs below, which is the owner's extrapolatable top. Deciding "am I the top?" would decide whether an arbitrary stream ever produces a signal (LPO), and the only theorem that needs classical choice is "every element is a rung or the top". Lean kernel, no `sorry`.
* **The logic of the gap is complete.** A GL decision procedure, cross-checked against an independent countermodel search, reproduces the following. Löb's theorem. A theory that proves its own consistency is inconsistent. *A sentence asserting its own provability is provable* (Henkin), so affirmative self-closure is safe. A sentence denying its own provability is equivalent to consistency (Gödel), so negative self-reference is exactly what stays `[OPEN]`. Solovay's theorem (cited from memory) makes GL complete for what arithmetic can say about its own provability.
* **Toward intellidynamics.** Modal agents whose outcomes GL decides: two FairBots, each cooperating iff it can prove the other cooperates, cooperate by Löb's theorem, and FairBot defects against DefectBot. This is a decidable prediction of what self-referential reasoners do.
