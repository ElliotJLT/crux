# crux roadmap

crux today captures Claude Code sessions and synthesises collaboration patterns across time. The strategic position it occupies is broader: the **human-side reflection layer for AI collaboration** — the counterpart to what providers are building on the model side (persistent memory, agent monitoring, automated eval).

The roadmap runs on two axes. **Depth** — when in the decision lifecycle capture happens. **Breadth** — how many AI surfaces it covers. Depth currently outranks breadth, for a reason given below.

## Depth — when capture happens

The original tool had one temporal layer: after the session ends. The Trail (merged Jun 2026) adds the layer the project was missing — and the next one is already visible.

| Layer | Moment | What it captures | Status |
|---|---|---|---|
| **Digest** | After the session | What you steered, what you let slide, patterns over time | Shipped (SessionEnd hook, 50+ digests) |
| **The Trail** | At the irreversible command | Contemporaneous justification at the rare, hard-to-undo moments | Day 1 shipped — dry-run classifier + [`taxonomy/cutlines.yml`](./taxonomy/cutlines.yml). Day 2 next: opt-in PreToolUse capture hook, off by default |
| **Delegation sign-off** | At acceptance of an autonomous run | The moment a run's invisible micro-decisions become yours. Disclosure ("the N decisions you'd most plausibly contest") → one real contest → trail | Designed, not built. `delegation` tier in cutlines.yml, then a disclosure hook at Stop |

**Day-1 evidence for why this axis leads.** The dry run over 192 real transcripts (2,668 commands, 22 active days) found the hard-to-undo moments are rare and mechanically separable from routine — 0.41 fires/day, 0.45% selectivity. And at those moments, contemporaneous justification essentially does not exist today. The instrument captures net-new information.

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

## The team layer — named, not sequenced

The practitioner accounts that surfaced through mid-2026 (Das's craftsman tax and the threads that followed; the ownership account in [`RESEARCH.md`](./RESEARCH.md)) point at two pains the individual instrument doesn't reach. Both are reads of data crux already captures, not new capture surfaces.

**Workflows have no home.** Skills, loops, and prompts accumulate per person — unversioned, unevaluated, unshared. Osmani's loop stack verifies every component of the loop, and nobody versions or owns the loop itself; when a loop rots, it rots silently until it's generating noise. The digest corpus already knows which workflows a person actually runs and how they change. A team-visible catalogue — which loops exist, who owns each, when it last changed, what its sessions look like — is a render mode over existing data. Ownership of a loop is also the honest answer to "what do I own now?" in a team where the AI executes: you own the system that does the work, versioned, evaluated, defensible.

**The retro gap.** Teams rebuilt their delivery process around AI in months and mostly never retro the collaboration itself, because there is no record to hold the retro over. A period of digests, shared by choice for one conversation, is the retro pack: pre-readable in ten minutes, argument-ready, grounded in what actually happened rather than what people remember feeling.

Constraint check, because this brushes against a hard line below: the Retro is voluntary shared reading of self-owned records, for a conversation. Not a dashboard, not a ranking, not visible to anyone the owner didn't hand it to. If it can't be built without becoming a surveillance surface, it doesn't get built.

Sequencing: behind Trail Day 2 and the disclosure hook. Named now because the render-mode table already implies the tech-lead reader, and because the team is where the ownership account says the damage is compounding.

## What's NOT on this roadmap

- A SaaS hosted product. Local-first, by design.
- Scoring. No "AI Judgment Score™" — the appetite read stays descriptive (verbs and blank-rates, never a number). The whole point is what gets reduced when patterns become numbers.
- Cross-user comparison — privacy-fraught, statistically thin, drives the wrong incentives.
- Gating by default. The Trail captures at one-way doors; it does not block them. Blanket real-time friction is insufferable (Mollick is right); the gating tier exists only for cut-lines a user explicitly promotes.
- Cryptographic attestation theatre. Append-only local JSONL in git. A verification layer that can't establish what it asserts is worse than none.

## How this evolves

If the strategic positioning survives external review, the next decisions become:

- Whether to push adoption inside one large org (the curriculum route)
- Whether to push for provider-level integration (the infrastructure route)
- Whether to keep it as personal-practice infrastructure (no scale ambition, real for those who use it)

These are different products. The Trail's Day-2 data, the disclosure hook, and v2 are the unblockers for that decision.
