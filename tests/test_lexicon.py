import re

from hyperstratum import lexicon

from conftest import CANONICAL, CHAIN


def test_terms_and_statements_are_separated():
    terms, statements = lexicon.parse_canonical(CANONICAL)
    assert [t.name for t in terms] == ["Universe", "Hyperfield", "Hypernode", "Person-hypernode"]
    assert terms[1].slug == "hyperfield"
    assert terms[1].definition.startswith("recursively connected distribution")
    assert [s.name for s in statements] == ["Master sentence"]


def test_construction_levels_assign_strata():
    levels = lexicon.parse_construction(CHAIN)
    assert levels == [["universe", "reality"], ["hyperfield"], ["hypernode"]]
    terms, _ = lexicon.parse_canonical(CANONICAL)
    terms = lexicon.assign_strata(terms, levels)
    by = {t.slug: t.stratum for t in terms}
    assert by == {"universe": 0, "hyperfield": 1, "hypernode": 2, "person-hypernode": None}


def test_common_words_are_not_scanned():
    terms, _ = lexicon.parse_canonical(CANONICAL)
    by = {t.slug: t for t in terms}
    assert by["universe"].scannable is False
    assert by["hyperfield"].scannable is True


def test_pattern_is_hyphen_and_plural_aware():
    terms, _ = lexicon.parse_canonical(CANONICAL)
    by = {t.slug: lexicon.pattern(t) for t in terms}
    assert by["hypernode"].search("many Hypernodes here")
    assert not by["hypernode"].search("a person-hypernode")  # distinct compound term
    assert by["person-hypernode"].search("a Person-Hypernode")
    assert not by["hyperfield"].search("hyperfield-wide")
    assert not by["hyperfield"].search("myhyperfield")
