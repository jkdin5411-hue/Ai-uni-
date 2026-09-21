#!/usr/bin/env python3
"""Parth end-to-end demo — runs the owner's acceptance scenarios in dry-run.

Usage:  python3 demo.py   (no dependencies, safe: every connector is dry-run)
"""
from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from parth.assistant import ParthAssistant, State  # noqa: E402
from parth.catalog import register_catalog  # noqa: E402
from parth.connectors import default_router  # noqa: E402
from parth.executor import Executor  # noqa: E402
from parth.planner import Step, TaskPlan, TaskPlanner  # noqa: E402
from parth.registry import Registry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"

HR = "═" * 74


def banner(title: str) -> None:
    print(f"\n{HR}\n  {title}\n{HR}")


def owner_approves(step) -> bool:
    print(f"      └─ Approval gate: '{step.title}' → Owner: हाँ, approved ✔")
    return True


def main() -> None:
    print(r"""
    ██████╗  █████╗ ███████╗████████╗██╗  ██╗
    ██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██║  ██║
    ██████╔╝███████║█████╗     ██║   ███████║
    ██╔═══╝ ██╔══██║██╔══╝     ██║   ██╔══██║
    ██║     ██║  ██║███████╗   ██║   ██║  ██║
    ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝
    Voice-first autonomous assistant · wake="Parth" · stop="Viram"
    (Prasthan removed by owner decision — replaced by Viram)
    """)

    # ---------------------------------------------------------------- setup
    registry = Registry()
    n = register_catalog(registry)
    router = default_router(dry_run=True)
    executor = Executor(connector_router=router.get, max_workers=4,
                        on_progress=lambda s: None)

    assistant = ParthAssistant(
        planner=TaskPlanner(), executor=executor, registry=registry,
        on_say=lambda chunk: print(f"    Parth ▸ {chunk}", end="", flush=True),
    )

    # ------------------------------------------------------ 1. catalog 151+
    banner("1 · CAPABILITY CATALOG (target: 151+, shipped: more)")
    print(f"    registered capabilities : {registry.count()}")
    for kind in ("skill", "tool", "agent"):
        print(f"      • {kind:<6}: {registry.count(kind)}")
    print(f"    every one supports: Create · Import · Export · Add-More")

    # ------------------------------------------------- 2. import / export
    banner("2 · SKILL IMPORT / EXPORT (from skills/*.parth.json)")
    for pkg in sorted(SKILLS_DIR.glob("*.parth.json")):
        cap = registry.import_package(pkg)
        print(f"    imported: {cap.kind:<5} '{cap.name}' ({len(cap.steps)} steps) ← {pkg.name}")
    export_dir = Path(tempfile.mkdtemp(prefix="parth-export-"))
    out = registry.export("social-media-blast", export_dir / "social-media-blast.parth.json")
    print(f"    exported: 'Social Media Blast' → {out.name}")
    import json as _json
    pkg = _json.loads(out.read_text(encoding="utf-8"))  # what another device would receive
    pkg["id"], pkg["name"] = "social-media-blast-copy", "Social Media Blast (copy)"
    copy = registry.import_manifest(pkg)  # Add More ← from anyone's export
    print(f"    re-imported round-trip ✔ as '{copy.name}'  registry now: {registry.count()} capabilities")

    # --------------------------------------------- 3. the BIG multi-app task
    banner("3 · ONE UTTERANCE → MULTI-APP TASK (dry-run, approval-gated)")
    mega = (
        "WhatsApp खोलो और देखो किसका मैसेज आया है, उनको रिप्लाई कर दो, "
        "और हर्षित सौरभ पंकज को ग्रुप बना करके मैसेज भेज दो कि आज Los Angeles घूमने चलना है। "
        "फिर Gmail खोलो, सारे emails देखो, important रहने दो और बाकी delete कर दो। "
        "फिर किसी free AI platform पे login करके अच्छा video बनाओ और download कर लेना। "
        "फिर YouTube पर video upload करो, ChatGPT से thumbnail बनाओ, "
        "SEO friendly title description tags डाल कर upload कर दो। "
        "फिर Instagram खोलो, दोस्तों को मैसेज भेजो, followers को group में message भेजो, "
        "comments का reply करो, same video post करो और story भी लगाओ। "
        "फिर Facebook पर same करो। फिर Telegram खोलो, groups में नया आया हो तो बताना। "
        "फिर फोन की unwanted storage साफ करो, पहले मुझे बताना। "
        "फिर browser में 50 dental clinics खोजो जिनकी website नहीं है, "
        "उनके लिए website बनाकर Netlify पर deploy करो और doctors को proposal message भेजो। "
        "फिर Google Cloud पर AI model training start करो। "
        "पूरा होने पर मेरे दूसरे phone पर call लगाकर report करना।"
    )
    print(f"    Owner says:\n    \"{mega[:110]}…\"\n")
    plan = assistant.planner.decompose(mega)
    print(f"    planned {len(plan.steps)} steps:")
    print("   " + plan.summary().replace("\n", "\n   "))
    print("\n    executing (parallel by phase, self-healing, dry-run)…")
    result = assistant.process(mega, approver=owner_approves)
    report = result["report"]
    print(f"\n    department : {result['department']}  (routed via '{result['route_reason']}')")
    print(f"    result     : {report.summary()}")
    for s in report.steps:
        mark = {"done": "✔", "skipped": "⊘", "failed": "✗",
                "stopped": "⏹", "awaiting_approval": "⏸"}.get(s["status"], "•")
        print(f"      {mark} [{s['id']}] {s['connector']}.{s['action']} → {s['status']}")

    # ------------------------------------------------------- 4. VIRAM stop
    banner("4 · 'VIRAM' — HARD STOP ON A LONG RUNNING TASK")
    import threading
    viram_event = threading.Event()
    cancel_after = {"n": 0}

    def progress(step) -> None:
        cancel_after["n"] += 1
        if cancel_after["n"] >= 4:
            print("    … owner says: विराम !")
            viram_event.set()

    loop_executor = Executor(connector_router=router.get, on_progress=progress, retry_delay=0)
    hunt = TaskPlan(command="client hunt loop: search → build → deploy → message (repeat until 10 accept)", steps=[])
    hunt_steps = [
        ("leadfinder", "find_businesses"), ("netlify", "build_website"),
        ("netlify", "deploy_site"), ("whatsapp", "open"),
        ("whatsapp", "send_group_message"), ("phone", "read_notifications"),
        ("telegram", "group_digest"), ("gmail", "read_emails"),
        ("youtube", "set_metadata"), ("instagram", "reply_comments"),
    ]
    for i, (c, a) in enumerate(hunt_steps):
        hunt.steps.append(Step(id=f"s{i+1}", title=f"{c}: hunt step {i+1}",
                               connector=c, action=a,
                               params={"utterance": "loop"}, phase=i))
    loop_report = loop_executor.run(hunt, cancel_event=viram_event, approver=owner_approves)
    print(f"    long task stopped → {loop_report.summary()}")
    print(f"    (work pauses; Parth waits silently for the next 'Parth')")

    # ------------------------------------------------------ 5. barge-in
    banner("5 · BARGE-IN — PARTH GOES SILENT WHEN THE OWNER SPEAKS")
    def noisy_say(chunk: str) -> None:
        print(chunk, end="", flush=True)

    assistant.on_say = noisy_say
    assistant.wake()
    spoken_chunks = {"n": 0}

    def interrupting_on_say(chunk: str) -> None:
        spoken_chunks["n"] += 1
        print(chunk, end="", flush=True)
        if spoken_chunks["n"] == 6:  # owner starts talking mid-sentence
            print("  ‹owner starts speaking›", end=" ")
            assistant.user_started_speaking()

    assistant.on_say = interrupting_on_say
    out = assistant.say("Report: WhatsApp replies sent, Gmail cleaned, video uploaded to "
                        "YouTube with SEO metadata, Instagram post and story are live.")
    print(f"\n    interrupted={out['interrupted']}  state={out['state']}")
    print("    → Parth silenced itself instantly and is now LISTENING")

    # ------------------------------------------------- 6. save & repeat
    banner("6 · SAVE & REPEAT — SCHEDULED WORKFLOW")
    wf_out = assistant.save_workflow(
        name="creator-evening-post",
        command_or_steps="YouTube पर video upload करो और Instagram पर story लगाओ",
        time="18:00", days="daily",
    )
    print(f"    saved: {wf_out['name']} ({wf_out['steps']} steps) at {wf_out['time']} daily")
    now = datetime(2026, 9, 21, 18, 30)
    due = assistant.workflows.due(now)
    print(f"    now={now:%H:%M} → due: {[w.name for w in due]}")
    for w in due:
        assistant.workflows.mark_run(w.id, now)
    print(f"    after run, due again today? {[w.name for w in assistant.workflows.due(now)]}")

    # ---------------------------------------------------------- 7. status
    banner("7 · STATUS")
    st = assistant.status()
    for k, v in st.items():
        print(f"    {k:<12}: {v}")

    banner("WHAT IS REAL vs WHAT IS STUB (honest)")
    print("""    REAL  · state machine (wake/ Viram/ barge-in), planner, parallel executor
           with retries + limits + approval gates, registry import/export,
           scheduler, company routing, 155-capability catalog, tests
    STUB  · app connectors run in dry-run (safe simulation); real device
           bridges (Shizuku/Accessibility/desktop) land in Phase 2–3 —
           see docs/04-problems-bugs-risks.md §7 for the full list
    NEXT  · wire live models, Android build, real connectors, signed packages""")


if __name__ == "__main__":
    main()
