# Parth — Technical Architecture (v1)

## 1. System overview

```
┌────────────────────────────────  DEVICE (phone / laptop / desktop)  ───────────────────────────┐
│                                                                                                 │
│  VOICE LAYER                 CORE (orchestrator)                CAPABILITY LAYER                │
│  ┌───────────────┐          ┌──────────────────────┐          ┌──────────────────────────┐     │
│  │ WakeWord      │ "Parth"  │  ParthEngine         │  uses    │  Registry                │     │
│  │ (on-device)   ├─────────►│  state machine       ├─────────►│  Skills/Tools/Agents     │     │
│  │ VAD / barge-in│          │  DORMANT→LISTENING→  │          │  create/import/export    │     │
│  │ STT  ◄────────┤          │  PLANNING→EXECUTING→ │          └───────────┬──────────────┘     │
│  │ TTS ──────────┤          │  REPORTING           │                      │                    │
│  └───────────────┘          └──────┬───────┬───────┘                      ▼                    │
│                                    │       │                  ┌──────────────────────────┐    │
│  MEMORY                           │       │                  │ Company org (CEO/CTO/    │    │
│  ┌───────────────┐                │       │                  │ Marketing/Finance/…)     │    │
│  │ Short-term    │◄───────────────┘       │                  │ parallel dept agents     │    │
│  │ Long-term     │◄───────────────────────┘                  └──────────────────────────┘    │
│  │ WorkflowStore │                                                        │                    │
│  │ (scheduled)   │          EXECUTION                                       │                    │
│  └───────────────┘          ┌──────────────────────┐                                         │
│                             │ Executor             │                                         │
│  SAFETY                     │ • parallel groups    │                                         │
│  ┌───────────────┐          │ • retries + backoff  │                                         │
│  │ ApprovalGate  │◄─────────┤ • step/time limits   │                                         │
│  │ RunLimits     │          │ • cancel event(Viram)│                                         │
│  │ AuditLog      │          └──────────┬───────────┘                                         │
│  └───────────────┘                     │                                                     │
└────────────────────────────────────────┼─────────────────────────────────────────────────────┘
                                         ▼
┌─────────────────────────────  DEVICE BRIDGES  ─────────────────────────────┐
│  Android: ShizukuBridge (privileged ops)  +  PhoneControl (a11y/UIAutom.) │
│  Termux/tmux shell  •  Desktop computer-use  •  Browser driver            │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     ▼
┌─────────────────────────────  CONNECTORS (dry-run safe by default)  ───────┐
│  WhatsApp • Gmail • YouTube • Instagram • Facebook • Telegram • TikTok     │
│  Browser/scraping • Netlify deploy • Google Cloud training • AI video gen  │
│  Thumbnail gen • Storage cleaner • Phone call reporter • …                 │
└────────────────────────────────────────────────────────────────────────────┘
```

## 2. Repository layout (this repo, v1 scaffold)

```
Ai-uni-/
├── docs/                        ← research, spec (this file set), risks, roadmap
├── parth-core/                  ← RUNNABLE cross-platform agent core (Python, stdlib-only)
│   ├── parth/
│   │   ├── control_words.py     ← WAKE="parth", STOP="viram" (prasthan explicitly removed)
│   │   ├── assistant.py         ← voice state machine (barge-in, viram, run-once-forever)
│   │   ├── planner.py           ← multi-app command → typed Step list (deterministic)
│   │   ├── executor.py          ← parallel execution, retries, limits, cancel, reports
│   │   ├── registry.py          ← skills/tools/agents: create + import + export + add-more
│   │   ├── scheduler.py         ← save workflow → run at allotted time/day
│   │   ├── company.py           ← CEO/CTO/Marketing/Finance/… department routing
│   │   ├── catalog.py           ← 160-entry capability catalog (target was 151+)
│   │   └── connectors/          ← app/system/web connector stubs (dry-run safe)
│   ├── demo.py                  ← end-to-end demo of the owner's example tasks
│   └── tests/test_core.py       ← unit tests (stdlib unittest)
├── android/                     ← Android app scaffold (Kotlin sources + manifest)
│   └── app/src/main/java/parth/assistant/
│       ├── ParthApp.kt, MainActivity.kt
│       ├── core/ParthEngine.kt            (state machine mirror of parth-core)
│       ├── service/ParthForegroundService.kt   (run-once-forever + boot)
│       ├── service/PhoneControlAccessibilityService.kt (screen automation)
│       ├── shizuku/ShizukuBridge.kt       (privileged system ops)
│       ├── voice/WakeWordEngine.kt        ("Parth" detection + barge-in VAD)
│       └── ui/FloatingResultWindow.kt     (overlay results, PC-style)
└── skills/                      ← example importable/exportable .parth.json packages
```

## 3. Key design decisions

### 3.1 Deterministic spine, LLM brain
Research (§6 of doc 01) shows agents fail when *control flow* is delegated to LLMs. Parth inverts
this: the **spine is typed, tested Python** (steps, retries, limits, gates); the LLM only performs
reasoning tasks (decomposition assist, reply drafting, summarization) behind the spine. `planner.py`
ships with deterministic keyword-based decomposition so the whole pipeline works with **zero API
keys**; an LLM-enhanced planner can be plugged into the same `TaskPlan` interface.

### 3.2 Control words as first-class API
`parth/control_words.py` is imported everywhere. "Prasthan" is on an explicit reject-list
(historical name, removed by owner decision). Wake/stop detection is normalization-based (case,
punctuation, Devanagari + Latin transliterations).

### 3.3 Run limits instead of "infinite until Viram" only
Owner rule: *complex tasks run until "Viram" or the limit is filled.* `Executor(max_steps=100,
step_timeout=30s, max_retries=3)` defaults; every loop task (client outreach, comment replies)
declares a per-day cap. This is the safety net for the 2 AM runaway-agent scenario.

### 3.4 Dry-run by default
Every connector ships in `dry_run=True`: it logs intended actions and returns structured results.
Real integrations flip the flag after the owner approves the connector in the app. This makes the
repo safe to run, test and demo anywhere.

### 3.5 Skill package format (`.parth.json`)
```json
{
  "parth_package": "skill",
  "format_version": 1,
  "id": "social-media-blast",
  "name": "Social Media Blast",
  "version": "1.0.0",
  "description": "...",
  "tags": ["social", "multi-post"],
  "steps": [ { "title": "Open WhatsApp", "connector": "whatsapp", "action": "open", "params": {} },
             { "title": "Send group message", "connector": "whatsapp", "action": "send_message",
               "params": {"recipients": ["Harshit","Saurabh","Pankaj"], "text": "..."},
               "approval_required": true } ]
}
```
Import validates the manifest, checks id collisions, registers into `Registry`. Export writes the
same format. The Android app and desktop CLI share it. (Signed manifests = roadmap item; risk doc §4.)

### 3.6 Parallelism model
`TaskPlan.groups` = list of steps that can run concurrently (e.g., "post to Instagram" ∥ "post to
YouTube"). The Executor runs groups with `ThreadPoolExecutor(max_workers=N)`, joins, then proceeds.
Device-UI steps are serialized through a **single device mutex** (you cannot tap two apps at once
on one phone — but parallel virtual displays / multi-window, Ruto-GLM-style, are the Android-side
answer; see risk doc §1).

### 3.7 Memory
- Short-term: current conversation + task scratchpad.
- Long-term: append-only JSON-lines event log + queryable index (owner memory: names, preferences,
  accounts, friends like Harshit/Saurabh/Pankaj).
- Workflow store: scheduled/repeatable tasks with `due()` semantics.

### 3.8 Android service architecture
1. `ParthForegroundService` — started once, foreground notification, survives app-back; restarted
   by watchdog and `BOOT_COMPLETED` receiver.
2. `WakeWordEngine` — on-device hotword ("Parth") + VAD for barge-in; when armed, streams STT.
3. `PhoneControlAccessibilityService` — reads layout tree, performs taps/swipes; used as
   unprivileged fallback.
4. `ShizukuBridge` — binds Shizuku; privileged ops via `IShell`/UiAutomation: system settings,
   permissions grants, airplane/tether toggles, app disable/uninstall, restricted shell.
5. `FloatingResultWindow` — `TYPE_APPLICATION_OVERLAY` result cards.

## 4. Data flow — owner's example task

```
"WhatsApp खोलो … Gmail साफ करो … YouTube पर video बनाकर upload करो …"
   → WakeWord("Parth" utterance start) → STT full utterance → Planner
   → TaskPlan:
       G1 (parallel): [wa.read_messages] [gmail.read_emails] [yt.search_trends]
       G2 (serial, device mutex): [wa.send_replies*] [wa.create_group*] [gmail.delete_unimportant†]
       G3 (parallel): [aivideo.generate] [gpt.thumbnail] [seo.metadata]
       G4 (serial): [yt.upload*] [ig.post*+story*] [fb.post*] [tg.notify_groups]
       (* = approval gate, † = approval gate + preview list)
   → Executor runs groups; failures retry (self-heal), then escalate to CEO agent
   → ExecutionReport → TTS summary + app screen + FloatingResultWindow + audit log
```

## 5. Testing & verification strategy

- `parth-core/tests/test_core.py` — state machine, control words (incl. Devanagari), planner
  decomposition, executor cancel/limits/retries, registry import/export round-trip, scheduler
  due-times, company routing, catalog ≥151 unique capabilities.
- `demo.py` — full dry-run of acceptance scenarios (spec §6).
- Android: unit tests mirror state machine; UI tests via espresso on CI; on-device
  Shizuku instrumented tests.
