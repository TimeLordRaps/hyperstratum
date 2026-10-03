import json

from hyperstratum import lexicon, refs, registry

from conftest import CANONICAL, PINS


def _ctx(root, **kw):
    reg = registry.load_registry(root, pins=PINS)
    terms, _ = lexicon.parse_canonical(CANONICAL)
    return refs.Resolver(reg, terms, root, **kw)


def test_find_refs():
    found = refs.find_refs("a [[alpha:README.md#L1-L2]] b [[Hyperfield]] c [[beta]] [[alpha:x.py]]")
    assert [f.raw for f in found] == [
        "[[alpha:README.md#L1-L2]]", "[[Hyperfield]]", "[[beta]]", "[[alpha:x.py]]"
    ]
    assert found[0].field == "alpha" and found[0].path == "README.md" and found[0].span == (1, 2)
    assert found[1].field is None and found[1].name == "Hyperfield"


def test_transclusion_is_live_text_with_permalink(root):
    r = _ctx(root)
    text, resolved = r.expand("see [[beta:docs/one.md#L3-L4]]", link_term=lambda s: f"T/{s}")
    assert "Line two mentions a person-hypernode" in text
    assert "Line three" in text and "<pre>" in text
    assert "https://github.com/TimeLordRaps/beta/blob/" + "b" * 40 + "/docs/one.md#L3-L4" in text
    assert resolved[0].status == "OK"


def test_term_and_field_links(root):
    r = _ctx(root)
    text, resolved = r.expand("[[Hyperfield]] and [[alpha]]", link_term=lambda s: f"../terms/{s}.html",
                              link_field=lambda n: f"../fields/{n}.html")
    assert "[Hyperfield](../terms/hyperfield.html)" in text
    assert "[alpha](../fields/alpha.html)" in text
    assert all(x.status == "OK" for x in resolved)


def test_missing_things_are_named(root):
    r = _ctx(root)
    _, res = r.expand("[[nope:a.md]] [[beta:nope.md]] [[beta:docs/one.md#L40-L50]] [[Nonterm]]",
                      link_term=lambda s: s)
    assert [x.status for x in res] == ["MISSING_FIELD", "MISSING_FILE", "BAD_RANGE", "MISSING_TERM"]


def test_move_is_detected_by_content_hash_across_fields(root):
    r = _ctx(root)
    _, res = r.expand("[[beta:docs/one.md#L3-L4]]", link_term=lambda s: s)
    lock = refs.make_lock(res)
    # the passage shifts from beta to alpha
    (root / "fields/alpha/docs").mkdir()
    (root / "fields/alpha/docs/one.md").write_text(
        (root / "fields/beta/docs/one.md").read_text())
    (root / "fields/beta/docs/one.md").unlink()
    r2 = _ctx(root, lock=lock)
    text, res2 = r2.expand("[[beta:docs/one.md#L3-L4]]", link_term=lambda s: s)
    assert res2[0].status == "MOVED"
    assert res2[0].moved_to == ("alpha", "docs/one.md", (3, 4))
    assert "Line two mentions" in text  # still renders from the new home


def test_drift_when_text_changed_since_lock(root):
    r = _ctx(root)
    _, res = r.expand("[[beta:docs/one.md#L3-L4]]", link_term=lambda s: s)
    lock = refs.make_lock(res)
    p = root / "fields/beta/docs/one.md"
    p.write_text(p.read_text().replace("Line two", "Line 2"))
    _, res2 = _ctx(root, lock=lock).expand("[[beta:docs/one.md#L3-L4]]", link_term=lambda s: s)
    assert res2[0].status == "DRIFTED"


def test_explicit_redirect(root):
    (root / "registry/moves.json").write_text(json.dumps(
        {"beta:docs/old.md": "beta:docs/one.md"}))
    r = _ctx(root)
    _, res = r.expand("[[beta:docs/old.md#L3-L3]]", link_term=lambda s: s)
    assert res[0].status == "REDIRECTED"
    assert res[0].moved_to[:2] == ("beta", "docs/one.md")


def test_lock_roundtrip_is_deterministic(root):
    r = _ctx(root)
    _, res = r.expand("[[beta:docs/one.md#L3-L4]] [[alpha:README.md]]", link_term=lambda s: s)
    a = refs.dump_lock(refs.make_lock(res))
    b = refs.dump_lock(refs.make_lock(list(reversed(res))))
    assert a == b and json.loads(a)["schema"] == "hyperstratum-ref-lock/1"


def test_code_is_not_evaluated(root):
    r = _ctx(root)
    src = "grammar: `[[alpha:nope.md]]` and\n```\n[[beta:gone.md]]\n```\nlive: [[alpha]]"
    text, res = r.expand(src, link_term=lambda s: s, link_field=lambda n: n)
    assert "`[[alpha:nope.md]]`" in text and "[[beta:gone.md]]" in text
    assert [x.status for x in res] == ["OK"]
