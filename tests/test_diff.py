import json

from hyperstratum import build, diff

from conftest import PINS, write


def _model(**over):
    base = {"source_ref": "r0", "fields": [], "refs": [], "problems": [],
            "ontology": {"terms": [{"slug": "hypernode"}]}}
    base.update(over)
    return base


def field(name, pin, open_=(), syms=(), mentions=None):
    return {"name": name, "pin": pin, "open": list(open_), "symbol_names": list(syms),
            "mentions": mentions or {}}


def test_no_previous_means_no_changes():
    assert diff.diff_models(None, _model()) is None


def test_every_category():
    old = _model(fields=[field("a", "1", ["q1"], ["x::f"], {"hypernode": 2}), field("gone", "9")],
                 refs=[{"key": "k", "status": "OK", "detail": ""}],
                 problems=[{"code": "P", "subject": "s1", "detail": ""}])
    new = _model(source_ref="r1",
                 fields=[field("a", "2", ["q1", "q2"], ["x::f", "x::g"], {"hypernode": 5}), field("fresh", "7")],
                 refs=[{"key": "k", "status": "MOVED", "detail": "d"}],
                 problems=[{"code": "P2", "subject": "s2", "detail": ""}])
    c = diff.diff_models(old, new)
    assert c["fields"]["added"] == ["fresh"] and c["fields"]["removed"] == ["gone"]
    assert c["fields"]["pin_changed"] == [{"name": "a", "old": "1", "new": "2"}]
    assert c["open_items"]["added"] == [{"field": "a", "text": "q2"}]
    assert c["symbols"]["a"]["added"] == 1 and c["symbols"]["a"]["removed"] == 0
    assert c["terms"] == [{"slug": "hypernode", "old": 2, "new": 5}]
    assert c["refs"] == [{"key": "k", "old": "OK", "new": "MOVED"}]
    assert c["problems"]["new"][0]["code"] == "P2" and c["problems"]["resolved"][0]["code"] == "P"
    assert c["empty"] is False


def test_identical_models_are_empty_and_markdown_says_so():
    m = _model(fields=[field("a", "1")])
    c = diff.diff_models(m, m)
    assert c["empty"] is True
    assert "No change" in diff.changes_markdown(c)


def test_old_models_missing_keys_do_not_crash():
    old = _model(fields=[{"name": "a", "pin": "1"}])
    new = _model(fields=[field("a", "1", ["q"])])
    c = diff.diff_models(old, new)
    assert c["open_items"]["added"] == []  # the old build did not record them: not claimed as new
    assert "open_items" in c["unknown"]


def test_load_previous_file_and_failure(tmp_path):
    p = tmp_path / "wiki.json"
    p.write_text(json.dumps(_model()))
    got, why = diff.load_previous(str(p))
    assert got["source_ref"] == "r0" and why == ""
    got, why = diff.load_previous(str(tmp_path / "nope.json"))
    assert got is None and why


def test_build_with_previous_writes_changes_page_and_markdown(root, tmp_path):
    out = tmp_path / "a"
    build.build_site(root, out, pins=PINS, blob_lookup=lambda s, p: None)
    prev = json.loads((out / "wiki.json").read_text())
    write(root / "fields/alpha/new.md", "[OPEN] a fresh question\n")
    out2 = tmp_path / "b"
    model = build.build_site(root, out2, pins=PINS, blob_lookup=lambda s, p: None, previous=prev)
    assert model["changes"]["open_items"]["added"][0]["text"].endswith("a fresh question")
    assert "a fresh question" in (out2 / "changes.html").read_text()
    assert "a fresh question" in (out2 / "changes.md").read_text()
    assert "changes.html" in (out2 / "index.html").read_text()
