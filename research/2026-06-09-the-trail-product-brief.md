## The Trail — point-of-decision capture at the irreversible moment

### Problem
crux captures sessions after they end. By the time the SessionEnd digest reconstructs a session, the reasoning behind the consequential calls is already gone — and in the transcript a knowing decision is indistinguishable from passive acceptance. The current tool can describe what you let slide; it was never present at the moment you committed.

There is a second gap. Most solo builders have turned off permission prompts because blanket allow/deny is insufferable. So today the highest-stakes actions — force-push, prod migration, DROP, secret rotation — run with *less* scrutiny than trivial ones, because they sit in the same auto-approved bucket.

### The concept
A thin, opt-in capture that fires only at irreversible, consequence-bearing moments. At a one-way door, it asks four neutral questions — who owns this, why now, how you'll watch it, how to undo it — and folds your own words into the trail. No score. No pass/fail. Just a record, written where it matters.

The trigger is a property of the operation, not your mood: a user-owned `cutlines.yml` of regexes over the tool input (force-push, `DROP|DELETE|TRUNCATE`, `rm -rf` outside scratch, deploy verbs, secret rotation). Reversible work runs free; the pause appears at roughly the 0.1% of moments where a half-second of deliberation is obviously warranted.

### The wedge
Let the agent run free on everything reversible; pause for half a second only on what you cannot take back. That benefit is felt on the first near-miss, before any reflection value accrues — which is why a builder installs it for themselves, not out of virtue.

Smallest first build (two days): Day 1, run the cut-line classifier log-only against existing local transcripts and publish the match rate and false-positive list — proving "irreversible is mechanically separable from routine" before any prompt fires. Day 2, add the opt-in PreToolUse hook that has Claude surface the four questions, capture the answer from the transcript, and append it to `~/.crux/attestations/` plus a new `## At the threshold` digest section. Ships off; enabled via `settings.json` like the SessionEnd install; honours `.crux-skip`.

### The analytic payoff
Over time, the rate at which you leave the justification blank or type "ship it" at one-way doors is itself the signal — declining willingness to own the high-stakes calls, surfaced descriptively. Same observable that approval-fatigue research already tracks, read for the opposite purpose: not "are you a compliant reviewer" but "has the wanting-to-own started to fade." That read is the freshest move here; build it and publish it as the differentiator.

### Why now
The irreversible action is the rare moment a builder would already hesitate — a natural, self-justifying pause that survives the "blanket friction is insufferable" objection. It is also the project's first component with a forcing function that is not willpower.

### Risks
- Rubber-stamp collapse: if the modal answer at a force-push is "ship it," the field is noise and the appetite read flatlines. Sample real fields early; if a clear majority are rubber-stamps, the artefact is theatre — stop.
- Calibration: a ruleset that over-fires gets switched off within a day. Dry-run first; keep the default set tiny and hard-irreversible only.
- Unfalsifiability trap: "read the noise as the finding" is honest but can mask failure. Hold the kill criteria.

### What NOT to do
- No hash-chain, Merkle tree, selective-disclosure, or "verifiable, tamper-evident, audit-grade" claims. The cryptography defends integrity but cannot establish that the words were the human's, nor that capture was complete — a verification that can't establish what it asserts is worse than none. Keep only append-only local JSONL committed to git.
- Do not claim this artefact does not exist. A per-deliverable human diligence statement is already taught (it is in the README); decision journals and HITL gates exist. Claim the increment honestly: the diligence statement, auto-triggered only at one-way doors, kept descriptive, and tracked for ownership-vs-cede over time.
- No real-time intervention by default. Off until installed; the gating tier is reserved for the user's own highest cut-lines.
- No scoring, no cross-user comparison. The four fields are free text; the readout surfaces the verbs and a blank-justification trend, never a number.

---

## Day-1 dry-run results (2026-06-09)

Log-only classifier (`scripts/cutline-dryrun.py` + `taxonomy/cutlines.yml`) over the full local transcript corpus. No hooks fired; full match detail stays local (never committed — repo rule).

- **Corpus:** 192 session transcripts, 2,668 Bash tool commands, 22 active days (May–June 2026).
- **Detector precision:** after two iteration passes (heredoc stripping; scratch-reclone and test-env annotations), 12 real hard-tier matches → **9 decision events** once retries are grouped.
- **Fire rate: 0.41/day. Selectivity: 0.45%** of all commands. The hook would interrupt roughly once every other working day — well inside the don't-get-disabled budget. Gate 1 (irreversible is mechanically separable from routine) **passes**.
- **Dominant one-way door:** `gh pr merge` to the default branch (4/9 events), then dev-DB resets (consequential here because worktrees share one dev Postgres) and force branch-deletes.
- **The founding baseline:** of 8 events with a captured preceding human message, **~6 were rubber stamps or blanket delegations** ("go for it", "you do it all", "solve it for me"), 1 had no human utterance at all, 1 was self-initiated. The contemporaneous JUSTIFY at one-way doors currently **does not exist** — the instrument would be capturing net-new information, and the appetite metric must be read as *change from this baseline*, not against zero.
- **Delegation split:** 0/12 one-way doors ran on a subagent sidechain — but several main-loop events were agent-initiated under a blanket prior "go ahead", which is the cedes-responsibility pattern in the wild.

Next: Day-2 capture hook (PreToolUse on the hard set, off by default), then re-measure the rubber-stamp rate against this baseline.

---

## The patron-era extension (added same day)

Mollick's ["What it feels like to work with Mythos"](https://www.oneusefulthing.org/p/what-it-feels-like-to-work-with) (Jun 9, 2026) names the shift the cut-line work has to reckon with: with Fable-class models, "the work has shifted from process to outcome. I no longer steer; I commission." The human's contact with the work collapses to three seams — **the brief** (what you ask for and what you'd reject), **the mid-flight redirect**, and **the sign-off** (accepting work you didn't watch). Everything else happens in "hundreds of small choices I never get a vote on."

This reframes, but does not break, the cut-line concept:

- Bash-level cut-lines instrument the *legible* one-way doors. The dry run proved the method: point-of-commitment capture is sparse, mechanically detectable, and baseline-measurable. But command-level capture alone instruments the visible fraction of a phenomenon that increasingly lives in delegation itself.
- **Accepting the output of a multi-hour autonomous run is a one-way door in the same taxonomy sense**: the hundred invisible micro-decisions become yours the moment you ship them, and you cannot retroactively have judged them. The detector generalises — fire on the *delegation event* (long-run completion, large agent fan-outs), not only the destructive command. The substrate already exposes this (run duration, agent count, tokens burned unattended).
- The same dry run captured the patron era in the wild: the day this note was written, a one-way door fired directly after the user message "solve it for me."

The staying-sharp loop this implies, each step instrumentable on the existing substrate:

1. **Pre-commit** — state expectations and rejection criteria *before* the run (makes the sign-off falsifiable; the decision-journal mechanism).
2. **Delegate** — let the run go; no theatre of watching a process too long to follow.
3. **Disclosure** — at completion, the model surfaces the N decisions it made on your behalf that you'd most plausibly contest. The black box can't be opened, but it can be made to testify.
4. **Contest** — genuinely contest one. One real contest per run beats reviewing everything shallowly (consistent with the finding that users who make the AI explain its work retain understanding; users who let it work cannot answer questions about what they "did").
5. **Trail** — count the reps. Contests, redirects, and real justifications are judgment repetitions; they atrophy silently because nothing counts them.

Candidate work, in order: a `delegation` tier in `cutlines.yml` (fires on run-completion events, dry-run first, same discipline); a disclosure hook ("contestable decisions report" at Stop); the appetite read extended from blank-justification rate at commands to contest rate at sign-offs. Same rails as everything else: descriptive, local-first, no score.
