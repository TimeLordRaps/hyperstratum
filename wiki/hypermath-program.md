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
