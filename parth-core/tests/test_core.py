"""Parth core test suite — stdlib unittest, no dependencies.

Run:  python3 -m unittest discover -s tests -v     (from parth-core/)
or:   python3 tests/test_core.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parth import control_words as cw
from parth.assistant import ParthAssistant, State
from parth.catalog import build_catalog, catalog_size, register_catalog
from parth.company import CompanyOrg
from parth.connectors import default_router
from parth.connectors.base import Connector
from parth.executor import Executor
from parth.planner import Step, TaskPlan, TaskPlanner
from parth.registry import Capability, Registry
from parth.scheduler import WorkflowStore

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"


def make_router():
    return default_router(dry_run=True)


def make_executor(**kw):
    kw.setdefault("retry_delay", 0)
    return Executor(connector_router=make_router().get, **kw)


def make_assistant(**kw):
    kw.setdefault("on_result", lambda r: None)  # keep test output clean
    return ParthAssistant(executor=make_executor(), **kw)


# --------------------------------------------------------------------- words
class TestControlWords(unittest.TestCase):
    def test_wake_word_variants(self):
        for t in ("Parth", "parth", "Paarth", "पार्थ", "Parth!", "Parth, WhatsApp खोलो"):
            self.assertTrue(cw.contains_wake_word(t), t)

    def test_stop_word_variants(self):
        for t in ("viram", "Viram", "विराम", "viraam", "…viram।", "ok viram"):
            self.assertTrue(cw.contains_stop_word(t), t)

    def test_prasthan_is_removed(self):
        # owner decision: "Prasthan" replaced by "Viram" — must trigger nothing
        for t in ("prasthan", "Prasthan", "प्रस्थान"):
            self.assertFalse(cw.contains_wake_word(t), t)
            self.assertFalse(cw.contains_stop_word(t), t)
        self.assertTrue(cw.is_deprecated_word("prasthan"))

    def test_plain_text_triggers_nothing(self):
        self.assertFalse(cw.contains_wake_word("WhatsApp खोलो"))
        self.assertFalse(cw.contains_stop_word("video upload करो"))

    def test_strip_wake_word(self):
        self.assertEqual(cw.strip_wake_word("Parth WhatsApp खोलो"), "WhatsApp खोलो")
        self.assertEqual(cw.strip_wake_word("पार्थ Gmail खोलो"), "Gmail खोलो")
        self.assertEqual(cw.strip_wake_word("no wake word here"), "no wake word here")


# ------------------------------------------------------------------ registry
class TestRegistry(unittest.TestCase):
    def test_create_and_count(self):
        r = Registry()
        r.create("skill", id="my-skill", name="My Skill", description="owner-made")
        r.create("agent", id="my-agent", name="My Agent", role="helper")
        r.create("tool", id="my-tool", name="My Tool")
        self.assertEqual(r.count(), 3)
        self.assertEqual(r.count("skill"), 1)

    def test_invalid_kind_rejected(self):
        with self.assertRaises(ValueError):
            Capability(id="x", kind="robot", name="X")

    def test_duplicate_id_rejected(self):
        r = Registry()
        r.create("skill", id="dup", name="A")
        with self.assertRaises(KeyError):
            r.create("skill", id="dup", name="B")

    def test_export_import_roundtrip(self):
        r = Registry()
        r.create("skill", id="round", name="Round", steps=[{"title": "one"}], tags=["t"])
        with tempfile.TemporaryDirectory() as td:
            p = r.export("round", Path(td) / "round.parth.json")
            r2 = Registry()
            cap = r2.import_package(p)
            self.assertEqual(cap.id, "round")
            self.assertEqual(cap.steps, [{"title": "one"}])
            self.assertEqual(r2.count(), 1)

    def test_import_example_packages(self):
        r = Registry()
        packages = sorted(SKILLS_DIR.glob("*.parth.json"))
        self.assertGreaterEqual(len(packages), 2, "example skill packages missing")
        for pkg in packages:
            cap = r.import_package(pkg)
            self.assertEqual(cap.kind, "skill")
            self.assertTrue(cap.steps)

    def test_import_bad_package_rejected(self):
        r = Registry()
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.parth.json"
            p.write_text('{"parth_package": "skill", "id": "x"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                r.import_package(p)


# ------------------------------------------------------------------- planner
class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = TaskPlanner()

    def test_whatsapp_read_reply(self):
        plan = self.planner.decompose(
            "WhatsApp खोलो और देखो किसका मैसेज आया है, उनको रिप्लाई कर दो")
        actions = {(s.connector, s.action) for s in plan.steps}
        self.assertIn(("whatsapp", "open"), actions)
        self.assertIn(("whatsapp", "read_messages"), actions)
        self.assertIn(("whatsapp", "reply"), actions)

    def test_gmail_delete_needs_approval(self):
        plan = self.planner.decompose(
            "Gmail खोलो, सारे emails देखो, important रहने दो और बाकी delete कर दो")
        actions = {(s.connector, s.action): s for s in plan.steps}
        self.assertIn(("gmail", "read_emails"), actions)
        del_step = actions[("gmail", "delete_unimportant")]
        self.assertTrue(del_step.approval_required, "deletion must be approval-gated")

    def test_mega_command_multi_app(self):
        mega = (
            "WhatsApp खोलो और देखो किसका मैसेज आया है, उनको रिप्लाई कर दो। "
            "फिर Gmail खोलो, सारे emails देखो, important रहने दो और बाकी delete कर दो। "
            "फिर free AI platform पे login करके video बनाओ और download कर लेना। "
            "फिर YouTube पर video upload करो और ChatGPT से thumbnail बनाओ। "
            "फिर Instagram खोलो, followers को message भेजो, comments का reply करो, "
            "post करो और story लगाओ। "
            "फिर फोन की unwanted storage साफ करो। "
            "फिर browser में 50 dental clinics खोजो, website बनाकर Netlify पर deploy करो। "
            "फिर Google Cloud पर AI model training start करो। "
            "पूरा होने पर मेरे दूसरे phone पर call लगाकर report करना।"
        )
        plan = self.planner.decompose(mega)
        self.assertGreaterEqual(len(plan.steps), 15, f"got {len(plan.steps)}")
        ids = [s.id for s in plan.steps]
        self.assertEqual(len(ids), len(set(ids)), "step ids must be unique")
        connectors = {s.connector for s in plan.steps}
        for expected in ("whatsapp", "gmail", "youtube", "instagram", "aivideo",
                         "thumbnail", "phone", "browser", "leadfinder", "netlify", "gcloud"):
            self.assertIn(expected, connectors, f"missing connector {expected}")
        self.assertTrue(any(s.approval_required for s in plan.steps))
        groups = plan.parallel_groups
        self.assertTrue(all(s.phase == 0 for s in groups[0]), "first group must be phase 0")
        self.assertEqual([g[0].phase for g in groups], sorted(g[0].phase for g in groups))
        # every step has params with the originating utterance
        self.assertTrue(all(s.params.get("utterance") is not None for s in plan.steps))

    def test_unknown_command_falls_back_to_ceo_query(self):
        plan = self.planner.decompose("kuch bhi random bolo")
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].connector, "assistant")

    def test_storage_cleanup_is_approval_gated(self):
        plan = self.planner.decompose("फोन की unwanted storage साफ करो, पहले मुझे बताना")
        clean = [s for s in plan.steps if s.action == "clean_storage"]
        self.assertTrue(clean and clean[0].approval_required)


# ------------------------------------------------------------------ executor
class TestExecutor(unittest.TestCase):
    def _plan(self, *specs):
        steps = [Step(id=f"s{i+1}", title=f"t{i+1}", connector=c, action=a, phase=ph,
                      approval_required=ap) for i, (c, a, ph, ap) in enumerate(specs)]
        return TaskPlan(command="test", steps=steps)

    def test_completed(self):
        plan = self._plan(("whatsapp", "open", 0, False), ("whatsapp", "read_messages", 1, False))
        report = make_executor().run(plan)
        self.assertEqual(report.status, "completed")
        self.assertTrue(all(s["status"] == "done" for s in report.steps))
        self.assertTrue(all(s["result"].get("dry_run") for s in report.steps))

    def test_viram_stops_work(self):
        import threading
        cancel = threading.Event()

        def progress(step):
            if step.id == "s2":
                cancel.set()  # owner says Viram mid-run

        plan = self._plan(("whatsapp", "open", 0, False), ("whatsapp", "read_messages", 1, False),
                          ("whatsapp", "reply", 2, False))
        report = make_executor(on_progress=progress).run(plan, cancel_event=cancel)
        self.assertEqual(report.status, "stopped_by_viram")
        by_id = {s["id"]: s["status"] for s in report.steps}
        self.assertEqual(by_id["s3"], "stopped")

    def test_limit_reached(self):
        plan = self._plan(("whatsapp", "open", 0, False), ("gmail", "open", 0, False),
                          ("whatsapp", "read_messages", 1, False))
        report = make_executor(max_steps=2).run(plan)
        self.assertEqual(report.status, "limit_reached")

    def test_approval_denied_skips(self):
        plan = self._plan(("whatsapp", "send_group_message", 2, True))
        report = make_executor().run(plan, approver=lambda s: False)
        self.assertEqual(report.status, "completed_with_skips")
        self.assertEqual(report.steps[0]["status"], "skipped")

    def test_no_approver_awaits(self):
        plan = self._plan(("gmail", "delete_unimportant", 2, True))
        report = make_executor().run(plan, approver=None)
        self.assertEqual(report.steps[0]["status"], "awaiting_approval")

    def test_self_healing_retries(self):
        class Flaky(Connector):
            name = "flaky"
            ACTIONS = {"flail": "fails twice then recovers"}

            def __init__(self):
                super().__init__(dry_run=False)
                self.calls = 0

            def _execute_real(self, action, params):
                self.calls += 1
                if self.calls < 3:
                    return {"status": "error", "detail": "boom"}
                return {"status": "ok", "detail": "recovered"}

        flaky = Flaky()
        plan = self._plan(("flaky", "flail", 0, False))
        report = Executor(connector_router=lambda n: flaky, retry_delay=0).run(plan)
        self.assertEqual(report.status, "completed")
        self.assertEqual(report.steps[0]["status"], "done")
        self.assertEqual(report.steps[0]["retries"], 2)
        self.assertEqual(flaky.calls, 3)

    def test_unknown_connector_fails_gracefully(self):
        plan = self._plan(("nonexistent", "whatever", 0, False))
        report = make_executor(max_retries=0).run(plan)
        self.assertEqual(report.status, "completed_with_errors")
        self.assertEqual(report.steps[0]["status"], "failed")

    def test_parallel_group_runs(self):
        plan = self._plan(("whatsapp", "open", 0, False), ("gmail", "open", 0, False),
                          ("youtube", "open", 0, False), ("telegram", "open", 0, False))
        report = make_executor().run(plan)
        self.assertEqual(report.status, "completed")
        self.assertEqual(len(report.steps), 4)


# ----------------------------------------------------------------- scheduler
class TestScheduler(unittest.TestCase):
    def test_due_logic(self):
        store = WorkflowStore()
        store.add("morning-brief", steps=[{"title": "brief"}], time="08:00", days="daily")
        now = datetime(2026, 9, 21, 8, 0)  # Monday
        self.assertEqual([w.name for w in store.due(now)], ["morning-brief"])
        store.mark_run(store.list()[0].id, now)
        self.assertEqual(store.due(now), [], "already ran today")

    def test_not_due_before_time(self):
        store = WorkflowStore()
        store.add("evening-post", steps=[], time="18:00", days="daily")
        self.assertEqual(store.due(datetime(2026, 9, 21, 17, 59)), [])

    def test_weekend_only(self):
        store = WorkflowStore()
        store.add("weekend-cleanup", steps=[], time="10:00", days="weekends")
        self.assertEqual(store.due(datetime(2026, 9, 21, 11, 0)), [])  # Monday
        self.assertTrue(store.due(datetime(2026, 9, 26, 11, 0)))       # Saturday

    def test_bad_time_rejected(self):
        store = WorkflowStore()
        with self.assertRaises(ValueError):
            store.add("bad", steps=[], time="25:00")


# ------------------------------------------------------------------- company
class TestCompany(unittest.TestCase):
    def setUp(self):
        self.company = CompanyOrg()

    def test_routing(self):
        self.assertEqual(self.company.route("invoice and budget paisa")[0], "Finance")
        self.assertEqual(self.company.route("instagram story post")[0], "Social Media")
        self.assertEqual(self.company.route("google cloud par model train")[0], "CTO / Technology")
        self.assertEqual(self.company.route("client proposal website netlify")[0], "Marketing")
        self.assertEqual(self.company.route("random greetings")[0], "CEO (Parth)")

    def test_org_chart_and_agents(self):
        chart = self.company.org_chart()
        self.assertIn("CEO", chart)
        self.assertGreaterEqual(len(self.company.all_agents()), 11)


# ------------------------------------------------------------------- catalog
class TestCatalog(unittest.TestCase):
    def test_at_least_151(self):
        self.assertGreaterEqual(catalog_size(), 151, "owner target: 151+ capabilities")

    def test_unique_ids_and_valid_kinds(self):
        caps = build_catalog()
        ids = [c.id for c in caps]
        self.assertEqual(len(ids), len(set(ids)))
        for c in caps:
            self.assertIn(c.kind, ("skill", "tool", "agent"))
            self.assertTrue(c.description)
            self.assertTrue(c.tags)

    def test_register_into_registry(self):
        r = Registry()
        n = register_catalog(r)
        self.assertEqual(n, catalog_size())
        self.assertEqual(r.count(), n)
        self.assertGreaterEqual(r.count("skill"), 80)
        self.assertGreaterEqual(r.count("tool"), 30)
        self.assertGreaterEqual(r.count("agent"), 10)


# ----------------------------------------------------------------- assistant
class TestAssistant(unittest.TestCase):
    def test_wake_and_process(self):
        a = make_assistant()
        self.assertEqual(a.state, State.DORMANT)
        a.wake()
        self.assertEqual(a.state, State.LISTENING)
        result = a.hear("Parth WhatsApp खोलो और देखो किसका मैसेज आया है")
        self.assertEqual(result["event"], "task_complete")
        self.assertEqual(result["report"].status, "completed")
        self.assertGreaterEqual(len(result["report"].steps), 2)
        self.assertEqual(a.state, State.LISTENING)  # session still active

    def test_viram_ends_session(self):
        a = make_assistant()
        a.wake()
        out = a.hear("Viram")
        self.assertEqual(out["event"], "viram")
        self.assertEqual(a.state, State.DORMANT)

    def test_barge_in(self):
        a = make_assistant()
        a.wake()
        spoken = {"n": 0}

        def on_say(chunk):
            spoken["n"] += 1
            if spoken["n"] == 3:
                a.user_started_speaking()  # owner starts talking mid-utterance

        a.on_say = on_say
        out = a.say("Report: replies sent and video uploaded successfully to YouTube")
        self.assertTrue(out["interrupted"])
        self.assertEqual(a.state, State.LISTENING)

    def test_hear_ignores_when_dormant(self):
        a = make_assistant()
        out = a.hear("WhatsApp खोलो")
        self.assertEqual(out["event"], "ignored")

    def test_save_workflow_and_due(self):
        a = make_assistant()
        out = a.save_workflow("test-wf", "WhatsApp खोलो", time="09:00", days="daily")
        self.assertEqual(out["event"], "workflow_saved")
        self.assertTrue(a.workflows.due(datetime(2026, 9, 21, 9, 30)))
        self.assertFalse(a.workflows.due(datetime(2026, 9, 21, 8, 30)))

    def test_status_reflects_control_words(self):
        a = make_assistant()
        st = a.status()
        self.assertEqual(st["wake_word"], "parth")
        self.assertEqual(st["stop_word"], "viram")
        self.assertTrue(st["background"], "run-once, run-forever")


if __name__ == "__main__":
    unittest.main(verbosity=2)
