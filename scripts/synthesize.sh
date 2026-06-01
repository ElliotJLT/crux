#!/bin/bash
# decision-trail synthesize — generates trajectory synthesis from accumulated digests
# Can be run manually, via cron, or called by /trail.
#
# Usage: ./synthesize.sh [--force]
#   --force: generate even if fewer than 5 new digests since last synthesis

set -euo pipefail

DECISION_TRAIL_DIR="${DECISION_TRAIL_DIR:-$HOME/decision-trail}"
CLAUDE_BIN="$(command -v claude)"
DIGEST_DIR="$DECISION_TRAIL_DIR/decisions/digests"
SYNTH_DIR="$DECISION_TRAIL_DIR/decisions/synthesis"
LOG="$DECISION_TRAIL_DIR/scripts/auto-digest.log"

log() { echo "$(date '+%H:%M:%S') [synthesize] $1" >> "$LOG"; }

# Dependency check
for dep in jq python3; do
  if ! command -v "$dep" &>/dev/null; then
    echo "decision-trail: missing dependency: $dep" >&2
    exit 1
  fi
done

if [[ -z "$CLAUDE_BIN" ]]; then
  echo "decision-trail: claude CLI not found in PATH" >&2
  exit 1
fi

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
fi

mkdir -p "$SYNTH_DIR"

# Count total digests
DIGEST_COUNT=$(ls "$DIGEST_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
if [[ "$DIGEST_COUNT" -eq 0 ]]; then
  echo "No digests found in $DIGEST_DIR"
  exit 0
fi

# Find the most recent synthesis
LAST_SYNTH=$(ls -t "$SYNTH_DIR"/*.md 2>/dev/null | head -1)
LAST_SYNTH_DATE=""
if [[ -n "$LAST_SYNTH" ]]; then
  LAST_SYNTH_DATE=$(basename "$LAST_SYNTH" .md)
fi

# Count digests newer than last synthesis
if [[ -n "$LAST_SYNTH" ]]; then
  NEW_COUNT=$(find "$DIGEST_DIR" -name "*.md" -newer "$LAST_SYNTH" 2>/dev/null | wc -l | tr -d ' ')
else
  NEW_COUNT="$DIGEST_COUNT"
fi

log "total_digests=$DIGEST_COUNT new_since_last=$NEW_COUNT last_synth=$LAST_SYNTH_DATE"

if [[ "$NEW_COUNT" -lt 5 && "$FORCE" -eq 0 ]]; then
  echo "Only $NEW_COUNT new digests since last synthesis (need 5+). Use --force to override."
  exit 0
fi

# Collect all digests
ALL_DIGESTS=""
for f in $(ls "$DIGEST_DIR"/*.md 2>/dev/null | sort); do
  ALL_DIGESTS+="$(cat "$f")"
  ALL_DIGESTS+=$'\n\n---\n\n'
done

# Run metrics to get quantitative data
METRICS_OUTPUT=""
if python3 -c "from decision_trail.metrics import collect_from_digests, build_summary; from pathlib import Path" 2>/dev/null; then
  METRICS_OUTPUT=$(python3 -c "
from pathlib import Path
from decision_trail.metrics import collect_from_digests, build_summary

root = Path('$DECISION_TRAIL_DIR')
sessions = collect_from_digests(root)
summary = build_summary(sessions)

# Count interaction types and collaboration modes from Classification sections
import re
auto_count = 0
aug_count = 0
interaction_types = {}

for p in sorted((root / 'decisions' / 'digests').glob('*.md')):
    text = p.read_text()
    mode = None
    itype = None
    # New format: YAML frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        m = re.search(r'^collaboration_mode:\s*(\w+)', fm, re.MULTILINE)
        if m:
            mode = m.group(1).lower()
        t = re.search(r'^interaction_type:\s*([\w-]+)', fm, re.MULTILINE)
        if t:
            itype = t.group(1).lower()
    # Fallback to legacy prose format
    if mode is None:
        m = re.search(r'\*\*Collaboration mode:\*\*\s*(automation|augmentation)', text, re.IGNORECASE)
        if m:
            mode = m.group(1).lower()
    if itype is None:
        t = re.search(r'\*\*Interaction type:\*\*\s*(directive|feedback-loop|task-iteration|validation|learning)', text, re.IGNORECASE)
        if t:
            itype = t.group(1).lower()
    if mode == 'automation':
        auto_count += 1
    elif mode == 'augmentation':
        aug_count += 1
    if itype:
        interaction_types[itype] = interaction_types.get(itype, 0) + 1

print(f'Sessions: {summary.total_sessions}')
print(f'Avg engagement: {summary.avg_engagement_score:.0f}/100')
print(f'Avg override rate: {summary.avg_override_rate:.0%}')
print(f'Total redirects: {summary.total_redirects}')
print(f'Total unchallenged: {summary.total_unchallenged}')
print(f'Total wrong calls: {summary.total_wrong_calls}')
print(f'Override trend: {summary.override_rate_trend.direction}')
print(f'Engagement trend: {summary.engagement_trend.direction}')
if summary.coasting_alerts:
    for a in summary.coasting_alerts:
        print(f'ALERT: {a.message}')
total_classified = auto_count + aug_count
if total_classified > 0:
    print(f'Automation sessions: {auto_count}/{total_classified} ({auto_count/total_classified*100:.0f}%)')
    print(f'Augmentation sessions: {aug_count}/{total_classified} ({aug_count/total_classified*100:.0f}%)')
    print(f'Benchmark: high-tenure users average ~59% augmentation (Anthropic Economic Index)')
if interaction_types:
    print(f'Interaction types: {interaction_types}')

# Pattern frequency from new-format YAML frontmatter
pattern_counts = {}
project_counts = {}
for p in sorted((root / 'decisions' / 'digests').glob('*.md')):
    text = p.read_text()
    fm_match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not fm_match:
        continue
    fm = fm_match.group(1)
    proj = re.search(r'^project:\s*([\w-]+)', fm, re.MULTILINE)
    if proj:
        project_counts[proj.group(1)] = project_counts.get(proj.group(1), 0) + 1
    pat = re.search(r'^patterns:\s*\[(.*?)\]', fm, re.MULTILINE)
    if pat:
        for tag in re.findall(r'[\w-]+', pat.group(1)):
            pattern_counts[tag] = pattern_counts.get(tag, 0) + 1
if pattern_counts:
    top = sorted(pattern_counts.items(), key=lambda x: -x[1])[:10]
    print(f'Top patterns: {top}')
if project_counts:
    print(f'Project breakdown: {project_counts}')
" 2>/dev/null) || true
fi

# Truncate digests to fit context (use bash substring — pipe to head SIGPIPEs under pipefail)
TRUNCATED="${ALL_DIGESTS:0:60000}"

MONTH=$(date +%Y-%m)
TMPFILE=$(mktemp /tmp/dt-synth-XXXXXX.txt)
cat > "$TMPFILE" << ENDPROMPT
You are generating a decision-trail trajectory synthesis from accumulated session digests.

QUANTITATIVE METRICS:
${METRICS_OUTPUT:-No metrics available — classify from digests directly.}

DIGESTS:
${TRUNCATED}

FRAMEWORK — Anthropic Economic Index interaction types:
- directive: user gives clear instructions, AI executes
- feedback-loop: iterative refinement with review cycles
- task-iteration: collaborative subtask building
- validation: using AI to check/verify existing work
- learning: exploring, asking questions, building understanding

Collaboration modes:
- automation: AI does work human could do but faster
- augmentation: AI extends what human can do, human thinks alongside

Benchmark: high-tenure Claude users average ~59% augmentation (Anthropic Economic Index).

Voice: write directly to Elliot in second person ("you"). Conversational, tight,
no corporate hedging. Honest over flattering. Quote real moments from the digests
where it lands harder than abstract description.

Open with a one-line punchline (the headline insight of the month). Then sections.

Generate the synthesis in this exact format, including YAML frontmatter so it's
RAG-queryable like the digests:

---
month: ${MONTH}
sessions: [N]
top_patterns: [list the 3-5 most frequent patterns from the metrics above]
trending_up: [patterns or behaviours genuinely improving — empty list if none]
trending_down: [patterns or behaviours degrading — empty list if none]
coasting_alert: [true | false]
---

# ${MONTH} — [3-7 word headline]

> [One line under 30 words. The single observation that defines the month.]

## What the numbers say
[3-5 bullets. Use the quantitative metrics above. Frame against the 59% augmentation benchmark. Call out the top patterns by frequency and what they signal.]

## What's getting sharper
[2-4 bullets. Specific behaviours that improved across sessions. Cite session_ids in [[wikilink]] form when you can. If nothing's improving, say so.]

## Where you're coasting
[2-4 bullets. Honest read of patterns drifting in the wrong direction. Artifact paradox resistance dropping? Augmentation share falling? Same redirect appearing across sessions because the lesson didn't stick? Cite sessions.]

## Beyond the index
[2-4 bullets on behaviours that don't fit the 4D fluency framework but matter — trust calibration, multi-session orchestration, strategic killing. Anthropic's research lists 13 such "unobservable" behaviours; surface the ones visible in your sessions.]

## The pattern of the month
**[bold one-line dominant pattern].** [2-3 sentences on what this says about how you're collaborating with AI right now, and what would shift it.]

## Coasting alerts
[If any: list specifically — e.g. "3 directive-heavy sessions in a row (sessions X, Y, Z)" or "augmentation share dropped from 80% to 50%". If none: "No coasting signals this month."]

RULES:
- Ground every observation in specific session_ids when possible. No vague claims.
- No file paths, env vars, API keys, architecture details, or internal service names.
- Quote user moments from digests where they hit harder than paraphrase.
- Second person throughout.
- If fewer than 3 classified sessions exist, say "Preliminary — only N classified sessions" at the top.
ENDPROMPT

log "generating synthesis ($(wc -c < "$TMPFILE" | tr -d ' ') bytes)..."

SYNTHESIS=$(cat "$TMPFILE" | "$CLAUDE_BIN" -p 2>> "$LOG")
CLAUDE_EXIT=$?
log "claude exit=$CLAUDE_EXIT synthesis_len=${#SYNTHESIS}"

rm -f "$TMPFILE"

if [[ -z "$SYNTHESIS" ]]; then
  log "ERROR: empty synthesis"
  echo "Error: synthesis generation failed"
  exit 1
fi

SYNTH_FILE="$SYNTH_DIR/${MONTH}.md"
echo "$SYNTHESIS" > "$SYNTH_FILE"
log "wrote $SYNTH_FILE"
echo "Synthesis written to $SYNTH_FILE"

# Commit and push
cd "$DECISION_TRAIL_DIR"
git add "$SYNTH_FILE" 2>> "$LOG"
git commit -m "synthesis: ${MONTH}" >> "$LOG" 2>&1
git push >> "$LOG" 2>&1
log "synthesis DONE"
