# judgment-trail roadmap

> The bigger argument for why this layer needs to exist: [`docs/auto-reflection.md`](./docs/auto-reflection.md).

The current tool captures Claude Code sessions only. That's roughly 20% of a heavy AI user's actual collaboration surface. Cross-LLM coverage is the obvious next move. Below is the staged buildout — what's shipped, what's next, and what's deferred.

## Where the project sits

judgment-trail today is a Claude Code-only practice tool that auto-captures sessions, classifies collaboration patterns against a controlled vocabulary, and synthesises trajectory across time. The strategic position it occupies is broader: the **human-side reflection layer for AI collaboration** — a parallel to what AI providers are building on the model side (persistent memory, agent monitoring, automation eval).

## Cross-LLM capture — staged buildout

| Version | Surfaces covered | Estimated share of a heavy user's AI engagement | Status |
|---|---|---|---|
| **v1** | Claude Code SessionEnd hook | ~20% | Shipped |
| **v2** | + Cursor SQLite watcher + Claude.ai conversation-export ingester | ~60% | Next |
| **v3** | + GitHub Copilot OTel watcher + ChatGPT conversation-export ingester + Windsurf | ~80% | Planned |
| **v4** | + MV3 browser extension for Perplexity, Gemini web, v0, the long tail | ~90% (brittle) | Deferred |

**Why staged.** No single install can cover 80% cleanly today — vendor surfaces are too heterogeneous. The realistic architecture is a local daemon that combines file watchers for surfaces with local data, scheduled vendor-export ingestion for surfaces without, and an opt-in API proxy for power users hitting providers directly. Each version is independently useful; we don't have to wait for v4 to make the tool more honest than v1.

## Render modes — one infrastructure, multiple interfaces

The same capture + taxonomy stack serves different audiences differently. We name them now; we build them after v2:

| Persona | What they need | Render mode |
|---|---|---|
| AI-heavy PM / builder, can't see what's eroding | Visibility | **Mirror** — patterns, synthesis, surrender signatures |
| Senior engineer skeptical of AI to preserve craft | Proof use can coexist with skill preservation | **Calibration** — show when augmentation is real vs. when delegation masks absent judgment |
| Junior dev whose human-administrative bits got eaten | Repositioning | **Contribution attribution** — surface where your shaping actually changed the output |
| Junior dev whose learning is threatened | Friction at the right moment | **Tutor mode** — graduated friction, prevent answer-grabbing |

## What's NOT on this roadmap

- A SaaS hosted product. Local-first, by design.
- A scoring system or "AI Judgment Score™" — the whole point is what gets reduced when patterns become numbers.
- Cross-user comparison — privacy-fraught, statistically thin, drives the wrong incentives.
- Real-time intervention during active sessions (yet). Mollick is right that blanket friction is insufferable. Tutor mode is opt-in by user, not on by default.

## How this evolves

If the strategic positioning ([`docs/auto-reflection.md`](./docs/auto-reflection.md)) survives external review (one credible AI researcher or institute reader engages with the argument), the next decisions become:

- Whether to push for adoption inside one large org (a curriculum play — picking the guild route)
- Whether to push for provider-level integration (an infrastructure play — picking the Anthropic route)
- Whether to keep it as personal-practice infrastructure (no scale ambition, but real for the people who use it)

These are different products. We don't have to decide yet. v2 + the position doc are the unblockers for that decision.
