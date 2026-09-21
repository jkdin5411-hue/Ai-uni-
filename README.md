# Parth (Ai-uni-)

**Voice-first, always-on, autonomous agentic assistant** that uses devices like a
human — operating a rooted/Shizuku Android phone, desktops, laptops and the
browser — to complete extreme multi-step, multi-app tasks from **one spoken
instruction**.

- **Wake word:** `Parth` — say the name to activate.
- **Stop word:** `Viram` (विराम) — replaces the removed "Prasthan" design; halts
  speech and work instantly, ends the session.
- **Barge-in:** the moment you start speaking, Parth goes silent and listens.
- **Run once, run forever:** started once, it keeps running (app-back, screen-off,
  reboot) — foreground service + boot receiver on Android.
- **151+ capabilities:** every Skill / Agent / Tool supports **Create · Import ·
  Export · Add More** (`.parth.json` packages).
- **A company inside:** CEO, CTO, Marketing, Finance, Social Media, Legal, HR,
  Research, Content Studio, Security, Operations — parallel department agents.
- **Safety your way:** destructive actions (delete/send money/post public) always
  ask first — your own rule — and long runs stop at "Viram" or the configured
  limit.

## Repository map

| Path | What it is |
|---|---|
| `docs/01-research-problems-and-ideas.md` | **Internet-wide research**: problems & pains of everyday people, office workers, drivers/travellers, content creators, film/web-series producers, AI engineers/freelancers/developers, and phone-automation power users — each mapped to Parth capabilities (with sources) |
| `docs/02-parth-product-spec.md` | Full product spec: interaction model, control words, device coverage, capability system, company org, acceptance scenarios (your example tasks) |
| `docs/03-architecture.md` | Technical architecture & repository layout |
| `docs/04-problems-bugs-risks.md` | **The honest problems/errors/bugs/risks list** with mitigations + what's still open |
| `parth-core/` | **Runnable cross-platform agent core** (Python, stdlib-only, 39 tests green) |
| `android/` | Android app scaffold (Kotlin): foreground service, wake word, accessibility phone-control, Shizuku bridge, floating result window, boot receiver |
| `skills/` | Example importable/exportable skill packages (`.parth.json`) |

## Quickstart (core)

```bash
cd parth-core
python3 tests/test_core.py      # 39 tests — control words, planner, executor,
                                # registry import/export, scheduler, catalog ≥151
python3 demo.py                 # end-to-end dry-run of the mega multi-app task,
                                # Viram hard-stop, barge-in, save-&-repeat
```

No dependencies. Every connector runs in **dry-run** (safe simulation) — flip a
connector to real mode only when you enable it in-app.

## The demo in one line

One utterance — *"WhatsApp खोलो… Gmail साफ करो… AI platform पे video बनाओ…
YouTube/Instagram/Facebook/Telegram पर post करो… storage साफ करो… 50 clinics
खोजो, website बनाकर Netlify पर deploy करो… Google Cloud पर training start करो…
मेरे दूसरे phone पर call करके report करना"* — becomes a **36-step plan**
across 11 connectors with approval gates on every destructive/outbound action,
executed phase-parallel, stoppable any instant with **"Viram"**.

## Status & roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Research, spec, architecture, risk list, runnable core + tests + catalog (155) | ✅ done (this repo) |
| 2 | Android app build (Gradle), real wake-word model, phone-use engine on device | ⏳ scaffold ready |
| 3 | Real connectors (WhatsApp/Gmail/YouTube/…, Shizuku ops, desktop computer-use), signed packages | ⏳ |
| 4 | Live model layer (cloud + local GGUF), Hinglish fine-tune, "condensed model" R&D (distillation/MoE track — docs/04 §6) | ⏳ |

**Honest limits (docs/04 §7):** connectors are dry-run stubs; the Android side
needs a Gradle build on your machine; the LLM planner and real TTS/STT engines
plug into existing interfaces; skill signatures are designed, not yet enabled.

## Control words (final decision)

| Word | Effect |
|---|---|
| `Parth` | wake / arm listening / address the assistant |
| `Viram` | silence speech · stop/pause work · end session |
| ~~`Prasthan`~~ | removed — must never trigger anything (enforced in code & tests) |
