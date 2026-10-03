"""Tests for order-of-limits labels and the commutation check.

The numerical claims are checked against oracles that do not share code with
the system under test: closed forms for the toy functions, and for the
Curie-Weiss magnet the mean-field fixed point m = tanh(beta m), solved here by
iteration, against an exact finite-N sum computed in the module.
"""

from __future__ import annotations

import math

import pytest

from hyperphysics.limits import (
    LimitEstimate,
    Status,
    Verdict,
    Word,
    all_orders,
    commutation,
    decide,
    curie_weiss_magnetization,
    sequence_limit,
    to_infinity,
    to_zero,
)


# ----------------------------------------------------------------- labels


def test_label_counts_nested_stages():
    x, y = to_infinity("x", 1, 2, 8), to_infinity("y", 1, 2, 8)
    assert str(Word.of(x).label) == "ω"
    assert str(Word.of(x, y).label) == "ω^2"
    assert str(Word.of(x, y, to_zero("h", 1, 0.5, 8)).label) == "ω^3"


def test_a_diagonal_group_is_one_limit_of_order_type_omega():
    x, y = to_infinity("x", 1, 2, 8), to_infinity("y", 1, 2, 8)
    assert str(Word.of((x, y)).label) == "ω"


def test_the_ordinal_alone_does_not_distinguish_orders_the_word_does():
    x, y = to_infinity("x", 1, 2, 8), to_infinity("y", 1, 2, 8)
    a, b = Word.of(x, y), Word.of(y, x)
    assert a.label == b.label  # same depth ...
    assert a != b  # ... different procedures
    assert a.notation != b.notation


def test_notation_is_outermost_first_like_mathematics():
    x, y = to_infinity("x", 1, 2, 8), to_zero("h", 1, 0.5, 8)
    assert Word.of(x, y).notation == "lim[h→0+] lim[x→∞]"


# -------------------------------------------------------- sequence limits


def test_geometric_convergence_is_converged_with_a_bounded_residual():
    est = sequence_limit([2.0 ** -k for k in range(1, 30)])
    assert est.status is Status.CONVERGED and abs(est.value) <= est.residual + 1e-12


def test_divergence_and_oscillation_are_not_reported_as_limits():
    assert sequence_limit([float(k) for k in range(1, 30)]).status is Status.UNSETTLED
    assert sequence_limit([1e15 * (k + 1) for k in range(8)]).status is Status.DIVERGED
    assert sequence_limit([(-1.0) ** k for k in range(30)]).status is Status.UNSETTLED


def test_a_drift_below_the_tolerance_is_not_a_limit():
    # Differences of 1e-8 are under the tolerance, but they do not shrink: the
    # sequence is still creeping upward and nothing certifies where it stops.
    assert sequence_limit([1e-8 * k for k in range(1, 40)]).status is Status.UNSETTLED


def test_slow_algebraic_convergence_is_unsettled_not_converged():
    # 1/k does reach 0, but the sampled window cannot certify it.
    assert sequence_limit([1.0 / k for k in range(1, 400)]).status is Status.UNSETTLED


# --------------------------------------------------------------- the toys


def _ratio(x, y):
    return x / (x + y)


def test_a_non_commuting_pair_gives_two_different_answers():
    x, y = to_infinity("x", 1, 2, 40), to_infinity("y", 1, 2, 40)
    report = commutation(_ratio, all_orders(x, y))
    assert report.verdict is Verdict.DO_NOT_COMMUTE
    values = sorted(round(e.value, 6) for e in report.results.values())
    assert values == [0.0, 1.0]


def test_the_diagonal_limit_is_a_third_answer():
    t = to_infinity("t", 1, 2, 40)
    x, y = to_infinity("x", 1, 2, 40), to_infinity("y", 1, 2, 40)
    est = Word.of((x, y)).evaluate(_ratio)
    assert est.status is Status.CONVERGED and est.value == pytest.approx(0.5)
    assert str(Word.of((x, y)).label) == "ω"
    assert t  # the single-parameter schedule type is the same object


def test_a_commuting_control_commutes():
    x, y = to_infinity("x", 1, 2, 40), to_infinity("y", 1, 2, 40)
    report = commutation(lambda x, y: 1 / x + 1 / y, all_orders(x, y))
    assert report.verdict is Verdict.COMMUTE and report.max_gap <= 1e-6


def test_unsettled_inputs_make_the_verdict_unknown_never_commute():
    x, y = to_infinity("x", 1, 2, 12), to_infinity("y", 1, 2, 12)
    report = commutation(lambda x, y: math.sin(x + y), all_orders(x, y))
    assert report.verdict is Verdict.UNKNOWN


def _e(value, residual):
    return LimitEstimate(value, Status.CONVERGED, residual)


def test_decision_rule_needs_the_gap_to_exceed_the_uncertainty():
    # 1e-9 apart, but each answer is only known to 1e-3: neither claim is earned.
    assert decide([_e(0.0, 1e-3), _e(1e-9, 1e-3)], tol=1e-6)[0] is Verdict.UNKNOWN
    # 1e-9 apart, exact, and finer than the tolerance: they commute.
    assert decide([_e(0.0, 0.0), _e(1e-9, 0.0)], tol=1e-6)[0] is Verdict.COMMUTE
    # 1e-9 apart, exact, and the tolerance is finer than the gap: they do not.
    assert decide([_e(0.0, 0.0), _e(1e-9, 0.0)], tol=1e-12)[0] is Verdict.DO_NOT_COMMUTE
    # any unsettled member forbids both claims.
    bad = LimitEstimate(0.0, Status.UNSETTLED, 1.0)
    assert decide([_e(0.0, 0.0), bad], tol=1e-6)[0] is Verdict.UNKNOWN


# ------------------------------------------------------ the physical case


def mean_field_spontaneous(beta: float) -> float:
    """Oracle: the positive root of m = tanh(beta m), or 0 if only m = 0 exists."""
    m = 1.0
    for _ in range(10_000):
        m = math.tanh(beta * m)
    return m


def test_finite_n_magnetization_is_odd_in_h_and_zero_at_h_zero():
    assert curie_weiss_magnetization(200, 2.0, 0.0) == pytest.approx(0.0, abs=1e-12)
    a, b = curie_weiss_magnetization(200, 2.0, 0.05), curie_weiss_magnetization(200, 2.0, -0.05)
    assert a == pytest.approx(-b, abs=1e-12) and a > 0


def _words(beta, h_floor_for_n_first, h_inner_steps):
    n = to_infinity("N", 100, 2, 8)  # N = 100 ... 12800
    h_outer = to_zero("h", 0.32, 0.5, h_floor_for_n_first)
    h_inner = to_zero("h", 0.1, 0.5, h_inner_steps)

    def f(N, h):
        return curie_weiss_magnetization(int(N), beta, h)

    n_inner_then_h = Word.of(n, h_outer)  # lim[h→0+] lim[N→∞]
    h_inner_then_n = Word.of(h_inner, n)  # lim[N→∞] lim[h→0+]
    return f, n_inner_then_h, h_inner_then_n


def test_ferromagnet_orders_of_limits_disagree_below_the_critical_temperature():
    f, thermo_first, field_first = _words(beta=2.0, h_floor_for_n_first=9, h_inner_steps=55)
    # Finite-size corrections fall like 1/N and the schedule stops at N = 12800, so
    # the N-limit can be certified to about 1e-4, not the default 1e-6. The test
    # states that choice and checks that the default refuses to certify it.
    assert thermo_first.evaluate(f).status is Status.UNSETTLED
    a, b = thermo_first.evaluate(f, rel_tol=1e-3), field_first.evaluate(f, rel_tol=1e-3)
    ms = mean_field_spontaneous(2.0)
    assert a.status is Status.CONVERGED and b.status is Status.CONVERGED
    assert abs(a.value - ms) <= a.residual  # the residual claim holds against the oracle
    assert a.residual < 0.05  # and is informative
    assert abs(b.value) <= b.residual + 1e-9
    report = commutation(f, [thermo_first, field_first], rel_tol=1e-3)
    assert report.verdict is Verdict.DO_NOT_COMMUTE and report.max_gap > 0.9


def test_the_same_orders_commute_above_the_critical_temperature():
    f, a, b = _words(beta=0.5, h_floor_for_n_first=37, h_inner_steps=37)
    report = commutation(f, [a, b])
    assert report.verdict is Verdict.COMMUTE
    assert mean_field_spontaneous(0.5) == pytest.approx(0.0, abs=1e-6)


def test_an_inadequate_schedule_is_flagged_not_silently_decided():
    # Taking the field to 1e-12 at fixed N <= 12800 never reaches the regime
    # N*h >> 1, so the inner N-limit has not settled and must say so.
    f, a, _ = _words(beta=2.0, h_floor_for_n_first=37, h_inner_steps=37)
    est = a.evaluate(f)
    assert est.status is not Status.CONVERGED


def test_estimates_are_plain_data():
    est = LimitEstimate(0.5, Status.CONVERGED, 1e-9)
    assert est.value == 0.5 and est.status is Status.CONVERGED
