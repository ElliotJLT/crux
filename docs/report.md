# Measuring the human side of AI

*A field report on a gap nobody is filling, and why even measuring it turns out to be hard. June 2026.*

---

## The gap

For two years the work has gone into measuring the model. Evals, observability, agent memory. More than $200M of funding, and almost all of it points at the machine. The person sitting next to it has no equivalent gauge. You can audit an agent's every step. You cannot audit your own.

The worry is not hypothetical. Wharton's name for what is happening is *cognitive surrender*: the work ships faster while the human's grip on it gets thinner. Ethan Mollick's case is that willpower will not fix this; the constraint has to be built into the system, because the evidence has been piling up for two years.

## What is already known

Independent studies keep landing in the same place.

- Consultants given GPT-4 beat the control group on tasks the model handled well, and lost to it on tasks the model got confidently wrong (BCG / Dell'Acqua, N=758). They did not lose competence. They lost the habit of pushing back.
- People using an LLM spent roughly half the mental effort of people using search on the same task (MIT Media Lab).
- Passive AI use lowers ownership and self-efficacy, and the dip outlasts the tool itself (Nature, Lee et al., N=539).
- Among 81,000 Claude users, losing one's edge came fourth on the list of concerns. 13,000 raised it directly, and close to half said they already feel it (Anthropic).
- The more polished the output looks, the less people check it. Context-checking and reasoning-questioning both fall (Anthropic, AI Fluency Index).

The thread running through all of it is not "people use AI too much." It is that the human stops doing the part that was theirs: deciding what to trust, and checking whether it is true.

## The hypothesis

The first thing to erode is not the quality of the output. It is the wanting to check.

If that is right, the signal to watch is not whether the code passes. It is the mix in how a person answers the machine. Four things you can do when the AI hands you something: verify that it is correct, steer how it looks or works, give it the next instruction, or wave it through. Track that mix over time, the theory goes, and the erosion shows up in the human long before it shows up in the work.

## What happens when you try to measure it

Two findings, and the second is the interesting one.

First, the rough shape. Read against real coding sessions, the estimates land somewhere around:

- you check whether the AI is actually right maybe one time in four;
- you wave work through without looking maybe one time in seven;
- about a third of what you send is not a check at all, it is the next instruction.

Treat those as estimates, not readings off a dial.

Second, and this is the part worth keeping: the number will not hold still. Count it with keywords and a stray question mark reads as scrutiny it was not. Hand the same sessions to an LLM to grade and it labels them differently on each pass, by enough to flip the headline. The honest answer is a range, and the range is wide.

That instability is the result, not a failure of effort. Human judgment is hard to see from the outside, which is the reason no gauge for it exists. If it were easy, someone with $200M would have shipped it already.

## What a fix could look like

Quiet, local, and aimed at the person rather than the model.

- It captures the decisions behind the work on your own machine: what you steered, what you checked, what you let go.
- It shows the mix and the drift over time, the way a training log shows a runner their pace. No score. Nothing leaves the device.
- It stays silent during the work. The read is for afterwards, and it is for you.

The aim is not a verdict. It is a mirror at the one point in the loop that cannot watch itself: the human signing off.

## Open questions

The honest list, roughly ordered by how much each would change the picture.

- What is the right unit to watch? A single turn, a whole session, the irreversible commands, or the moment you accept a long autonomous run you never watched?
- How much checking is silent? Reading a diff and saying nothing is real scrutiny that no transcript records, and no measure here can see it.
- Does the gap compound over months, or do people correct once they can see it? Answering that needs far more history than a couple of months.
- Does showing someone their own mix change how they work, or just hand them a number to game?
- Is the right altitude the individual, the team's curriculum, or the platform itself? History says the last two are what actually keep a skill alive. The first helps whoever bothers to look.
- And the one that kills most attempts: how do you surface any of this without becoming the nagging tool people switch off on day one?

## Where this stands

This is an open inquiry, not a finished answer. The gap is real and well-evidenced. A clean way to measure it is not yet in hand, and the difficulty of measuring it is itself a finding. A personal tool is worth building for the person who runs it, and on its own it will not save the population. That has always taken a curriculum, a platform, or a professional standard.

If you work near this, in research, in AI adoption, or in building, the argument and the open questions are here to be argued with.
