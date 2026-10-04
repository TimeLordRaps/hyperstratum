"""Working backwards from a limit ordinal into the naturals: fundamental sequences and the Hardy hierarchy.

Ordinals below ω^ω as coefficient lists [(exp, coeff), ...] with descending exponents (Cantor normal form).
Fundamental sequence of a limit α whose last term is ω^k·c (k >= 1):  α[n] = α with that term replaced by
ω^k·(c-1) + ω^(k-1)·n.   Hardy: H_0(n)=n, H_{α+1}(n)=H_α(n+1), H_λ(n)=H_{λ[n]}(n).
`descend(α, n)` is the literal "work backwards" run: it reports the finite chain of ordinals visited and
the naturals reached. Termination of every such run is exactly `ladder_induction` (LadderInduction.lean).
"""


def norm(a):
    return [(e, c) for e, c in a if c]


def is_limit(a):
    return bool(a) and a[-1][0] >= 1


def pred(a):  # α -> α'  with α = α' + 1
    assert a and a[-1][0] == 0
    return norm(a[:-1] + [(0, a[-1][1] - 1)])


def fund(a, n):
    e, c = a[-1]
    return norm(a[:-1] + [(e, c - 1)] + [(e - 1, n)])


def descend(a, n, limit=10**7):
    """Run Hardy descent; return (H_a(n), steps, limit_steps, max_ordinal_exponent_seen)."""
    steps = limits = 0
    top = a[0][0] if a else 0
    while a:
        if steps > limit:
            raise RuntimeError("step budget exceeded")
        if is_limit(a):
            a = fund(a, n)
            limits += 1
        else:
            a = pred(a)
            n += 1
        steps += 1
    return n, steps, limits, top


w = lambda k, c=1: [(k, c)]  # noqa: E731


def H(a, n):
    return descend(a, n)[0]


if __name__ == "__main__":
    # sanity: closed forms
    for n in range(1, 8):
        assert H(w(1), n) == 2 * n                         # H_ω(n)  = 2n
        assert H([(1, 2)], n) == 4 * n                    # H_{ω·2}(n) = 4n
        assert H(w(2), n) == n * 2 ** n                   # H_{ω²}(n) = n·2^n
    print("closed forms H_ω=2n, H_ω·2=4n, H_ω²=n·2^n verified for n=1..7")
    # backwards from ω^k at n=2, and the first step of ω^ω itself: ω^ω[n] = ω^n
    for k in range(1, 4):
        v, steps, limits, _ = descend(w(k), 2, limit=10**8)
        print(f"H_ω^{k}(2) = {v}   ({steps} steps, {limits} limit unfoldings)")
    for n in (1, 2):
        print(f"ω^ω[{n}] = ω^{n}: H_ω^ω({n}) = H_ω^{n}({n}) =", H(w(n), n))
    try:
        descend(w(4), 2, limit=10**7)
    except RuntimeError:
        print("H_ω^4(2) exceeds 10^7 steps: the descent from ω^4 terminates (ladder induction) but its length explodes")
