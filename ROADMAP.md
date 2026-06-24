# crux roadmap

> The bigger argument for why this layer needs to exist: [`docs/auto-reflection.md`](./docs/auto-reflection.md).

crux today captures Claude Code sessions and synthesises collaboration patterns across time. The strategic position it occupies is broader: the **human-side reflection layer for AI collaboration** — the counterpart to what providers are building on the model side (persistent memory, agent monitoring, automated eval).

The roadmap runs on two axes. **Depth** — when in the decision lifecycle capture happens. **Breadth** — how many AI surfaces it covers. Depth currently outranks breadth, for a reason given below.

## Depth — when capture happens

The original tool had one temporal layer: after the session ends. The [Trail](./research/2026-06-09-the-trail-product-brief.md) (merged Jun 2026) adds the layer the project was missing — and the next one is already visible.

| Layer | Moment | What it captures | Status |
|---|---|---|---|
| **Digest** | After the session | What you steered, what you let slide, patterns over time | Shipped (SessionEnd hook, 50+ digests) |
| **The Trail** | At the irreversible command | Contemporaneous justification at one-way doors (force-push, prod migration, `DROP`, merge to default) | Day 1 shipped — dry-run classifier + [`taxonomy/cutlines.yml`](./taxonomy/cutlines.yml). Day 2 next: opt-in PreToolUse capture hook, off by default |
| **Delegation sign-off** | At acceptance of an autonomous run | The moment a run's invisible micro-decisions become yours. Disclosure ("the N decisions you'd most plausibly contest") → one real contest → trail | Designed, not built. `delegation` tier in cutlines.yml, then a disclosure hook at Stop |

**Day-1 evidence for why this axis leads.** The dry run over 192 real transcripts (2,668 commands, 22 active days) found irreversible moments are mechanically separable from routine — 0.41 fires/day, 0.45% selectivity. And the founding baseline: of 8 one-way doors with a captured preceding human message, **~6 were rubber stamps or blanket delegations**. Contemporaneous justification at the moments of highest consequence currently does not exist. The instrument captures net-new information.

**The metric this unlocks** is the project's first leading indicator: the rate at which justification is left blank (or contests are skipped) at one-way doors, tracked over time. Not a score — a descriptive read on whether the wanting-to-own is fading, before output quality ever shows it.

## Why depth before breadth

The discourse converged in a single week of June 2026. Mollick's [patron-era piece](https://www.oneusefulthing.org/p/what-it-feels-like-to-work-with): the human's contact with the work collapses to the brief, the mid-flight redirect, and the sign-off. Osmani's [Loop Engineering](https://addyosmani.com/blog/loop-engineering/): the job becomes designing systems that prompt the agents — with maker/checker verification for every component *except the human designing the loop*. Boris Cherny, head of Claude Code: "I don't prompt Claude anymore… my job is to write loops."

Fewer judgment moments, each carrying more weight, none of them instrumented. Adding capture surfaces (breadth) multiplies data about a shrinking phenomenon; instrumenting the remaining seams (depth) measures the thing that's actually at risk. So the Trail's Day-2 hook and the disclosure hook outrank the Cursor watcher.

## Breadth — cross-LLM capture, staged

Still real, still planned — resequenced behind the depth work.

| Version | Surfaces covered | Estimated share of a heavy user's AI engagement | Status |
|---|---|---|---|
| **v1** | Claude Code SessionEnd hook | ~20% | Shipped |
| **v2** | + Cursor SQLite watcher + Claude.ai conversation-export ingester | ~60% | Planned, after Trail Day 2 |
| **v3** | + GitHub Copilot OTel watcher + ChatGPT conversation-export ingester + Windsurf | ~80% | Planned |
| **v4** | + MV3 browser extension for Perplexity, Gemini web, v0, the long tail | ~90% (brittle) | Deferred |

**Why staged.** No single install can cover 80% cleanly today — vendor surfaces are too heterogeneous. The realistic architecture is a local daemon combining file watchers (surfaces with local data), scheduled vendor-export ingestion (surfaces without), and an opt-in API proxy (direct API users). Each version is independently useful.

## Render modes — one infrastructure, multiple interfaces

The same capture + taxonomy stack serves different audiences differently. Named now; built after the depth work and v2:

| Persona | What they need | Render mode |
|---|---|---|
| AI-heavy PM / builder, can't see what's eroding | Visibility | **Mirror** — patterns, synthesis, surrender signatures |
| Senior engineer skeptical of AI to preserve craft | Proof use can coexist with skill preservation | **Calibration** — when augmentation is real vs. when delegation masks absent judgment. The Trail's attestation record is the evidence base |
| Junior dev whose human-administrative bits got eaten | Repositioning | **Contribution attribution** — where your shaping actually changed the output |
| Junior dev whose learning is threatened | Friction at the right moment | **Tutor mode** — graduated, opt-in, scoped to learning contexts |

## What's NOT on this roadmap

- A SaaS hosted product. Local-first, by design.
- Scoring. No "AI Judgment Score™" — the appetite read stays descriptive (verbs and blank-rates, never a number). The whole point is what gets reduced when patterns become numbers.
- Cross-user comparison — privacy-fraught, statistically thin, drives the wrong incentives.
- Gating by default. The Trail captures at one-way doors; it does not block them. Blanket real-time friction is insufferable (Mollick is right); the gating tier exists only for cut-lines a user explicitly promotes.
- Cryptographic attestation theatre. Append-only local JSONL in git. A verification layer that can't establish what it asserts is worse than none.

## How this evolves

If the strategic positioning ([`docs/auto-reflection.md`](./docs/auto-reflection.md)) survives external review, the next decisions become:

- Whether to push adoption inside one large org (the curriculum route)
- Whether to push for provider-level integration (the infrastructure route)
- Whether to keep it as personal-practice infrastructure (no scale ambition, real for those who use it)

These are different products. The Trail's Day-2 data, the disclosure hook, and v2 are the unblockers for that decision.
