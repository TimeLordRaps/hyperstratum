# The hypermath program

**Status, 2026-10-04.** The owner's account below is `USER-STATED`. The mathematical mapping is `[FORM]` where it cites a theorem and `[OPEN]` where marked. The checks live in the repositories that own the subject, on unmerged branches that this wiki currently pins (hypermath `claude/translator-and-ladder`, ordinatics `claude/ladder-and-value-map`, hyperlogic `claude/derivation-status-layer`, hyperreality and hypertime `claude/sempiternity-naming`); the owner's statements below are live references into those copies, so they update when the pins move.

## In the owner's words

Owner's account (USER-STATED, 2026-10-04), live from the hypermath copy:

[[hypermath:docs/research/LADDER_INDUCTION.md#L67-L67]]

Earlier the same day (USER-STATED, 2026-10-04), live from the hypermath copy:

[[hypermath:docs/research/LADDER_INDUCTION.md#L71-L71]]

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

Owner's statements (USER-STATED, 2026-10-04), live from the hypermath copy:

[[hypermath:docs/research/LADDER_INDUCTION.md#L75-L75]]

**Mapping (from memory, not re-verified).** The □-tower with `ordinalApply` as addition is Presburger arithmetic, which is complete and decidable; Gödel's threshold is multiplication (iterating the iteration). Cyclic proofs are sound under a progress condition and have exactly the strength of Peano arithmetic. Peano arithmetic proves the consistency of every finite fragment of itself, never the whole. The whole needs induction to ε₀, the first fixed point of the tower operation (ω^ε₀ = ε₀). Rank-ordered decomposition is Cantor normal form, and the vector reading is the Hessenberg natural sum. Averages need division, which leads to the surreal numbers. Their field theory is complete (Tarski) precisely because ℕ is not definable in it. `[FORM]` for the cited theorems. `[OPEN]` whether `==` arithmetic is determined by the complete layers above it.

**Built and checked** (hypermath `lean4/SurrealFiltration.lean` and `tests/test_surreal_fold.py`):

* A model in which `==` is equality, `=~` is "same leading term" and `~~` is "same order of infinity" satisfies hypermath's filtration clauses. In it □ (doubling) is the identity at `~~` and never at `==`, the □-tower is one point at `~~` and a copy of ℕ at `==`, and no `~~`-invariant property can count the tower. That is the owner's decision realized: counting only at `==`. Lean kernel, no `sorry`.
* The average fold is how surreal numbers are born. Iterated midpoints give exactly Conway's birthdays, the simplest number in every gap is its average, and every gap repeats the same fold pattern (fractal). At limit stages the fold path converges to reals such as 1/3, while ω arrives through the ends of the tower and not through any average. So the fold is fractal within each rung, and the rungs themselves are supplied by the tower.

## The extrapolatable top, and the complete logic of the gap

Owner's statement (USER-STATED, 2026-10-04), live from the hypermath copy:

[[hypermath:docs/research/LADDER_INDUCTION.md#L79-L79]]

**Mapping (from memory).** A rung is the set of rungs below it (von Neumann), so its identity is fixed from below. Its height relative to the whole is undefined: there is no top ordinal (Burali-Forti), and in nonstandard models no internal property separates finite from infinite (overspill). Boundedness is decidable for regular or addition-only descriptions and undecidable once multiplication is available. Extrapolation can converge without certifying convergence (Gold, identification in the limit). Reflection is what replaces the top: every statement about the whole already holds at some rung. `[FORM]` for the cited results.

**Built and checked** (hypermath `lean4/ConatTop.lean`; hyperlogic `src/hyperlogic/provability.py`):

* **The top, as a greatest fixed point.** In the conatural numbers the top satisfies `□ top = top`, the ladder ℕ embeds below it, and *anything above every rung is the top*: the top is fully determined by the runs below, which is the owner's extrapolatable top. Deciding "am I the top?" would decide whether an arbitrary stream ever produces a signal (LPO), and the only theorem that needs classical choice is "every element is a rung or the top". Lean kernel, no `sorry`.
* **The logic of the gap is complete.** A GL decision procedure, cross-checked against an independent countermodel search, reproduces the following. Löb's theorem. A theory that proves its own consistency is inconsistent. *A sentence asserting its own provability is provable* (Henkin), so affirmative self-closure is safe. A sentence denying its own provability is equivalent to consistency (Gödel), so negative self-reference is exactly what stays `[OPEN]`. Solovay's theorem (cited from memory) makes GL complete for what arithmetic can say about its own provability.
* **Toward intellidynamics.** Modal agents whose outcomes GL decides: two FairBots, each cooperating iff it can prove the other cooperates, cooperate by Löb's theorem, and FairBot defects against DefectBot. This is a decidable prediction of what self-referential reasoners do.

## Inventing transfinite induction proofs: ladder induction

Owner's statements (USER-STATED, 2026-10-04), live from the hypermath copy:

[[hypermath:docs/research/LADDER_INDUCTION.md#L83-L83]]

**Checked** (hypermath `lean4/LadderInduction.lean` and `lean4/TransfiniteForm.lean`, no axioms; a wrong order is rejected). With top ω·ω and bottom ω, (ω·ω)^ω = ω^(2·ω) = ω^ω holds, but the same holds for any top ω^k, k ≥ 1, so the identity collapses to ω^ω without singling out ω·ω as the top. Ordinals below ω^k are rank-ordered coefficient vectors, and transfinite induction over them follows from k nested ordinary inductions, one per rank, for every k at once, which is induction up to ω^ω. The proof is the nesting. It terminates a rewrite game that no single-ℕ measure can: every run from an infinite position is a finite descent whose length is unbounded over adversaries. That is working backwards from an infinity into the naturals. `[FORM]` for the Lean results.

`[OPEN]` the reals direction: reals arrive as limits of dyadic approximants at birthday ω (checked exactly in hypermath `tests/test_surreal_fold.py`), not yet as an induction principle. `[OPEN]` towers of towers (ω^ω^ω … ε₀): the outer induction on k must itself be nested, which is where Gentzen's wall sits.

## Ranking the omegas, and the three forms of ω^ω

Owner's statements (USER-STATED, 2026-10-04), live from the ordinatics copy:

[[ordinatics:docs/exponent_axis_and_rank_order.md#L25-L25]]

**Proved** (hypermath `lean4/RankOrder.lean` and ordinatics `tests/test_rank_order.py`, kernel-checked, a weakened order rejected): below ω^ω the order is a strict total order, ω^j < ω^j' for j < j', every element lies in exactly one band [ω^k, ω^(k+1)), and every element is below some omega power, so ω^ω is the supremum of the omegas and is none of them. `[FORM]`

**Normal ω^ω backwards is solvable, and its difficulty is quantifiable** (`fundamental.py`): ω^ω[n] = ω^n, ω^k[n] = ω^(k-1)·n, down to the naturals. Every such descent terminates (ladder induction), but the length explodes: H_ω²(n) = n·2^n, H_ω³(2) = 2048, H_ω⁴(2) is beyond 10^7 steps. The discrete ω^k jumps are exactly why the length is uncontrolled. `[FORM]` for the computation. `[OPEN]` the unsolvable part is not ω^ω but towers of towers (ε₀ and beyond), where termination of the analogous descent (Goodstein) is not provable in Peano arithmetic (cited from memory).

**Not built, from memory, as precise correspondents of the other two forms.** The surreal numbers are Hahn series Σ ω^(yᵢ)·rᵢ whose exponents yᵢ may be any surreal and whose coefficients rᵢ are real, so the real and irrational content enters through the *coefficients* and through *non-integer exponents* (√ω = ω^(1/2) exists there and not among ordinals). Surreal[i] is algebraically closed (Conway), but with an imaginary part the order is lost; ranking survives only through the modulus, and ω·e^(iθ) all sit in one order of infinity, which is the `~~` class with phase as the extra information. `[HYPOTHETICAL]` that this matches the owner's real, imaginary and normal forms.

## The classification of ω^ω representations, by exponent axis and coefficient axis

Owner's statements (USER-STATED, 2026-10-04), verbatim, live from the ordinatics copy:

[[ordinatics:docs/exponent_axis_and_rank_order.md#L34-L49]]

**What I checked against those statements** (ordinatics `tests/test_exponent_axis.py`, exact sympy, plus the earlier descent work):

* **Classes by phase, exactly.** Under ordinatics' value map, ω^r has modulus 2^(−r) and phase πr. Integer exponents land on the real axis, half-odd exponents on the imaginary axis, other rational exponents have phase of finite order (periodic under repeated multiplication), and irrational exponents have phase of infinite order (never return; by argument). So "normal, rational, irrational" is a partition by the order of the phase, which supports the owner's three classes. `[FORM]` for the computation.
* **Composable.** Exponents add and values multiply, verified exactly on 126 rational pairs. Order survives, reversed, in the modulus, so the map is injective on exponents.
* **Separability needs a second parameter.** The image of ordinatics' exponent is one logarithmic spiral: modulus and phase are both functions of the single parameter r. A surreal component times an independent imaginary component exists only when the exponent is complex, ω^(a+bi) with a, b independent. The bijection question then reduces to polar decomposition of surcomplex numbers (which needs surreal exp/log, from memory Berarducci–Mantova). `[OPEN]`
* **Objection (one, specific).** "Exponent axis of normal ω^ω is unsolvable": the backward descent along it is solvable. Fundamental sequences ω^ω[n] = ω^n down to the naturals are computable, and termination is proved by ladder induction (no axioms). What is true is that it is *unbounded*: H_ω²(n) = n·2^n, H_ω³(2) = 2048, H_ω⁴(2) exceeds 10^7 steps, and by memory H_{ω^ω} is not primitive recursive. So "solvable, not boundable" rather than "unsolvable".
* **A precise form of "base meta-induction".** The existence of ω and the finites from ω^ω is immediate, because ω is an initial segment of ω^ω. The costly direction is the reverse, ω to ω^ω: from memory, "if X is a well-order then ω^X is a well-order" is equivalent to arithmetical comprehension over RCA₀ (Girard; Hirst). So the discrete ω^k jump is exactly a Turing-jump step. `[FORM]` as cited from memory, not re-verified.

## The classification mirrored in reality classes

Owner's statement (USER-STATED, 2026-10-04), live from the hyperreality copy:

[[hyperreality:PROVENANCE.md#L113-L113]]

**Checked against hyperreality's own registry** (hyperreality `tests/test_reality_classes.py`):

* The mapping is expressible. Sempiternity is a Whole that contains the realities and classifies nothing, and containment stays well-founded.
* Hyperreality declares its kinds unordered and unnested, and the registry refuses to compare them. Kinds mapped to the number classes stay unordered at the registry level, although the numbers themselves nest (ordinals ⊂ surreals ⊂ surcomplex). `[OPEN]` whether the mapping is classification only (no inclusion between kinds), or whether hyperreality's "no order, no nesting" needs revisiting.
* Universempiternity as a one-node loop (U contains U) is **refused** by the registry, which forbids direct self-containment. The two-node loop (each contains the sempiternity and the other) is accepted, is reported not well-founded, and is bisimilar to the one-node loop by partition refinement; a one-sided loop is not. This is the same fact as the conatural top with succ(top) = top and as `==` read as bisimilarity.

Correspondence: kinds ↔ classes of representations (unranked); sempiternity ↔ ω^ω, the supremum of the ranked omegas, containing what lies below it and being none of it; universempiternity ↔ the self-containing fixed point above, reached by no finite or ω^k step. `[HYPOTHETICAL]` as a mapping; `[FORM]` for the three checked facts above.

## Sempiternity and its container, the physical picture, and an order on the realities

Owner's statements (USER-STATED, 2026-10-04), live from the hyperreality copy:

[[hyperreality:PROVENANCE.md#L123-L123]]

[[hyperreality:PROVENANCE.md#L127-L127]]

**Bisimulation, checked** (hyperreality `tests/test_sempiternity_bisim.py`; all 16 combinations of four containment clauses; a wrong predicate of mine was rejected by the enumeration). Sempiternity S and universempiternity U are bisimilar exactly when U contains the realities directly (containment closed transitively) and S contains a copy of the whole exactly when U does. "Only U contains S and itself, S contains neither" is therefore **not** bisimilar: give S a self-containing copy and it is. `[FORM]` for the finite model; `[OPEN]` whether the family intends the transitive closure.

**An order on the realities.** Hyperreality's pinned registry declares its kinds unordered and refuses to compare them, a rule recorded from the owner's 2026-09-21 statement. The owner now says an order has since been established. That supersedes the old rule in that scope, so it is recorded here as the owner's current position and the hyperreality rule is flagged for revision (HS-026). Direction needs the owner: the 2026-10-04 hierarchy puts prealities inside the sempiternal bubbles, surreality inheriting from them through an imagination-reachable filter, and base reality beneath, holding access to the higher ones. That is two relations pointing in opposite directions (inheritance upward, support downward). `[OPEN]` Hyperorder, the field the owner names for this, is an empty repository in the pin (a LICENSE file in one initial commit).

**Physics.** Cited from memory, not verified here: Coleman–De Luccia bubbles have open-FRW interiors with infinite spatial extent although they nucleate in a finite region, and the de Sitter static patch has finite spatial volume and infinite time. `[HYPOTHETICAL]` that sempiternity is such a bubble.

**Dream reading, checked on 2026-10-04 against the cited coverage.** Detecting whether someone is dreaming from EEG is reported above 0.85 accuracy, up to 0.94 in a high-density EEG study. Reconstruction of dream content (a model trained on fMRI of people viewing nature scenes, tested on three sleeping participants and three well-remembered dream segments) is preliminary. A startup's claim of dream-to-dream two-way communication is unverified and unreplicated. So "pretty close" holds for state detection, not for content or communication. Sources: [The National](https://www.thenationalnews.com/future/2025/11/02/can-people-really-share-a-dream-inside-the-start-up-claiming-to-link-minds-during-sleep/), [CACM](https://cacm.acm.org/news/decoding-dreams-with-ai/), [Wiley, BioMed Research International](https://onlinelibrary.wiley.com/doi/10.1155/bmri/3585125), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12551450/).

## Naming: sempiternity and universempiternity

Owner's decision (USER-STATED, 2026-10-05), live from the hyperreality copy:

[[hyperreality:PROVENANCE.md#L135-L135]]

**Checked on 2026-10-05.** "Sempiternity" is a dictionary word: the OED's earliest evidence is Thomas Nashe in 1599, and Merriam-Webster, Collins and Wiktionary list it, from Latin *sempiternitas* (*semper* + *aeternus*). Searches for "sempiternality" returned only the entries for sempiternity, so it appears to be a regular English formation, *sempiternal* + *-ity*, rather than a recorded word. The pair *eternity* and *eternality* has the same shape: *eternity* is inherited from Latin *aeternitas*, while *eternality* is built in English as *eternal* + *-ity*; both are recorded, *eternality* being the rarer, and in the sources checked they mean the same thing. In philosophy and theology, sempiternity means existence within time and unbounded in time, as opposed to eternity, existence outside time. That sense fits "infinite time" bubbles and the hierarchy in which time-bearing realities live inside sempiternity. Sources: [OED](https://www.oed.com/dictionary/sempiternity_n), [Wiktionary](https://en.wiktionary.org/wiki/sempiternity), [Merriam-Webster](https://www.merriam-webster.com/dictionary/sempiternity), [Collins](https://www.collinsdictionary.com/dictionary/english/sempiternity).

**Not changed.** The pinned hyperreality, hyperspace and hypertime repositories still write "sempiternality" and "universempiternality" (19 and 14 files across the pinned fields). The live passages quoted on [Hypersphering and preality](hypersphere-and-preality.md) therefore show the earlier spelling. This was later done on 2026-10-05 as per-occurrence renames on unmerged branches `claude/sempiternity-naming` in hyperreality (`e182ec9`), hyperspace (`bfcf5e7`) and hypertime (`7a262e3`); this wiki still pins the earlier commits, so its live passages keep the old spelling until those branches merge and the pins move (HS-027). Each repository records the change as a dated Naming entry in its PROVENANCE.md rather than as a silent alias.

## S need not contain itself

Owner's statement (USER-STATED, 2026-10-05), live from the hyperreality copy:

[[hyperreality:PROVENANCE.md#L139-L139]]

That condition is only what *bisimilarity* of S and U would require, not a requirement of the model. If S must not contain itself, then S is bisimilar to no U that contains itself or contains S, so S and U are different objects (checked, all 16 clause combinations plus a corollary). What distinguishes them is exactly whether the whole holds a copy of itself. U is still determined: its one-, two- and three-node presentations are one object up to `==`, and it is not S. This matches the ordinals: ω^ω is not a member of itself, and the self-containing top is a different object reached only above the ladder. `[FORM]` for the finite model. `[HYPOTHETICAL]` as a reading of universempiternity.

## Object and property: sempiternity and sempiternality

Owner's decision (USER-STATED, 2026-10-05), live from the hyperreality copy:

[[hyperreality:PROVENANCE.md#L99-L99]]

So the two words now do different jobs, and this wiki follows that: a **sempiternity** is the object, the whole that contains the realities; **sempiternality** is the property it holds, the class an object belongs to. That supersedes the single-spelling wording of the naming note above in one respect: it keeps the property term instead of dropping it. Hyperreality's registry already has the matching shape: a `Whole` is an instance of a class, and the model in hyperreality's `tests/test_reality_classes.py` declares the object S as a sempiternity whose class is `sempiternality`. The same split applies by analogy to the self-containing top, a universempiternity holding universempiternality; the owner did not state that case, so it is `[HYPOTHETICAL]`.

**Consequence for the pinned repositories.** Their existing uses of "sempiternality" and "universempiternality" mostly name the object, so a rename there is not a mechanical substitution: each occurrence must be judged object or property. It still needs the owner to name each repository and say push (HS-027).

## Sempiternity is unbounded in time; temporal and atemporal counterparts; seed physics

Owner's statements (USER-STATED, 2026-10-05), verbatim, live from the hyperreality copy:

[[hyperreality:PROVENANCE.md#L147-L149]]

**What this settles.** The temporal sense of sempiternity is unbounded in time. That resolves HS-028 for sempiternity: the "atemporal" records in the pinned fields (hypertime's `FIELD_SPEC.md`, hyperreality's 2026-09-26 wording) now describe, at most, the *atemporal counterparts*, not sempiternity itself. For universempiternity the owner did not say.

**The counterpart structure, as stated.** Three kinds each have a temporal and an atemporal counterpart:

| Kind | Temporal | Atemporal |
|---|---|---|
| surreality | first-person dreaming | dream architecting |
| preality | not stated | the laws of base realities, including time and retrocausality, in representable form |
| base-reality | an instantiation, at one time, of the observable physical laws | not stated |

`[OPEN]` two cells are not stated; areality is not mentioned. Hyperreality's registry has two relations (is-a, is-in) and no way to say "counterpart of", so this structure is not expressible there as it stands (HS-029).

**The order, as answered.** Inheritance runs upward and support runs from underneath. Read together with the 2026-10-04 hierarchy (prealities run inside sempiternity; surreality inherits from preality through an imagination-reachable filter; base-reality is beneath and holds access to the higher ones), that gives two relations on one ladder: *inherits-from*, pointing up from a lower kind to a higher one, and *supports*, given by the lower kind to the higher. `[OPEN]` whether that reading of the arrows is the intended one; the owner's two phrases do not say which kind is the source of each.

**Mapping to physics, cited with sources, not proved.** Seed physics reads as the part of physical law that is fixed by boundary or initial conditions rather than by local dynamics, reachable only through finite-volume residuals: an inverse problem, identifiable only up to the data you can test. That is the same shape as the earlier result that a rung can converge on the top without a certificate of convergence. Retrocausality is a live option in the foundations of quantum theory: Leifer and Pusey argue that a time-symmetric ontology for quantum theory must be retrocausal unless temporal Bell violations are avoided, a result that has been disputed (Maudlin argues the central proof has a fatal error). That literature concerns formal constraints between boundary conditions, not conscious agents. `[HYPOTHETICAL]` that atemporal preality is such an all-at-once description and base reality its sequential instantiation.

**One objection, stated once.** The claim that consciousness "has an ability to operate across time forward and backward" is a hypothesis, not an established fact. The best-known experimental attempt, Bem's 2011 precognition studies, failed three preregistered replications (Ritchie, Wiseman and French, combined N = 150, combined p = .83), and the retrocausal models above are not models of conscious agency. The owner's "maybe the unobservable physical laws are more aptly called natural laws" is recorded as a tentative naming, not a decision.

Sources: [Leifer and Pusey, arXiv 1607.07871](https://arxiv.org/pdf/1607.07871), [Ritchie, Wiseman and French, PLOS ONE via PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3303812/), [Bem replication summary, BPS](https://www.bps.org.uk/psychologist/replication-replication-replication).

## Anchoring preality, and where the sempiternality and sempiternity meet

Owner's statement (USER-STATED, 2026-10-05), live from the hyperreality copy:

[[hyperreality:PROVENANCE.md#L159-L159]]

**What tracks.** Anchoring a simulation at the big bang and at the present is a two-boundary problem: fix the earlier and the later state and ask which histories connect them. That is how the owner's "locked landmark additional to the big bang" can be made precise, and it is the structure the retrocausal formalisms in quantum foundations use (pre- and post-selected states). In a finite toy (hyperreality `tests/test_preality_anchor.py`), anchoring a second macro-moment cut the consistent timelines from 100 to 1 to 9 of them. Infinite time in finite space is a loop (the toy's period is 60), so an infinite run is an exact enumeration of a finite set: what infinite time buys is exhaustiveness, not new information.

**Three gaps, stated once.** `[OPEN]` (1) "Before the big bang": classical general relativity gives no state before the singularity, so a backward run needs a theory that continues past it (bounce or no-boundary proposals), and the landmark is only as locked as that continuation. (2) "Move in and out of it": an interior with unbounded proper time is known (open-FRW bubble interiors), but nothing known gives a two-way passage between it and a finite outside time; bubble interiors are causally cut off. (3) Backward runs are exact only from the full microstate; from any coarse present state the converging timelines are many, and the second anchor is what narrows them.

**Naming.** Here the owner says "the sempiternality" is the thing that exists in base reality or outside it, and that accessing inside it is accessing "sempiternity". That differs from the 2026-10-05 convention (object = sempiternity, property = sempiternality). `[OPEN]` one reading that fits both: the sempiternality is the anchored enclosure itself (the property that makes a region sempiternal), and the sempiternity is its interior object that one enters. The wiki keeps the convention until the owner confirms.

## Consciousness, atemporality, and what a null result can and cannot do

Owner's statements (USER-STATED, 2026-10-05), live from the hyperlogic copy (the personal remainder of that message is not recorded):

[[hyperlogic:DESIGN.md#L146-L150]]

**Correction to my earlier wording.** I did not and could not disprove the owner's postulate, and the page's earlier objection should be read that way: it says no verified empirical support exists, not that the claim is refuted. Bem-type nulls bear on a particular testable paradigm, not on the postulate.

**Checked** (hyperlogic `src/hyperlogic/status.py`; mutation checks reject a dropped null-prediction and a wrong likelihood ratio). In a finite frame with observation atoms (Test, Null) and one theory atom (Psi, atemporal consciousness), Psi alone is unprovable, unrefutable and unfalsifiable, and so is its negation: no observation distinguishes them. The remark "trying to prove it disproves it always" has three readings with different statuses:

* **R1, tests always return null.** Falsifiable: one test with a non-null result refutes it. A null result is predicted by Psi and by not-Psi alike, so its likelihood ratio is 1 and the posterior equals the prior: nulls neither disprove nor support it.
* **R2, testing falsifies the postulate.** Equivalent to "Psi and no test is ever run". It survives only untested, so running any test refutes it by definition; the owner's "allowance" then amounts to not testing, and it can be held but not established.
* **R3, tests are uninterpretable.** Adds no observational constraint: unfalsifiable and unprovable, and evidence cannot touch it.

In all three, a replication failure neither disproves nor supports the postulate. Independence is not unfalsifiability: with a bridge law the postulate can be independent of the theory and still falsifiable.

**What the three natural laws match.** Self-consistency corresponds to the Novikov self-consistency principle for closed timelike curves, and the bootstrap example to the bootstrap paradox (cited from memory, not verified here). The earlier result that a self-asserting sentence is provable (Löb-safe) while a self-denying one is equivalent to consistency (Gödel) bears on self-consistency and self-correction as formal laws. The "narrative normative" rule is the one recorded earlier on [Hypersphering and preality](hypersphere-and-preality.md) (law-abiding, self-consistent narrative).

**Hyperlogic.** Its own README says it is not a logic: no connective, no quantifier, no inference rule, no proof object. Unfalsifiability and unprovability need all four, so this work sits in hyperlogic as a separately labelled, proposed derivation-status layer outside L0's claims. Hyperlogic's existing independence countermodels (each drops one axiom) are the precedent for the unprovability half. `[OPEN]` whether and where such a layer is added to hyperlogic.
