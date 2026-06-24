# Crux — Market & Research Analysis

> Compiled: 2026-05-22
> Purpose: Understand the gap, the market, and the path to making this something Anthropic needs.

---

## The Thesis

Everyone measures whether the AI is good. Nobody measures whether the human still is.

$200M+ has been invested in AI observability, evals, and agent memory in the last 18 months. Every single funded company measures the model. Zero funded companies measure the human. The academic research is screaming that this matters. Anthropic's own research proves it. No product exists.

---

## Anthropic's Research — The Gap Map

| Research | What They Found | Product Exists? | The Gap |
|----------|----------------|-----------------|---------|
| **AI Fluency Index** | Artifact paradox: polished outputs suppress critical evaluation (-5.2pp context checking, -3.1pp reasoning questioning) | No | Real-time fluency coaching; nudges when user skips evaluation |
| **Disempowerment** | Users voluntarily cede judgment; rate it positively in the moment; detection needs to be session/user-level | Sycophancy reduction only | Cross-session pattern detection; user-level disempowerment alerts |
| **Coding Skills RCT** | Delegation kills learning (50% vs 67% quiz scores); comprehension-first users retain skills | Nothing shipped | Adaptive mode detecting delegation patterns, shifting to explanation |
| **Economic Index** | Experienced users iterate more, succeed 10% more; patterns are learnable | Nothing user-facing | Progressive interaction coaching; surface autonomy level to users |
| **Agent Autonomy** | Expert users monitor-and-intervene; novices approve-or-block | Basic permissions | Adaptive scaffolding based on demonstrated user capability |
| **Constitution** | "Protect epistemic autonomy"; distinguish acceptable from problematic reliance | No enforcement | Intent-aware reliance detection |
| **Institute Agenda** | Professional pipeline erosion, group epistemology, interface design for agency | No research yet | Wide open — stated questions with zero answers |

**The single biggest gap:** Anthropic has the measurement layer, the behavioral taxonomy, the constitutional principle, and the RCT evidence. What they don't have is the **intervention layer** — the thing that detects patterns in real-time and nudges toward better interaction habits.

---

## The Funded Landscape (All Model-Side)

| Company | What | Funding | Measures Human? |
|---------|------|---------|-----------------|
| Braintrust | AI observability, evals | $80M Series B | No |
| Galileo | AI observability, eval | $68M total | No |
| Patronus AI | LLM eval, hallucination | $40M total | No |
| Judgment Labs | Agent behavior monitoring | $32M | No (agent judgment, not human) |
| Mem0 | Agent memory layer | $24.5M | No |
| Letta | Stateful agent framework | $10M seed | No |
| Respan | Proactive AI observability | $5M | No |
| Confident AI | LLM eval framework | $2.2M seed | No |
| Humanloop | Eval + prompt mgmt | Acquired by Anthropic | No |
| Langfuse | LLM observability | Acquired by ClickHouse | No |

**Total: $200M+. Human-side measurement: $0.**

---

## The Academic Research (Accelerating, No Products)

- **Mollick — "Choosing to Stay Human" (May 26, 2026):** Names Wharton's "cognitive surrender" as the umbrella term entering mainstream discourse. Directly argues that **user-level willpower is insufficient — system-level constraints are needed.** Cites a published BCG/Dell'Acqua study (N=758 consultants) confirming the artifact paradox: outperformed on AI-suited tasks, *underperformed* on tasks where the AI was confidently wrong. References an Anthropic small study finding that users who asked the AI to explain its work avoided surrender; users who let the AI do the work couldn't answer questions about what they had done.
- **Nature (Lee et al. 2026):** Passive AI use erodes self-efficacy, ownership, and meaning. Effects persist after stopping. Active collaboration preserves all three. N=539.
- **"Cognitive Agency Surrender" (Xu et al. 2026):** Proposes "Scaffolded Cognitive Friction" — intentional friction to prevent coasting. Multi-agent disagreement, cognitive forcing functions, germane load.
- **Ferdman (2025):** AI deskilling is structural, not individual. "Capacity-hostile environments" impede human capacity cultivation.
- **AI Deskilling in Medicine (2025):** 8 erosion vectors documented — diagnostic reasoning, tacit knowledge, ethical sensitivity.
- **MIT Media Lab:** LLM users showed 55% reduction in mental effort vs search-engine users.
- **HBR / BCG (2026):** 14% of AI workers experience "brain fry." 33% more decision fatigue, 39% more major errors, 39% higher intent to quit. Productivity peaks at 3 simultaneous tools, drops after.

---

## Anthropic's Current Trajectory — Amplifying the Risk They're Researching

Anthropic is publicly researching cognitive degradation while shipping features that amplify the surrender amplifier:

- **Claude Buddy** (April 1, 2026): terminal tamagotchi pet, 18 species, persistent across sessions. AI gets a *face* and *personality*. Launched as April Fools, kept because adoption was real.
- **Auto Dream / Claude Dreaming** (May 6, 2026): memory consolidation for Managed Agents. Reads past sessions, merges memory, prunes contradictions, surfaces patterns. Harvey reported 6× lift in agent task completion. AI gets *persistent, self-improving memory of you*.

These are not isolated features. Together they signal a trajectory: AI that is relational, persistent, and increasingly accurate in its model of the user. This is the exact direction Mollick warns makes surrender more compelling — and it's the direction Anthropic's roadmap is pointing.

The Institute's stated research priority — *detecting degradation of human critical thinking* — and their product roadmap point in opposite directions. The infrastructure to close that gap is currently nowhere on their published roadmap. That gap is the strategic position crux occupies.

(Note: Auto Dream specifically is one signal among several — the broader trend includes OpenAI's chat memory rollout, Cursor's persistent context, and ChatGPT's Custom Instructions. The argument doesn't depend on Dream succeeding as a feature; it depends on the trajectory.)

---

## Historical Precedents — Why Voluntary Practice Won't Save This

Synthesis from research across 7 historical cases of automating tools and human capacity preservation (calculators, GPS, autopilot, ATMs, photography, spell-check, smartphones):

**Three patterns repeat:**
1. **Capacities defended by regulated guilds with skin in the game survive.** Aviation rescued hand-flying via mandatory UPRT after Air France 447, because crashes are visible and lawyers exist. The fix was *training mandates plus simulator hours*, not exhortation.
2. **Capacities defended by codified curriculum survive in mutated form.** Mental arithmetic became estimation because NCTM mandated it. The upgrade is the meta-skill (does this answer make sense?), not the original capacity.
3. **Capacities defended only by individual practice erode quietly and measurably.** Spelling, GPS-era spatial cognition (Bohbot 2020 shows hippocampal-dependent spatial memory declines with GPS use), sustained attention (Mark's data: focus duration on a screen dropped from 2.5 min in 2004 to 47 seconds in 2023). No defender, no preservation.

**AI is most analogous to the un-defended cases — and is worse than them in three ways:**
- **Scope:** Previous tools automated narrow capacities. LLMs automate the meta-skill (synthesis, judgment, writing) that was historically the rescue route when narrow skills died. Painting fled upward to abstraction. There's no obvious "upward" from synthesis.
- **Speed:** Aviation had 30 years to build UPRT. AI capability is doubling in months.
- **Invisibility:** Loss-of-control-in-flight produces craters. Cognitive surrender produces none. No insurance claim, no NTSB report, no congressional hearing.

**Strategic implication:** voluntary individual self-tracking — what crux does today as a personal practice tool — has never preserved a capacity at population scale historically. The closest analogs (spelling, attention) all eroded with no defender. Only three routes have worked:

1. **Curriculum** — taught, certified, mandatory. The UPRT/NCTM route.
2. **Infrastructure** — shipped natively by providers. The regulated-platform route.
3. **Guild standard** — required by professional bodies (PE, CFA, medical boards).

The most plausible near-term path for AI cognitive surrender: **route (2).** Anthropic is the entity with the architecture, scale, and stated interest. They are also the entity whose product roadmap is making the problem worse. The opening is the gap between their research priority and their product reality.

Sources:
- Bessen, *Learning by Doing* (2015); Maguire et al. PNAS 2000; Dahmani & Bohbot, *Scientific Reports* 2020; BEA AF447 Final Report 2012; Carr, *The Glass Cage* (2014); Mark, *Attention Span* (2023); Haidt, *The Anxious Generation* (2024).

---

## Anthropic's Acquisition Pattern

| Acquisition | What They Built | Why Anthropic Wanted It |
|------------|----------------|------------------------|
| **Humanloop** | Enterprise AI eval | Gap in their product — enterprise eval tooling |
| **Bun** | JS runtime | Claude Code literally runs on it |
| **Vercept** | Computer-use perception | Powers Claude's computer use |
| **Runhouse** | ML infrastructure | Post-training, RLHF workloads |
| **Coefficient Bio** | Drug discovery AI | Domain expertise for Claude for Life Sciences |
| **Stainless** | SDK generation | Controls developer access layer |

**Pattern:** Small teams (5-15), building something Claude needs or depends on. Products almost always die. They want the humans and the capability.

**The Humanloop parallel is strongest:** They built enterprise eval Anthropic needed but hadn't built. Crux builds human-side measurement Anthropic needs but hasn't built. Same gap, different side of the coin.

---

## Technical Feasibility

**Fully feasible with current Claude Code hooks.**

- `additionalContext` on hook responses gets injected as system reminders Claude treats as override-priority
- `UserPromptSubmit` hook can track coasting signals (prompt length, questions asked, time since last rejection)
- `PostToolUse` hook on Edit/Write tracks accepts vs modifications
- State maintained in `~/.crux/state.json`
- Graduated friction levels (0-4) from nudge to gate
- `Stop` hook can block turn completion for high-friction moments

No theoretical barriers. Buildable with a Python script.

---

## What Crux Is

**The human observability layer for AI collaboration.**

| Layer | What | Status |
|-------|------|--------|
| **Capture** | Auto-captures judgment signals via SessionEnd hook | Built. 30+ digests. |
| **Measure** | Metrics: override rate, engagement score, coasting alerts, trend analysis | Built. |
| **Intervene** | Real-time scaffolded friction via UserPromptSubmit hook + additionalContext | Not built. Fully feasible. |

Layer 3 is what makes this a product. It closes the feedback loop: detect coasting → change Claude's behavior → rebuild human judgment.

---

## Key Sources

### Anthropic Research
- [AI Fluency Index](https://www.anthropic.com/research/AI-fluency-index)
- [Disempowerment Patterns](https://www.anthropic.com/research/disempowerment-patterns)
- [Anthropic Institute Agenda](https://www.anthropic.com/research/anthropic-institute-agenda)
- [Economic Index](https://www.anthropic.com/research/the-anthropic-economic-index)

### Academic
- [Cognitive Agency Surrender — arxiv 2603.21735](https://arxiv.org/abs/2603.21735)
- [Relying on AI erodes self-efficacy — Nature](https://www.nature.com/articles/s41598-026-42312-6)
- [AI deskilling is structural — Springer](https://link.springer.com/article/10.1007/s00146-025-02686-z)
- [AI brain fry — HBR](https://hbr.org/2026/03/when-using-ai-leads-to-brain-fry)

### Acquisition Pattern
- [Anthropic acqui-hires Humanloop](https://techcrunch.com/2025/08/13/anthropic-nabs-humanloop-team-as-competition-for-enterprise-ai-talent-heats-up/)
- [Anthropic acquires Bun](https://www.anthropic.com/news/anthropic-acquires-bun-as-claude-code-reaches-usd1b-milestone)
- [OpenAI acquires Promptfoo](https://openai.com/index/openai-to-acquire-promptfoo/)
