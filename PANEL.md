# Crux panel protocol

Protocol version: 1.0

Crux is ongoing research on whether people keep exercising judgment when AI does the work. The panel is a plugin for Claude Code that counts two kinds of moment on your own machine and lets you export the counts. It is a study, not a product. Joining is optional and you can leave at any time.

## What it measures

### 1. One-way doors

A one-way door is a Bash command that is hard or impossible to take back: a force push, a deleted remote branch, `rm -rf`, destructive SQL, a deploy or publish, a PR merge, a repo deletion, a secret rotation. The full list is `taxonomy/cutlines.yml`, hard tier only. The twelve rules are: git-force-push, git-push-delete-remote, git-branch-force-delete, rm-rf, sql-destructive, db-reset, prod-migration, deploy, gh-release, gh-pr-merge, gh-repo-delete, secret-rotation. Text inside heredocs is ignored.

One exemption: an `rm -rf` does not count as a door when every target is routine. Nothing is logged for it, not even a count. A target is routine if it matches this case-insensitive regex:

```
(/tmp\b|/private/tmp|\btmp/|node_modules|\bdist\b|\bbuild/|\.cache|coverage|__pycache__|\bvenv\b|\.claude/worktrees|\btarget/)
```

An `rm -rf` followed later in the same command by `git clone` or `gh repo clone` is also exempt, using this case-insensitive, dot-matches-newline regex:

```
rm\s+-[a-z]*r[a-z]*f?\s+(\S+).*?(?:git|gh)\s+(?:repo\s+)?clone\b
```

So `rm -rf node_modules` and `rm -rf /tmp/x` pass; `rm -rf src` and `rm -rf node_modules src` fire. Both regexes are copied from `scripts/cutline-dryrun.py`.

What the plugin does at a door:

1. The first time a command matches, the plugin blocks it and tells Claude to ask you for a one-line reason. The command does not run.
2. Your next message in that session is recorded as your reason.
3. When Claude re-runs the command, it is allowed. A reason covers re-runs of the same rule in that session for 15 minutes.

Each door ends in one outcome:

- reasoned: you gave a reason and the command ran.
- blank: you gave a non-reason and the command ran.
- withdrawn: your reply contained a stop marker, or the command did not run within 15 minutes of your reply.
- unanswered: you never replied within 15 minutes.

A reply is blank if it has fewer than 4 words, or if the whole reply, lowercased and with punctuation removed, is a rubber-stamp reply. Otherwise it is reasoned.

- Rubber-stamp replies: ok, yes, yep, y, go, do it, ship it, just do it, fine, sure, approved, lgtm, proceed
- Stop markers: no, don't, stop, wait, cancel, hold on, instead

Markers match whole words or phrases, case-insensitively. A door that is still inside its 15-minute window at export time is left out of the counts and appears in a later export.

### 2. Sign-off of autonomous runs

When Claude finishes a turn in which the main agent made 8 or more tool calls, that is a sign-off. Tool calls are counted from your last prompt to the end of the turn; subagent calls are not counted. A turn that ends at an open one-way door is not counted as a sign-off.

Sizes: 8-19, 20-49, 50+ tool calls.

Your next message in the session is classified once, by these rules in this order:

1. contest: it contains a pushback marker, or it ends with "?".
2. accept: it has fewer than 12 words and contains an accept marker.
3. neutral: anything else.

If you never send another message, the sign-off counts as no response.

- Pushback markers: why, wrong, no, not, don't, instead, actually, revert, undo, rather, wait, hmm
- Accept markers: thanks, great, nice, perfect, ship, commit, merge, push, lgtm, good, next, done

A message that answers a one-way door is not also classified as a sign-off response. Slash commands and background task notices are ignored.

These parameters, the marker lists and the 15-minute window are fixed for the study. They change only with a protocol version bump, and data from different versions is not pooled.

## What stays on your machine

Everything is logged to `~/.crux/panel/` (or `CRUX_PANEL_DIR`). The local log holds timestamps, a session id, the rule id that fired, word counts, the classifications, and the text of your one-line reasons. It does not hold commands, file paths, project names, Claude's output or your other prompts.

Nothing is sent anywhere by the plugin. It makes no network calls.

## What an export contains

`export` writes counts per ISO week, a random participant id, the protocol version and a timestamp. For each week: sessions with activity, number of doors, doors by outcome, sign-offs, sign-off responses (contest, accept, neutral, none), and the same sign-off counts split by size. No command text, prompt text, reasons, file paths, project names or session ids are included. The export is plain JSON. Read it before you send it.

## Install

In Claude Code:

```
/plugin marketplace add ElliotJLT/crux
/plugin install crux-panel@crux
```

Or from a shell:

```
claude plugin marketplace add ElliotJLT/crux
claude plugin install crux-panel@crux
```

Restart Claude Code, or run `/reload-plugins`. Needs `python3` 3.9 or newer on your PATH. Tested on macOS.

Be aware of the effect on your sessions: the first attempt at each one-way door is blocked once and Claude will ask you why. That is the measurement.

## Export and send

Run `/crux-panel:panel-export` in Claude Code. It writes `~/.crux/panel/export.json`, prints the path and shows you the contents. Send the file to [needs: where participants send exports].

Please export after the first four weeks and again at the end of the 12-week study period.

## Pause or leave

- Pause: set `CRUX_PANEL=off` in your environment. Every hook then exits without doing anything.
- Leave: `claude plugin uninstall crux-panel@crux`, then `rm -rf ~/.crux/panel`. That removes the participant id and every log. Exports you already sent can be deleted on request, using the participant id in the file.

## Hypotheses (pre-registered)

H1 (descriptive): across participants, the blank-justification rate at one-way doors is above 25%.

H2: within a participant, the blank-justification rate rises over the study period (12 weeks) rather than falling.

H3: the sign-off contest rate is lower for long autonomous runs (50+ tool calls) than short ones (8-19).

Kill criterion: if fewer than 15 participants export at least 4 weeks of data, the study reports as underpowered and makes no population claim.

The blank-justification rate is blank / (reasoned + blank). The contest rate is contest / sign-offs.

## Known limits

- Claude Code writes the transcript asynchronously, so the last tool calls of a turn can be missing when the Stop hook counts them. Counts can run slightly low.
- The routine-`rm -rf` exemption is a text match on the target, not a check of what the path is. A path that merely contains `build/` or `node_modules` is treated as routine. The clone exemption looks at the whole command after the `rm`, so it can exempt an unrelated delete that is followed by a clone.
- The classifiers are word lists. They are crude on purpose and fixed in advance, so the error is the same for everyone.
- Participants are heavy Claude Code users who chose to join. The study makes no claim about the general population.
