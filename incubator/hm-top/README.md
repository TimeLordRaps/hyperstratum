# hm-top: the ladder, its self-containing top, and the complete logic of the gap

| File | Establishes |
|---|---|
| `ConatTop.lean` | Conatural numbers (greatest fixed point of "ground or □"): `□ top = top`; the ladder ℕ embeds injectively and commutes with □; the top is beyond every rung; anything above every rung *is* the top (the top is determined by all runs below); a top-detector would decide whether any Bool stream is all-false (LPO). Only `finite_or_top` needs classical choice. |
| `gl.py`, `gl_check.py` | GL decision procedure (sequent calculus GLS) with an independent finite-tree countermodel oracle (300/300 random agreements); Löb, G2, "proving own consistency ⇒ inconsistent", Henkin's self-assertion closes, Gödel's self-denial ≡ consistency; arithmetic truth of letterless sentences; modal agents: FairBot cooperates with itself, defects against DefectBot. |

Run: `HM_LEAN=… python -m pytest tests -vv -s`. Mutation gate: weakening the GL rule to the K rule loses both Löb and axiom 4. (Dropping only the added □A makes the search non-terminating: that premise is what both proves Löb and bounds the search.)
Literature cited from memory: Solovay 1976 (GL arithmetically complete), LaVictoire et al. 2014 (program equilibrium via provability logic).

## Added: the reality-class mapping against hyperreality's registry

`reality_classes.py` builds the owner's mapping (base ← normal/rational/irrational, surreality ← surreal, areality ← imaginary,
sempiternity ⊃ the realities, universempiternity self-containing) as a `hyperreality.Registry` (imported read-only from
`fields/hyperreality`). Findings: expressible; kinds stay unordered although the number classes nest; the registry refuses the
one-node loop U ∋ U (direct self-containment) but accepts the two-node loop, which is not well-founded and is bisimilar to the
one-node loop (partition refinement). A one-sided loop is not bisimilar (negative control).

## Added: is sempiternity bisimilar to its container?

`sempiternity_bisim.py` enumerates all 16 combinations of four clauses (S contains S; U contains U; U contains S; U contains the
realities directly) and checks the derived criterion: S ~ U iff U contains the realities and (S contains a copy of the whole exactly when
U does). 4 of 16 are bisimilar; the owner's "only U contains S and itself" is not (a wrong, earlier predicate of mine is rejected by the
enumeration, which is how it was caught).

## Added: a finite toy for anchoring preality at both ends

`preality_anchor.py` (Arnold's cat map on a 60 x 60 torus, 10 x 10 coarse-graining; a non-reversible map is rejected): infinite time in finite space is a loop (period 60, so an exhaustive run is exact enumeration of a finite set); a microstate has one exact past while a macro-moment has one timeline per compatible microstate (100); anchoring a second macro-moment later keeps 1 to 9 of those 100 (mean 2.8 over 36 possible end macrostates). It illustrates what "locked landmark additional to the big bang" can mean (a two-boundary problem), not that any physical system behaves this way.
