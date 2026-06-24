#!/bin/bash
# crux digest worker — generates a digest from session metadata
# Called by auto-digest.sh with the work file path as $1

CRUX_DIR="${CRUX_DIR:-$HOME/crux}"
CLAUDE_BIN="$(command -v claude)"
DIGEST_DIR="$CRUX_DIR/decisions/digests"
LOG="$CRUX_DIR/scripts/auto-digest.log"

log() { echo "$(date '+%H:%M:%S') $1" >> "$LOG"; }

WORK_FILE="$1"
if [[ -z "$WORK_FILE" || ! -f "$WORK_FILE" ]]; then
  log "ERROR: no work file"
  exit 1
fi

INPUT=$(cat "$WORK_FILE")
rm -f "$WORK_FILE"

TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')
REASON=$(echo "$INPUT" | jq -r '.reason // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

log "=== session: reason=$REASON cwd=$CWD ==="

# Opt-out: skip if .crux-skip exists in the session's working directory
if [[ -f "$CWD/.crux-skip" ]]; then
  log "SKIP: .crux-skip found in $CWD"
  exit 0
fi

# Opt-out: skip via environment variable
if [[ "$CRUX_SKIP" == "1" ]]; then
  log "SKIP: CRUX_SKIP=1"
  exit 0
fi

# Skip non-substantive sessions
if [[ -z "$TRANSCRIPT" || ! -f "$TRANSCRIPT" ]]; then
  log "SKIP: no transcript file"
  exit 0
fi

# Extract condensed transcript using Python
export DT_TRANSCRIPT="$TRANSCRIPT"
CONDENSED=$(python3 "$CRUX_DIR/scripts/extract-transcript.py")

# Skip short sessions
USER_COUNT=$(echo "$CONDENSED" | grep -c "^USER:" || true)
log "user_messages=$USER_COUNT"
if [[ "$USER_COUNT" -lt 4 ]]; then
  log "SKIP: too few messages ($USER_COUNT)"
  exit 0
fi

# Determine digest filename
TODAY=$(date +%Y-%m-%d)
mkdir -p "$DIGEST_DIR"
EXISTING=$(ls "$DIGEST_DIR"/${TODAY}-session-*.md 2>/dev/null | wc -l | tr -d ' ')
NEXT=$((EXISTING + 1))
DIGEST_FILE="$DIGEST_DIR/${TODAY}-session-${NEXT}.md"

# Load the controlled vocab for patterns (RAG-stable tags)
PATTERNS_FILE="$CRUX_DIR/taxonomy/patterns.yml"
if [[ -f "$PATTERNS_FILE" ]]; then
  PATTERNS_VOCAB=$(cat "$PATTERNS_FILE")
else
  PATTERNS_VOCAB="(taxonomy file missing — invent kebab-case slugs)"
fi

# Find the most recent prior digest to enable trajectory linking
PRIOR_DIGEST=$(ls -t "$DIGEST_DIR"/*.md 2>/dev/null | head -1)
PRIOR_CONTEXT=""
if [[ -n "$PRIOR_DIGEST" ]]; then
  PRIOR_NAME=$(basename "$PRIOR_DIGEST" .md)
  PRIOR_LEDE=$(head -20 "$PRIOR_DIGEST")
  PRIOR_CONTEXT="MOST RECENT PRIOR DIGEST (for trajectory linking — only link if genuinely related):
session_id: ${PRIOR_NAME}
${PRIOR_LEDE}
"
fi

# Truncate to stay within context limits
TRUNCATED=$(echo "$CONDENSED" | head -c 40000)

# Build the full prompt in a temp file
TMPFILE=$(mktemp /tmp/dt-prompt-XXXXXX.txt)
cat > "$TMPFILE" << ENDPROMPT
You are generating a crux digest from a Claude Code session transcript.

The digest has two audiences:
1. Elliot, reading it next month to spot how his judgement is trending.
2. An LLM doing retrieval across many digests for trajectory analysis.

So the digest must be (a) readable in 30 seconds with a clear punchline, and
(b) structured with YAML frontmatter so it's queryable.

PATTERN VOCAB (use exact slugs from this list; if a pattern isn't covered, omit it):
${PATTERNS_VOCAB}

${PRIOR_CONTEXT}

OUTPUT FORMAT — emit exactly this, nothing else:

---
date: ${TODAY}
session_id: ${TODAY}-session-${NEXT}
project: [short kebab-case project name e.g. argus, crux, applications, or "general"]
duration: [short | medium | long]
shape: [research | shipping | refinement | planning | debugging | writing | mixed]
interaction_type: [directive | feedback-loop | task-iteration | validation | learning]
collaboration_mode: [automation | augmentation]
fluency:
  delegation: [strong | medium | weak | not-observed]
  description: [strong | medium | weak | not-observed]
  discernment: [strong | medium | weak | not-observed]
  diligence: [strong | medium | weak | not-observed]
patterns: [pick 1-4 slugs from the vocab above]
concepts: [3-6 free-form topical tags — kebab-case, domain or tool names]
related: [list 0-1 prior session_ids if there's a genuine arc; otherwise []]
---

# [3-6 word session title] — ${TODAY}

> [One line under 25 words. Self-contained — no "this" or "that" referring to outside context. The punchline of the session. Ideally contains a real user quote.]

## The moment
[2-4 sentences. The single decision that shaped the session. Quote the user verbatim where it lands — italicise quotes. Concrete over abstract.]

## What you steered
[Max 3 bullets. Use second person ("you"). Each bullet should embed a real quote or a specific decision.]
- **[short verb phrase].** *"[user quote]"* → [what changed because of it]

## What you let slide
[1-3 bullets. Be honest — moments the user accepted output without scrutiny. Was the trust warranted, or lazy? If genuinely nothing slid, write "Nothing notable — every output got checked."]
- [What was accepted → was the trust warranted? → consequence if not]

## The pattern
**[bold one-line pattern in plain English].** [1-2 sentences explaining when this shows up and what it costs or unlocks.]

## Trajectory note
[1-2 sentences. If the session echoes the prior digest above, name it with [[session_id]] wikilink and say what's repeating. If not, write "Standalone — no echo of recent sessions."]

HARD RULES:
- If the session was trivial (config, installs, quick lookups), output exactly: SKIP
- Honest over flattering. If the user coasted, say so plainly.
- No file paths, env vars, API keys, architecture details, internal service names, or company-confidential info anywhere.
- Real quotes only — never fabricate user words. If you can't find a quote that lands, paraphrase and skip the italics.
- YAML must be valid. Use [] for empty lists. Lowercase enum values.
- Project name: pick from {argus, crux, applications, multiverse, boulot, cervo, bungalow-ai, writing, general} — or invent a kebab-case one if none fit.
- Concepts are flexible topical tags (e.g. autonomous-agents, claude-skills, mcp, hooks, cv, linkedin-post). Avoid hyper-specific feature names.
- Patterns MUST be from the vocab above. Empty list is fine if nothing matches.
- "Trajectory note" only links a prior session if the pattern or project genuinely overlaps.

TRANSCRIPT:
${TRUNCATED}
ENDPROMPT

PROMPT_SIZE=$(wc -c < "$TMPFILE" | tr -d ' ')
log "generating digest (${PROMPT_SIZE} bytes)..."

# Generate digest — stdin from prompt file, /dev/null for claude's stdin
DIGEST=$(cat "$TMPFILE" | "$CLAUDE_BIN" -p 2>> "$LOG")
CLAUDE_EXIT=$?
log "claude exit=$CLAUDE_EXIT digest_len=${#DIGEST}"

rm -f "$TMPFILE"

# Skip trivial or failed
if [[ "$DIGEST" == *"SKIP"* ]] || [[ -z "$DIGEST" ]]; then
  log "SKIP: trivial or empty"
  exit 0
fi

# Skip if the response looks like an API error or timeout, not a real digest.
# Real digests start with YAML frontmatter (---). Anything else is garbage.
if ! echo "$DIGEST" | head -1 | grep -q '^---$'; then
  log "SKIP: response doesn't start with frontmatter (likely API error or auth failure)"
  log "first line: $(echo "$DIGEST" | head -1)"
  exit 0
fi
if ! echo "$DIGEST" | grep -q '## The moment'; then
  log "SKIP: response missing 'The moment' section (likely malformed)"
  exit 0
fi

# Write digest
echo "$DIGEST" > "$DIGEST_FILE"
log "wrote $DIGEST_FILE"

# Commit and push
cd "$CRUX_DIR"
git add "$DIGEST_FILE" 2>> "$LOG"
TOPIC=$(head -1 "$DIGEST_FILE" | sed 's/^# [0-9-]* — //' | head -c 50)
git commit -m "digest: ${TOPIC}" >> "$LOG" 2>&1
git push >> "$LOG" 2>&1
log "DONE"
