"""Workflow store: "save this and do it every day at 18:00".

Owner requirement: show or describe a workflow/prompt, say "save kar lo, aisa roz
is time par karna" → Parth stores it with an allotted time/day and executes it
automatically.
"""
from __future__ import annotations

import json
import time as _time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, time as dtime
from pathlib import Path
from typing import Any, Optional

WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@dataclass
class Workflow:
    id: str
    name: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    time: str = "08:00"          # HH:MM (24h)
    days: set[int] = field(default_factory=lambda: set(range(7)))  # 0=Mon..6=Sun
    prompt: str = ""
    created_at: float = field(default_factory=_time.time)
    last_run: Optional[str] = None  # ISO date of last run

    def __post_init__(self) -> None:
        hh, mm = self.time.split(":")
        if not (0 <= int(hh) <= 23 and 0 <= int(mm) <= 59):
            raise ValueError(f"bad time {self.time!r}, expected HH:MM")
        self.days = {d % 7 for d in self.days}

    def due(self, now: datetime) -> bool:
        if now.weekday() not in self.days:
            return False
        if now.time() < dtime(*map(int, self.time.split(":"))):
            return False
        return self.last_run != now.date().isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "steps": self.steps, "time": self.time,
            "days": sorted(self.days), "prompt": self.prompt,
            "created_at": self.created_at, "last_run": self.last_run,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Workflow":
        return cls(
            id=d["id"], name=d["name"], steps=d.get("steps", []),
            time=d.get("time", "08:00"), days=set(d.get("days", range(7))),
            prompt=d.get("prompt", ""), created_at=d.get("created_at", _time.time()),
            last_run=d.get("last_run"),
        )


class WorkflowStore:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def save(self, wf: Workflow) -> str:
        if not wf.id:
            wf.id = f"wf-{uuid.uuid4().hex[:8]}"
        self._workflows[wf.id] = wf
        return wf.id

    def add(self, name: str, steps: list[dict[str, Any]], time: str = "08:00",
            days: str | set[int] | range = "daily", prompt: str = "") -> Workflow:
        if days == "daily":
            day_set: set[int] = set(range(7))
        elif days == "weekdays":
            day_set = set(range(5))
        elif days == "weekends":
            day_set = {5, 6}
        else:
            day_set = set(days)
        wf = Workflow(id=f"wf-{uuid.uuid4().hex[:8]}", name=name, steps=steps,
                      time=time, days=day_set, prompt=prompt)
        self.save(wf)
        return wf

    def get(self, wf_id: str) -> Workflow:
        return self._workflows[wf_id]

    def list(self) -> list[Workflow]:
        return list(self._workflows.values())

    def due(self, now: datetime) -> list[Workflow]:
        return [w for w in self._workflows.values() if w.due(now)]

    def mark_run(self, wf_id: str, now: Optional[datetime] = None) -> None:
        wf = self._workflows[wf_id]
        wf.last_run = (now or datetime.now()).date().isoformat()

    def remove(self, wf_id: str) -> None:
        self._workflows.pop(wf_id, None)

    # ---------- persistence ----------
    def to_json(self) -> str:
        return json.dumps([w.to_dict() for w in self._workflows.values()],
                          ensure_ascii=False, indent=2)

    def save_json(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.to_json(), encoding="utf-8")
        return p

    def load_json(self, path: str | Path) -> int:
        p = Path(path)
        for d in json.loads(p.read_text(encoding="utf-8")):
            wf = Workflow.from_dict(d)
            self.save(wf)
        return len(self._workflows)
