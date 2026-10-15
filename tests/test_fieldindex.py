"""The hyperfields index: what it reads from a checkout, and what its page says.

The unit tests build a fixture workspace with its own registry, `.gitmodules` and checkouts, so they
do not depend on `fields/`. Three tests read the real workspace and skip when it is not checked out.
"""

import importlib.util
import json
import pathlib

import pytest

from hyperstratum import fieldindex, registry

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIELDS = ROOT / "fields"
PRESENT = FIELDS.is_dir() and any(p.is_dir() and any(p.iterdir()) for p in FIELDS.iterdir())


def make_workspace(tmp_path, fields):
    """`fields` maps a name to a spec: role, tagline, files (relative path -> text), pinned, pending."""
    root = tmp_path / "ws"
    (root / "registry").mkdir(parents=True)
    (root / "fields").mkdir()
    meta, gitmodules, pins = {}, [], {}
    for name, spec in fields.items():
        meta[name] = {"role": spec["role"], "tagline": spec["tagline"]}
        if spec.get("pending"):
            meta[name]["pending"] = spec["pending"]
        if spec.get("pinned", True):
            gitmodules.append(f'[submodule "fields/{name}"]\n\tpath = fields/{name}\n'
                              f'\turl = https://github.com/TimeLordRaps/{name}.git\n')
            pins[name] = "b" * 40
            (root / "fields" / name).mkdir(parents=True, exist_ok=True)
        for rel, text in spec.get("files", {}).items():
            path = root / "fields" / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    (root / "registry" / "fields.json").write_text(json.dumps({"fields": meta}), encoding="utf-8")
    (root / ".gitmodules").write_text("".join(gitmodules), encoding="utf-8")
    return root, pins


HM = """-- axiom ax-commented: not a declaration
/- a block comment
axiom ax-inside-block : not counted
-/
axiom ax-one:
    a body line that says derive nothing
derive d-two:
  body
non-derive nd-three :: Set
opaque norm-four :: Realm -> Norm
  axiom ax-indented-is-not-top-level
open nd-five
lawful-word not a keyword
"""


def test_declarations_are_top_level_keywords_and_comments_are_skipped():
    found = [(d.kind, d.name, d.line) for d in fieldindex.parse_declarations(HM, "spec.hm")]
    assert found == [("axiom", "ax-one", 5), ("derive", "d-two", 7), ("non-derive", "nd-three", 9),
                     ("opaque", "norm-four", 10), ("open", "nd-five", 12)]


def test_a_non_derive_is_not_counted_as_a_derive():
    kinds = [d.kind for d in fieldindex.parse_declarations(HM, "spec.hm")]
    assert kinds.count("derive") == 1 and kinds.count("non-derive") == 1


README = """# Hyperethics

[![ci](https://example.org/badge.svg)](https://example.org)

A **self-grounded moral foundation** derived from one primitive operation.
Hypermath-adjacent: where [hypermath](https://github.com/TimeLordRaps/hypermath)
derives a formal universe from `□` under application.

## Next section

Not the summary.
"""


def test_the_readme_title_and_summary_strip_badges_links_and_emphasis():
    title, summary = fieldindex.readme_summary(README)
    assert title == "Hyperethics"
    assert summary == ("A self-grounded moral foundation derived from one primitive operation. "
                       "Hypermath-adjacent: where hypermath derives a formal universe from □ under application.")


def test_a_long_summary_is_cut_at_a_word_boundary():
    _, summary = fieldindex.readme_summary("# T\n\n" + " ".join(["word"] * 200))
    assert summary.endswith("…")
    assert summary[:-1].endswith("word")
    assert len(summary) <= fieldindex.SUMMARY_LIMIT + 1


def test_debt_rows_are_read_by_identifier_and_the_header_is_not():
    debt = """| ID | location | mechanism | status |
|---|---|---|---|
| HS-039 | `hyperoptimization` (local clone) | the repo | OPEN |
| not-an-id | x | y | z |
| HS-040 | docs/x.md, the second | more | VERIFIED_RESOLVED |
"""
    rows = fieldindex.parse_debt(debt)
    assert [(r.id, r.where) for r in rows] == [("HS-039", "hyperoptimization (local clone)"),
                                               ("HS-040", "docs/x.md, the second")]


def test_decisions_are_read_from_headings_only():
    text = "# Decisions\n\n## D01 A price is the surprisal\n\ntext\n\n### D02: second\n\n- D03 not a heading\n"
    assert fieldindex.parse_decisions(text) == [("D01", "A price is the surprisal"), ("D02", "second")]


def test_the_index_lists_every_registered_field_and_says_what_is_missing(tmp_path):
    root, pins = make_workspace(tmp_path, {
        "alpha": {"role": "foundation", "tagline": "A", "files": {
            "README.md": "# Alpha\n\nIt is alpha.\n",
            "src/a.py": "x = 1\n",
            "tests/test_a.py": "def test_one():\n    pass\n",
            "spec.hm": "axiom ax-one:\n  body\n",
            "TECHNICAL_DEBT.md": "| HS-001 | docs/a.md | m | OPEN |\n",
        }},
        "beta": {"role": "applied", "tagline": "B"},
        "gamma": {"role": "unplaced", "tagline": "", "pinned": False, "pending": "waiting on the owner"},
    })
    index = fieldindex.build_index(root, pins=pins)
    assert [e.name for e in index.entries] == ["alpha", "beta", "gamma"]
    alpha, beta, gamma = index.entries
    assert alpha.checked_out and alpha.title == "Alpha" and alpha.summary == "It is alpha."
    assert [(d.kind, d.name) for d in alpha.declarations] == [("axiom", "ax-one")]
    assert alpha.scan.test_functions == 1 and alpha.scan.files == 5
    assert [r.id for r in alpha.debt] == ["HS-001"] and alpha.notes == ()
    assert not beta.checked_out and beta.scan is None and beta.declarations == ()
    assert any("checkout is empty" in note for note in beta.notes)
    assert gamma.pin is None and not gamma.checked_out
    assert "not pinned in the index" in gamma.notes and "pending: waiting on the owner" in gamma.notes


def test_the_page_escapes_what_the_documents_say_and_makes_no_requests(tmp_path):
    hostile = "# <script>alert(1)</script>\n\n<img src=x onerror=alert(2)> and <b>bold</b> text\n"
    root, pins = make_workspace(tmp_path, {
        "alpha": {"role": "foundation", "tagline": "<img src=x onerror=alert(3)>",
                  "files": {"README.md": hostile, "tests/test_a.py": "def test_x():\n    pass\n"}},
    })
    page = fieldindex.render(fieldindex.build_index(root, pins=pins))
    assert "<script>alert(1)</script>" not in page
    assert "&lt;img src=x onerror=alert(3)&gt;" in page
    assert "<img" not in page
    assert '<link' not in page and '<script src' not in page
    assert 'src="http' not in page


def test_rendering_the_same_tree_twice_gives_the_same_bytes(tmp_path):
    root, pins = make_workspace(tmp_path, {
        "alpha": {"role": "foundation", "tagline": "A", "files": {"README.md": "# Alpha\n\nText.\n"}},
        "beta": {"role": "declared", "tagline": "B"},
    })
    first = fieldindex.render(fieldindex.build_index(root, pins=pins))
    second = fieldindex.render(fieldindex.build_index(root, pins=pins))
    assert first == second and 'id="f-alpha"' in first and 'id="f-beta"' in first


@pytest.mark.skipif(not PRESENT, reason="fields/ not checked out")
def test_the_real_workspace_lists_every_registered_field_and_counts_every_specification_file():
    index = fieldindex.build_index(ROOT)
    registered = {f.name for f in registry.load_registry(ROOT).fields}
    assert {e.name for e in index.entries} == registered
    page = fieldindex.render(index)
    assert all(f'id="f-{name}"' in page for name in registered)
    counted = sum(len(e.scan.hm) for e in index.entries if e.scan)
    assert counted == len(list(FIELDS.glob("*/**/*.hm")))
    assert "<script src" not in page and "<link" not in page


@pytest.mark.skipif(not PRESENT, reason="fields/ not checked out")
def test_the_script_writes_one_page_and_nothing_else(tmp_path):
    spec = importlib.util.spec_from_file_location("build_field_index", ROOT / "scripts" / "build_field_index.py")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    assert script.main(["--output", str(tmp_path / "out")]) == 0
    assert [p.name for p in (tmp_path / "out").iterdir()] == ["index.html"]
    assert "Hyperfields" in (tmp_path / "out" / "index.html").read_text(encoding="utf-8")
