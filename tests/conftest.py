"""Fixture workspace: a hyperstratum root with fake hyperfield checkouts.

Nothing here touches the network or git; pins are injected, so the unit tests
exercise the wiki's own logic and not the transport that fills `fields/`.
"""
from __future__ import annotations

import json
import pathlib

import pytest

CANONICAL = """# Canonical Definitions

## Universe

```txt
Universe = the whole containing order.
```

## Hyperfield

```txt
Hyperfield = recursively connected distribution of values across base forms and meta-forms.
```

## Hypernode

```txt
Hypernode = local recursive form-point.
```

## Person-hypernode

```txt
Person-hypernode = recursive self-perceiving hypernode inside a society-of-minds.
```

## Master sentence

```txt
A hyperrepresentation is a recursive-graph of hypernodes.
```
"""

CHAIN = """# Dependency Graph

## Construction order

```txt
Universe / Reality
        ↓
Hyperfield
        ↓
Hypernode
```

## Interpretive order

```txt
Hyperrepresentation(Universe)
```
"""

PINS = {"alpha": "a" * 40, "beta": "b" * 40}


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def root(tmp_path: pathlib.Path) -> pathlib.Path:
    write(tmp_path / "specs/canonical-definitions.md", CANONICAL)
    write(tmp_path / "specs/dependency-graph.md", CHAIN)
    write(
        tmp_path / ".gitmodules",
        "\n".join(
            f'[submodule "fields/{n}"]\n\tpath = fields/{n}\n'
            f"\turl = https://github.com/TimeLordRaps/{n}.git\n\tbranch = main\n"
            for n in PINS
        ),
    )
    write(
        tmp_path / "registry/fields.json",
        json.dumps(
            {
                "fields": {
                    "alpha": {"role": "hyperfield", "tagline": "the first field"},
                    "beta": {"role": "hyperfield", "tagline": "the second field"},
                    "gamma": {
                        "role": "hyperfield",
                        "tagline": "no commits yet",
                        "pending": "repository has no commit on main",
                    },
                }
            }
        ),
    )
    write(
        tmp_path / "fields/alpha/README.md",
        "# Alpha\n\n![badge](x.svg)\n\nAlpha studies the Hyperfield of toy things.\n"
        "It cites [beta](https://github.com/TimeLordRaps/beta/blob/"
        + "b" * 40
        + "/docs/one.md#L2).\n\n[OPEN] Is a hypernode a field?\n",
    )
    write(
        tmp_path / "fields/alpha/core.py",
        '"""Core."""\n\nclass Thing:\n    """A toy thing."""\n\n'
        "def _private():\n    pass\n\ndef visible(x):\n    \"\"\"Do it.\n\n    More.\"\"\"\n    return x\n",
    )
    write(
        tmp_path / "fields/alpha/FIELD.json",
        json.dumps({"scope": "Toys.", "classification": "FRAME", "exclusions": ["No cats."]}),
    )
    write(
        tmp_path / "fields/beta/docs/one.md",
        "# One\n\nLine two mentions a person-hypernode and a hypernode.\n"
        "Line three: [FORM] [FRAME] [FRAME] tags. See alpha.\nLine four.\n",
    )
    write(tmp_path / "fields/beta/README.md", "# Beta\n\nBeta body, no terms.\n")
    write(
        tmp_path / "fields/beta/Thm.lean",
        "theorem foo : True := trivial\n-- sorry in a comment\ndef bar := sorry\n",
    )
    write(tmp_path / "fields/beta/node_modules/junk.md", "hypernode hypernode\n")
    write(tmp_path / "fields/beta/.lake/junk.md", "hypernode\n")
    return tmp_path
