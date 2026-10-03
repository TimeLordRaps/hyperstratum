"""Order of limits, stated once, so that a limit procedure can be cited by name.

WHY THIS MODULE EXISTS
----------------------
Physics reaches its continuum and classical regimes through limits, and several
limits in a row rarely commute. The thermodynamic limit and the zero-field limit
of a ferromagnet give different magnetizations depending on which is taken
first; in loop quantum gravity the large-spin limit on a fixed graph and the
refinement of the graph are two limits whose order is the whole question. A
claim such as "spacetime is the continuum limit of the foam" is incomplete until
it says *which limits, in which order, along which schedule*.

So a limit procedure is written down as a **word**: an ordered list of stages,
innermost first, each with a parameter, a target and an explicit schedule. The
word carries an ordinal **label** (its depth) and a **notation** (its order).
`commutation` evaluates several words on the same function and reports whether
their answers agree, disagree, or cannot be told apart.

WHAT IS AND IS NOT CLAIMED
--------------------------
* The label of a word with `n` nested stages is `ω^n`; a group of parameters sent
  to their targets together along one schedule (a diagonal limit) is a single
  stage of order type `ω`. This is a *description* of the nesting, not new
  physics. It does **not** distinguish the order of the stages: `lim_x lim_y` and
  `lim_y lim_x` have the same label and are different words. The word, not the
  ordinal, is what a citation must carry.
* Recalled, not retrieved, and unverified here: by Shoenfield's limit lemma a
  function is `Δ⁰₂` exactly when it is the limit of a computable function, and
  `n`-fold iterated limits of computable functions are the `Δ⁰ₙ₊₁` level. That
  is the sense in which depth `n` buys power; this module does not use it.
* The numerical estimator is deliberately conservative and is **not** a proof of
  convergence. It reads only the last `window` steps of a finite schedule and
  certifies a limit only if the successive differences there contract by at
  least a fixed factor. A tail error bound follows *if that contraction
  continues past the sampled range*, which is an assumption, stated, not
  checked. Slow (algebraic) convergence is therefore reported UNSETTLED, never
  as a limit.
* An inner limit must be taken far past the outer stage's range. A schedule that
  does not do so reports UNSETTLED. The schedules are part of the label.
* A verdict of COMMUTE or DO_NOT_COMMUTE is returned only when the numbers earn
  it. Otherwise the verdict is UNKNOWN.

Everything here uses the standard library only and takes dimensionless
magnitudes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from itertools import permutations
from typing import Callable, Mapping, Sequence

__all__ = [
    "CURIE_WEISS_FAILS_WHEN",
    "LimitEstimate",
    "OrdinalLabel",
    "Stage",
    "Status",
    "Verdict",
    "Word",
    "all_orders",
    "commutation",
    "curie_weiss_magnetization",
    "decide",
    "sequence_limit",
    "to_infinity",
    "to_zero",
]

# ---------------------------------------------------------------------------
# Estimating one limit from a finite schedule.
# ---------------------------------------------------------------------------

WINDOW = 3  # successive differences examined: the last WINDOW + 1 values
CONTRACTION = 0.75  # each difference must be at most this fraction of the previous
FLOAT_FLOOR = 1e-12  # differences below this (relative) are below the noise
DIVERGED_AT = 1e12


class Status(str, Enum):
    CONVERGED = "converged"
    DIVERGED = "diverged"
    UNSETTLED = "unsettled"


@dataclass(frozen=True, slots=True)
class LimitEstimate:
    """A limit estimate with the status that says whether to believe it."""

    value: float
    status: Status
    residual: float  # bound on |value - limit| under the contraction assumption


def sequence_limit(values: Sequence[float], rel_tol: float = 1e-6) -> LimitEstimate:
    """Estimate lim of a sequence from its tail, or say that it cannot.

    If the last WINDOW differences each contract by at least CONTRACTION, the
    tail error of the last value is at most `d_last * q / (1 - q)` with
    `q = CONTRACTION`, i.e. `3 * d_last`. That bound is the residual.
    """
    tail = list(values[-(WINDOW + 1):])
    if len(tail) < WINDOW + 1:
        return LimitEstimate(float(tail[-1]) if tail else math.nan, Status.UNSETTLED, math.inf)
    last = float(tail[-1])
    if any((not math.isfinite(v)) or abs(v) > DIVERGED_AT for v in tail):
        return LimitEstimate(last, Status.DIVERGED, math.inf)
    diffs = [abs(tail[i + 1] - tail[i]) for i in range(WINDOW)]
    scale = max(1.0, abs(last))
    d_last = diffs[-1]
    residual = 3.0 * d_last
    if d_last <= FLOAT_FLOOR * scale:
        return LimitEstimate(last, Status.CONVERGED, residual)
    contracting = all(diffs[i + 1] <= CONTRACTION * diffs[i] for i in range(WINDOW - 1))
    if contracting and residual <= rel_tol * scale:
        return LimitEstimate(last, Status.CONVERGED, residual)
    return LimitEstimate(last, Status.UNSETTLED, residual)


# ---------------------------------------------------------------------------
# Stages, words, labels.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Stage:
    """One parameter sent to a target along an explicit schedule."""

    parameter: str
    target: str  # "inf" or "0+"
    schedule: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.target not in ("inf", "0+"):
            raise ValueError(f"target must be 'inf' or '0+', not {self.target!r}")
        if len(self.schedule) < WINDOW + 1:
            raise ValueError(f"a schedule needs at least {WINDOW + 1} values")
        steps = zip(self.schedule, self.schedule[1:])
        if self.target == "inf" and not all(b > a for a, b in steps):
            raise ValueError("a schedule to infinity must be strictly increasing")
        if self.target == "0+" and not (
            all(b < a for a, b in zip(self.schedule, self.schedule[1:])) and self.schedule[-1] > 0
        ):
            raise ValueError("a schedule to 0+ must be strictly decreasing and positive")

    @property
    def symbol(self) -> str:
        return "∞" if self.target == "inf" else "0+"

    def extended(self, steps: int) -> "Stage":
        """Continue the schedule geometrically by `steps` more values."""
        ratio = self.schedule[-1] / self.schedule[-2]
        more = tuple(self.schedule[-1] * ratio ** (k + 1) for k in range(steps))
        return Stage(self.parameter, self.target, self.schedule + more)


def to_infinity(parameter: str, start: float, ratio: float, steps: int) -> Stage:
    if ratio <= 1:
        raise ValueError("ratio must exceed 1")
    return Stage(parameter, "inf", tuple(start * ratio**k for k in range(steps)))


def to_zero(parameter: str, start: float, ratio: float, steps: int) -> Stage:
    if not 0 < ratio < 1:
        raise ValueError("ratio must lie in (0, 1)")
    return Stage(parameter, "0+", tuple(start * ratio**k for k in range(steps)))


@dataclass(frozen=True, slots=True)
class OrdinalLabel:
    """`ω^n`: the order type of `n` nested limits each of order type `ω`."""

    exponent: int

    def __str__(self) -> str:
        return "ω" if self.exponent == 1 else f"ω^{self.exponent}"


@dataclass(frozen=True, slots=True)
class Word:
    """An ordered limit procedure. `groups[0]` is the innermost limit."""

    groups: tuple[tuple[Stage, ...], ...]

    @staticmethod
    def of(*items: Stage | tuple[Stage, ...]) -> "Word":
        groups = tuple((i,) if isinstance(i, Stage) else tuple(i) for i in items)
        if not groups or any(not g for g in groups):
            raise ValueError("a word needs at least one stage per group")
        for g in groups:
            if len({len(s.schedule) for s in g}) != 1:
                raise ValueError("stages in one group must share a schedule length")
        names = [s.parameter for g in groups for s in g]
        if len(names) != len(set(names)):
            raise ValueError("a parameter may appear once in a word")
        return Word(groups)

    @property
    def label(self) -> OrdinalLabel:
        return OrdinalLabel(len(self.groups))

    @property
    def notation(self) -> str:
        """Outermost limit first, as written in mathematics."""
        parts = [
            "lim[" + ",".join(f"{s.parameter}→{s.symbol}" for s in g) + "]"
            for g in reversed(self.groups)
        ]
        return " ".join(parts)

    def evaluate(self, f: Callable[..., float], rel_tol: float = 1e-6) -> LimitEstimate:
        """Evaluate the nested limit of `f`, inner limits first.

        An inner limit that has not settled for any of the values the outer
        stage actually relies on makes the outer limit UNSETTLED too: an outer
        limit of an unsettled inner one is not certified.
        """

        def at(level: int, assignment: dict[str, float]) -> LimitEstimate:
            if level < 0:
                return LimitEstimate(float(f(**assignment)), Status.CONVERGED, 0.0)
            group = self.groups[level]
            values: list[float] = []
            inner: list[LimitEstimate] = []
            for k in range(len(group[0].schedule)):
                assigned = dict(assignment)
                for s in group:
                    assigned[s.parameter] = s.schedule[k]
                est = at(level - 1, assigned)
                values.append(est.value)
                inner.append(est)
            relied = inner[-(WINDOW + 1):]
            for est in relied:
                if est.status is not Status.CONVERGED:
                    return est
            est = sequence_limit(values, rel_tol)
            return LimitEstimate(est.value, est.status,
                                 est.residual + max(e.residual for e in relied))

        return at(len(self.groups) - 1, {})


def all_orders(*stages: Stage, margin: int = 60) -> list[Word]:
    """Every order of single-parameter stages, with inner stages extended.

    An inner limit has to outrun the range of the stage outside it, so a stage
    at depth `d` below the outermost is continued `d * margin` steps.
    """
    words = []
    for perm in permutations(stages):  # perm[0] is innermost
        depth = len(perm)
        words.append(Word.of(*(
            s.extended(margin * (depth - 1 - level)) for level, s in enumerate(perm)
        )))
    return words


# ---------------------------------------------------------------------------
# Deciding whether several words agree.
# ---------------------------------------------------------------------------


class Verdict(str, Enum):
    COMMUTE = "commute"
    DO_NOT_COMMUTE = "do-not-commute"
    UNKNOWN = "unknown"


def decide(estimates: Sequence[LimitEstimate], tol: float = 1e-6) -> tuple[Verdict, float]:
    """(verdict, largest gap). COMMUTE and DO_NOT_COMMUTE must each be earned.

    * COMMUTE: every pair agrees to within `tol` *and* every estimate is known to
      within `tol`. Otherwise two answers that merely look alike would pass.
    * DO_NOT_COMMUTE: some pair differs by more than their combined uncertainty
      plus `tol`.
    * UNKNOWN: anything else, including any unsettled member.
    """
    if any(e.status is not Status.CONVERGED for e in estimates):
        return Verdict.UNKNOWN, math.nan
    gap, slack = 0.0, 0.0
    for i, a in enumerate(estimates):
        for b in estimates[i + 1:]:
            gap = max(gap, abs(a.value - b.value))
            slack = max(slack, a.residual + b.residual)
    if gap <= tol and slack <= tol:
        return Verdict.COMMUTE, gap
    if gap > slack + tol:
        return Verdict.DO_NOT_COMMUTE, gap
    return Verdict.UNKNOWN, gap


@dataclass(frozen=True, slots=True)
class Commutation:
    results: Mapping[str, LimitEstimate]  # keyed by the word's notation
    verdict: Verdict
    max_gap: float


def commutation(f: Callable[..., float], words: Sequence[Word], tol: float = 1e-6,
                rel_tol: float = 1e-6) -> Commutation:
    """`rel_tol` is the precision each limit must be certified to; `tol` is the
    precision the verdict resolves. Convergence like 1/N cannot be certified to
    1e-6 on a schedule that stops at N = 1e4, and is then reported UNSETTLED
    rather than loosened silently: loosening is the caller's explicit choice."""
    results = {w.notation: w.evaluate(f, rel_tol) for w in words}
    verdict, gap = decide(list(results.values()), tol)
    return Commutation(results, verdict, gap)


# ---------------------------------------------------------------------------
# Worked example: the Curie-Weiss ferromagnet.
# ---------------------------------------------------------------------------

CURIE_WEISS_FAILS_WHEN = (
    "the temperature is above the critical one (beta <= 1 with J = 1): both orders then agree, "
    "so the example shows nothing",
    "N is too small for N * h * beta * m >> 1 at the smallest h taken first: the "
    "thermodynamic limit has not been reached and the schedule must say UNSETTLED",
    "the model is mean-field (every spin couples to every other): it exhibits the order-of-limits "
    "effect cleanly and is not a model of any real magnet's critical behaviour",
)


@lru_cache(maxsize=64)
def _log_binomials(n: int) -> tuple[float, ...]:
    top = math.lgamma(n + 1)
    return tuple(top - math.lgamma(k + 1) - math.lgamma(n - k + 1) for k in range(n + 1))


def curie_weiss_magnetization(n: int, beta: float, h: float) -> float:
    """Exact magnetization per spin of `n` Ising spins with all-to-all coupling.

    `H = -(1/2n)(sum s)^2 - h sum s`, `s = ±1`, inverse temperature `beta` and
    coupling `J = 1` (dimensionless). Exact for finite `n`: a log-sum-exp over the
    `n + 1` values of the total spin.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    lb = _log_binomials(n)
    logw = [lb[k] + beta * ((n - 2 * k) ** 2 / (2 * n) + h * (n - 2 * k)) for k in range(n + 1)]
    top = max(logw)
    num = den = 0.0
    for k, lw in enumerate(logw):
        w = math.exp(lw - top)
        num += w * (n - 2 * k)
        den += w
    return num / den / n
