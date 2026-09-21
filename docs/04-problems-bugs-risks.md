# Parth — Problems, Errors, Bugs & Risks (honest engineering list)

> The owner asked: *"Dekho sari problems and error batao and bugs ko bhe"* — here is the complete
> honest list of everything that will fight back during the build, with mitigations. Items marked
> **[SOLVED-IN-REPO]** are already handled in this scaffold; **[MITIGATED]** have a designed
> countermeasure; **[OPEN]** needs work.

---

## 1. Android platform constraints (phone-use engine)

| # | Problem | Severity | Status / Mitigation |
|---|---|---|---|
| 1.1 | **Only ONE UiAutomation service can register at a time** (Shizuku privileged mode conflicts with test tools/Thanox) | High | [MITIGATED] Mode manager: a11y fallback when UiAutomation is taken; detect and inform |
| 1.2 | **Shizuku privileges die on reboot**; wireless-ADB auto-start needs trusted WLAN (Android 13+) + disabling ADB authorization timeout; some OEMs (OnePlus) re-block "restricted settings" | High | [MITIGATED] Boot receiver + root fallback (owner's phone is rooted — root start is reliable); document per-OEM steps |
| 1.3 | **OEM battery-optimization killers** (Xiaomi/Oppo/Vivo/Huawei) murder background services | High | [MITIGATED] Foreground service + Service-Keeper-style watchdog + user setup wizard ("ignore battery optimizations", autostart whitelist) |
| 1.4 | Background **microphone access** restricted since Android 9+; always-on listening needs foreground service + user trust | High | [MITIGATED] On-device-only wake word; hot mic audio never leaves device until "Parth" is heard |
| 1.5 | `SYSTEM_ALERT_WINDOW` (floating windows) needs Settings canary on many ROMs | Medium | [MITIGATED] Setup wizard grants it; fallback to full-screen result activity |
| 1.6 | AccessibilityService + notification-listener permissions reset or get killed; Play-store policy restricts a11y usage declaration | Medium | [SOLVED-IN-REPO for sideload] Owner installs via sideload — no Play policy; still declare usage honestly |
| 1.7 | Banking/finance apps detect root, ADB, dev options and refuse to run | Medium | [MITIGATED] IMD-style stealth profile toggle (hide dev options/Shizuku when launching banking apps) |
| 1.8 | **Modded apps** (owner's mod YouTube/Instagram) update and break automation selectors; they also risk account bans | High | [MITIGATED] Vision-based (VLM) interaction instead of brittle selectors + selector packs per app version; ban-risk documented §2 |
| 1.9 | Screen automation race conditions: app loads slow, animations, CAPTCHAs, permission popups | Medium | [MITIGATED] Self-healing policy (spec §2.4): wait-for-state, retry, escalate; CAPTCHA → notify owner |
| 1.10 | Parallel actions on ONE phone are physically impossible (one focus) | Medium | [MITIGATED] Device mutex in Executor + Android multi-window/virtual-display track (Ruto-GLM approach) |
| 1.11 | Termux: Android 10+ `W` lock kills background sessions; tmux server dies with it | Medium | [MITIGATED] Acquire wakelock, disable phantom process killer (ADB/root), keepalive script |
| 1.12 | Battery drain from always-on wake word + VAD | Medium | [OPEN] Use DSP-backed hotword (PM/QDSP paths), duty-cycled VAD; measure in field tests |

## 2. App-automation & platform-policy risks (WhatsApp/IG/YouTube/… automation)

| # | Problem | Severity | Status / Mitigation |
|---|---|---|---|
| 2.1 | **WhatsApp bans unofficial automation/bulk messaging** — mass sends from modded clients are the #1 account-ban cause | Critical | [MITIGATED] Rate caps, human-paced delays, per-day message limits, warm-up curves, group-message batching; owner informed ban risk is real |
| 2.2 | Instagram/Facebook detect scripted behavior (device fingerprints, velocity) → action blocks | High | [MITIGATED] Same pacing caps + engagement-pattern humanization; avoid modded clients for sensitive actions |
| 2.3 | **YouTube's July 15, 2025 policy**: low-effort/repetitive AI content demonetized | High | [MITIGATED] Legal/Compliance agent runs originality + disclosure checks pre-upload |
| 2.4 | Logging into AI-video sites / Netlify / Google Cloud via the owner's Gmail → 2FA prompts, "suspicious activity" locks | High | [MITIGATED] Owner pre-authorizes sessions; credential vault with per-service session persistence; approval gate on 2FA |
| 2.5 | **Scraping 100+ leads/day and messaging 101 prospects/day** can violate CAN-SPAM/GDPR/PECR and platform ToS; legal exposure varies by country | High | [MITIGATED] Compliance caps, opt-out handling, jurisdiction rules in Legal agent; final call stays with owner (documented consent) |
| 2.6 | Netlify free-tier deploy limits; site spam detection | Medium | [MITIGATED] Deploy queue with per-account caps |
| 2.7 | Google Cloud training costs money uncontrollably if a loop misfires | High | [SOLVED-IN-REPO design] Budget guard: hard spend cap checked before every training job; alert threshold |
| 2.8 | AI-video platforms change UI/quotas weekly (free tiers churn) | Medium | [MITIGATED] Connector abstraction: provider registry, multiple fallbacks, health checks |

## 3. Agent-level problems (the hard AI part)

| # | Problem | Severity | Status / Mitigation |
|---|---|---|---|
| 3.1 | **Hallucination cascade** — one wrong early value corrupts the whole run | Critical | [SOLVED-IN-REPO] Typed deterministic spine; dry-run default; approval gates before irreversible actions |
| 3.2 | Infinite loops / runaway costs on "keep working until Viram" | Critical | [SOLVED-IN-REPO] `max_steps`, `step_timeout`, per-loop day caps, cancel event wired to "Viram" |
| 3.3 | **Prompt injection through screen/web content** (a malicious page tells the agent to do something) | Critical | [OPEN→DESIGNED] Content firewall: screen text is data, never instructions; dangerous verbs require explicit owner confirmation; allowlist of instruction sources |
| 3.4 | Tool overload reduces reliability (research §6) | High | [SOLVED-IN-REPO] Company-org routing gives each agent a narrow toolset |
| 3.5 | Non-determinism makes debugging a black box | High | [SOLVED-IN-REPO] Structured `ExecutionReport` per run; every step emits trace events; audit log |
| 3.6 | Cross-app state consistency (message replied in step 3, deleted in step 7) | Medium | [MITIGATED] Task scratchpad + idempotency keys per step |
| 3.7 | Memory drift (old facts overriding new) | Medium | [MITIGATED] Append-only log + recency-weighted retrieval; user-visible memory inspector |
| 3.8 | Barge-in false positives (TV noise triggers "user speaking") | Medium | [OPEN] VAD threshold tuning + wake-word re-arm requirement; field-test on owner's device |
| 3.9 | Hinglish STT accuracy for code-mixed speech | Medium | [OPEN] Best-of-breed STT comparison (Indic + code-mixed benchmarks); custom vocabulary (owner's contact names!) |

## 4. Security risks (rooted + privileged assistant = high-value target)

| # | Problem | Severity | Status / Mitigation |
|---|---|---|---|
| 4.1 | A privileged, always-listening assistant with every permission is a **single point of total compromise** | Critical | [MITIGATED] All action-capable surfaces behind approval gates; audit log; no remote-control channel without paired-device crypto handshake |
| 4.2 | Skill/plugin supply-chain attacks (malicious imported skills) — the #1 agent runtime risk per OWASP AST10 | Critical | [DESIGNED] Signed manifests, import review screen, sandboxed step execution, capability declarations |
| 4.3 | Credential storage (Gmail, Netlify, GCloud tokens) on a rooted phone | Critical | [MITIGATED] Android Keystore (strongbox where available) + optional off-device secrets manager; never log secrets |
| 4.4 | Shizuku privilege lending means any app the owner grants can act as ADB | High | [MITIGATED] Parth shows exactly which privileges are lent, to whom, with revocation UI |
| 4.5 | Physical access to a rooted always-unlocked automation phone | High | [OWNER-DECISION] Documented: keep device physically secured; screen-lock policy recommended |

## 5. Product/process risks

| # | Problem | Severity | Status / Mitigation |
|---|---|---|---|
| 5.1 | "AGI-level" expectations vs bounded, auditable autonomy | High | [DOCUMENTED] Spec §10 sets the honest line: extreme capability, bounded autonomy |
| 5.2 | Building everything at once → nothing works | High | [SOLVED-IN-REPO] Layered milestone plan (§7); core spine already runs & tests green |
| 5.3 | Play Store distribution impossible for this permission profile | Medium | [DOCUMENTED] Sideload + own update channel (owner-controlled) |
| 5.4 | 101 client-approaches/day assumes reply quality ≥ human freelancer | Medium | [OPEN] Proposal QA loop (CEO agent review) + A/B personalization; start at 20/day and ramp |

## 6. The "condensed AI model" goal — honest engineering assessment

Owner wants a real AI model with **vision + TTS + STT + S2S + agentic ability**, trained on Google
Cloud, built on *new technology where fewer parameters hold more knowledge* (not today's
parameters-grow-with-data paradigm). Reality check + credible plan:

1. **What exists today that matches the intent:** knowledge distillation (small student models
   inheriting large-teacher capability), Mixture-of-Experts (active parameters ≪ total), extreme
   quantization (1–4-bit), Matryoshka representations (nested embedding sizes), and
   retrieval-augmented memory (knowledge stored *outside* weights). A "condensed" Parth model =
   distilled MoE multimodal student + external memory — this is a real research direction, not
   fantasy.
2. **What is NOT realistic:** training a from-scratch foundation model from the phone/laptop —
   even "small" multimodal models need GPU clusters and curated data pipelines.
3. **Credible track (roadmap Phase 4):** pick an open multimodal backbone → distill to ≤3–4B
   active params (LoRA/QLoRA fine-tunes for Hinglish + agentic function-calling) → quantize for
   on-device → wire to Parth's tool spine → training jobs on Google Cloud with **budget caps**
   (risk 2.7) and dataset-consent vetting (Legal agent).
4. **Sprint-1 status:** the *agentic spine* the model plugs into is built, tested and running in
   this repo (`parth-core/`). The model track starts once connectors are live (Phase 3).

## 7. Known bugs/limitations in THIS repo scaffold (v1)

Being fully honest per owner instruction ("koi error ho to pehle khud solve karo, phir batao" —
solved what I could, listing the rest):

1. **Connectors are dry-run stubs** — they simulate and log; real WhatsApp/Gmail/YouTube API and
   device bridges are the next build phase. *(Deliberate: safe-to-run repo.)* [OPEN]
2. **Android side is scaffold sources** — complete architecture files, but needs a Gradle build on
   a machine with the Android SDK; wake word engine needs a real model (recommend openWakeWord
   custom "Parth" model or Porcupine custom keyword). [OPEN]
3. **Planner is keyword-deterministic** — bulletproof for the cataloged verbs, but the LLM planner
   (which handles arbitrary phrasing) plugs into `TaskPlan` and is not yet wired to a live model. [OPEN]
4. **No TTS/STT engines wired** — voice layer interfaces exist (`assistant.on_say` /
   `on_user_voice`), engines land with the Android build. [OPEN]
5. **Skill manifests are not yet cryptographically signed** — validation exists, signatures are
   Phase 3. [OPEN]
6. **Scheduler runs while the host process lives** — daemonization/systemd + Android
   `AlarmManager` are the platform-side implementations. [OPEN]
7. Multi-device call-reporting requires a telephony/SIP bridge — designed (`connectors.system.
   call_reporter`), implementation pending SIM/VoIP choice. [OPEN]

---

## 8. Risk acceptance summary (owner sign-off requested)

- I accept WhatsApp/Instagram ban risk from automation (with pacing caps). ☐
- I accept legal responsibility for outreach volume (compliance caps active by default). ☐
- I approve the "condensed model" research track as defined in §6. ☐
- I understand destructive actions always ask me first (my own requirement). ☐
