from hyperstratum import registry

from conftest import PINS


def test_parse_gitmodules(root):
    entries = registry.parse_gitmodules((root / ".gitmodules").read_text())
    assert [e["path"] for e in entries] == ["fields/alpha", "fields/beta"]
    assert entries[0]["url"] == "https://github.com/TimeLordRaps/alpha.git"


def test_load_registry_merges_pins_and_metadata(root):
    reg = registry.load_registry(root, pins=PINS)
    alpha = reg.by_name["alpha"]
    assert alpha.pin == "a" * 40
    assert alpha.role == "hyperfield" and alpha.tagline == "the first field"
    assert alpha.repo_url == "https://github.com/TimeLordRaps/alpha"
    assert alpha.permalink("docs/x.md", "L3-L4") == (
        "https://github.com/TimeLordRaps/alpha/blob/" + "a" * 40 + "/docs/x.md#L3-L4"
    )
    assert alpha.path == root / "fields/alpha"


def test_pending_field_is_reported_not_failed(root):
    reg = registry.load_registry(root, pins=PINS)
    gamma = reg.by_name["gamma"]
    assert gamma.pin is None and gamma.pending
    codes = {(p.code, p.severity) for p in reg.problems()}
    assert ("PENDING_PIN", "info") in codes
    assert not [p for p in reg.problems() if p.severity == "error"]


def test_unregistered_submodule_and_missing_submodule(root):
    (root / "registry/fields.json").write_text(
        '{"fields": {"alpha": {"role": "hyperfield", "tagline": "x"},'
        ' "delta": {"role": "hyperfield", "tagline": "y"}}}'
    )
    reg = registry.load_registry(root, pins=PINS)
    got = {(p.code, p.subject): p.severity for p in reg.problems()}
    assert got[("UNREGISTERED_SUBMODULE", "beta")] == "warning"
    assert got[("MISSING_SUBMODULE", "delta")] == "error"


def test_missing_checkout_is_an_error(root, tmp_path_factory):
    import shutil

    shutil.rmtree(root / "fields/beta")
    reg = registry.load_registry(root, pins=PINS)
    assert ("NO_CHECKOUT", "beta") in {(p.code, p.subject) for p in reg.problems()}
