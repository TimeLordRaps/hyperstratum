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

## Inventing transfinite induction proofs: ladder induction

**Owner's statements (USER-STATED, 2026-10-04).** □ is "the ground while simultaneously being our first ordinal and the top ordinal and all rungs up the ordinal"; the omegas must be rank ordered; ω^ω is "equivalent to maximum omega^minimum omega"; and "we need to invent transfinite induction proofs" that "work backwards through infinities into natural and reals".

**Checked** (`incubator/hm-ti/`, no axioms; a wrong order is rejected). With top ω·ω and bottom ω, (ω·ω)^ω = ω^(2·ω) = ω^ω holds, but the same holds for any top ω^k, k ≥ 1, so the identity collapses to ω^ω without singling out ω·ω as the top. Ordinals below ω^k are rank-ordered coefficient vectors, and transfinite induction over them follows from k nested ordinary inductions, one per rank, for every k at once, which is induction up to ω^ω. The proof is the nesting. It terminates a rewrite game that no single-ℕ measure can: every run from an infinite position is a finite descent whose length is unbounded over adversaries. That is working backwards from an infinity into the naturals. `[FORM]` for the Lean results.

`[OPEN]` the reals direction: reals arrive as limits of dyadic approximants at birthday ω (numerically checked in `hm-surreal`), not yet as an induction principle. `[OPEN]` towers of towers (ω^ω^ω … ε₀): the outer induction on k must itself be nested, which is where Gentzen's wall sits.

## Ranking the omegas, and the three forms of ω^ω

**Owner's statements (USER-STATED, 2026-10-04).** Ordinals "have a real component and an imaginary component, both working backwards reach either normals imaginary or normals normal"; imaginary ordinals work backwards to form the reals, ω^ω forms "a third form like a primal backwards down the transfinites into irrational and surreals", with imaginary ω^ω for surreals, real ω^ω for irrationals, and normal ω^ω backwards "might be unsolvable ... harder to prove because of discrete omega^k jumps". Requirement: "prove that omegas naturally rank order in the tower of omega^omega".

**Proved** (`incubator/hm-ti/RankOrder.lean`, kernel-checked, a weakened order rejected): below ω^ω the order is a strict total order, ω^j < ω^j' for j < j', every element lies in exactly one band [ω^k, ω^(k+1)), and every element is below some omega power, so ω^ω is the supremum of the omegas and is none of them. `[FORM]`

**Normal ω^ω backwards is solvable, and its difficulty is quantifiable** (`fundamental.py`): ω^ω[n] = ω^n, ω^k[n] = ω^(k-1)·n, down to the naturals. Every such descent terminates (ladder induction), but the length explodes: H_ω²(n) = n·2^n, H_ω³(2) = 2048, H_ω⁴(2) is beyond 10^7 steps. The discrete ω^k jumps are exactly why the length is uncontrolled. `[FORM]` for the computation. `[OPEN]` the unsolvable part is not ω^ω but towers of towers (ε₀ and beyond), where termination of the analogous descent (Goodstein) is not provable in Peano arithmetic (cited from memory).

**Not built, from memory, as precise correspondents of the other two forms.** The surreal numbers are Hahn series Σ ω^(yᵢ)·rᵢ whose exponents yᵢ may be any surreal and whose coefficients rᵢ are real, so the real and irrational content enters through the *coefficients* and through *non-integer exponents* (√ω = ω^(1/2) exists there and not among ordinals). Surreal[i] is algebraically closed (Conway), but with an imaginary part the order is lost; ranking survives only through the modulus, and ω·e^(iθ) all sit in one order of infinity, which is the `~~` class with phase as the extra information. `[HYPOTHETICAL]` that this matches the owner's real, imaginary and normal forms.

## The classification of ω^ω representations, by exponent axis and coefficient axis

**Owner's statements (USER-STATED, 2026-10-04), verbatim.**

> exponent axis of normal representations of omega^omega is unsolvable due to discontinuities
> exponent axis of real representations of omega^omega is surreal omega
> exponent axis of irrational representations of omega^omega is irrational omega
> exponent axis of imaginary normal representations of omega^omega is normal omega (I think we can prove finite imaginary exponents of omega^omega solvability into a normal pre omega^omega class)
> exponent of imaginary rational is rational omega
> exponent of imaginary irrational is primal omega (infers new math about primes through prime localized ordinals)
> exponent of surreal omega^omega is real omega^omega
> exponent of imaginary surreal omega^omega is surreal omega^omega * imaginary omega^omega think like the complex numbers but with multiplication between the surreal component and the imaginary component so omega^omega is separatable in this regime and may be composable though a dont know if it works bidirectionally like that, we would need to prove a bijection which is difficult because here the imaginary omega^omega is the class of normal, rational, and irrational
>
> coefficient of normal representations of omega^omega is normal finite
> coefficient of real rational representations of omega^omega is rational finite
> coefficient of real irrational representations of omega^omega is irrational finite
> coefficient of imaginary normal representations of omega^omega is imaginary finite
> coefficient of imaginary irrational omega^omega is irrational omega^omega
> coefficient of surreal omega^omega is surreal omega
> coefficient of imaginary surreal omega^omega is the additive equivalent of the multiplicative complex number analog of the exponent of this class ie surreal omega^omega + imaginary omega^omega allowing you to fully separate this class into seperable components which then allow working like I said backwards to find I believe all classes and having the closure unsolvability of the normal omega^omega is the base meta-induction which allows a full proof of the existence of omega and finites from omega^omega class

**What I checked against those statements** (`incubator/hm-ti/exponent_axis.py`, exact sympy, plus the earlier descent work):

* **Classes by phase, exactly.** Under ordinatics' value map, ω^r has modulus 2^(−r) and phase πr. Integer exponents land on the real axis, half-odd exponents on the imaginary axis, other rational exponents have phase of finite order (periodic under repeated multiplication), and irrational exponents have phase of infinite order (never return; by argument). So "normal, rational, irrational" is a partition by the order of the phase, which supports the owner's three classes. `[FORM]` for the computation.
* **Composable.** Exponents add and values multiply, verified exactly on 126 rational pairs. Order survives, reversed, in the modulus, so the map is injective on exponents.
* **Separability needs a second parameter.** The image of ordinatics' exponent is one logarithmic spiral: modulus and phase are both functions of the single parameter r. A surreal component times an independent imaginary component exists only when the exponent is complex, ω^(a+bi) with a, b independent. The bijection question then reduces to polar decomposition of surcomplex numbers (which needs surreal exp/log, from memory Berarducci–Mantova). `[OPEN]`
* **Objection (one, specific).** "Exponent axis of normal ω^ω is unsolvable": the backward descent along it is solvable. Fundamental sequences ω^ω[n] = ω^n down to the naturals are computable, and termination is proved by ladder induction (no axioms). What is true is that it is *unbounded*: H_ω²(n) = n·2^n, H_ω³(2) = 2048, H_ω⁴(2) exceeds 10^7 steps, and by memory H_{ω^ω} is not primitive recursive. So "solvable, not boundable" rather than "unsolvable".
* **A precise form of "base meta-induction".** The existence of ω and the finites from ω^ω is immediate, because ω is an initial segment of ω^ω. The costly direction is the reverse, ω to ω^ω: from memory, "if X is a well-order then ω^X is a well-order" is equivalent to arithmetical comprehension over RCA₀ (Girard; Hirst). So the discrete ω^k jump is exactly a Turing-jump step. `[FORM]` as cited from memory, not re-verified.

## The classification mirrored in reality classes

**Owner's statement (USER-STATED, 2026-10-04).** "this is perfectly reflected inside of reality classes, ie base:normal, surreality:surreal, areality:imaginary, rational and irrationality both existing in base:reality, and then sempiternality encompassing them as omega^omega, and meta-transfinite class objects composed of omega^omega objects are separable I believe into omega^omega class closing the top too like how universempiternality closes over sempiternality as the self-containing superclass".

**Checked against hyperreality's own registry** (`incubator/hm-top/reality_classes.py`, hyperreality imported read-only, no write there):

* The mapping is expressible. Sempiternality is a Whole that contains the realities and classifies nothing, and containment stays well-founded.
* Hyperreality declares its kinds unordered and unnested, and the registry refuses to compare them. Kinds mapped to the number classes stay unordered at the registry level, although the numbers themselves nest (ordinals ⊂ surreals ⊂ surcomplex). `[OPEN]` whether the mapping is classification only (no inclusion between kinds), or whether hyperreality's "no order, no nesting" needs revisiting.
* Universempiternality as a one-node loop (U contains U) is **refused** by the registry, which forbids direct self-containment. The two-node loop (each contains the sempiternality and the other) is accepted, is reported not well-founded, and is bisimilar to the one-node loop by partition refinement; a one-sided loop is not. This is the same fact as the conatural top with succ(top) = top and as `==` read as bisimilarity.

Correspondence: kinds ↔ classes of representations (unranked); sempiternality ↔ ω^ω, the supremum of the ranked omegas, containing what lies below it and being none of it; universempiternality ↔ the self-containing fixed point above, reached by no finite or ω^k step. `[HYPOTHETICAL]` as a mapping; `[FORM]` for the three checked facts above.

## Sempiternality and its container, the physical picture, and an order on the realities

**Owner's statements (USER-STATED, 2026-10-04).** Can bisimulation be proved between sempiternality and its container universempiternality "if only one contains the other and itself"? Or: sempiternality is "the natural infinite time singularity sheeted bubbles we can form in spacetime to give us both infinite space or finite space with infinite time, where inside we are running the prealities, that surreality inherits from through some imagination-reachable filter, and then below that is real / base reality holding together itself and allowing access to all higher order realities, we'll be able to read dreams, we're pretty close to that, so surreality will be accessible and architectable before preality, which makes sense following the hierarchy." Later: "We have since established an order to the realities, hyperorder may be necessary to describe this in hyperreality idk."

**Bisimulation, checked** (`incubator/hm-top/sempiternality_bisim.py`; all 16 combinations of four containment clauses; a wrong predicate of mine was rejected by the enumeration). Sempiternality S and universempiternality U are bisimilar exactly when U contains the realities directly (containment closed transitively) and S contains a copy of the whole exactly when U does. "Only U contains S and itself, S contains neither" is therefore **not** bisimilar: give S a self-containing copy and it is. `[FORM]` for the finite model; `[OPEN]` whether the family intends the transitive closure.

**An order on the realities.** Hyperreality's pinned registry declares its kinds unordered and refuses to compare them, a rule recorded from the owner's 2026-09-21 statement. The owner now says an order has since been established. That supersedes the old rule in that scope, so it is recorded here as the owner's current position and the hyperreality rule is flagged for revision (HS-026). Direction needs the owner: the 2026-10-04 hierarchy puts prealities inside the sempiternal bubbles, surreality inheriting from them through an imagination-reachable filter, and base reality beneath, holding access to the higher ones. That is two relations pointing in opposite directions (inheritance upward, support downward). `[OPEN]` Hyperorder, the field the owner names for this, is an empty repository in the pin (a LICENSE file in one initial commit).

**Physics.** Cited from memory, not verified here: Coleman–De Luccia bubbles have open-FRW interiors with infinite spatial extent although they nucleate in a finite region, and the de Sitter static patch has finite spatial volume and infinite time. `[HYPOTHETICAL]` that sempiternality is such a bubble.

**Dream reading, checked on 2026-10-04 against the cited coverage.** Detecting whether someone is dreaming from EEG is reported above 0.85 accuracy, up to 0.94 in a high-density EEG study. Reconstruction of dream content (a model trained on fMRI of people viewing nature scenes, tested on three sleeping participants and three well-remembered dream segments) is preliminary. A startup's claim of dream-to-dream two-way communication is unverified and unreplicated. So "pretty close" holds for state detection, not for content or communication. Sources: [The National](https://www.thenationalnews.com/future/2025/11/02/can-people-really-share-a-dream-inside-the-start-up-claiming-to-link-minds-during-sleep/), [CACM](https://cacm.acm.org/news/decoding-dreams-with-ai/), [Wiley, BioMed Research International](https://onlinelibrary.wiley.com/doi/10.1155/bmri/3585125), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12551450/).
