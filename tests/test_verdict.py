import json

from hyperstratum import cli

from conftest import PINS, write


def run(root, tmp_path):
    v = tmp_path / "verdict.json"
    code = cli.main(["check", "--root", str(root), "--no-git", "--verdict", str(v)],
                    pins=PINS, blob_lookup=lambda s, p: None)
    return code, json.loads(v.read_text())


def test_clean_when_nothing_needs_a_human(root, tmp_path):
    code, v = run(root, tmp_path)
    assert code == 0 and v["clean"] is True and v["attention"] == []
    assert v["schema"] == "hyperstratum-verdict/1"


def test_drift_and_errors_need_a_human(root, tmp_path):
    write(root / "wiki/n.md", "[[beta:docs/one.md#L3-L4]]\n")
    cli.main(["lock", "--root", str(root), "--no-git"], pins=PINS, blob_lookup=lambda s, p: None)
    p = root / "fields/beta/docs/one.md"
    p.write_text(p.read_text().replace("Line two", "Line 2"))
    code, v = run(root, tmp_path)
    assert code == 0 and v["clean"] is False
    assert [a["code"] for a in v["attention"]] == ["DRIFTED"]


def test_stale_sibling_citation_alone_is_not_attention(root, tmp_path):
    write(root / "fields/alpha/s.md", "[s](https://github.com/TimeLordRaps/beta/blob/" + "e" * 40 + "/x.md)\n")
    _, v = run(root, tmp_path)
    assert v["clean"] is True and v["warnings"] >= 1


def test_hyperstratum_definition_drift_is_attention(root, tmp_path):
    write(root / "fields/alpha/s.md", "[d](https://github.com/TimeLordRaps/hyperstratum/blob/" + "c" * 40 + "/specs/x.md)\n")
    cli.main(["check", "--root", str(root), "--no-git", "--verdict", str(tmp_path / "v.json")],
             pins=PINS, blob_lookup=lambda s, p: {"c" * 40: "111", "HEAD": "222"}[s])
    v = json.loads((tmp_path / "v.json").read_text())
    assert v["clean"] is False and v["attention"][0]["code"] == "CITATION_DRIFTED"
