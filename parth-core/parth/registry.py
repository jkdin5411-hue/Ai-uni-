"""Capability registry: Skills, Agents, Tools — create + import + export + add-more.

Every capability kind supports the four operations the owner required:
  * Create   – `Registry.create(kind=..., ...)`
  * Import   – `Registry.import_package(path)` (.parth.json) or from a manifest dict
  * Export   – `Registry.export(id, path)`
  * Add More – `Registry.add(capability)` (e.g. bulk from catalog or marketplace)
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

KINDS = ("skill", "tool", "agent")
FORMAT_VERSION = 1
PACKAGE_EXT = ".parth.json"


@dataclass
class Capability:
    id: str
    kind: str  # skill | tool | agent
    name: str
    description: str = ""
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    # skills: declarative step list (same shape as planner Step params)
    steps: list[dict[str, Any]] = field(default_factory=list)
    # agents: role prompt + allowed tool ids
    role: str = ""
    tools: list[str] = field(default_factory=list)
    # tools: optional local callable (never serialized)
    handler: Optional[Callable[..., Any]] = field(default=None, repr=False)

    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}, got {self.kind!r}")
        if not self.id or not self.name:
            raise ValueError("Capability needs a non-empty id and name")

    # ---------- serialization ----------
    def to_manifest(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tags": list(self.tags),
            "steps": [dict(s) for s in self.steps],
            "role": self.role,
            "tools": list(self.tools),
            "created_at": self.created_at,
        }

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "Capability":
        errors = validate_manifest(manifest)
        if errors:
            raise ValueError("invalid manifest: " + "; ".join(errors))
        fields = {
            k: manifest[k]
            for k in ("id", "kind", "name", "description", "version", "tags", "steps", "role", "tools")
            if k in manifest
        }
        return cls(**fields)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    for key in ("id", "kind", "name"):
        if not manifest.get(key):
            errors.append(f"missing required field: {key}")
    if manifest.get("kind") not in KINDS:
        errors.append(f"kind must be one of {KINDS}")
    if manifest.get("steps") is not None and not isinstance(manifest["steps"], list):
        errors.append("steps must be a list")
    if manifest.get("tags") is not None and not isinstance(manifest["tags"], list):
        errors.append("tags must be a list")
    return errors


class Registry:
    """In-memory registry with import/export. Persist via to_json/save_json."""

    def __init__(self) -> None:
        self._items: dict[str, Capability] = {}

    # ---------- core ops ----------
    def add(self, cap: Capability, overwrite: bool = False) -> str:
        if not isinstance(cap, Capability):
            raise TypeError("expected a Capability")
        if cap.id in self._items and not overwrite:
            raise KeyError(f"capability id already registered: {cap.id}")
        self._items[cap.id] = cap
        return cap.id

    def create(self, kind: str, **kwargs: Any) -> Capability:
        """Owner creates a brand-new skill/agent/tool in-app."""
        cap = Capability(kind=kind, **kwargs)
        return self.add(cap) and cap or cap  # add may raise on duplicates

    def get(self, cap_id: str) -> Capability:
        return self._items[cap_id]

    def list(self, kind: Optional[str] = None, tag: Optional[str] = None) -> list[Capability]:
        out = list(self._items.values())
        if kind:
            out = [c for c in out if c.kind == kind]
        if tag:
            out = [c for c in out if tag in c.tags]
        return out

    def remove(self, cap_id: str) -> None:
        self._items.pop(cap_id, None)

    def count(self, kind: Optional[str] = None) -> int:
        return len(self.list(kind=kind))

    # ---------- import / export ----------
    def export(self, cap_id: str, path: str | Path) -> Path:
        cap = self._items[cap_id]
        package = {"parth_package": cap.kind, "format_version": FORMAT_VERSION}
        package.update(cap.to_manifest())
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    def import_package(self, path: str | Path, overwrite: bool = False) -> Capability:
        p = Path(path)
        package = json.loads(p.read_text(encoding="utf-8"))
        return self.import_manifest(package, overwrite=overwrite, source=str(p))

    def import_manifest(self, package: dict[str, Any], overwrite: bool = False, source: str = "") -> Capability:
        kind = package.get("parth_package") or package.get("kind")
        if kind not in KINDS:
            raise ValueError(f"{source or 'package'}: parth_package must be one of {KINDS}")
        manifest = {k: v for k, v in package.items() if k not in ("parth_package", "format_version")}
        manifest["kind"] = kind
        cap = Capability.from_manifest(manifest)
        self.add(cap, overwrite=overwrite)
        return cap

    # ---------- persistence ----------
    def to_json(self) -> str:
        return json.dumps([c.to_manifest() for c in self._items.values()], ensure_ascii=False, indent=2)

    def save_json(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.to_json(), encoding="utf-8")
        return p

    def load_json(self, path: str | Path, overwrite: bool = False) -> int:
        p = Path(path)
        items = json.loads(p.read_text(encoding="utf-8"))
        for manifest in items:
            self.import_manifest({"parth_package": manifest["kind"], **manifest}, overwrite=overwrite)
        return len(items)
