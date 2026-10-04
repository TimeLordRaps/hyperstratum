# hm-top: the ladder, its self-containing top, and the complete logic of the gap

| File | Establishes |
|---|---|
| `ConatTop.lean` | Conatural numbers (greatest fixed point of "ground or □"): `□ top = top`; the ladder ℕ embeds injectively and commutes with □; the top is beyond every rung; anything above every rung *is* the top (the top is determined by all runs below); a top-detector would decide whether any Bool stream is all-false (LPO). Only `finite_or_top` needs classical choice. |
| `gl.py`, `gl_check.py` | GL decision procedure (sequent calculus GLS) with an independent finite-tree countermodel oracle (300/300 random agreements); Löb, G2, "proving own consistency ⇒ inconsistent", Henkin's self-assertion closes, Gödel's self-denial ≡ consistency; arithmetic truth of letterless sentences; modal agents: FairBot cooperates with itself, defects against DefectBot. |

Run: `HM_LEAN=… python -m pytest tests -vv -s`. Mutation gate: weakening the GL rule to the K rule loses both Löb and axiom 4. (Dropping only the added □A makes the search non-terminating: that premise is what both proves Löb and bounds the search.)
Literature cited from memory: Solovay 1976 (GL arithmetically complete), LaVictoire et al. 2014 (program equilibrium via provability logic).
