# crux

## Framing

Two layers, and they don't mix.

**The instrument** is a practice tool, not a portfolio:

- **"AI fluency is measurable. AI judgment isn't."** — Anthropic's fluency index covers the floor. Crux captures what sits above it.
- The artifact paradox is the hook: polished AI output makes people less critical. There's no feedback loop for collaboration quality. Crux is that feedback loop.
- Practice, not performance. This is a training log (like a runner's log), not a CV or showcase. Primary audience is yourself. Legibility to others is a side effect.
- Never use "This is how I think" or similar personal branding language. The profile is called "Collaboration Log", not "Decision Profile".

**The public documents** (RESEARCH.md, docs/) carry a research position as of v2 (July 2026), and edits must preserve it:

- The quiet threat to work is capability erosion inside employment, not displacement. Output proxies can't detect it because output is the part the AI supplies.
- Canonical vocabulary — keep the terms stable, they are the asset: **cognitive surrender** (umbrella), **the ownership account**, **record of title**, **appetite atrophy**, **the contest rate**, **the defendability test**, **the craftsman tax** (Das's term, credited).
- **Crux is ongoing research, not a product.** Never frame it as a tool seeking adoption; frame it as a study with a replication path. Feature work is parked (see ROADMAP status note).
- The endgame is the **memo to the platform layer** (research.html#memo): instrument native, disclosure at sign-off, opt-in longitudinal panel. Not a SaaS — the anti-surveillance constraint is the position, not a limitation.
- **Reflect (Anthropic, 9 Jul 2026) shipped tier one** — usage measurement on the chat surface (research.html#answered). Never claim "nobody measures the human" anymore; the claim is "nobody measures judgment." Timeline discipline: Reflect (9 Jul) preceded the v2 memo going live (10 Jul); the doc's ask dates to June. Always "the same week" / convergence — never causation.
- Differentiation from provenance/attestation tools: they certify the past; crux measures whether the person could do it again tomorrow. Never frame crux as proof for an adversary.

## Architecture

- `/marmite` captures session digests — collaboration patterns, not project changelogs
- `/trail` produces monthly synthesis grounded in Anthropic's AI Fluency Index (4D framework + 13 unobservable behaviors)
- `profile` command reads digests + synthesis and renders to markdown + HTML
- Auto-capture: `scripts/auto-digest.sh` → `scripts/digest-worker.sh` (SessionEnd hook)
- Backfill: `scripts/backfill-digests.sh` reformats legacy digests into the schema below (idempotent)

## Digest schema (RAG-queryable)

Every digest starts with YAML frontmatter so digests can be filtered/queried by an
LLM doing retrieval across history. The body is written in second person, leads
with a one-line embedding-ready punchline, and uses real user quotes where they land.

Frontmatter fields:
- `date`, `session_id` — keys
- `project` — kebab-case project slug (e.g. crux, writing, general)
- `duration` — short | medium | long
- `shape` — research | shipping | refinement | planning | debugging | writing | mixed
- `interaction_type` — directive | feedback-loop | task-iteration | validation | learning (Anthropic Economic Index)
- `collaboration_mode` — automation | augmentation (Anthropic Economic Index)
- `fluency` — per-dimension {strong | medium | weak | not-observed} for delegation/description/discernment/diligence
- `patterns` — controlled vocab from `taxonomy/patterns.yml` (1-4 slugs, must match exactly)
- `concepts` — free-form topical kebab-case tags (3-6)
- `related` — list of prior session_ids if a trajectory arc exists

Body sections (stable, in order):
1. Title + TL;DR blockquote
2. `## The moment` — defining decision, with verbatim user quote if available
3. `## What you steered` — second person, embed quotes
4. `## What you let slide` — honest, no padding
5. `## The pattern` — bold one-liner + expansion
6. `## Trajectory note` — [[wikilink]] to prior session if there's an arc

## Pattern taxonomy

`taxonomy/patterns.yml` is the controlled vocab. Add new patterns here before
using them — RAG retrieval depends on stable spelling across sessions.

## Rules for all output

- No internal project details, architecture, env vars, column names, file paths, or service names in any public-facing file (digests, synthesis, profile, README)
- Quality bar for digests: "would a senior engineer reading this learn something about how this person thinks? If not, cut it."
- Ground every synthesis observation in evidence from digests. Don't infer what isn't there.
- Watch for multi-session coordination patterns — how the user orchestrates parallel Claude sessions is signal.
- Never fabricate user quotes. Only italicise text that appears verbatim in the source transcript.
- Body is second person ("you"). Frontmatter is structured. No prose classification inside the body.

## Auto Dream integration

Crux and Auto Dream form a feedback loop:

1. `/marmite` captures session digests including memory persistence signals (corrections that stuck vs. had to be re-taught)
2. `/trail` synthesizes patterns and writes `memory-bridge.md` — the 3-7 most durable collaboration preferences, phrased as actionable instructions
3. Auto Dream consolidates `memory-bridge.md` into working memory during its normal consolidation cycle
4. Next session: Claude starts with those preferences already loaded → marmite tracks whether they held

The memory bridge is the handoff point. It ages naturally — preferences that stop appearing in digests drop out at next synthesis. No manual pruning needed.

## Key references

- [Anthropic AI Fluency Index](https://www.anthropic.com/research/AI-fluency-index) — 4D framework, artifact paradox, 13 unobservable behaviors
- [Victoria Ferrier: AI Is The Wrong Unit of Analysis](https://www.linkedin.com/pulse/ai-wrong-unit-analysis-victoria-ferrier-gbasc/) — human capacity > AI capability
- [Matt Shumer: Something Big Is Happening](https://blog.mattshumer.com/p/something-big-is-happening) — differentiation urgency
