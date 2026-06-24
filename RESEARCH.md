# Measuring the Human, Not Just the Model

### A field study of cognitive surrender, run on my own work

**Elliot Little · A living research document · last updated June 2026 · v1**

> A living research document, revised as the data grows. What happened when I built an instrument to measure my own judgment under AI and ran it across four months of my own work. The number that started it: across two hundred-plus sessions, I verified the AI was actually right about **one time in four**. But the number isn't the interesting part. I check the AI's *voice* far more than its *facts*. I'll fix a clumsy sentence and wave through a claim I never checked. The riskier the action, the *less* I scrutinised it, because I'd quietly switched the guardrails off. And the one habit I set out to fix came back a month later: awareness, on its own, changed nothing.

---

## Contents

1. The asymmetry
2. Why the output can't answer this
3. The prior evidence
4. Why now — the judgment moments are vanishing
5. Method — how I captured it
6. Results — run on myself
7. The leading indicator
8. What this deliberately is not
9. Why a personal tool won't save the population
10. What this implies
11. Open questions
12. Limitations and honest status

---

## 1. The asymmetry

In the last eighteen months, more than $200M has gone into knowing whether the *model* is good: evaluation harnesses, observability, hallucination detection, agent memory. Braintrust, Galileo, Patronus, Judgment Labs, Mem0, Humanloop. Every funded company in the category measures the model. I can find none that measures the human sitting next to it.

This is a strange thing to leave unmeasured, because the human is the half that can't be re-run. You can audit an agent's every step — every tool call, every token, every decision in the loop. You cannot audit your own. There is no log of what you actually checked, what you waved through, or whether the instinct to push back is still firing. The model side has a complete observability stack. The human side has nothing equivalent.

That gap is the subject of this document. Not whether the AI is good; that question is well funded and well studied. Whether the *person directing it* is still doing the thing they think they're doing.

## 2. Why the output can't answer this

The reflex is to look at the work. If the output is good, the collaboration must have been good. This reflex is wrong, and it is wrong in a way that is now well documented: as AI output becomes statistically indistinguishable from human output, inspecting the artefact tells you less and less about how it was made or who was thinking while it was made.

Two distinct questions fall out of that collapse, and they are not the same question:

- **Provenance** — *was this work genuinely human-led, and can that be shown to someone else?* This is a question of trust, attestation, and verification against an adversary. It is being worked on seriously, and it is not the question this document takes up.
- **Judgment** — *is the person directing the AI still exercising the judgment they believe they are?* This is a question of self-knowledge, not proof. It has no adversary. The only audience that matters is the person themselves.

Crux takes the second question. The distinction matters because it determines what the instrument can honestly be. A provenance system has to convince a third party, which pulls it toward cryptography, tamper-evidence, and formal guarantees. A judgment instrument convinces no one but you, so it does not need, and should not claim, any of that. Its entire value is that it is *for you*, and it falls apart the moment it pretends to be evidence for anyone else (see §8).

So this is measurement, in the plain sense: an honest record of how you actually engaged, read back to you over time. It does not detect anything and it proves nothing.

## 3. The prior evidence

The risk this measures is not speculative. Across separate studies, run by separate teams, with no shared method, the same shape keeps appearing: AI makes the work easier and the human less critical, and the loss outlasts the tool.

- **BCG / Dell'Acqua (N=758 consultants).** Consultants with AI access beat controls on tasks the AI handled well. They *underperformed* controls on tasks where the AI was confidently wrong. They did not lose competence. They lost the habit of pushing back.
- **MIT Media Lab.** LLM users expended roughly half the mental effort of search-engine users completing the same task.
- **Nature, Lee et al. (N=539).** Passive AI use lowers self-efficacy, ownership, and meaning, and the dip persists *after* the AI use stops. Active collaboration preserves all three.
- **Anthropic, survey of ~81,000 users.** "Losing one's edge" ranked the fourth-largest concern. Thirteen thousand raised it unprompted; close to half said they already feel it.
- **Anthropic coding RCT.** Delegating work dropped comprehension (50% vs 67% on later questions). Asking the AI to *explain* its work preserved the skill. The difference was whether the human stayed in the reasoning.
- **Anthropic AI Fluency Index.** The artifact paradox, measured: the more polished the output, the less the user checks the context (−5.2pp) and questions the reasoning (−3.1pp). Polish actively suppresses scrutiny.

Six findings, one direction. The convergence is the point: this is not one lab's result that might not replicate. It is the same erosion seen from six angles.

## 4. Why now — the judgment moments are vanishing

Three things are happening to AI at once, and all three make pushing back harder.

**It is becoming relational.** Persistent companions, voice, personality continuity. The model is being given a face, and pushing back on something with a face feels like rudeness.

**It is becoming persistent.** Cross-session memory consolidation: merging what the model noticed about you, remembering your concessions. The model is being given a memory of you, and it is harder to argue with something that remembers the last time you agreed.

**It is becoming accurate about you specifically.** As context and memory improve, the model's representation of what you'd say gets better. It increasingly sounds like what you would have said if you'd been smarter for longer, which is exactly the output hardest to challenge.

None of these are bad. They are the natural direction of progress, and they produce real gains. But together they shrink the human's contact with the work to a handful of seams. In June 2026, three of the most-read voices in the field described the same shift within days of each other:

> "I no longer steer. I commission." — Ethan Mollick

> "I don't prompt Claude anymore… my job is to write loops." — Boris Cherny, Head of Claude Code

> "The loop doesn't know if you understand the work or are avoiding it. You do." — Addy Osmani

The work has moved from process to outcome. What's left of the human's contact is three moments: **the brief** (what you ask for and what you'd reject), **the mid-flight redirect**, and **the sign-off** (accepting work you didn't watch). Everything else happens in hundreds of small choices you never get a vote on.

And note what the loop-engineering stack instruments: maker/checker splits, verifier models grading stop conditions, adversarial review of generated code. There is observability on every part of the loop *except the human who designs it and signs off*. Osmani's closing line assumes the human knows the difference between using the loop to go faster on work they understand and using it to avoid understanding the work at all. My own data, below, says the human often doesn't. The judgment moments are getting rarer and heavier at the same time, and not one of them is measured.

## 5. Method — how I captured it

I built the smallest instrument that could answer the question on real data, and ran it on myself before claiming anyone else has the problem.

**Capture is local and passive.** A session-end hook on my coding environment reads each session when it ends and writes a structured digest: what I steered, what I checked, what I let go. Zero commands, zero friction, nothing identifiable leaves the machine. The point was to measure normal behaviour, which means the measurement cannot change it.

**Classification uses a controlled vocabulary.** Each session is tagged against a stable, named taxonomy of collaboration patterns grouped by fluency dimension (delegation, description, discernment, diligence). The vocabulary is fixed and versioned rather than invented per session, so patterns are comparable across months. That is the precondition for seeing a *trend* rather than a snapshot.

**Two altitudes, two corpora.** Erosion shows up differently depending on how closely you look, so I measured at two:

- *Session level* — the per-session digests above, classified and synthesised over four months. This answers "what do I habitually do with finished work."
- *Command level* — a separate, log-only pass over my full local transcript corpus (192 session transcripts, 2,668 shell commands, 22 active days), matching against a tiered list of irreversible operations: force-pushes, production migrations, destructive SQL, merges to the default branch. This answers "what do I do at the moments I can't take back."

Nothing in either corpus is reconstructed after the fact for this document; the digests were written contemporaneously and the command pass was run log-only, with the full match detail held locally and never published.

## 6. Results — run on myself

I built the tool half-expecting to come out looking fine. I did not.

**The headline.** Across more than two hundred real coding sessions and the nine hundred-odd messages I sent inside them, four moves account for almost everything I do with the AI's output. I **verify it's actually right about one time in four.** I **steer how it looks** about as often. **A third of the time I'm just handing over the next task.** And roughly **one time in seven I wave it through** without really reading it.

The shape is specific and unflattering: I am good at steering the surface (fixing the voice, redirecting the approach) and weak at checking the substance. *I catch what's wrong with how the AI writes. I coast on whether what it says is true.*

**Session level confirms it.** Across the classified corpus, diligence — the fluency dimension that covers verification and follow-through — is weak in roughly 65% of sessions, while every other dimension is strong or medium in most. Diligence is the structural outlier. The pattern "accepts polish uncritically" is among my top three by frequency and shows *no improving trend* across the four months. It is not a phase. And the lesson never stuck at the system level: I caught the AI's voice-tells in one month, escalated to a process fix, and the same fix slipped the next. Awareness without infrastructure produced no behaviour change.

**Command level is worse, where it matters most.** At the irreversible moments, the 0.45% of commands where a half-second of deliberation is obviously warranted, the dry run found 9 genuine decision events in 22 days (0.41 per day; sparse enough that capturing them would not be insufferable). Of the 8 events that had a preceding human message, **roughly six were rubber stamps or blanket delegations**: "go for it", "you do it all", "solve it for me". One had no human utterance at all. Contemporaneous justification at one-way doors essentially did not exist, in the person who *built the measurement tool*.

So the highest-stakes actions ran with *less* scrutiny than trivial ones, because, like most solo builders, I had turned off permission prompts, dropping force-pushes and destructive migrations into the same auto-approved bucket as everything else.

The session-level finding (verifies voice, not substance) and the command-level finding (rubber stamps at one-way doors) are the same erosion measured at two altitudes. Call any single number an estimate; measure it a few ways and it shifts a point or two. The shape does not move.

I built this instrument specifically to catch this kind of thing, ran it on my own work half-expecting to come out fine, and it caught me anyway. That's the part I keep returning to: the awareness was already there. It wasn't enough.

## 7. The leading indicator

Here is the part that is new.

Everything else in the field measures surrender *after* it shows up in the work — once output quality degrades, once a confident wrong answer ships, once the consultant underperforms. That is a lagging indicator. By the time it fires, the habit is already gone.

There is an earlier signal. Dependency erodes two things in sequence: first the capability, then the *wanting* to exercise it. Skill atrophy is the loss of the ability to check. **Appetite atrophy** is the loss of the desire to, and it comes first. A person who *can* still challenge the AI but no longer *bothers* is the early case, not the late one.

That is measurable. The rate at which you leave the justification blank, or type "ship it", at a one-way door (on tasks you are plainly still capable of judging) is a direct read on appetite, surfaced descriptively and tracked over time. The question isn't whether you're a compliant reviewer. It's whether the wanting-to-own has started to fade. Extended to the patron era, the same read becomes the *contest rate* at sign-off: when an autonomous run completes, does the human genuinely contest even one of the decisions it made on their behalf, or accept the whole thing whole?

This is the project's first leading indicator, and its sharpest contribution. It reads the fading of the instinct to own the call *before* the call goes wrong.

## 8. What this deliberately is not

The constraints below are not modesty. Each one is load-bearing, and removing it would break the thing.

- **No score.** Reducing the patterns to a number re-instates the worth-by-output logic the project exists to reject, and hands the user something to game instead of something to see. The readout surfaces what you steered, checked, and let slide. Never a grade.
- **No cross-user comparison.** The unit of analysis is *this person, over months*. Not a leaderboard. A ranked version would be a worse product and a worse idea.
- **Local-first, no exfiltration.** Nothing identifiable leaves the device. Privacy is not a feature here; it is the precondition for measuring honest behaviour at all. An instrument you'd perform for is an instrument that measures the performance.
- **No cryptographic attestation, by choice.** It would be natural to wrap this in tamper-evidence and sell it as an audit-grade record. I deliberately don't. Cryptography can prove a file wasn't altered; it cannot prove the words were the human's, nor that the capture was complete. A verification that can't establish what it asserts is worse than none. It manufactures false confidence. Because this instrument answers only to the person running it, it needs no proof for anyone else. The record stays a plain, append-only, local log.
- **No real-time nagging by default.** It does not interrupt during work. The one exception is reserved for the user's own highest cut-lines, opt-in, off until installed. A tool that nags is a tool people switch off on day one.

## 9. Why a personal tool won't save the population

The ceiling is real, and worth stating plainly.

I commissioned a synthesis of seven historical cases of automating tools and the human capacities they threatened: calculators, GPS, autopilot, ATMs, photography, spell-check, smartphones. The pattern is unambiguous:

- Capacities defended by **regulated guilds with skin in the game survive.** Aviation rescued hand-flying after Air France 447 with mandatory recovery training, because crashes are visible and lawyers exist.
- Capacities defended by **codified curriculum survive in mutated form.** Mental arithmetic became estimation because a standards body wrote it into the curriculum. The meta-skill got rescued; the original didn't.
- Capacities defended **only by individual practice erode quietly and measurably.** Spelling. Post-GPS spatial memory (Bohbot 2020). Sustained attention (average screen focus fell from 2.5 minutes in 2004 to 47 seconds in 2023). No defender, no preservation.

AI is most like the undefended cases, and worse in three ways. **Scope:** previous tools automated narrow skills; LLMs automate the meta-skill (synthesis, judgment) that was historically the rescue route. There is no obvious "upward" from synthesis. **Speed:** aviation had thirty years to build its training mandate; AI capability doubles in months. **Invisibility:** loss of control in flight leaves craters and an NTSB report. Cognitive surrender leaves no claim, no hearing, no alarm.

The implication is hard and I will state it plainly: voluntary individual self-tracking has never preserved a capacity at population scale. The closest analogs all eroded with no defender. A practice tool genuinely helps the individual who runs it. It will not, on its own, save the population. Only three routes have ever worked: **curriculum, provider infrastructure, or guild standard**, each with a forcing function that is not willpower. This tool is a working demonstration of the *shape* of the missing measurement. It is not the thing that ships it at scale.

## 10. What this implies

The same capture-and-synthesis substrate serves different audiences as different things. These aren't separate products; they're different readings of one record.

- **For individuals — the Mirror.** Patterns over time, the surrender signatures surfaced, what got challenged versus waved through, at the one moment the loop can't watch itself: sign-off. It helps the person who runs it. Don't mistake that for solving the category.
- **For enterprises — the Trail.** The audit trail you actually need is not the AI's logs of what it did. It is the human's record of what they engaged with, challenged, and let through. AI-side-only observability is a one-sided accountability picture, and it will be a problem the first time something significant goes wrong. The requirement is that the chain of responsibility stay *identifiable*, not collapsed into "the machine."
- **For professional bodies.** The AI-collaboration audit trail will become part of professional competence within five years. The fields that codify what "competent AI use" means will define it. The fields that wait will have it defined for them.
- **For providers.** Ship the human-side counterpart to the model-side memory and observability you already build. The research agenda already names degradation of human critical thinking as a priority; the product gap is the obvious place to close it.
- **For builders.** The infrastructure is buildable today with hooks, file watchers, and scheduled exports. The hard problem is not technical. It is the design problem of surfacing the data in a way that changes behaviour without becoming insufferable. That problem is unsolved and worth working on.

## 11. Open questions

I do not have these answered. They are the honest edges of the work.

1. **What's the right unit to watch?** A single turn, a whole session, the irreversible commands, or the moment you accept a long run you never watched.
2. **How much checking is silent?** Reading a diff and saying nothing is real scrutiny that no transcript can see. Some of what reads as coasting may be quiet competence, and the instrument can't yet tell them apart.
3. **Does the gap compound, or self-correct?** Does the drift worsen over months, or do people correct once they can see it? Answering that needs far more history than I have.
4. **Does seeing it change anything?** Does showing someone their own mix change how they work, or just hand them a number to game?
5. **What's the right altitude?** The individual, the team's curriculum, or the platform itself. And how do you surface it without becoming the tool people switch off on day one?

## 12. Limitations and honest status

This is one person's data. The corpus is small (tens of classified sessions, 192 transcripts, four months, a single tool surface, maybe a fifth of even my own AI use). The headline numbers are estimates that move a point or two depending on how you slice them. Silent checking is invisible to the method and may flatter or damn me unfairly. The leading indicator in §7 has a real failure mode: if the modal answer at a one-way door is "ship it", the field is noise and the signal flatlines. In that case the artefact is theatre and the right move is to stop. I am holding that kill criterion.

What this is, then, is not a finished result. It is the form of the argument clear enough to attack and improve — with real, if undersized, data behind every claim. It is a living document; it will be revised as the corpus grows and the open questions close. The repo is public and MIT-licensed; there are no patents and there will not be, because a measurement instrument for your own judgment only works if it is inspectable.

---

### Sources

**Practitioner:** Mollick, *Choosing to Stay Human* (May 2026) and *What it feels like to work with Mythos* (Jun 2026); Osmani, *Loop Engineering* (Jun 2026); Cherny (Head of Claude Code).

**Anthropic research:** AI Fluency Index; *What 81,000 People Want from AI*; the Economic Index; Institute Research Agenda; coding-skills RCT.

**Academic:** Dell'Acqua et al. (BCG, N=758); Lee et al., *Nature Scientific Reports* (2026, N=539); MIT Media Lab; Mark, *Attention Span* (2023); Dahmani & Bohbot, *Scientific Reports* (2020); BEA, AF447 Final Report (2012); Carr, *The Glass Cage* (2014); Bessen, *Learning by Doing* (2015).

**Tool:** github.com/ElliotJLT/crux — open source, MIT, run in the open.

*Crux · A living research document · v1 · June 2026 · No patents. Public by design.*
