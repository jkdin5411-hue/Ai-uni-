"""ParthAssistant — the voice state machine.

Implements the owner's interaction rules exactly:
  * wake word "Parth" arms listening;
  * barge-in: if the user starts speaking while Parth speaks, Parth goes silent
    and listens;
  * "Viram" (replaces "Prasthan") — stops speech, pauses/stops work, ends the
    session;
  * start once, keep running: the assistant object persists independent of any
    UI; on device this maps to a foreground service that survives app-back and
    auto-starts on boot;
  * after finishing work it reports via on_result (the app screen and/or a
    floating window on device).
"""
from __future__ import annotations

import threading
from enum import Enum
from typing import Any, Callable, Optional

from . import control_words as cw
from .company import CompanyOrg
from .executor import ExecutionReport, Executor
from .planner import TaskPlanner
from .registry import Registry
from .scheduler import WorkflowStore


class State(str, Enum):
    DORMANT = "dormant"          # running in background, only wake-word listening
    LISTENING = "listening"      # armed, capturing the owner's utterance
    SPEAKING = "speaking"        # talking (interruptible — barge-in)
    PLANNING = "planning"        # decomposing the command
    EXECUTING = "executing"      # running multi-step work (stoppable via Viram)
    REPORTING = "reporting"      # showing the result


SayCallback = Callable[[str], None]
ResultCallback = Callable[[Any], None]
Approver = Callable[[Any], bool]


class ParthAssistant:
    """One instance lives for the whole device session (run-once, run-forever)."""

    def __init__(
        self,
        planner: Optional[TaskPlanner] = None,
        executor: Optional[Executor] = None,
        registry: Optional[Registry] = None,
        company: Optional[CompanyOrg] = None,
        workflows: Optional[WorkflowStore] = None,
        on_say: Optional[SayCallback] = None,
        on_result: Optional[ResultCallback] = None,
        on_listen: Optional[SayCallback] = None,
    ) -> None:
        self.planner = planner or TaskPlanner()
        self.registry = registry or Registry()
        self.company = company or CompanyOrg()
        self.workflows = workflows or WorkflowStore()
        self.executor = executor or Executor(connector_router=lambda name: None)
        self.on_say = on_say
        self.on_result = on_result
        self.on_listen = on_listen

        self.state = State.DORMANT
        self.background = True  # survives app-back; on device: foreground service
        self._session_active = False
        self._speech_interrupted = False
        self._cancel = threading.Event()
        self._mutex = threading.Lock()
        self.last_report: Optional[ExecutionReport] = None

    # ------------------------------------------------------------ wake / viram
    def wake(self) -> dict[str, Any]:
        """Wake word 'Parth' heard (or app opened)."""
        with self._mutex:
            self._session_active = True
            self.state = State.LISTENING
        if self.on_listen:
            self.on_listen("listening…")
        return {"event": "wake", "state": self.state.value}

    def viram(self, reason: str = "owner said Viram") -> dict[str, Any]:
        """STOP word — silence speech, cancel work, end the session."""
        self._speech_interrupted = True
        self._cancel.set()
        with self._mutex:
            self._session_active = False
            self.state = State.DORMANT
        out = {"event": "viram", "reason": reason, "state": self.state.value}
        self._cancel = threading.Event()  # re-arm for the next session
        return out

    # ------------------------------------------------------------ barge-in
    def user_started_speaking(self) -> bool:
        """VAD event: the owner began speaking. If Parth is talking → go silent."""
        if self.state == State.SPEAKING:
            self._speech_interrupted = True
            return True
        return False

    def say(self, text: str) -> dict[str, Any]:
        """Speak, but in chunks so barge-in can silence Parth mid-utterance."""
        with self._mutex:
            self.state = State.SPEAKING
        self._speech_interrupted = False
        spoken: list[str] = []
        for word in text.split():
            if self._speech_interrupted or self._cancel.is_set():
                break
            spoken.append(word)
            if self.on_say:
                self.on_say(word if len(spoken) == 1 else " " + word)
        interrupted = self._speech_interrupted or self._cancel.is_set()
        with self._mutex:
            if interrupted:
                self.state = State.LISTENING  # silenced → listen to the owner
            else:
                self.state = State.LISTENING if self._session_active else State.DORMANT
        return {"spoken": " ".join(spoken), "interrupted": interrupted,
                "state": self.state.value}

    # ------------------------------------------------------------ hearing
    def hear(self, text: str) -> dict[str, Any]:
        """A complete utterance from the STT engine."""
        if cw.contains_stop_word(text):
            return self.viram(reason=f"stop word in: {text!r}")
        if cw.contains_wake_word(text):
            command = cw.strip_wake_word(text)
            if not command.strip():
                return self.wake()
            if not self._session_active:
                self.wake()
            return self.process(command)
        if self.state == State.LISTENING:
            return self.process(text)
        return {"event": "ignored", "reason": "not listening; say 'Parth' first",
                "state": self.state.value}

    # ------------------------------------------------------------ processing
    def process(self, command: str, approver: Optional[Approver] = None) -> dict[str, Any]:
        dept, agent, why = self.company.route(command)
        with self._mutex:
            self.state = State.PLANNING
        plan = self.planner.decompose(command)
        with self._mutex:
            self.state = State.EXECUTING
        report = self.executor.run(plan, cancel_event=self._cancel, approver=approver)
        self.last_report = report
        with self._mutex:
            self.state = State.REPORTING
        self.show_result(report)
        with self._mutex:
            self.state = State.LISTENING if self._session_active else State.DORMANT
        return {"event": "task_complete", "department": dept, "agent": agent.name,
                "route_reason": why, "report": report}

    # ------------------------------------------------------------ results
    def show_result(self, report: ExecutionReport) -> None:
        """On device: opens the Parth app screen AND/OR a floating window."""
        if self.on_result:
            self.on_result(report)
        else:
            print("\n┌─ PARTH RESULT " + "─" * 40)
            print(report.summary())
            print("└" + "─" * 56)

    # ------------------------------------------------------------ save & repeat
    def save_workflow(self, name: str, command_or_steps, time: str = "08:00",
                      days="daily") -> dict[str, Any]:
        """'Parth, save kar lo — roz subah 8 baje aisa hi karna.'"""
        if isinstance(command_or_steps, str):
            plan = self.planner.decompose(command_or_steps)
            steps = [s.to_dict() for s in plan.steps]
            prompt = command_or_steps
        else:
            steps = list(command_or_steps)
            prompt = ""
        wf = self.workflows.add(name=name, steps=steps, time=time, days=days, prompt=prompt)
        return {"event": "workflow_saved", "id": wf.id, "name": wf.name,
                "time": wf.time, "steps": len(wf.steps)}

    # ------------------------------------------------------------ introspection
    def status(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "background": self.background,
            "wake_word": cw.WAKE_WORD,
            "stop_word": cw.STOP_WORD,
            "capabilities": self.registry.count(),
            "workflows": len(self.workflows.list()),
            "last_report": self.last_report.summary() if self.last_report else None,
        }
