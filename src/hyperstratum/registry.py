"""The set of hyperfields, joined from three sources that must agree.

* `.gitmodules`           -- which repositories are pinned, and where from.
* the index (gitlinks)    -- the exact commit each one is pinned at.
* `registry/fields.json`  -- what each one *is* (role, tagline), which git
                             cannot know.

A repository present in one source and absent from another is reported, never
silently dropped: the wiki's coverage claim is only as good as this join.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
from dataclasses import dataclass, field

FIELDS_DIR = "fields"
OWNER = "TimeLordRaps"


@dataclass(frozen=True)
class Problem:
    code: str
    severity: str  # "error" | "warning" | "info"
    subject: str
    detail: str

    def as_dict(self) -> dict:
        return {"code": self.code, "severity": self.severity, "subject": self.subject,
                "detail": self.detail}


@dataclass(frozen=True)
class Field:
    name: str
    role: str
    tagline: str
    url: str | None
    pin: str | None
    path: pathlib.Path
    pending: str | None = None
    registered: bool = True

    @property
    def repo_url(self) -> str:
        base = self.url or f"https://github.com/{OWNER}/{self.name}"
        return base[:-4] if base.endswith(".git") else base

    def permalink(self, path: str = "", lines: str | None = None) -> str:
        """URL of `path` at the *pinned* commit: stable, not 'whatever main is now'."""
        ref = self.pin or "HEAD"
        url = f"{self.repo_url}/blob/{ref}/{path}" if path else f"{self.repo_url}/tree/{ref}"
        return f"{url}#{lines}" if lines else url


@dataclass
class Registry:
    root: pathlib.Path
    fields: list[Field]
    _problems: list[Problem] = field(default_factory=list)

    @property
    def by_name(self) -> dict[str, Field]:
        return {f.name: f for f in self.fields}

    def problems(self) -> list[Problem]:
        return list(self._problems)


def parse_gitmodules(text: str) -> list[dict]:
    entries: list[dict] = []
    current: dict | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("[submodule"):
            current = {"name": line.split('"')[1] if '"' in line else line}
            entries.append(current)
        elif current is not None and "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            current[key.strip()] = value.strip()
    return entries


def git_pins(root: pathlib.Path) -> dict[str, str]:
    """Pinned commit per `fields/<name>`, read from the index (mode 160000)."""
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-s", "--", FIELDS_DIR],
        capture_output=True, text=True, check=True,
    ).stdout
    pins: dict[str, str] = {}
    for line in out.splitlines():
        meta, _, path = line.partition("\t")
        mode, sha, _stage = meta.split()
        if mode == "160000":
            pins[pathlib.PurePosixPath(path).name] = sha
    return pins


def checkout_heads(registry: Registry) -> dict[str, str]:
    heads: dict[str, str] = {}
    for f in registry.fields:
        if not f.path.is_dir():
            continue
        done = subprocess.run(["git", "-C", str(f.path), "rev-parse", "HEAD"],
                              capture_output=True, text=True)
        if done.returncode == 0 and (f.path / ".git").exists():
            heads[f.name] = done.stdout.strip()
    return heads


def load_registry(root: pathlib.Path, pins: dict[str, str] | None = None) -> Registry:
    root = pathlib.Path(root)
    gm_file = root / ".gitmodules"
    modules = parse_gitmodules(gm_file.read_text(encoding="utf-8")) if gm_file.exists() else []
    meta_file = root / "registry" / "fields.json"
    meta = (json.loads(meta_file.read_text(encoding="utf-8")).get("fields", {})
            if meta_file.exists() else {})
    if pins is None:
        pins = git_pins(root)

    problems: list[Problem] = []
    submodules = {pathlib.PurePosixPath(m.get("path", m["name"])).name: m for m in modules}
    names = sorted(set(meta) | set(submodules))
    fields: list[Field] = []
    for name in names:
        info = meta.get(name)
        mod = submodules.get(name)
        pending = (info or {}).get("pending")
        if info is None:
            problems.append(Problem("UNREGISTERED_SUBMODULE", "warning", name,
                                    "pinned in .gitmodules but has no entry in registry/fields.json"))
        if mod is None:
            if pending:
                problems.append(Problem("PENDING_PIN", "info", name, str(pending)))
            else:
                problems.append(Problem("MISSING_SUBMODULE", "error", name,
                                        "registered, not pending, but absent from .gitmodules"))
        else:
            if name not in pins:
                problems.append(Problem("NO_GITLINK", "error", name,
                                        "in .gitmodules but the index has no commit pinned for it"))
            if not (root / FIELDS_DIR / name).is_dir():
                problems.append(Problem("NO_CHECKOUT", "error", name,
                                        f"{FIELDS_DIR}/{name} is not checked out"))
        fields.append(Field(
            name=name,
            role=(info or {}).get("role", "unclassified"),
            tagline=(info or {}).get("tagline", ""),
            url=mod.get("url") if mod else None,
            pin=pins.get(name) if mod else None,
            path=root / FIELDS_DIR / name,
            pending=pending if mod is None else None,
            registered=info is not None,
        ))
    return Registry(root=root, fields=fields, _problems=problems)
