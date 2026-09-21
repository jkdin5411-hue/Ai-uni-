"""Connector base — every connector is DRY-RUN SAFE by default.

Real integrations (actual UI automation via Shizuku/a11y on Android, real APIs)
flip `dry_run=False` after the owner enables the connector in-app. This keeps
the repo safe to run, test and demo anywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionResult:
    connector: str
    action: str
    status: str  # ok | error
    detail: str = ""
    dry_run: bool = True
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector": self.connector, "action": self.action, "status": self.status,
            "detail": self.detail, "dry_run": self.dry_run, "data": self.data,
        }


class Connector:
    """Subclass and define `actions` + optional `_execute_real`."""

    name = "base"

    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def actions(self) -> dict[str, str]:
        return getattr(self, "ACTIONS", {})

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        acts = self.actions()
        if action not in acts:
            return ActionResult(self.name, action, "error",
                                f"unknown action {action!r} (known: {sorted(acts)})").to_dict()
        if self.dry_run:
            return ActionResult(
                self.name, action, "ok",
                f"[DRY-RUN] {self.name}.{action} → {acts[action]}",
                dry_run=True,
                data={"params": params},
            ).to_dict()
        return self._execute_real(action, params)

    def _execute_real(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        return ActionResult(self.name, action, "error",
                            "real mode not implemented for this connector yet").to_dict()


class ConnectorRouter:
    def __init__(self, connectors: dict[str, Connector]) -> None:
        self.connectors = connectors

    def get(self, name: str) -> Connector | None:
        return self.connectors.get(name)

    def names(self) -> list[str]:
        return sorted(self.connectors)
