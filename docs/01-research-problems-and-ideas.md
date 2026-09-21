# Parth — Global Research: Problems, Pains & Product Ideas (v1)

> Research compiled 2026-09-21 from across the internet. This document is the evidence base for the
> Parth assistant (see `02-parth-product-spec.md`). Every persona section lists the real problems
> people report, with sources, and then translates them into concrete product ideas for Parth.

---

## 0. Executive summary

Across every persona we researched — everyday people at home, office workers, drivers and
travellers, content creators, film/web-series producers, AI engineers & freelancers, and people who
want an AI that physically operates their phone — the same root problems repeat:

1. **Too much low-value "work about work"** — messages, emails, status updates, switching apps,
   repeating oneself to tools that don't listen.
2. **Always-on pressure with no team** — creators and solo professionals do 8 jobs at once and
   burn out; the people who survive hire help. Parth's answer: hire *agents* instead.
3. **Tools that almost work together** — AI video clips of 8 seconds, agents that demo well then
   fail in production, assistants that mishear and talk over you.
4. **Fragmented attention is dangerous** — 3,208 people died in 2024 in the US alone in
   distraction-related crashes; hands-free, voice-first, barge-in-capable interaction is a safety
   feature, not a gimmick.
5. **Permission walls** — phones lock normal apps out of system control; the Shizuku ecosystem
   proves there is huge demand for AI agents that operate Android at ADB/root level.

**Parth's design conclusions from this research:** always-listening with a private on-device wake
word ("**Parth**"), instant silence-when-the-user-speaks (barge-in), a hard stop word ("**Viram**")
for long autonomous runs, parallel multi-app task execution with human approval gates before
destructive actions, import/export/create for every skill/tool/agent, and a company-style
multi-agent org (CEO/CTO/Marketing/Finance/...) so no single overloaded agent exists.

---

## 1. Everyday person at home — problems

### What the internet says

- **Mental load is invisible, constant work.** "Mental Load" is the planning, monitoring and
  remembering layer of life — shopping, scheduling, childcare coordination, bills — that runs in
  the background even when you're doing something else. Signs: replaying upcoming tasks in your
  head while doing other activities, small everyday tasks feeling like a mountain [28](https://www.beurer.com/gesundheitsratgeber/en/wellbeing/mental-load.php).
- **Life admin is a whole second job.** Household audits find the load splits into daily living
  (meals, dishes, laundry, pets), weekly ops (groceries, bill checks), monthly admin
  (prescriptions, budget reviews, car checks, school deadlines), seasonal tasks, plus social labor
  (gifts, thank-you notes, family visits) and personal maintenance [27](https://everblog.com/blogs/life-with-everblog/mental-load-checklist).
- **The system lives in people's heads.** The load gets heavier when to-do lists live only in your
  head, there's no clear tracking system, decisions are constant and unplanned, and digital
  notifications never stop [29](https://laurajadeprado.com/blog/2026/02/22/how-to-reduce-your-mental-load-and-stop-feeling-overwhelmed-by-everyday-life-admin/).
- **Voice assistants under-deliver at home.** Households hit background-noise failures, trouble
  with multiple commands at once, and language-recognition problems; users have poor mental models
  of what the assistant can actually do, creating an expectations gap [25](https://www.tandfonline.com/doi/full/10.1080/0144929X.2026.2619105?scroll=top&needAccess=true).

### Problems → Parth ideas

| Problem | Parth capability |
|---|---|
| To-dos live in your head | Always-on voice capture: "Parth, yaad rakhna..." → task/memory agent writes it down |
| Bills, renewals, appointments | Proactive scanner: reads Gmail/SMS for due dates, proposes a weekly "life admin" batch with one approval |
| Meal/grocery planning | Pantry tracker + grocery-list agent, reorder suggestions |
| Notifications never stop | Notification triage agent: summarizes, filters, batches the important ones |
| Family coordination | Shared family calendar agent; birthday/reminder social-labor automation |
| Assistant doesn't understand | Wake-word + barge-in voice UX, multi-command single-utterance parsing (see §8) |

---

## 2. Office person — problems

### What the internet says

- **Interruptions are constant.** Employees face ~275 interruptions per day during core work
  hours — one ping every two minutes; 79% get distracted within an hour of starting a task and 59%
  can't hold focus for even 30 minutes [1](https://www.makerstations.io/workplace-distraction-statistics/).
  Knowledge workers are interrupted on average **every 2 minutes** by meetings, messages or
  notifications [2](https://www.breeze.pm/articles/workplace-productivity-statistics).
- **The message flood is enormous.** The average worker receives **117 emails and 153 Teams
  messages per day**; 48% say work feels chaotic and fragmented; 82% use no structured time
  management system [2](https://www.breeze.pm/articles/workplace-productivity-statistics).
- **Most work is "work about work."** Asana-reported research: ~60% of knowledge-worker time goes
  to chasing status, unnecessary meetings, tool switching and coordination — not the actual job
  [2](https://www.breeze.pm/articles/workplace-productivity-statistics). Up to 49% of the workday goes to
  tasks that bring little or no value, including unnecessary emails (22%) and inefficient commutes (12%) [3](https://byoxon.com/blog/time-management-statistics/).
- **Meetings eat the calendar.** Average knowledge worker: 15.4 hours/week in meetings vs 12.1
  hours of uninterrupted focus; 71% of senior leaders call meetings unproductive; 5 hours/week
  per employee are wasted in unproductive meetings [1](https://www.makerstations.io/workplace-distraction-statistics/).
- **Refocusing is expensive.** Workers average ~12 minutes on a task before an interruption, and
  regaining focus takes over 23 minutes; ~200 hours/year are spent just switching between apps [1](https://www.makerstations.io/workplace-distraction-statistics), [3](https://byoxon.com/blog/time-management-statistics/).
- **Well-being is suffering.** 40% of employees globally felt a lot of stress the previous day;
  global engagement fell to 20%, the lowest since 2020 [4](https://www.makerstations.io/workplace-mental-health-statistics/);
  43% of office workers spend 10+ hours/week on "productivity theater" — looking busy [1](https://www.makerstations.io/workplace-distraction-statistics/).
  24% of employees cite task overload and 24% cite lacking the right tools as productivity blockers [5](https://high5test.com/employee-productivity-statistics/).

### Problems → Parth ideas

| Problem | Parth capability |
|---|---|
| 117 emails + 153 messages/day | Inbox & chat triage agent: reads, ranks, drafts replies, batches the rest for one approval |
| Status chasing (60% of time) | Auto status-report writer that collates project state across tools |
| 15.4 h/week of meetings | Meeting agent: joins, transcribes, produces decisions/action items, files them |
| 200 h/year app switching | One voice interface over all apps — the user never switches apps; Parth does |
| 23 min to refocus | Focus-guard mode: Parth holds interrupts, summarizes them after the focus block |
| Productivity theater | Execution-first design: Parth does the task and shows receipts, not dashboards |

---

## 3. Driving & travelling — problems

### What the internet says

- **Distracted driving kills.** In 2024, 3,208 people died in US crashes where distraction was a
  contributing factor (8% of all crash deaths); 437 of those involved cellphone use; and
  police data *underestimates* the real numbers [30](https://www.iihs.org/research-areas/distracted-driving).
  Another 315,167 people were injured in distraction-affected crashes [31](https://www.fcc.gov/consumers/guides/dangers-texting-while-driving).
- **Manipulating a phone is 2–6× more crash-prone.** Naturalistic studies consistently link
  texting/manipulating a phone to sharply increased crash risk; drivers with high phone
  distraction are **240% more likely to crash**; a single text takes eyes off the road ~5 seconds —
  a football field at 55 mph [30](https://www.iihs.org/research-areas/distracted-driving), [31](https://www.fcc.gov/consumers/guides/dangers-texting-while-driving).
- **People still do it.** 17% of American adults admit using the phone behind the wheel; the
  highest share of phone-using drivers in fatal crashes is the 25–34 age group [32](https://www.whistleout.com/CellPhones/Guides/distracted-driving-by-state), [31](https://www.fcc.gov/consumers/guides/dangers-texting-while-driving).
- **Travel adds admin load.** Inefficient commutes alone eat ~12% of low-value workday time [3](https://byoxon.com/blog/time-management-statistics/);
  travel adds bookings, itineraries, packing, and coordination — classic mental-load burdens (§1).

### Problems → Parth ideas

| Problem | Parth capability |
|---|---|
| Touching the phone while driving is lethal | **Driving mode**: 100% voice-only, screen-off operation; wake word "Parth" + spoken confirmations |
| Can't reply while driving | Auto-reply agent ("driving, will respond at 4pm"), urgent-sender allowlist |
| Missed logistics mid-trip | Travel agent: itinerary, gate changes, hotel/check-in, currency, packing list |
| Hands busy | Barge-in conversation: user speaks anytime, Parth silences instantly and listens |
| "Report when done" while away | Cross-device callback: Parth **calls the user's other phone** with a professional voice report (owner requirement, validated by this pain) |

---

## 4. Content creators — problems (create, edit, post, automate)

### What the internet says

- **Burnout is the headline number.** 78% of creators say burnout is impacting their motivation
  and physical/mental health; the *worst-hit* are mid-tier creators (50k–500k followers) who are
  full-time but lack a team — the ones who have "hired their way out" report the lowest burnout [6](https://thecreatoreconomy.com/post/creator-burnout-78-percent-mental-health-2026).
  63% of full-time creators experienced burnout in the last 12 months [7](https://www.wpbeginner.com/research/creator-economy-statistics-that-will-blow-you-away/).
- **Idea generation is the top burnout driver.** Over 51% of creators cite "constantly having to
  come up with new ideas and post to new platforms" as a top cause of burnout [8](https://shortvids.co/content-creation-challenges-and-solutions/).
- **Post-everywhere pressure.** 45%+ of full-time creators say the pressure to post everywhere
  causes burnout; 75% believe algorithms punish creators who aren't publishing constantly [7](https://www.wpbeginner.com/research/creator-economy-statistics-that-will-blow-you-away/).
- **One person, eight jobs.** Creators are "the creator, photographer, editor, writer, admin,
  negotiator, accountant, and sometimes customer service rep" [9](https://www.hercozycrew.com/post/is-being-a-content-creator-worth-it-in-2025-the-pros-and-cons-you-should-know).
- **Platform rules are shifting under AI content.** YouTube's policy update effective July 15,
  2025 means low-effort, repetitive AI content may be demonetized [8](https://shortvids.co/content-creation-challenges-and-solutions/).
- **Money is a constant worry.** 14.6% of professional creators say their greatest challenge is
  finding brand deals [7](https://www.wpbeginner.com/research/creator-economy-statistics-that-will-blow-you-away/).

### Problems → Parth ideas

| Problem | Parth capability |
|---|---|
| Idea block (51%) | Idea engine: trend scanning per niche, content frameworks, hooks bank, daily idea brief |
| Post-everywhere pressure (45%) | One-utterance multi-platform pipeline: script → AI video → thumbnail → SEO title/description/tags → YouTube + Instagram + Facebook + TikTok + Telegram, each auto-formatted |
| 8 jobs at once | Creator "company" of agents: editor agent, thumbnail agent, SEO agent, comment-reply agent, analytics agent |
| Algorithm anxiety | Consistency engine: scheduled workflows ("save this, run daily at 6pm"), queue never goes empty |
| Comment/DM flood | Engagement triage: reply drafting in the creator's voice, escalation for sensitive/brand-safety issues |
| Brand-deal hunting | Outreach agent: lead research, personalization, follow-up sequences (with anti-spam limits — see doc 04) |
| Demonetization risk | Policy-aware metadata & originality checks before upload (post-July-2025 YouTube rules) |

---

## 5. Movie & web-series producers — problems (AI scene generation, production)

### What the internet says

- **The tools are short and watermarked.** Leading video-generation platforms restrict outputs to
  ~8 seconds and 720p/1080p, impose monthly generation limits, and mandate watermarking
  (e.g. SynthID); some don't generate audio natively, forcing separate sound production [12](https://vibecentral.ai/report/filmmaking/the-impact-of-generative-ai-on-filmmaking-tools-breakthroughs-and-ethical-challenges/).
- **Fine control is missing.** Filmmakers report struggles with temporal continuity,
  shot-composition control, convincing hands/fingers, in-scene text, realistic dialogue, and
  photorealism; maintaining visual/narrative coherence for a 90-minute film is beyond current
  platforms; generation is computationally expensive [12](https://vibecentral.ai/report/filmmaking/the-impact-of-generative-ai-on-filmmaking-tools-breakthroughs-and-ethical-challenges/).
- **Artists' top asks: consistency, controllability, fine-grained editing, motion refinement.** A
  CVPR 2025 survey of GenAI filmmaking found strong demand for controlling character movement,
  generating multiple characters in one frame, and better 3D output (meshes often lack style and
  topology, requiring manual retopology); dataset bias skews generations [11](https://openaccess.thecvf.com/content/CVPR2025W/CVEU/papers/Zhang_Generative_AI_for_Film_Creation_A_Survey_of_Recent_Advances_CVPRW_2025_paper.pdf).
- **Cost-per-finished-clip is the real number.** A $0.10/sec model can produce a $40 finished
  clip because of retries; character continuity "is an agent problem" — the fix is an orchestration
  layer that pins character references and chains last-frame→next-generation, running storyboard,
  render and extend stages in parallel [13](https://medium.com/data-science-collective/the-2026-ai-video-production-playbook-bc683d5b85da).
- **Indie filmmakers are alone.** Directors using AI find themselves suddenly playing set
  designer, lighting director and costumer — roles requiring expertise they don't have —
  "frustrating and draining"; plus stigma from peers and unresolved copyright questions (e.g.
  Runway's reported scraping of YouTube and studio content) [14](https://techcrunch.com/2026/02/20/ais-promise-to-indie-filmmakers-faster-cheaper-lonelier/).
- **Legal/consent minefield.** Digital replicas ("digital doubles") of actors without consent,
  extended likeness reuse in sequels, manipulative transformations, and compensation models are
  the core disputes; the SAG-AFTRA-style agreements require informed consent and compensation for
  digital replicas [10](https://www.taylorwessing.com/en/interface/2025/media-hot-topics-2025/the-use-of-generative-ai-in-film-productions).

### Problems → Parth ideas

| Problem | Parth capability |
|---|---|
| 8-second clips, no continuity | Orchestration pipeline: storyboard-first planning, character reference sheets, last-frame chaining, multi-shot stitching (per [13](https://medium.com/data-science-collective/the-2026-ai-video-production-playbook-bc683d5b85da)) |
| One director, every role | **Virtual crew agents**: set-designer agent, lighting agent, costumer agent, continuity/script-supervisor agent, editor agent |
| Consistency drift | Continuity checker: diffs every generated shot against the character sheet; flags drift before it compounds |
| Cost blowouts | Budget guard: cost-per-finished-clip accounting, retry caps, model routing (cheap drafts → premium finals) |
| Rights & consent | Consent & rights ledger: per-actor digital-replica consent records, per-asset license tracking (SAG-AFTRA-aligned) [10](https://www.taylorwessing.com/en/interface/2025/media-hot-topics-2025/the-use-of-generative-ai-in-film-productions) |
| 3D asset quality | Retopology/rigging QA agent with human escalation |

---

## 6. AI engineers, freelancers & developers — problems (agentic assistants)

### What the internet says

- **The prototype-to-production gap is the #1 theme.** Prototypes are easy; scaling agentic
  workflows into reliable, observable, governed systems introduces hard complexity: workflow
  decomposition, deterministic orchestration, avoiding LLM drift, multi-agent communication, tool
  schemas, concurrency, retries, logging, cost control, and reproducibility across model updates [15](https://arxiv.org/html/2512.08769v1).
- **Almost nobody is in production.** Only 11% of organizations actively use agentic AI in
  production (14% ready to deploy, 38% piloting, 30% exploring); Gartner predicts **over 40% of
  agentic AI projects will fail by 2027** over legacy-system integration problems [18](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/agentic-ai-strategy.html), [16](https://gigster.com/blog/why-your-enterprise-isnt-ready-for-agentic-ai-workflows/).
- **Hallucination cascades.** A single hallucinated value in an early step cascades through the
  whole process; agent debugging is a "black box" problem unlike traditional software [17](https://www.comet.com/site/blog/ai-agents/).
- **Too many tools per agent destroys reliability.** Attaching many tools to one agent increases
  ambiguity, token use, and wrong/missing tool calls; MCP-tool ambiguity caused "flickering,
  non-reproducible failures" in one documented case, fixed by direct typed tool functions [15](https://arxiv.org/html/2512.08769v1).
- **Security lives at the skill/plugin boundary.** Runtime risks cluster at the plugin and skill
  execution layer, not the LLM layer: enforce signed skill manifests, review supply chains,
  sandbox every skill execution (OWASP AST10) [19](https://mlflow.org/articles/building-production-ready-ai-agents-in-2026/).
- **Monolithic agents are fragile.** A failure in one capability breaks everything; decompose
  early; keep deterministic tasks in typed code, not LLM reasoning; observability must be built in
  from day one [19](https://mlflow.org/articles/building-production-ready-ai-agents-in-2026/), [17](https://www.comet.com/site/blog/ai-agents/).

### Problems → Parth ideas

| Problem | Parth capability |
|---|---|
| Prototype → production gap | Parth core ships with a **tested** orchestrator: typed steps, retries, checkpoints, step limits, audit log (see `parth-core/`) |
| Hallucination cascades | Deterministic guardrails: approval gates, dry-run mode by default, structured step results |
| Tool overload | Small per-department agents (company org) each with a narrow toolset, routed by intent |
| Skill supply-chain risk | Signed, versioned, importable/exportable skill packages with manifests (doc 03 format) |
| No observability | Every step emits a trace event; runs produce an inspectable `ExecutionReport` |
| Solo freelancer overload | Parth-as-agency: the freelancer's own CEO/CTO/Marketing/Finance agents working in parallel |

---

## 7. People who want an AI that controls their phone like a human — the Shizuku ecosystem

### What the internet says

This is exactly the owner's use case (rooted/ADB-unlocked phone, system-level permissions, "don't
worry about permissions"). The ecosystem already exists and is actively growing:

- **Shizuku gives apps ADB-level privileges without root.** It connects over ADB (wireless on
  Android 11+) and lends elevated privileges to other apps; privileges persist until reboot. With
  Shizuku, automation apps can toggle airplane mode, Wi-Fi tether, Bluetooth, kill apps, run
  restricted shell commands, change system settings, disable/uninstall apps — actions normal apps
  cannot do [21](https://www.reddit.com/r/tasker/comments/1lulpiq/dev_tasker_662beta_shizuku_integration/).
- **Known operational quirks (→ our bug list).** Boot auto-start needs a "trusted WLAN" (Android
  13+) and disabling ADB authorization timeout in developer options; some OEMs (e.g. OnePlus)
  require manually re-allowing "restricted settings" after reboot [21](https://www.reddit.com/r/tasker/comments/1lulpiq/dev_tasker_662beta_shizuku_integration/).
- **A whole class of AI phone-agents already exists**, validating demand: ClawGUI (on-device
  GUI-agent runner controlled via Shizuku), Mythara (local-first agentic AI OS layer, 65+
  on-device tools: calls, SMS, calendar, Termux, face recognition), Open-AutoGLM-Android
  (vision-language-model-driven device automation), OpenCyvis (AI phone that sees the screen and
  operates apps from natural language, works in background), OpenDroid (autonomous on-device agent
  planning and executing multi-step tasks via screen automation), OpenMinis (Linux shell + browser
  automation + system control via Shizuku), roubao (on-device AI phone automation via
  vision-language models, no PC needed), Ruto-GLM (multitasking framework with virtual screens /
  multi-window for agents) [20](https://github.com/timschneeb/awesome-shizuku/blob/master/README.md).
- **Only ONE UiAutomation service can run at a time.** Shizuku-mode automation uses Android's
  UiAutomation framework; while the automation service is active, other UiAutomation consumers
  (automation test tools, Thanox) fail to register — a real compatibility constraint [22](https://github.com/xjunz/AutoTask/blob/master/README.md).
- **Companion infrastructure exists for persistence and stealth-safety:** Service-Keeper
  auto-restarts services the system kills; IMD hides developer options/ADB/Shizuku from
  restrictive apps like banking apps, then restores them; Dhizuku shares DeviceOwner permissions
  with third-party apps [20](https://github.com/timschneeb/awesome-shizuku/blob/master/README.md).
- **Accessibility-service mode is the non-privileged fallback.** Automation assistants support
  both Shizuku (privileged, UiAutomation) and AccessibilityService (unprivileged, event-driven)
  modes, with system-level keep-alive in both [22](https://github.com/xjunz/AutoTask/blob/master/README.md).

### Problems → Parth ideas

| Problem | Parth capability |
|---|---|
| Apps can't modify system settings | **Shizuku bridge**: privileged system ops (settings, tether, airplane, permissions, app control) with an explicit permission broker UI ("grant everything I allow") |
| Agents need to *see* the screen | Screenshot → vision model → grounded taps/swipes via Accessibility/UiAutomation; layout-tree reading in a11y mode |
| Service killed by OEM battery savers | Foreground service + Service-Keeper-style watchdog + boot auto-start (with the Shizuku trusted-WLAN caveat documented) |
| Banking apps detect dev modes | Optional IMD-style stealth profile toggle |
| One UiAutomation at a time | Mode manager: detect conflicts, offer a11y fallback |
| "Do it like a human" | Human-paced interaction profiles (delays, natural scroll), multi-window/virtual display via Ruto-GLM-style approach |

---

## 8. Voice-assistant pain points (cross-cutting every persona)

- **Understanding is the #1 pain.** 60% of voice-assistant users say accurate understanding of
  prompts is one of their primary challenges; 38% cite irrelevant/inaccurate responses; 36% cite
  privacy/security concerns; 19% cite expectation mismatches; 16% trouble connecting with other
  apps/devices; 13% lack of personalization [23](https://www.voices.com/company/press/reports/voice-assistants).
- **Untapped potential.** 46% of users feel they're not using assistants' full capability; 45%
  would use them more if they were "smarter"; Google even discontinued 17 underutilized Assistant
  functions [23](https://www.voices.com/company/press/reports/voice-assistants).
- **Privacy fear of always-listening.** 52% worry about voice assistants listening to private
  conversations in the background [24](https://www.capgemini.com/wp-content/uploads/2019/09/Report-%E2%80%93-Conversational-Interfaces_Web-Final.pdf).
- **Irritation drivers.** Dissatisfied users report problems with responsiveness, usability,
  connectivity and compatibility; frustration at assistants *repeating commands back*, *performing
  actions not asked for*, or *going silent* [26](https://www.sciencedirect.com/science/article/abs/pii/S0268401223000439).
- **Multi-command & noise failures at home** [25](https://www.tandfonline.com/doi/full/10.1080/0144929X.2026.2619105?scroll=top&needAccess=true).

### Design answers baked into Parth (owner requirements validated by research)

| Research finding | Parth design decision |
|---|---|
| 52% fear passive listening | Wake word "Parth" detected **on-device**; mic hot-word only until armed |
| Assistants talk over people / repeat commands | **Barge-in**: the moment the user speaks, Parth goes silent and listens |
| Long autonomous runs need a kill switch | Stop word "**Viram**" (replaces the earlier "Prasthan" design) halts speech and work instantly |
| 46% untapped potential / 19% expectation gap | One assistant, 151+ cataloged capabilities, honest capability manifest |
| 16% can't connect to other apps | Phone-use (Shizuku/a11y) + desktop computer-use + browser + API connectors |
| 13% no personalization | Personality/memory system; user-importable skills, agents, tools |

---

## 9. Idea matrix — problem → Parth capability → persona served

| # | Problem (source §) | Parth capability | Personas |
|---|---|---|---|
| 1 | Mental load / life admin (§1) | Memory & reminder agent, weekly admin batch | Home |
| 2 | 117 emails + 153 chats/day (§2) | Triage + draft-reply agent with approval gate | Office |
| 3 | 60% work-about-work (§2) | Status-report automator, meeting agent | Office |
| 4 | 275 interruptions/day (§2) | Focus-guard: hold-and-summarize interrupts | Office |
| 5 | 2–6× crash risk manipulating phone (§3) | Voice-only driving mode, auto-reply | Driver |
| 6 | Travel admin (§3) | Itinerary/packing/booking agent | Traveller |
| 7 | Away from phone, wants report (owner) | Cross-device voice call report | All |
| 8 | Idea block (51%) (§4) | Trend-scanning idea engine | Creator |
| 9 | Post-everywhere burnout (45%) (§4) | One-utterance multi-platform publish pipeline | Creator |
| 10 | 8 creator jobs at once (§4) | Creator company: editor/SEO/thumbnail/engagement agents | Creator |
| 11 | Algorithm punish-fear (75%) (§4) | Scheduled workflow store ("daily at 18:00") | Creator |
| 12 | 8-sec AI clips, drift (§5) | Storyboard→generate→stitch orchestration w/ character refs | Producer |
| 13 | Indie director plays every role (§5) | Virtual crew agents | Producer |
| 14 | Actor-likeness consent (§5) | Rights & consent ledger | Producer |
| 15 | Cost-per-finished-clip (§5) | Budget guard + model routing | Producer |
| 16 | Agent prototype→prod gap (§6) | Typed steps, retries, limits, traces, dry-run default | Developer |
| 17 | Tool overload (§6) | Department agents w/ narrow toolsets | Developer |
| 18 | Skill supply-chain risk (§6) | Signed import/export packages | Developer |
| 19 | System-level phone control (§7) | Shizuku bridge + permission broker | Phone-power-user |
| 20 | Agents can't see screen (§7) | Screenshot→VLM→grounded action loop | Phone-power-user |
| 21 | Service killed / boot issues (§7) | Watchdog + boot receiver + trusted-WLAN handling | Phone-power-user |
| 22 | Misunderstanding (60%) (§8) | On-device wake + cloud STT + confirmation for destructive ops | All |
| 23 | Assistants talk over you (§8) | Barge-in silence + listen | All |
| 24 | No kill switch (§8) | "Viram" hard-stop for speech and work | All |
| 25 | Expectation gap (§8) | Honest 151+ capability catalog, per-capability manifest | All |

---

## 10. Source index

1. Workplace Distraction Statistics — makerstations.io
2. Workplace productivity statistics — breeze.pm
3. Time Management Statistics — byoxon.com
4. Workplace Mental Health Statistics — makerstations.io
5. Employee Productivity Statistics — high5test.com
6. Creator burnout 78% — thecreatoreconomy.com
7. Creator Economy Statistics — wpbeginner.com
8. Content Creation Challenges — shortvids.co
9. Content creator pros & cons — hercozycrew.com
10. Generative AI in film productions (legal) — taylorwessing.com
11. Generative AI for Film Creation: Survey — CVPR 2025 Workshop
12. Impact of Generative AI on Filmmaking — vibecentral.ai
13. 2026 AI Video Production Playbook — Medium (Data Science Collective)
14. AI's promise to indie filmmakers — TechCrunch
15. Production-Grade Agentic AI Workflows — arXiv 2512.08769
16. Why Enterprises Aren't Ready for Agentic AI — Gigster
17. AI Agents: Definitive Guide — Comet
18. The agentic reality check — Deloitte Insights
19. Building Production-Ready AI Agents — MLflow
20. awesome-shizuku — github.com/timschneeb
21. Tasker 6.6.2 Shizuku integration — r/tasker
22. AutoTask (Shizuku + AccessibilityService) — github.com/xjunz
23. Voice Assistant survey — Voices.com
24. Conversational Interfaces report — Capgemini
25. Households & voice assistants — Taylor & Francis
26. Voice assistant irritation study — ScienceDirect
27. Mental Load Checklist — everblog.com
28. Mental Load explainer — Beurer
29. Life admin & mental load — laurajadeprado.com
30. Distracted driving — IIHS
31. Dangers of texting while driving — FCC
32. Distracted driving by state — WhistleOut

(All URLs are embedded inline as citations above.)
