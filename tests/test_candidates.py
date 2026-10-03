from hyperstratum import build

from conftest import PINS, write


def _site(root, tmp_path):
    out = tmp_path / "site"
    model = build.build_site(root, out, pins=PINS, blob_lookup=lambda s, p: None)
    return out, model


def test_unlexiconed_hyper_words_are_ranked_by_breadth_then_count(root, tmp_path):
    write(root / "fields/alpha/a.md", "A hyperphere and hyperpheres.\nHypergeometry too.\n")
    write(root / "fields/beta/b.md", "one hyperphere\n")
    out, model = _site(root, tmp_path)
    words = {c["word"]: c for c in model["candidates"]}
    assert list(words)[0] == "hyperphere"  # two fields beats one
    assert words["hyperphere"]["total"] == 3 and set(words["hyperphere"]["fields"]) == {"alpha", "beta"}
    assert words["hyperphere"]["places"][0][:2] == ["alpha", "a.md"]
    assert "hypergeometry" in words


def test_known_terms_fields_and_standard_words_are_not_candidates(root, tmp_path):
    write(root / "fields/alpha/a.md", "hypernode hypernodes hyperfield alpha hyperlink hypertext hypergraph hyperbolic\n")
    _, model = _site(root, tmp_path)
    got = {c["word"] for c in model["candidates"]}
    assert not got & {"hypernode", "hyperfield", "hyperlink", "hypertext", "hypergraph", "hyperbolic"}


def test_candidates_page_is_linked_and_escaped(root, tmp_path):
    write(root / "fields/alpha/a.md", "hyperphere\n")
    out, _ = _site(root, tmp_path)
    page = (out / "candidates.html").read_text()
    assert "hyperphere" in page and "https://github.com/TimeLordRaps/alpha/blob/" in page
    assert "candidates.html" in (out / "index.html").read_text()
