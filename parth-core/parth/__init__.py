"""Parth — voice-first autonomous agentic assistant (cross-platform core).

Wake word: "Parth" · Stop word: "Viram" (replaces the old "Prasthan" design).
"""
from . import control_words
from .assistant import ParthAssistant, State
from .company import CompanyOrg
from .executor import ExecutionReport, Executor
from .planner import Step, TaskPlan, TaskPlanner
from .registry import Capability, Registry
from .scheduler import Workflow, WorkflowStore

__version__ = "0.1.0"

__all__ = [
    "control_words", "ParthAssistant", "State", "CompanyOrg",
    "ExecutionReport", "Executor", "Step", "TaskPlan", "TaskPlanner",
    "Capability", "Registry", "Workflow", "WorkflowStore", "__version__",
]
