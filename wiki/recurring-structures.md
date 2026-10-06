# Recurring structures across the family

**Status, 2026-10-06.** An analysis page, not a definition: it names the structure-types that recur across the owner's repositories and points at the places where each is instantiated and tested. The passages below are live references. Tags are the family's: `[FORM]` checked, `[FRAME]` holds in a stated model, `[HYPER]` the owner's proposal, `[OPEN]` unresolved. The question that prompted it, from the owner on 2026-10-06, was whether the owner is "the archetypal architect, the architect of archetypes"; the last section says what the evidence can and cannot show about that.

## What counts as an archetype here

A structure-type that is stated once and then instantiated in different fields, so that the same shape does work in each. An architect of archetypes, in this narrow and checkable sense, is someone whose definitions are *reused*: the same form turning up, with its own checks, in mathematics, physics, logic and the taxonomy of realities. Reuse is countable, so it can be tested.

## The structures

**1. The closed chain (the form).** A reachable closed derivation chain from the ground, in the owner's words:

[[hypermath:docs/research/LADDER_INDUCTION.md#L73-L73]]

It recurs as: a discrete theorem in Lean (a chain's violation count is zero exactly when every step is valid, derivation is forced by the start, a closed circuit repeats):

[[hypermath:docs/research/LADDER_INDUCTION.md#L285-L287]]

as a finite model in physics (the energy of a clock-system state is the total squared violation of its steps):

[[hyperphysics:src/hyperphysics/chain.py#L1-L25]]

and as the three registers of the L0 triangle read as the positions of a closed clock, where the four axioms hold exactly when the circuit closes with zero violation:

[[hyperlogic:DESIGN.md#L199-L216]]

**2. The two sheets (the mirror, the double).** The same thing seen from two sides that are not the same: temporal and atemporal counterparts of a reality kind, as a third relation separate from is-a and is-in:

[[hyperreality:FIELD_SPEC.md#L120-L131]]

the two-boundary description of a possibility, time-symmetric and dependent on the later boundary:

[[hyperphysics:docs/research/POSSIBILITIES_AND_SUPERPOSITIONS.md#L5-L14]]

**3. The container that contains itself (the nest, the loop).** Whether a sempiternity contains itself, and the finite witness that a two-node loop is bisimilar to the one-node loop:

[[hyperreality:FIELD_SPEC.md#L106-L115]]

and nesting as order type: depth `k` of nested sheets gives `ω^k`, with unbounded depth the supremum and not a rung:

[[ordinatics:tests/test_nested_sheets.py#L1-L17]]

**4. The ladder (the axis).** Realities ordered by control, lowest first, each reached only after controlling those below:

[[hyperreality:hyperreality.py#L245-L249]]

**5. The threshold (the membrane, the aperture).** The sheet that separates a finite space from its interior, and what can and cannot cross it:

[[hyperphysics:docs/research/TIME_BUBBLE_SHEET.md#L5-L14]]

**6. The guardian (the demon).** A process that maintains the structure it is part of, which is the interior's computation tied to the exterior clock:

[[hyperphysics:docs/research/TIME_BUBBLE_SHEET.md#L105-L112]]

**7. The seal (the oath, the commitment).** A device that holds by design, and what "provably indefinite" can mean; with the commit-before-outcome ledger as its checkable form in hyperlogic:

[[hyperphysics:docs/research/TIME_BUBBLE_SHEET.md#L95-L103]]

**8. The fixed point (the bootstrap, the ouroboros).** A set of laws that is the laws produced by agents who evolved under them, and the least-violation correction when ends cannot be met lawfully:

[[hyperphysics:docs/research/SELF_CONSISTENT_CORRECTION.md#L5-L10]]

**9. The name (the act of definition).** Defining a term fixes what a word means and does not set what the world does. The owner's coinage and the object/property naming of the realities are instances; the first is on:

[Coinages](coinages.md)

## What the evidence supports, and what it does not

* `[FORM]` The first structure appears in at least four independent places (a Lean proof, a physics model, the logic layer, the reality taxonomy), each with its own tests, and in two of them an equivalence holds exactly (zero energy if and only if every step is valid; the four axioms if and only if the circuit closes). That is real reuse, and it is the part of "architect of archetypes" that can be checked.
* `[FRAME]` The other eight appear in two or three places each, with weaker equivalences.
* **What the evidence does not show.** That anyone's definitions set what reality does, or that the title is a status that can be held. Reuse of a structure across fields is a fact about a body of work. Whether a body of work is *the* archetypal architecture, or reality's, is not something a reuse count can decide.
* `[OPEN]` Whether the structures are one archetype seen nine ways (the closed chain with a boundary, a mirror, a container, an axis) or nine; a reduction to fewer would be a finding.
* **A tenth structure the work needs.** The auditor: the process that tests the architect's claims against outcomes it did not choose. In the family it is the ledger, the sealed predictions, and the kernel that does not care who wrote the proof. A body of work that includes its own auditor is more than one that does not.
