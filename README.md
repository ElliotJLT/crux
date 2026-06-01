# decision-trail

[![Decision Profile](https://img.shields.io/badge/profile-live-blue)](https://elliotjlt.github.io/decision-trail/)

**You're shipping faster than ever. Are you also getting sharper — or just getting carried?**

---

## The problem no one tracks

You commit code. You close tickets. You ship features. Your output has never been higher.

But output isn't the same as judgment. And right now, nothing measures whether the human behind the AI is improving, plateauing, or quietly atrophying.

Anthropic studied [nearly 10,000 conversations](https://www.anthropic.com/research/AI-fluency-index) and found that when AI produces polished output, users become *less* critical — they stop questioning, stop fact-checking, stop pushing back. They call it the **artifact paradox**. The better the AI gets, the easier it is to coast.

When they [interviewed 80,508 Claude users](https://anthropic.com/features/81k-interviews), cognitive atrophy was the #4 concern. 13,000 people explicitly worried about it. Nearly half already felt it.

> "I don't think as much as I used to. I struggle to put the ideas I do have into words." — Heavy AI user, United States

Wharton has now codified the umbrella term: **cognitive surrender**. Ethan Mollick's [*Choosing to Stay Human*](https://www.oneusefulthing.org/p/choosing-to-stay-human) (May 2026) makes the case that the answer isn't user-level willpower but system-level constraints. This is the gap judgment-trail exists to surface.

This isn't about using AI less. It's about knowing whether you're still thinking while you use it.

## Fluency is table stakes

Anthropic's [4D framework](https://www.anthropic.com/ai-fluency/overview) — Delegation, Description, Discernment, Diligence — defines baseline AI competency. Courses will teach it. Everyone will pass. It stops being a differentiator fast.

What separates people who get better with AI from people who get carried by it is a layer above fluency:

- **Trust calibration** — knowing when to let the AI run vs when to check its work. Task-by-task, not blanket.
- **Artifact paradox resistance** — the more polished the output looks, the harder you examine it.
- **Meta-cognition** — correcting the AI's process, not just its output.
- **Strategic killing** — deciding what not to build, even when the AI builds it well.
- **Pattern recognition** — seeing your own habits across sessions, not just within them.

These are dispositions, not skills. You develop them through practice — but only if you can see them. Your GitHub shows what got committed. It doesn't show what you rejected, redirected, or killed.

## decision-trail

A practice for developing AI judgment. Like a training log for a runner — the primary value is to you.

**Zero commands. Zero friction.**

A [Claude Code hook](https://code.claude.com/docs/en/hooks.md) fires when every session ends. It reads the transcript, extracts collaboration patterns, and generates a digest automatically. You don't invoke anything. You don't remember anything. You just work.

For manual sessions, `/marmite` still works — type it at the start, say "wrap" when you're done, and Claude silently tracks the moments where you redirect, reframe, set a quality bar, or kill a direction.

### What a digest looks like

```markdown
# 2026-02-23 — eval scoring diagnosis

~4h research session. Suspected a generation problem, investigated before fixing.

- Instinct to diagnose before treating — scores looked bad but the question
  was whether the answers were wrong or the measurement was wrong. Chose to
  investigate the scorer first.
- Conservative fix philosophy: built targeted matchers with guards that would
  rather miss a match than fabricate one. Precision over recall.
- Refused to chase a low score when the test conditions were unreliable.
  Flagged it as bad data instead of reacting to the number.
- Held the fix as research rather than shipping immediately. Won't merge
  until re-validated under correct conditions.
- Pattern: diagnose root cause before touching anything, don't ship under
  uncertainty, resist the urge to fix what isn't broken.
```

Skimmable in 15 seconds. No scores. No self-assessment. Just a record of how someone actually thinks when building with AI.

### Surfacing patterns over time

Individual digests capture sessions. The real signal is in the trajectory across them.

Run `/trail` periodically to generate a synthesis:

```markdown
# Synthesis — February 2026 (3 sessions)

## Recurring patterns
- Consistently diagnoses root cause before fixing. Two sessions where the
  obvious fix was wrong and investigation saved significant rework.
- Delegates mechanical execution freely but always verifies judgement calls.
  Trust is calibrated by task type, not blanket.

## Evolution
- First session: accepted AI-generated digests at face value. By third
  session: caught the digest leaking architecture and rewrote the skill.
  Meta-awareness of AI output quality is increasing.

## Beyond fluency
- Artifact paradox resistance: actively challenges polished output in 2/3
  sessions. This is the behaviour Anthropic's research shows most users
  stop doing.
```

The synthesis surfaces whether your collaboration instincts are sharpening, plateauing, or eroding. You can't course-correct a disposition you can't see.

## Who This Is For

- **Engineers** already building with AI who want a feedback loop for judgment, not just code.
- **Tech leads** who need to develop their team's AI collaboration instincts, not just their prompt skills.
- **Hiring managers** looking for a signal beyond code tests — [aptitude assessments are up 54x since 2024](https://gritdaily.com/software-dev-hiring-shifting-from-syntax-to-judgment/) because nothing else exists.
- **Teams** where [tacit knowledge is disappearing](https://aijourn.com/are-we-automating-professional-services-into-a-knowledge-crisis/) — digests are a knowledge transfer mechanism. Juniors can read how seniors think.

## Where this is heading

judgment-trail today is a Claude Code-only practice tool. The position it occupies is the **human-side reflection layer** for AI collaboration — a parallel to what providers are building on the AI side (Anthropic's [Auto Dream](https://platform.claude.com/docs/en/managed-agents/dreams), persistent memory; OpenAI's chat memory; etc).

The roadmap (see [`ROADMAP.md`](./ROADMAP.md)) covers cross-LLM capture (Cursor, Claude.ai exports, Copilot OTel, ChatGPT exports), persona-specific render modes, and the strategic position doc [`docs/auto-reflection.md`](./docs/auto-reflection.md) — the longer argument for why this layer needs to exist.

## Setup

### Auto-capture (recommended)

Clone the repo and hook it into Claude Code:

```bash
git clone https://github.com/ElliotJLT/decision-trail.git ~/decision-trail
chmod +x ~/decision-trail/scripts/auto-digest.sh ~/decision-trail/scripts/digest-worker.sh
```

Then add the SessionEnd hook to your global Claude Code settings (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/decision-trail/scripts/auto-digest.sh"
          }
        ]
      }
    ]
  }
}
```

That's it. Every session with 4+ user messages now generates a digest automatically when you exit. Short sessions and trivial ones (config, installs, quick lookups) are skipped. Digests land in `decisions/digests/`.

Each digest is automatically classified using Anthropic's [Economic Index](https://www.anthropic.com/research/the-anthropic-economic-index) framework — tagging the interaction type (directive, feedback-loop, task-iteration, validation, learning) and collaboration mode (automation vs augmentation).

**Requires:** `jq`, `python3`, and `claude` CLI in your PATH. The install script checks for these.

**Custom install path:** Set `DECISION_TRAIL_DIR` to override the default `~/decision-trail` location.

**Opt out** of auto-capture for a specific project by dropping an empty file in its root:

```bash
touch /path/to/project/.dt-skip
```

Or skip globally for a session with `DT_SKIP=1`.

### Manual commands (optional)

```bash
mkdir -p ~/.claude/commands
curl -o ~/.claude/commands/marmite.md \
  https://raw.githubusercontent.com/ElliotJLT/decision-trail/main/.claude/commands/marmite.md
curl -o ~/.claude/commands/trail.md \
  https://raw.githubusercontent.com/ElliotJLT/decision-trail/main/.claude/commands/trail.md
```

`/marmite` gives richer in-session tracking (it observes as you work, not post-hoc from the transcript). `/trail` generates monthly synthesis. Both work in every project.

### Auto-synthesis (optional)

Once you have 5+ digests, generate a trajectory synthesis:

```bash
~/decision-trail/scripts/synthesize.sh
```

This produces a synthesis in `decisions/synthesis/YYYY-MM.md` that shows:
- Your augmentation/automation split vs Anthropic's 59% augmentation benchmark
- Which interaction types you use most (and which you're missing)
- Trend direction — improving, flat, or declining
- Coasting alerts if you're drifting toward directive-heavy sessions

Run it weekly via cron, or just run `/trail` which covers the same ground.

### CLI (optional)

```bash
pip install decision-trail

# Cognitive engagement dashboard
decision-trail metrics

# Generate your shareable profile
decision-trail profile --format both

# Preview locally
decision-trail serve
```

## The Thesis

Everyone will be fluent. [Anthropic can measure it](https://www.anthropic.com/research/AI-fluency-index), courses can teach it, and the floor is rising fast enough that it stops being a differentiator. But population-level measurement (how do people use AI on average?) is different from individual measurement (how do *you* use AI, and is it changing?). decision-trail bridges that gap.

Anthropic is already teaching people to write [AI diligence statements](https://www.anthropic.com/tutorials/writing-an-ai-diligence-statement) — transparent disclosures of what AI did, what you did, and how you verified the result. It takes 10 minutes per deliverable when you do it manually.

What can't be taught is the layer above fluency: the instinct to challenge, the discipline to kill, the judgment to know when the AI is confidently wrong. [Ferrier calls it Learning Power](https://victoriaferrier.substack.com/p/ai-is-the-wrong-unit-of-analysis). [Shumer calls it the thing that makes you irreplaceable](https://shumer.dev/something-big-is-happening). [Osmani calls it taste](https://addyosmani.com/blog/next-two-years/).

decision-trail captures that layer automatically — by making it visible to the person who needs to see it most: you.

## Reading

- [Ethan Mollick: Choosing to Stay Human](https://www.oneusefulthing.org/p/choosing-to-stay-human) (May 2026) — Codifies Wharton's "cognitive surrender" as the umbrella term. Argues the answer is system-level constraints, not user-level willpower. The intellectual anchor for what this tool is for.
- [Anthropic: Auto Dream — Managed Agent Memory Consolidation](https://platform.claude.com/docs/en/managed-agents/dreams) (May 2026) — Anthropic's own memory layer for AI. judgment-trail is the parallel for the human side.
- [Anthropic: What 81,000 People Want from AI](https://anthropic.com/features/81k-interviews) — Cognitive atrophy is the #4 concern. 13,000 users worried about it. Half already feel it.
- [Anthropic: Writing an AI Diligence Statement](https://www.anthropic.com/tutorials/writing-an-ai-diligence-statement) — The manual version of what decision-trail automates
- [Anthropic: The AI Fluency Index](https://www.anthropic.com/research/AI-fluency-index) — Why polished output makes people less critical
- [Anthropic: The Anthropic Economic Index](https://www.anthropic.com/research/the-anthropic-economic-index) — How AI is used in the economy: automation vs augmentation, 5 interaction types, and the benchmark data decision-trail classifies against
- [Anthropic: The Impact of AI on Computer Science Education](https://www.anthropic.com/research/impact-of-ai-on-computer-science-education) — How AI changes skill acquisition and the case for deliberate practice
- [Victoria Ferrier: AI Is The Wrong Unit of Analysis](https://victoriaferrier.substack.com/p/ai-is-the-wrong-unit-of-analysis) — Human capacity, not AI capability, determines success
- [Matt Shumer: Something Big Is Happening](https://shumer.dev/something-big-is-happening) — The inflection point and why differentiation matters now
- [Taste Is the New Bottleneck](https://www.designative.info/2026/02/01/taste-is-the-new-bottleneck-design-strategy-and-judgment-in-the-age-of-agents-and-vibe-coding/) — Why judgment can no longer remain tacit
- [Addy Osmani: The Next Two Years](https://addyosmani.com/blog/next-two-years/) — What makes engineers valuable when AI codes
- [Hiring Is Shifting From Syntax to Judgment](https://gritdaily.com/software-dev-hiring-shifting-from-syntax-to-judgment/) — 54x increase in aptitude assessments
- [Are We Automating Into a Knowledge Crisis?](https://aijourn.com/are-we-automating-professional-services-into-a-knowledge-crisis/) — The tacit knowledge gap
- [Boris Cherny: What Happens After Coding Is Solved](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens) — Head of Claude Code on the builder role
- [AI vs Gen Z: The Junior Developer Crisis](https://stackoverflow.blog/2025/12/26/ai-vs-gen-z/) — How stepping-stone tasks are disappearing

## License

MIT
