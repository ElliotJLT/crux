# Measuring the Human, Not Just the Model

### A field study of cognitive surrender, run on my own work

**Elliot Little · A living research document · last updated July 2026 · v1.1 · No patents, public by design**

> *What happens to a person's judgment while the AI does the work, and can you even see it changing? This is a field report, revised as the data grows. I built an instrument to measure my own AI collaboration and ran it across four months of my own work; on the record, I visibly push back about one time in four. The number is the hook, not the point. The point is that this is not a new phenomenon — it is a forty-year-old, repeatedly replicated finding from automation research, now arriving in software — and that the person inside it is the last to be able to see it.*

---

## The asymmetry

In the last eighteen months, more than $200M has gone into knowing whether the *model* is good: evaluation harnesses, observability, hallucination detection, agent memory. Braintrust, Galileo, Patronus, Judgment Labs, Mem0, Humanloop. Every funded company in the category measures the model. I can find none that measures the human sitting next to it.

This is a strange thing to leave unmeasured, because the human is the half that can't be re-run. You can audit an agent's every step. You cannot audit your own. The model side has a complete observability stack. The human side has nothing equivalent.

That gap is the subject of this document. Not whether the AI is good — that question is well funded and well studied — but whether the person directing it is still doing the thing they think they're doing.

## Why the output can't answer this

The reflex is to look at the work. If the output is good, the collaboration must have been good. As AI output becomes statistically indistinguishable from human output, that inference breaks: the artefact tells you less and less about how it was made, or who was thinking while it was made.

Two distinct questions fall out of that, and they are not the same:

- **Provenance** — *was this work genuinely human-led, and can that be shown to someone else?* A question of trust and attestation, with an adversary. Worth working on; not the question here.
- **Judgment** — *is the person directing the AI still exercising the judgment they believe they are?* A question of self-knowledge, with no adversary but yourself.

Crux takes the second. The distinction sets what the instrument can honestly be: a judgment instrument convinces no one but you, so it needs no cryptography and no proof, and falls apart the moment it pretends to be evidence for anyone else. This is measurement, in the plain sense — an honest record of how you actually engaged, read back to you over time.

## This is not new: forty years of automation research

The most important thing I can say about cognitive surrender is that it is not a 2025 discovery. The human-factors literature has been describing it since 1983, in cockpits, control rooms, and operating theatres, long before a language model wrote anyone's code.

Lisanne Bainbridge named it the **irony of automation** (Bainbridge, 1983): automate the easy parts of a task and you leave the human with the harder residual job of *monitoring* — a job humans are poorly suited to — while their hands-on skill quietly decays from disuse. The result is a person who is least practised at exactly the moment an automation failure demands they take over. Her conclusion was the opposite of intuitive: the more capable the automation, the *more* skilled and better-trained its human operator needs to be.

The empirical base under that idea is deep and consistent:

- **Overreliance is a named, documented failure mode**, not a personal weakness. Parasuraman & Riley (1997) classify it as the "misuse" of automation; it produces failures of monitoring and decision bias.
- **Experts are not immune, and practice doesn't fix it.** Parasuraman & Manzey's (2010) integrative review concludes that automation complacency and automation bias are "found in both naive and expert participants," that complacency "cannot be overcome with simple practice," and that bias "cannot be prevented by training or instructions." This is the single most load-bearing finding for everything below: the problem is attentional and structural, not a matter of trying harder.
- **A good-but-imperfect aid can make you worse than no aid at all.** Skitka, Mosier & Burdick (1999) showed participants with a highly-but-not-perfectly reliable automated aid *underperformed* those with none, via both omission errors (missing what the aid didn't flag) and commission errors (following it when it was wrong). Tellingly, training reduced commission errors but *not* omission errors.
- **It happens to professionals, and disposition matters more than mandate.** In high-fidelity glass-cockpit studies, experienced airline pilots made the same omission and commission errors — and even misremembered seeing cues they had never actually verified (Mosier et al., 1998). The pilots who cross-checked were the ones with an *internalised* sense of accountability; externally imposed accountability made no difference.
- **The mechanism is loss of situation awareness.** Endsley (1996) calls it the "out-of-the-loop performance problem": shift a person from active doer to passive monitor and they become slow to notice that something has gone wrong and slow to understand the state of the system once they do.

The "artifact paradox," polished output suppressing scrutiny, is in this older vocabulary just **automation complacency** under a new name. The mechanism is well established; what's sobering is that it has already resisted forty years of awareness.

## The same pattern, now in software

What's genuinely new is the domain and the speed. The recent evidence maps the old findings onto AI-assisted knowledge work almost point for point.

- **Confidence in the AI predicts *less* critical thinking.** In a survey of 319 knowledge workers analysing 936 real GenAI work examples, higher confidence in the tool was associated with less critical thinking, while higher confidence in oneself was associated with more (Lee et al., 2025). The work doesn't disappear; it shifts from *doing* to *verifying* — exactly the monitoring role Bainbridge warned about.
- **Frictionless generation leaves less behind.** An EEG study (Kosmyna et al., 2025, preprint) found essay-writers using an LLM showed the weakest, least-distributed neural connectivity of three groups, and **83% could not quote a single sentence** from the essay they had just produced (versus ~11% of the others), with the lowest sense of ownership. The authors call the residue "cognitive debt." Small sample, single task, not yet peer-reviewed — but directionally striking.
- **Delegation lowers comprehension; comprehension-first preserves it.** An Anthropic randomised trial (Shen & Tamkin, 2026) had people learn an unfamiliar library either by hand or with AI. The AI group scored **50% on a comprehension quiz versus 67%** for hand-coders (Cohen's *d* = 0.74) — roughly two letter grades — for a time saving that wasn't statistically significant. The largest gap was on debugging. But participants who generated code *and then asked questions to understand it* scored higher. How you use it is the whole variable.
- **The craft signal in the artefact is degrading.** An analysis of 211M changed lines of code (GitClear, 2025; vendor research, correlational) found copy-pasted code rose from 8.3% to 12.3% (2021–2024), refactoring ("moved" code) fell from ~25% to under 10%, and duplicated blocks grew several-fold — output up, maintainability down.
- **Adoption is rising while trust falls.** Stack Overflow's 2025 survey of 49,000+ developers found AI use climbing to ~80% even as trust in its accuracy dropped from 40% to 29%; the top frustration (45%) was "almost right, but not quite," and 66% reported spending *more* time fixing AI code. People increasingly rely on output they themselves distrust.

The same split shows up across other professions. In automated cockpits, it is the *cognitive* skills (navigation, deciding what to do) that erode with disuse, while stick-and-rudder skills are largely retained (Casner et al., 2014) — judgment goes before fluency, which is precisely the distinction this project is built on. Habitual GPS use predicts steeper decline in hippocampal-dependent spatial memory (Dahmani & Bohbot, 2020; longitudinal *r* = −0.68, n = 13 — suggestive, small). Radiologists given an incorrect AI suggestion saw accuracy collapse across every experience level (Dratsch et al., 2023) — though that is real-time automation bias, not proven long-term deskilling.

## Why now — the judgment moments are vanishing

Three things are happening to AI at once, and all three make pushing back harder. It is becoming **relational** (a face is harder to argue with), **persistent** (it remembers your concessions), and **accurate about you specifically** (it increasingly sounds like what you'd have said if you'd been smarter for longer).

Together they shrink the human's contact with the work to a handful of seams. In June 2026, three of the most-read voices in the field described the same shift within days of each other:

> "I no longer steer. I commission." — Ethan Mollick

> "I don't prompt Claude anymore… my job is to write loops." — Boris Cherny, Head of Claude Code

> "The loop doesn't know if you understand the work or are avoiding it. You do." — Addy Osmani

The work has moved from process to outcome. What's left of the human's contact is three moments: **the brief**, **the mid-flight redirect**, and **the sign-off**. And the loop-engineering stack instruments every part of itself (maker/checker splits, verifier models, adversarial review), *except the human who designs it and signs off*. Osmani's line assumes the human knows the difference between using the loop to go faster and using it to avoid understanding. The evidence below says the human is the last to know.

## The ownership account

The studies above measure capability: comprehension scores, error rates, neural connectivity. Through mid-2026 a second account has been accumulating in practitioner writing — essays, forum threads with thousands of working engineers in them — and it is consistent enough to treat as data. Its subject is not whether the skill is decaying but whether the work still belongs to the person who shipped it. The same account comes up in private, whenever engineers are asked how the year has actually felt.

The reports share a shape, and each element has a study standing behind it:

- **Decisions that don't embed.** Engineers describe finishing AI-heavy projects faster and knowing them less. A decision you make lodges; a decision made mid-flight by the loop and presented for approval afterward does not. This is Kosmyna's 83%-can't-quote finding narrated from the inside — and it is what Shen & Tamkin's debugging gap predicts it should feel like six months on, when the code needs changing and the person who shipped it reads it like a stranger.
- **The defendability test.** The practitioner version of a comprehension quiz is social: someone asks *why was this done?* and the person who shipped it can narrate the outcome but not the decisions under it. Rozenblit & Keil showed people discover the illusion of explanatory depth only when forced to explain; an AI-heavy workflow arranges for that discovery to happen out loud, in front of whoever asked.
- **Verification as the residual job — and as tax.** Lee et al. measured the shift from doing to verifying. The practitioner accounts supply the texture: reading confident prose for the buried wrong assumption, task-switching in the minutes while the agent runs, never quite trusting what comes back. Deedy Das (Menlo Ventures, June 2026), on the split inside teams pushed to adopt: "The craftsmen are tired. Very tired. The entire burden of review falls on the craftsman. The burden of understanding." The verification lands hardest on the most expert, because they are the ones still able to do it.
- **The reward loop, stranded.** An engineering manager, in the 8,000-upvote thread that followed Das's remarks: normal coding cycles through problem-solving and the reward of solving; AI-assisted coding parks you in "the solution validation phase" where you "barely get any reward. It becomes very mechanical and takes away what a lot of devs love about their job." That is loss of felt reward — distinct from loss of skill, and untouched by status or pay.
- **The inversion, lived.** From the same thread: "I am no developer anymore. I am the Product Owner with the technical skill they wish they had… plus QA engineer." Mollick's patron shift, reported in the past tense from the floor.

Two features of this account matter for the instrument.

**It is bimodal.** The same tool, deployed the same way, lands as liberation for the outcome-oriented and as bereavement for the craft-oriented — the threads carry both voices, and the split doesn't track seniority. Population statistics will average the phenomenon away. The unit that can register it is one person, over months, which is the unit this instrument measures.

**And every report is, mechanically, a missing-record problem.** The decisions existed. They were made in flight — by the person, the model, or the two of them — and left no trace the person can retrieve at the moment of challenge. Organisations are starting to answer the identity half of this with ownership: give people a problem and an outcome, not tickets. Right instinct, and it doesn't touch this. Owning an outcome without a record of the decisions underneath it is stewardship of a black box; you can only defend what you can reconstruct, and the workflow that produced the artefact is exactly the workflow that leaves no reconstruction behind.

That sharpens what the digest in this project is for. Not only a mirror for judgment drift — a **record of title**: the contemporaneous account of what you steered, checked, and let slide, written while it was warm, retrievable at the moment someone asks *why*. The literature's question is whether you're still thinking. The practitioners' question is whether the work is still yours. The same record answers both.

## Method — how I captured it

I build AI in education, where accuracy and pedagogy are the product rather than a feature, so this question isn't abstract for me. I built the smallest instrument that could answer it on real data and ran it on myself before claiming anyone else has the problem.

**Capture is local and passive.** A session-end hook reads each session when it ends and writes a structured digest — what I steered, what I checked, what I let go. Nothing identifiable leaves the machine; the measurement can't change the behaviour it measures.

**Classification uses a controlled vocabulary** — a stable, versioned taxonomy of collaboration patterns grouped by fluency dimension (delegation, description, discernment, diligence), so patterns are comparable across months and a *trend* is visible rather than a snapshot.

**Two altitudes.** Session level (per-session digests, classified over four months) and command level (a log-only pass over my full local transcript corpus of 192 sessions, 2,668 shell commands, 22 active days, flagging the rare moments that are hard or impossible to undo). Nothing is reconstructed after the fact: digests were written contemporaneously, the command pass was run log-only, and the full match detail stays local.

One scope note up front. This watches a single channel: my own coding sessions, and only what shows up in the transcript. It does not see the verification real work runs on — code review, automated tests, red-teaming, staged rollout, and domain checks for accuracy before anything reaches a user. A thin in-session signal is a finding about that channel, not a verdict on anyone's total diligence.

## Results — run on myself

I built the tool half-expecting to come out looking fine. I didn't.

**The headline.** Across more than two hundred real coding sessions and the nine hundred-odd messages inside them, four moves account for almost everything that shows up in the record. About **one time in four**, I visibly push back on whether it's right. I steer how it reads about as often. A third of the time I'm handing over the next task. And roughly one in seven leaves no visible check at all — with one honest caveat: a transcript only sees what I say out loud, so it can't separate a silent, careful read from a genuine wave-through.

**The shape is specific.** The pushback that surfaces is mostly about how the AI writes — the voice, the approach — and less often, on the record, about whether it's *true*. That visible-judgment gap is the thing worth watching. At session level, diligence is the structural outlier: weak in roughly 65% of sessions while the other dimensions hold up, and "accepts polish uncritically" is a top-three pattern with no improving trend across four months. The lesson never stuck at the system level — I caught a habit, escalated it to a process fix, and the same fix slipped the next month.

**Command level is worse, where it matters most.** The hard-to-undo moments are rare (under half a percent of commands) and they were the moments I deliberated over *least*. So the highest-stakes actions ran with less deliberation than trivial ones, not more.

I take this seriously: I build with guardrails and care about using AI safely, and the substantive checks in my professional work happen off the transcript, in review and testing. Even so, my own in-session record of judgment came out thinner than I'd assumed. Call any single number an estimate; measure it a few ways and it shifts a point or two. But the shape doesn't move.

## You can't see it from the inside

The strongest argument for an external record is that introspection demonstrably fails here, and fails worst for the people most affected.

The cleanest evidence is the METR randomised trial (Becker et al., 2025): 16 experienced open-source developers, working on 246 real issues in repositories they knew well, were **19% slower** with AI — while *forecasting* a 24% speed-up beforehand and still *estimating* a 20% speed-up afterward. A roughly 39-point gap between felt and actual, in experts, on their own code. (Small sample, experienced devs on mature repos; the robust, transferable finding is the perception gap, not a universal slowdown. METR's 2026 follow-up couldn't cleanly re-measure productivity because 30–50% of developers refused to do tasks without AI — which is its own kind of finding.)

This sits on top of decades of work on miscalibrated self-assessment. Poor performers systematically overrate themselves because the skill needed to do well is the same skill needed to *notice* you're doing badly (Kruger & Dunning, 1999); the gap survives real exams and even a cash incentive for accuracy (Ehrlinger et al., 2008). People rate their understanding of how things work far higher than they can actually explain, and only discover the gap when forced to spell it out (Rozenblit & Keil, 2002). And specifically with AI: people solving reasoning problems with a chatbot scored higher but overestimated themselves more — with *higher* AI-literacy predicting *worse* calibration, not better (Fernandes et al., 2025).

Put together: the feeling of competence is not a readout of competence, the AI inflates the feeling, and experience doesn't protect you. That is the entire case for externalising the record instead of trusting the gut.

## The leading indicator

Here is the part that is new. Everything else measures surrender *after* it shows up in the work — once quality degrades, once a confident wrong answer ships. That is a lagging indicator.

There is an earlier signal. Dependency erodes two things in sequence: first the capability, then the *wanting* to exercise it. Skill atrophy is the loss of the ability to check. **Appetite atrophy** is the loss of the desire to — and it comes first. A person who *can* still challenge the AI but no longer *bothers* is the early case, not the late one.

That is measurable, descriptively: the rate at which justification is left blank, or "ship it" is typed, at a one-way door — on tasks plainly still within your ability — read over time. The question isn't whether you're a compliant reviewer; it's whether the wanting-to-own has started to fade. Extended to the patron era, the same read becomes the *contest rate* at sign-off: when an autonomous run completes, do you genuinely contest even one of its decisions, or accept the whole thing whole?

## Why awareness isn't enough

The uncomfortable corollary of the automation literature is that knowing about this changes very little. Complacency and bias persist in trained experts (Parasuraman & Manzey, 2010); training fixed commission but not omission errors (Skitka et al., 1999); my own awareness, on its own, produced no behaviour change.

What *has* worked, where it has worked, is a structural forcing function rather than exhortation. Croskerry (2003) argued that in medicine, knowing a bias exists is insufficient — clinicians need pre-committed "cognitive forcing strategies" that force a metacognitive check before acting. Surgical and ICU checklists cut deaths and infections sharply when they genuinely changed the cognitive process (Pronovost et al., 2006; Haynes et al., 2009) — and, critically, did *nothing* when rolled out as box-ticking without engagement (Urbach et al., 2014). A recent synthesis names this directly for AI: "scaffolded cognitive friction," repurposing the machinery as a forcing function rather than a frictionless answer-dispenser (Xu et al., 2026, preprint).

This is also why the historical record is unforgiving for tools defended only by individual willpower. Capacities preserved at scale were rescued by **codified curriculum, professional/guild standard, or provider infrastructure** — never by people resolving to try harder. Aviation rescued manual flying after Air France 447 not with a memo but with mandatory Upset Prevention and Recovery Training written into recurrent checks (BEA, 2012; FAA, 2013; ICAO/FAA UPRT mandates). A London cab driver's posterior hippocampus is measurably enlarged by *The Knowledge* — a multi-year curriculum, not good intentions (Maguire et al., 2000). Spelling, GPS-era spatial memory, and sustained attention, defended by no one, eroded.

The implication for a tool like this is honest and limiting: a personal practice tool genuinely helps the person who runs it, and will not, on its own, preserve a capacity across a population. It demonstrates the shape of the missing measurement. Someone with curriculum, standard, or platform power ships it at scale.

## The honest objection

A document that only confirms itself is advocacy. The strongest counter-evidence is real, and it sharpens the thesis rather than sinking it.

**AI can deepen learning, not just offload it.** A randomised crossover trial at Harvard found students with a carefully designed AI tutor learned roughly twice as much as in active-learning class, in less time (Kestin et al., 2025). Intelligent tutoring systems have matched human tutors for years (VanLehn, 2011). Customer-support agents — especially novices — got 14–34% more productive and appeared to *learn* faster (Brynjolfsson et al., 2025). And cognitive offloading is, in general, a rational cost-benefit move, not a pathology (Risko & Gilbert, 2016).

**Alarm about new tools has a poor track record.** Orben (2020) documents a recurring "Sisyphean cycle" of technology panics in which fear outruns evidence and effect sizes prove far smaller than the headlines. Any claim that AI is rotting our judgment has to clear that bar, not assume it.

Two things rescue the argument, though — and both come from inside the counter-evidence. First, the wins are conditional on *how* the tool is used. Kestin's tutor was deliberately engineered to keep the learner active and refuse to hand over answers; VanLehn's effective systems were "step-based," not "answer-based"; Risko & Gilbert's own caveat is that offloaded capacities atrophy with disuse and that people are miscalibrated about *what* to offload. The decisive variable is active engagement versus passive consumption — which is exactly what this instrument tries to make visible. Second, even Dell'Acqua et al.'s (2025) celebrated BCG result cuts both ways: inside the "jagged frontier" of AI-suitable tasks, 758 consultants did ~12% more work, ~25% faster, at materially higher quality — but on a task placed just *outside* the frontier, AI users were 19 percentage points *less* likely to get it right, and the authors documented over-reliance, "falling asleep at the wheel." Knowing which side of the frontier you're on is judgment. Nobody is measuring it.

And the one reflex the optimistic case most needs, trusting how good the collaboration *felt*, is the exact reflex the evidence says to distrust. Students in active learning reliably *feel* they learned less while learning more (Deslauriers et al., 2019). Fluency is not the same as understanding, and feeling is not the same as fact.

## What this deliberately is not

Each constraint is load-bearing; removing it breaks the thing.

- **No score.** A single number re-instates the worth-by-output logic the project rejects and hands the user something to game. The readout surfaces what you steered, checked, and let slide. Never a grade.
- **No cross-user comparison.** The unit of analysis is *this person, over months* — not a leaderboard.
- **Stays on your machine.** Privacy is the precondition for measuring honest behaviour at all; an instrument you'd perform for measures the performance. Nothing identifiable leaves the device.
- **No cryptographic attestation — by choice.** It can prove a file wasn't altered, but not that the words were the human's, nor that capture was complete. A verification that can't establish what it asserts is worse than none. This answers only to the person running it.
- **No real-time nagging by default.** Off until installed; the one exception is reserved for the user's own highest cut-lines. And per the checklist evidence: a forcing function only works if it changes the actual cognitive process, not if it becomes another box to tick.

## What this implies

The same capture-and-synthesis substrate serves different readers as different things — not separate products, different readings of one record.

- **For individuals — the Mirror.** Patterns over time, the surrender signatures surfaced, at the one moment the loop can't watch itself: sign-off.
- **For teams — the Retro.** Teams rebuilt how they deliver around AI in months, and mostly never retro the collaboration itself — there is no record to retro over. Workflows live in individual dotfiles and habit; loops rot when nobody owns them; the actual ways-of-working exist nowhere except transcripts nobody reads. A period of digests, shared by choice for one conversation, is the retro pack: which workflows actually ran, what got steered, what got waved through, where ownership sits. Shared reading of self-owned records, never a dashboard of anyone else.
- **For enterprises — the Trail.** The audit trail you actually need is not the AI's logs of what it did, but the human's record of what they engaged with, challenged, and let through. AI-side-only observability is a one-sided accountability picture.
- **For professional bodies.** The AI-collaboration audit trail will become part of professional competence within five years. The fields that codify what "competent AI use" means will define it; the rest will have it defined for them.
- **For providers.** Ship the human-side counterpart to the model-side memory and observability you already build.

## Open questions

The answerable ones have moved into the argument above (whether you can self-assess: no; whether awareness alone fixes it: no). These remain genuinely open.

1. **Does the gap compound, or self-correct?** Does the drift worsen over months, or do people correct once they can see it? Answering needs far more longitudinal history than one person over four months.
2. **Does seeing your own mix change behaviour, or just hand you a number to game?** The intervention literature says forcing functions can change behaviour — but only when they alter the real cognitive process, not when they're performed.
3. **What's the right altitude — individual, team curriculum, or platform?** And how do you surface it without becoming the tool people switch off on day one?

## Limitations and honest status

This is one person's data: a small corpus (tens of classified sessions, 192 transcripts, four months, a single tool surface — maybe a fifth of even my own AI use). The headline numbers are estimates that move a point or two. Silent checking is invisible to the method, as is the structured verification real work runs on (review, tests, red-teaming, staged deployment), so the in-session signal may flatter or damn me unfairly; it is one channel, not the whole of anyone's diligence. Several supporting studies are preprints (Kosmyna; Xu) or vendor/correlational work (GitClear) and are flagged as such; some are real-time-bias rather than proven long-term deskilling (Dratsch); and genuine counter-evidence exists (above). The leading indicator has a real failure mode: if the modal answer at a one-way door is "ship it," the field is noise and the signal flatlines — in which case the artefact is theatre and the right move is to stop. I am holding that kill criterion.

What this is, then, is not a finished result. It is the form of the argument clear enough to attack and improve — with a forty-year evidence base behind the mechanism and real, if undersized, data behind the personal claim. It is a living document; it will be revised as the corpus grows and the open questions close. The repo is public and MIT-licensed; there are no patents, because a measurement instrument for your own judgment only works if it is inspectable. If this is your question too, I'd like to swap notes.

---

## References

*Grouped by role in the argument. Statistics in the text are drawn from these sources; preprints, vendor research, and contested findings are flagged where they appear.*

**Automation & human factors (the mechanism)**
- Bainbridge, L. (1983). Ironies of Automation. *Automatica*, 19(6), 775–779.
- Parasuraman, R., & Riley, V. (1997). Humans and Automation: Use, Misuse, Disuse, Abuse. *Human Factors*, 39(2), 230–253.
- Mosier, K. L., Skitka, L. J., Heers, S., & Burdick, M. (1998). Automation Bias: Decision Making and Performance in High-Tech Cockpits. *International Journal of Aviation Psychology*, 8(1), 47–63.
- Skitka, L. J., Mosier, K. L., & Burdick, M. (1999). Does Automation Bias Decision-Making? *International Journal of Human-Computer Studies*, 51(5), 991–1006.
- Endsley, M. R. (1996). Automation and Situation Awareness. In Parasuraman & Mouloua (Eds.), *Automation and Human Performance* (pp. 163–181). Erlbaum.
- Parasuraman, R., & Manzey, D. H. (2010). Complacency and Bias in Human Use of Automation: An Attentional Integration. *Human Factors*, 52(3), 381–410.

**AI-era empirical (the same pattern in software)**
- Becker, J., Rush, N., Barnes, E., & Rein, D. (2025). Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity. METR / arXiv:2507.09089. (METR 2026 follow-up: *We Are Changing Our Developer Productivity Experiment Design*.)
- Lee, H.-P., Sarkar, A., Tankelevitch, L., Drosos, I., Rintel, S., Banks, R., & Wilson, N. (2025). The Impact of Generative AI on Critical Thinking. *CHI 2025* (Microsoft Research).
- Kosmyna, N., et al. (2025). Your Brain on ChatGPT: Accumulation of Cognitive Debt When Using an AI Assistant for Essay Writing. MIT Media Lab / arXiv:2506.08872. *(Preprint.)*
- Shen, J. H., & Tamkin, A. (2026). How AI Assistance Impacts the Formation of Coding Skills. Anthropic.
- GitClear (2025). *AI Copilot Code Quality: 2025 Research* (211M changed lines). *(Vendor research; correlational.)*
- Stack Overflow (2025). *2025 Developer Survey* (n ≈ 49,000+).
- Casner, S. M., Geven, R. W., Recker, M. P., & Schooler, J. W. (2014). The Retention of Manual Flying Skills in the Automated Cockpit. *Human Factors*, 56(8), 1506–1516.
- Dahmani, L., & Bohbot, V. D. (2020). Habitual Use of GPS Negatively Impacts Spatial Memory During Self-Guided Navigation. *Scientific Reports*, 10, 6310.
- Dratsch, T., et al. (2023). Automation Bias in Mammography: The Impact of AI BI-RADS Suggestions on Reader Performance. *Radiology*, 307(4), e222176. *(Real-time bias, not long-term deskilling.)*

**Self-assessment & metacognition (why you can't see it)**
- Kruger, J., & Dunning, D. (1999). Unskilled and Unaware of It. *Journal of Personality and Social Psychology*, 77(6), 1121–1134.
- Rozenblit, L., & Keil, F. (2002). The Misunderstood Limits of Folk Science: An Illusion of Explanatory Depth. *Cognitive Science*, 26(5), 521–562.
- Ehrlinger, J., Johnson, K., Banner, M., Dunning, D., & Kruger, J. (2008). Why the Unskilled Are Unaware. *Organizational Behavior and Human Decision Processes*, 105(1), 98–121.
- Fernandes, D., et al. (2025). AI Makes You Smarter, But None the Wiser: The Disconnect Between Performance and Metacognition. *CHI 2025* / arXiv:2409.16708.

**Interventions & skill formation (what would actually work)**
- Sweller, J., & Cooper, G. A. (1985). The Use of Worked Examples as a Substitute for Problem Solving in Learning Algebra. *Cognition and Instruction*, 2(1), 59–89.
- Croskerry, P. (2003). Cognitive Forcing Strategies in Clinical Decisionmaking. *Annals of Emergency Medicine*, 41(1), 110–120.
- Roediger, H. L., & Karpicke, J. D. (2006). Test-Enhanced Learning. *Psychological Science*, 17(3), 249–255.
- Pronovost, P., et al. (2006). An Intervention to Decrease Catheter-Related Bloodstream Infections in the ICU. *NEJM*, 355(26), 2725–2732.
- Haynes, A. B., Weiser, T. G., Berry, W. R., Gawande, A. A., et al. (2009). A Surgical Safety Checklist to Reduce Morbidity and Mortality in a Global Population. *NEJM*, 360(5), 491–499. (Null on mass rollout: Urbach et al., 2014, *NEJM*.)
- Xu, K., Shen, Y., Yan, L., & Ren, Y. (2026). Cognitive Agency Surrender: Defending Epistemic Sovereignty via Scaffolded AI Friction. arXiv:2603.21735. *(Preprint.)*

**Counter-evidence & critiques (the honest objection)**
- Dell'Acqua, F., et al. (2025). Navigating the Jagged Technological Frontier. *Organization Science* (HBS WP 24-013, N = 758).
- Brynjolfsson, E., Li, D., & Raymond, L. (2025). Generative AI at Work. *Quarterly Journal of Economics*, 140(2) (NBER WP 31161).
- Kestin, G., Miller, K., Klales, A., Milbourne, T., & Ponti, G. (2025). AI Tutoring Outperforms In-Class Active Learning. *Scientific Reports*, 15, 17458.
- VanLehn, K. (2011). The Relative Effectiveness of Human Tutoring, Intelligent Tutoring Systems, and Other Tutoring Systems. *Educational Psychologist*, 46(4), 197–221.
- Risko, E. F., & Gilbert, S. J. (2016). Cognitive Offloading. *Trends in Cognitive Sciences*, 20(9), 676–688.
- Deslauriers, L., McCarty, L. S., Miller, K., Callaghan, K., & Kestin, G. (2019). Measuring Actual Learning Versus Feeling of Learning. *PNAS*, 116(39), 19251–19257.
- Orben, A. (2020). The Sisyphean Cycle of Technology Panics. *Perspectives on Psychological Science*, 15(5), 1143–1157.
- Carr, N. (2014). *The Glass Cage: Automation and Us*. W. W. Norton.

**Practitioner & contemporary framing**
- Mollick, E. (2026). *What It Feels Like to Work with Mythos* and *Choosing to Stay Human* (2025). One Useful Thing.
- Osmani, A. (2026). *Loop Engineering*. Cherny, B. (2026), Head of Claude Code.
- Das, D. (2026). On the "craftsman tax" in AI-mandated engineering teams. Menlo Ventures commentary, via Business Insider (June 2026) and the ~8,000-upvote r/technology discussion that followed. *(Practitioner reports; selection bias toward the aggrieved, counter-voices noted in text.)*
- Anthropic. *AI Fluency Index*; *What 81,000 People Want from AI*; *The Anthropic Economic Index*.

*Crux · A living research document · v1.1 · July 2026 · No patents. Public by design.*
