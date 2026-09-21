# Parth — Product Specification (v1.0)

> Parth is a voice-first, always-on, autonomous agentic assistant that **uses devices like a human
> does** — operating Android phones (rooted / Shizuku / ADB level), desktops, laptops and the
> browser — to complete extreme, multi-step, multi-app tasks from a single spoken instruction.
>
> This spec is derived from (a) the owner's requirements (recorded verbatim below where exact) and
> (b) the research evidence in `01-research-problems-and-ideas.md`.

---

## 1. Identity & personality

- **Name:** Parth.
- **Wake word:** `Parth` — say the name to activate/ask. *(Deliberately NOT adding "Prasthan" as
  wake/start word — owner decision 2026-09-21.)*
- **Stop / pause word:** `Viram` (विराम) — **replaces "Prasthan"** everywhere. Saying "Viram":
  - while Parth is **speaking** → Parth goes silent immediately;
  - while Parth is **working** on a long/complex task → Parth pauses/stops the work and reports
    status;
  - while Parth is **listening** → ends the listening session.
- **Personality:** professional, calm, human-like, polite; speaks like a well-trained executive
  assistant. No robotic repetition of commands back (a documented top irritation of voice
  assistants — see research §8).
- **Language:** bilingual (Hindi + English Hinglish) with extensible language packs.

## 2. Core interaction model (voice state machine)

```
            "Parth"                    user speaks while
  ┌────────┐ (wake)   ┌───────────┐     Parth speaks      ┌───────────┐
  │ DORMANT├─────────►│ LISTENING ├◄──────────────────────┤ SPEAKING  │
  └────────┘          └─────┬─────┘   (barge-in: silence) └───────────┘
      ▲                     │ full utterance captured
      │                     ▼
      │               ┌───────────┐    plan accepted     ┌───────────┐
      │   "Viram"     │ PLANNING  ├─────────────────────►│ EXECUTING │
      └───────────────┤           │                      │ (parallel)│
                      └───────────┘                      └─────┬─────┘
                         ▲          "Viram" (hard stop)        │ done / limit
                         │                                     ▼
                         │                               ┌───────────┐
                         └───────────────────────────────┤ REPORTING │
                                (return to DORMANT)      └───────────┘
```

Rules:

1. **One utterance, many steps.** A single spoken instruction may contain dozens of sub-tasks
   across many apps (see §6 examples). Parth decomposes and executes them.
2. **Barge-in.** Any time Parth is speaking, if the user starts speaking, Parth instantly goes
   silent and listens.
3. **Continuous work until Viram or limit.** For complex/loop tasks Parth keeps working until the
   owner says "Viram" **or** the configured run limit is reached (step/time/message caps). No
   mid-task questions unless a mandatory approval gate (§4) triggers.
4. **Self-healing.** If an error or problem occurs mid-task, Parth must first try to solve it
   itself (search → fix → retry, up to N attempts) before reporting failure. Owner should not be
   bothered with solvable errors.
5. **Run once, run forever.** After first start, Parth keeps running in the background — leaving
   or backing out of the app does not stop it. It auto-starts on device boot. A persistent
   notification shows state (DORMANT / LISTENING / WORKING).
6. **Results display.** After completing work Parth shows the result: opens its app UI **and/or**
   a floating window overlay (PC/laptop-style, on phone via SYSTEM_ALERT_WINDOW) with the summary,
   photos/videos, and details of what was done.
7. **Research answers.** "Parth, X ke bare mein khojo aur summary do" → Parth searches, returns a
   spoken + visual summary with photos/videos and source details.
8. **Demonstration learning (save & repeat).** If the owner shows or describes an
   image/video/workflow/prompt and says "save kar lo, aisa roz is time par karna" — Parth saves it
   as a **scheduled workflow** (time + days) and executes it automatically at the allotted time/day.

## 3. Device & platform coverage

| Surface | Mechanism |
|---|---|
| Android (primary, owner's rooted phone) | Shizuku (ADB-level privileges; the phone is rooted and Shizuku-enabled — treat system-level permission as available), AccessibilityService (UI automation fallback), UiAutomation via Shizuku (privileged mode) |
| System modification | Shizuku-style privilege lending: modify system settings, grant permissions to other apps, toggle tether/airplane/wireless, disable/uninstall apps, restricted shell commands — **including granting Parth itself every permission the owner allows** |
| Termux / terminal | Full Termux + tmux control (owner grants tmux and shell permissions) |
| Windows / macOS / Linux | Desktop computer-use: screen vision + mouse/keyboard control, window management |
| Browser | Web automation (login flows, form filling, scraping, deployments) |
| Cross-device | Parth on phone A can **place a voice call to the owner's second device** to deliver a professional report when a task finishes or a client accepts |

## 4. Safety & approval model

The owner grants every permission Parth requests and does not want to be blocked — **except**:

- **Destructive gates (owner-specified):** deleting emails/files/storage, sending money, posting
  public content on the owner's accounts, and messaging new contacts → Parth **must** show what it
  intends to do and wait for the owner's approval (voice "haan/yes" or tap). *(Owner explicitly
  required this for storage/email deletion: "मुझसे डिलीट करने से पहले पूछो. ")*
- **Run limits:** default caps on steps per task, messages per day, spend per day (configurable).
  "Viram" always overrides everything.
- **Audit log:** every action is recorded (what, when, which app, result) and exportable.

## 5. Capability system — Skills, Agents, Tools (151+)

Every one of the three capability kinds has **Create + Import + Export + Add More**:

```
┌────────────────────────────────────────────────────────┐
│  Parth → Skills   [Create] [Import] [Export] [Add More]│
│  Parth → Agents   [Create] [Import] [Export] [Add More]│
│  Parth → Tools    [Create] [Import] [Export] [Add More]│
└────────────────────────────────────────────────────────┘
```

- **Skill** = a packaged workflow/recipe (e.g., "YouTube upload pipeline", "Gmail triage") — JSON
  manifest + steps + prompts. Import/export as `.parth.json` files; users can create their own in
  the app or import from anyone.
- **Agent** = a role with a prompt/personality, a toolset and a mandate (e.g., "SEO Agent").
- **Tool** = an executable capability (app connector, system op, API, script).
- **Catalog target: 151+ capabilities shipped**, each individually listed, versioned, and
  import/exportable (see `parth-core/parth/catalog.py` → 160 entries at v1).
- **Marketplace-ready:** packages are signed manifests; importing a third-party skill is gated by
  a review screen (supply-chain safety, research §6).

## 6. Example owner tasks (acceptance scenarios)

These are the owner's literal examples; each must be executable as ONE spoken instruction:

1. **Messaging suite:** "WhatsApp खोलो, देखो किसका मैसेज आया है, उनको reply कर दो, और हर्षित, सौरभ, पंकज का group बनाकर message भेजो कि आज Los Angeles घूमने चलना है।"
2. **Gmail triage:** "Gmail खोलो, सारे emails देखो, important रहने दो, बाकी delete कर दो — पहले मुझे बताना, मैं approve करूँ तब delete करना।"
3. **Storage cleanup:** "Phone की unwanted/hidden storage चीज़ें delete करो — list दिखाओ, approval के बाद delete।"
4. **Content pipeline:** "YouTube (mod) खोलो; किसी free AI video platform पे मेरे Gmail से login करो, अच्छा video बनाओ, download करो; ChatGPT से thumbnail बनवाओ; SEO-friendly title, description, tags डालकर video upload कर दो। फिर Instagram खोलो: दोस्तों को message भेजो, followers के group में 'आज शाम कुछ अच्छा होने वाला है' भेजो, comments/replies का answer दो, वही video post करो और story भी लगाओ। फिर Facebook पे same। फिर Telegram: दोस्तों को message, groups में नई ज़रूरी चीज़ें मुझे बताना।"
5. **Client acquisition loop:** "50 dental clinics (US/LA/Europe) खोजो जिनकी website नहीं है; हर एक का business data collect करके premium animated website बनाओ; Netlify पे deploy करके URL उनको proposal message में भेजो। रोज़ 101 approaches। जब तक 20 targeted / 10 accepted न हो जाएं, loop चलता रहे: खोजो → बनाओ → भेजो। जिस doctor ने accept किया, मुझे alert भेजते रहना।"
6. **Media & music:** "YouTube खोलो, जीना-जीना song लगाओ। बाद में उस song को बेहतर song से change करना। Browser में web scraping चालू करो…"
7. **AI R&D:** "मेरे laptop पर एक AI model बनाओ — vision, text-to-speech, speech-to-text, speech-to-speech, full agentic। फिर Google Cloud पे मेरे account से project import करके training चालू कर दो। Model ऐसी नई technology से बनाओ जिसमें parameters कम रहें पर knowledge/power ज़्यादा हो (condensed)।"
8. **App design:** "YouTube/इंटरनेट पर best app UIs देखकर full production-grade, professional (non-AI-looking) design plan बनाओ — मुझे दिखाओ, मैं 'haan' बोलूँ तो आगे बढ़ाएँ।"
9. **Cross-device report:** Owner leaves phone A at home, carries phone B → Parth **calls phone B**
   and reports professionally.
10. **Save & repeat:** "यह workflow save कर लो, रोज़ सुबह 8 बजे ऐसा ही करना।"

## 7. Company organization (multi-agent agency)

Parth internally runs as a **full company** — each department is an agent (importable/exportable/
creatable per §5), routed by intent:

```
                         ┌──────────────┐
                         │  CEO (Parth) │  ← orchestrator, final decisions
                         └──────┬───────┘
        ┌───────────┬───────────┼────────────┬────────────┐
        ▼           ▼           ▼            ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
   │  CTO    │ │Marketing│ │ Finance  │ │ Social  │ │ Legal &  │
   │ (tech/  │ │ (leads, │ │ (invoices│ │ Media   │ │ Compliance│
   │  devops)│ │  growth)│ │  budgets)│ │ (posts) │ │ (consent) │
   └─────────┘ └─────────┘ └──────────┘ └─────────┘ └──────────┘
        ┌───────────┬───────────┬────────────┬────────────┐
        ▼           ▼           ▼            ▼            ▼
   [HR/agents] [Operations] [Research] [Content Studio] [Security]
```

- Departments **work in parallel** on independent tasks (research §6: narrow toolsets per agent,
  not one overloaded agent).
- The CEO agent owns the approval gates (§4) and the audit log.
- Legal/Compliance owns the actor-likeness consent ledger and platform-policy checks
  (YouTube July-2025 AI-content rules, anti-spam limits).

## 8. Model layer (online/offline, any model)

- **Pluggable model registry:** cloud APIs (OpenAI/Anthropic/Google/…), local models (GGUF/ONNX on
  phone & laptop), with automatic fallback: cloud → local → cached skills.
- **On-device always:** wake word ("Parth") detection and VAD (barge-in) must run locally —
  privacy (52% of users fear passive listening, research §8).
- **STT/TTS:** cloud for accuracy, local fallback for offline; speech-to-speech pass-through mode.
- **Vision:** screenshot understanding for phone/desktop use; photo/video analysis for research
  summaries.
- **Owner's "new technology" model goal** (few parameters, condensed knowledge): R&D track —
  distillation, MoE, quantization, and continual-learning architectures; see `04-problems-bugs-risks.md`
  §6 for the honest engineering plan (this is a research program, not a one-week build).

## 9. Non-functional requirements

- **Speed:** wake→listen latency < 300 ms; plan→first-action < 2 s (cached plans instant).
- **Parallelism:** up to N concurrent step executions (default 4; configurable).
- **Persistence:** service survives app-back, screen-off, and reboot (boot receiver + watchdog).
- **Offline:** core state machine, wake word, scheduled workflows, and local-model skills work
  without internet.
- **Extensibility:** every capability importable/exportable; SDK for creating new skills in-app.
- **Honesty:** capability manifest states what each skill/tool/agent can and cannot do
  (research §8: expectation gap is a top complaint).

## 10. Out of scope for v1 (tracked in roadmap)

- Real payment integrations (invoices drafted, humans pay).
- Fully autonomous "AGI" reasoning — Parth ships bounded, auditable autonomy (see risk doc).
- Actual training of a from-scratch foundation model — replaced by distillation/fine-tuning track.
