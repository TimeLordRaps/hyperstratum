from hyperstratum import lexicon, registry, scan

from conftest import CANONICAL, PINS


def _setup(root):
    reg = registry.load_registry(root, pins=PINS)
    terms, _ = lexicon.parse_canonical(CANONICAL)
    return reg, terms


def test_mentions_have_line_numbers_and_skip_vendored_dirs(root):
    reg, terms = _setup(root)
    s = scan.scan_field(reg.by_name["beta"], terms)
    m = s.mentions["hypernode"]
    assert m.count == 1  # node_modules/ and .lake/ are carried, not authored
    assert m.locations == [("docs/one.md", 3)]
    assert s.mentions["person-hypernode"].locations == [("docs/one.md", 3)]


def test_tags_symbols_open_items(root):
    reg, terms = _setup(root)
    a = scan.scan_field(reg.by_name["alpha"], terms)
    assert [x.name for x in a.symbols] == ["Thing", "visible"]
    assert a.symbols[1].doc == "Do it." and a.symbols[1].line == 9
    assert a.open_items == [("README.md", 8, "[OPEN] Is a hypernode a field?")]
    b = scan.scan_field(reg.by_name["beta"], terms)
    assert b.tags == {"FORM": 1, "FRAME": 2}
    kinds = {(x.kind, x.name) for x in b.symbols}
    assert ("theorem", "foo") in kinds and ("def", "bar") in kinds
    assert b.sorry_count == 1  # the comment line does not count


def test_contract_and_excerpt(root):
    reg, terms = _setup(root)
    a = scan.scan_field(reg.by_name["alpha"], terms)
    assert a.contract["scope"] == "Toys."
    assert a.excerpt.startswith("Alpha studies the Hyperfield")


def test_sibling_edges_and_citations(root):
    reg, terms = _setup(root)
    scans = {n: scan.scan_field(f, terms, scan.sibling_names(reg)) for n, f in reg.by_name.items() if f.pin}
    edges = scan.build_edges(scans, reg)
    got = {(e.source, e.target, e.kind): e.count for e in edges}
    assert got[("alpha", "beta", "url")] == 1
    assert got[("beta", "alpha", "name")] == 1
    cites = scans["alpha"].citations
    assert cites[0].target == "beta" and cites[0].sha == "b" * 40
    assert cites[0].path == "docs/one.md" and cites[0].line == 6


def test_citation_audit_against_pins_and_hyperstratum_blobs(root):
    reg, terms = _setup(root)
    scans = {n: scan.scan_field(f, terms, scan.sibling_names(reg)) for n, f in reg.by_name.items() if f.pin}
    assert scans  # every pinned field scans without error before its citations are audited
    old, new = "c" * 40, "d" * 40
    blobs = {(old, "specs/x.md"): "111", ("HEAD", "specs/x.md"): "222"}
    c_cur = scan.Citation("alpha", "README.md", 1, "beta", "b" * 40, "docs/one.md")
    c_old = scan.Citation("alpha", "README.md", 2, "beta", new, "docs/one.md")
    c_drift = scan.Citation("alpha", "README.md", 3, "hyperstratum", old, "specs/x.md")
    c_same = scan.Citation("alpha", "README.md", 4, "hyperstratum", "HEAD", "specs/x.md")
    blobs[("HEAD", "specs/x.md")] = "222"

    def lookup(sha, path):
        return blobs.get((sha, path))

    out = scan.audit_citations([c_cur, c_old, c_drift, c_same], reg, lookup)
    assert [a.status for a in out] == ["CURRENT", "BEHIND", "DRIFTED", "CURRENT"]
    assert out[1].detail  # states what is and is not known
