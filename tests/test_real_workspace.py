"""The repository's own wiring, against the real `fields/` checkout.

Absent checkout is a visible skip unless HYPERSTRATUM_REQUIRE_FIELDS=1, which
the wiki workflow sets: there, absence is a failure, not a quiet pass.
"""
import os
import pathlib

import pytest

from hyperstratum import registry

ROOT = pathlib.Path(__file__).resolve().parents[1]
present = (ROOT / "fields").is_dir() and any((ROOT / "fields").iterdir()) if (ROOT / "fields").exists() else False


def test_fields_are_checked_out_when_required():
    if os.environ.get("HYPERSTRATUM_REQUIRE_FIELDS") == "1":
        assert present, "fields/ is empty: checkout with submodules: true"
    elif not present:
        pytest.skip("fields/ not checked out (set HYPERSTRATUM_REQUIRE_FIELDS=1 to require)")


@pytest.mark.skipif(not present, reason="fields/ not checked out")
def test_real_registry_has_no_errors():
    reg = registry.load_registry(ROOT)
    errors = [p for p in reg.problems() if p.severity == "error"]
    assert not errors, errors
