import json
import pathlib
import posixpath
import re

from hyperstratum import build

from conftest import PINS, write


def _build(root, tmp_path, **kw):
    out = tmp_path / "site"
    model = build.build_site(root, out, pins=PINS, blob_lookup=lambda s, p: None, **kw)
    return out, model


def test_site_has_term_field_open_and_index_pages(root, tmp_path):
    out, model = _build(root, tmp_path)
    for rel in ["index.html", "terms/hyperfield.html", "terms/person-hypernode.html",
                "fields/alpha.html", "fields/beta.html", "open.html", "audit.html", "wiki.json"]:
        assert (out / rel).is_file(), rel
    term = (out / "terms/hypernode.html").read_text()
    assert "local recursive form-point" in term
    assert "https://github.com/TimeLordRaps/beta/blob/" + "b" * 40 + "/docs/one.md#L3" in term
    assert "fields/beta.html" in term.replace("../", "")
    field = (out / "fields/alpha.html").read_text()
    assert "Toys." in field and "No cats." in field and "visible" in field
    assert "pending" in (out / "index.html").read_text().lower()  # gamma is named, not hidden


def test_wiki_json_is_deterministic(root, tmp_path):
    a, _ = _build(root, tmp_path)
    first = (a / "wiki.json").read_bytes()
    import shutil
    shutil.rmtree(a)
    b, _ = _build(root, tmp_path)
    assert (b / "wiki.json").read_bytes() == first
    data = json.loads(first)
    assert data["schema"] == "hyperstratum-wiki/1"
    assert {f["name"] for f in data["fields"]} == {"alpha", "beta", "gamma"}


def test_every_relative_link_in_the_site_resolves(root, tmp_path):
    out, _ = _build(root, tmp_path)
    bad = []
    for page in out.rglob("*.html"):
        for target in re.findall(r'(?:href|src)="([^"]+)"', page.read_text()):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            path = posixpath.normpath(posixpath.join(page.parent.as_posix(), target.split("#")[0]))
            if not pathlib.Path(path).exists():
                bad.append((page.relative_to(out).as_posix(), target))
    assert not bad, bad


def test_field_content_is_escaped(root, tmp_path):
    write(root / "fields/beta/docs/evil.md", "# x\n\nhypernode <script>alert(1)</script>\n")
    out, _ = _build(root, tmp_path)
    html = (out / "terms/hypernode.html").read_text() + (out / "fields/beta.html").read_text()
    assert "<script>alert" not in html


def test_authored_pages_expand_refs_and_primer_renders(root, tmp_path):
    write(root / "wiki/note.md", "# Note\n\nSee [[Hyperfield]] and\n\n[[beta:docs/one.md#L3-L3]]\n")
    write(root / "docs/00-x.md", "# X\n\nLink to [defs](../specs/canonical-definitions.md).\n")
    out, model = _build(root, tmp_path)
    page = (out / "pages/note.html").read_text()
    assert "../terms/hyperfield.html" in page and "Line two mentions" in page
    primer = (out / "primer/docs/00-x.html").read_text()
    assert "specs/canonical-definitions.html" in primer


def test_unresolved_ref_in_authored_page_is_a_problem(root, tmp_path):
    write(root / "wiki/bad.md", "# Bad\n\n[[beta:gone.md]]\n")
    _, model = _build(root, tmp_path)
    assert any(p["code"] == "MISSING_FILE" for p in model["problems"])
