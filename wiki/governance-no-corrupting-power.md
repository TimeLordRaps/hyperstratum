# No corrupting power: the governance rule

**Status, 2026-10-11.** A pointer page. The rule is the owner's (Tyler Roost, USER-STATED 2026-10-11): no power that is corrupting is allowable in any formal governance system, because otherwise the system is self-toppling, from inside through shadow control or from outside through explicit or implicit control. The formalization lives in [[hyperethics]] as its L2 layer, on branch `claude/l2-governance` (unmerged: `main` there is protected and wants a pull request and the `conformance-gate`), so this wiki pins that branch head until it merges. Tags are the family's: `[FORM]` checked, `[FRAME]` holds in a stated model, `[HYPER]` proposal, `[OPEN]` unresolved.

## The rule, in his words

[[hyperethics:L2_governance.hm#L13-L19]]

## What it is, and how "allowable" is read

The rule pays for something L0 refused to give. L0 refutes `nd-universal-immanence`, the claim that every bearer inhabits what it creates, and says a later layer that wants it must add an axiom and pay. L2 is that payment, for bearers that hold power. "Allowable" is read as membership and not permission, which is why the rule needs no *ought* and cannot be repealed by a law it governs:

[[hyperethics:README.md#L196-L212]]

## Seven clauses, none redundant

Each clause fails in a finite system where the other six hold, which is the evidence none can be dropped. Three of the user's words land on clauses: shadow control is `collusion-capturable` and `undeclared-control`; explicit control is `externally-held`; implicit control is `externally-held` when the command is secret and `self-funding-capture` in the other reading, which is `[OPEN]`:

[[hyperethics:README.md#L214-L230]]

## Checks are powers, and there is no apex

`[FORM]` on finite systems. A check is a veto and a veto is a power, so the rule applies to checks, and the chain of checks must close on itself. This is the same pigeonhole as L0's creative orbit closing on a finite carrier:

[[hyperethics:README.md#L232-L237]]

The derive in the spec, with the L0 comparison made explicit:

[[hyperethics:L2_governance.hm#L284-L299]]

## What the model finds, and what it does not

`[FRAME]`. Capture is priced exactly inside a small model whose assumptions are listed so they can be argued with. Two results are conclusive refutations by a countermodel that obeys the rule, and one finding narrows the declaration:

[[hyperethics:README.md#L239-L276]]

The finding that matters most for the declaration's "otherwise", stated where it is recorded as a non-derive:

[[hyperethics:L2_governance.hm#L375-L387]]

Read plainly: in this model a corrupting clause is a standing route and not, by itself, a fall. A gate one party can pass and a seat held from outside lower the price of taking a system. An exempt reach does so only beside such a gate. An unbounded term lowers what *keeping* a power costs and not what taking it costs. The universal form of "otherwise ... self-toppling" is `[HYPER]`; the bounded form is `[FRAME]`.

## L0 read through the rule

`[FORM]` for the bridge, exhaustive for two realms and for nothing larger:

[[hyperethics:README.md#L304-L329]]

## What can be run

`python -m hyperethics check FILE.json` reads a governance system from JSON and says whether it obeys the rule, why not, which of the three ways in are open, and what taking it costs. Six systems ship as examples in `examples/`. The reader fails closed: an unknown field is an error and a field left out takes the corrupting default.

## Open

- `[OPEN]` Which reading of **implicit control** is meant: command running outward in secret, or a structure that pays for its own capture. Both are implemented and reported (HS-037).
- `[OPEN]` Whether "allowable" as membership is what was meant, or whether a prohibition with an *ought* is wanted. L0 has no *ought*, so the second would be a new axiom to pay for.
- `[OPEN]` Prices and stakes are inputs supplied by whoever builds a model. The model is not shown to describe any real institution.
- `[OPEN]` The rule is adopted, not derived. It inherits L0's `GC-5` (the normative force of `norm-inhabits`) unchanged.
- Merge route: `main` on `hyperethics` is protected. The branch awaits a pull request, or the owner's word.
