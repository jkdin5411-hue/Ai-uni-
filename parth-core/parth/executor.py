"""Parallel step executor with retries, run limits, approval gates and Viram cancel.

Owner rules implemented here:
  * complex tasks keep working until "Viram" OR the configured limit is filled
    (max_steps / day caps);
  * destructive / new-outbound actions pause at an approval gate;
  * failures self-heal (retry with backoff) before being reported.
"""
from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .planner import Step, TaskPlan

Approver = Callable[[Step], bool]
ProgressCallback = Callable[[Step], None]


@dataclass
class ExecutionReport:
    command: str
    status: str = "completed"  # completed|completed_with_skips|completed_with_errors|
    #                          # stopped_by_viram|limit_reached|awaiting_approval
    steps: list[dict[str, Any]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    finished_at: float = 0.0

    @property
    def duration(self) -> float:
        return round(self.finished_at - self.started_at, 3)

    def counts(self) -> dict[str, int]:
        c: dict[str, int] = {}
        for s in self.steps:
            c[s["status"]] = c.get(s["status"], 0) + 1
        return c

    def summary(self) -> str:
        c = self.counts()
        parts = ", ".join(f"{v} {k}" for k, v in sorted(c.items())) or "no steps"
        return f"[{self.status}] {len(self.steps)} steps ({parts}) in {self.duration}s"


class _UnknownConnector:
    """Fallback so an unregistered connector fails gracefully, not fatally."""

    def __init__(self, name: str) -> None:
        self.name = name

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        return {"status": "error", "detail": f"no connector registered for '{self.name}'"}


class Executor:
    def __init__(
        self,
        connector_router: Callable[[str], Any],
        max_workers: int = 4,
        max_steps: int = 100,
        step_timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 0.05,
        on_progress: Optional[ProgressCallback] = None,
    ) -> None:
        self.router = connector_router
        self.max_workers = max_workers
        self.max_steps = max_steps
        self.step_timeout = step_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.on_progress = on_progress

    # ---------------------------------------------------------------- run
    def run(self, plan: TaskPlan, cancel_event: Optional[threading.Event] = None,
            approver: Optional[Approver] = None) -> ExecutionReport:
        cancel = cancel_event or threading.Event()
        report = ExecutionReport(command=plan.command)
        locks: dict[str, threading.Lock] = {s.connector: threading.Lock() for s in plan.steps}
        executed = 0
        limit_hit = False
        groups = plan.parallel_groups  # snapshot once (identity-stable)

        for group in groups:
            if cancel.is_set():
                break
            if executed >= self.max_steps:
                limit_hit = True
                break
            self._run_group(group, cancel, approver, locks)
            executed += len(group)
            if executed >= self.max_steps and group is not groups[-1]:
                limit_hit = True
                break

        # everything not executed gets marked stopped
        for s in plan.steps:
            if s.status == "pending":
                s.status = "stopped"
                s.result = {"detail": "not reached (cancelled or limit)"}

        report.steps = [s.to_dict() for s in plan.steps]
        report.finished_at = time.time()
        statuses = {s["status"] for s in report.steps}
        if cancel.is_set():
            report.status = "stopped_by_viram"
        elif limit_hit:
            report.status = "limit_reached"
        elif "failed" in statuses:
            report.status = "completed_with_errors"
        elif "skipped" in statuses or "awaiting_approval" in statuses:
            report.status = "completed_with_skips"
        else:
            report.status = "completed"
        return report

    # ---------------------------------------------------------------- group
    def _run_group(self, group: list[Step], cancel: threading.Event,
                   approver: Optional[Approver], locks: dict[str, threading.Lock]) -> None:
        if len(group) == 1:
            self._run_step(group[0], cancel, approver, locks)
            return
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(self._run_step, s, cancel, approver, locks) for s in group]
            for _ in as_completed(futures):
                pass

    # ---------------------------------------------------------------- step
    def _run_step(self, step: Step, cancel: threading.Event,
                  approver: Optional[Approver], locks: dict[str, threading.Lock]) -> None:
        if cancel.is_set():
            step.status = "stopped"
            step.result = {"detail": "Viram"}
            self._progress(step)
            return
        lock = locks[step.connector]
        with lock:  # one physical device / one app at a time
            if cancel.is_set():
                step.status = "stopped"
                step.result = {"detail": "Viram"}
                self._progress(step)
                return
            if step.approval_required:
                if approver is None:
                    step.status = "awaiting_approval"
                    step.result = {"detail": "owner approval required (gate open)"}
                    self._progress(step)
                    return
                if not approver(step):
                    step.status = "skipped"
                    step.result = {"detail": "owner declined"}
                    self._progress(step)
                    return
            attempts = 0
            last: dict[str, Any] = {}
            while attempts <= self.max_retries:
                attempts += 1
                step.status = "running"
                try:
                    res = self._call(step)
                except Exception as exc:  # noqa: BLE001 — agent must self-heal
                    last = {"status": "error", "detail": f"{type(exc).__name__}: {exc}"}
                else:
                    if isinstance(res, dict) and res.get("status") == "ok":
                        step.status = "done"
                        step.retries = attempts - 1
                        step.result = res
                        self._progress(step)
                        return
                    last = res if isinstance(res, dict) else {"status": "error", "detail": str(res)}
                time.sleep(self.retry_delay)  # backoff before self-heal retry
            step.status = "failed"
            step.retries = attempts - 1
            step.result = last
        self._progress(step)

    def _call(self, step: Step) -> dict[str, Any]:
        connector = self.router(step.connector)
        if connector is None:
            connector = _UnknownConnector(step.connector)
        fn = getattr(connector, "execute", None)
        if fn is None:
            return {"status": "error", "detail": f"connector '{step.connector}' has no execute()"}
        if self.step_timeout <= 0:
            return _as_dict(fn(step.action, step.params))
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(fn, step.action, step.params)
            return _as_dict(fut.result(timeout=self.step_timeout))

    def _progress(self, step: Step) -> None:
        if self.on_progress:
            try:
                self.on_progress(step)
            except Exception:  # noqa: BLE001 — progress must never break a run
                pass


def _as_dict(res: Any) -> dict[str, Any]:
    if isinstance(res, dict):
        return res
    if hasattr(res, "to_dict"):
        return res.to_dict()
    return {"status": "ok", "detail": str(res)}
