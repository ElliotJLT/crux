#!/bin/bash
# crux backfill — reformat legacy digests into the new RAG-friendly schema.
#
# Reads every digest in decisions/digests/. If it doesn't already start with
# YAML frontmatter (--- on the first line), passes it through Claude to re-render
# in the new format. Writes back in place. Idempotent.
#
# Usage:
#   ./backfill-digests.sh                # reformat all legacy digests
#   ./backfill-digests.sh <file.md>      # reformat one specific digest (for testing)
#   ./backfill-digests.sh --dry-run      # list what would be reformatted, don't run

set -euo pipefail

CRUX_DIR="${CRUX_DIR:-$HOME/crux}"
CLAUDE_BIN="$(command -v claude)"
DIGEST_DIR="$CRUX_DIR/decisions/digests"
PATTERNS_FILE="$CRUX_DIR/taxonomy/patterns.yml"
LOG="$CRUX_DIR/scripts/backfill.log"

log() { echo "$(date '+%H:%M:%S') $1" | tee -a "$LOG"; }

if [[ -z "$CLAUDE_BIN" ]]; then
  echo "crux: claude CLI not found in PATH" >&2
  exit 1
fi

if [[ ! -f "$PATTERNS_FILE" ]]; then
  echo "crux: patterns taxonomy missing at $PATTERNS_FILE" >&2
  exit 1
fi
PATTERNS_VOCAB=$(cat "$PATTERNS_FILE")

DRY_RUN=0
TARGET=""
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
elif [[ -n "${1:-}" ]]; then
  TARGET="$1"
fi

reformat_one() {
  local digest_path="$1"
  local digest_name
  digest_name=$(basename "$digest_path" .md)

  # Skip if already in new format (first line is ---)
  if head -1 "$digest_path" | grep -q '^---$'; then
    log "SKIP (already new format): $digest_name"
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "WOULD REFORMAT: $digest_name"
    return 0
  fi

  local existing_content
  existing_content=$(cat "$digest_path")

  # Date is in the filename, e.g. 2026-05-29-session-1.md
  local digest_date
  digest_date=$(echo "$digest_name" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}')

  local tmpfile
  tmpfile=$(mktemp /tmp/dt-backfill-XXXXXX.txt)
  cat > "$tmpfile" << ENDPROMPT
You are reformatting a legacy crux digest into the new RAG-friendly schema.

CRITICAL: do NOT invent facts or fabricate user quotes. Preserve the substance of
the original digest. If the original doesn't contain a real verbatim quote, do
not invent one — paraphrase and skip the italics.

Some legacy sections map naturally:
- Original "Redirects" → "What you steered"
- Original "Unchallenged" → "What you let slide"
- Original "Wrong calls" → fold into "What you let slide" if substantive, otherwise drop
- Original "Pattern" → "The pattern"
- Original "Classification" → YAML frontmatter (interaction_type, collaboration_mode)
- Fluency dimensions: infer "strong | medium | weak | not-observed" from the session description; if the original doesn't speak to a dimension, use "not-observed"

PATTERN VOCAB (pick 1-4 slugs that match the original digest's observations):
${PATTERNS_VOCAB}

OUTPUT FORMAT — emit exactly this, nothing else:

---
date: ${digest_date}
session_id: ${digest_name}
project: [short kebab-case from the original content e.g. argus, crux, applications, multiverse, boulot, cervo, bungalow-ai, writing, general]
duration: [short | medium | long — infer from original]
shape: [research | shipping | refinement | planning | debugging | writing | mixed]
interaction_type: [extract from original Classification section if present]
collaboration_mode: [extract from original Classification section if present]
fluency:
  delegation: [strong | medium | weak | not-observed]
  description: [strong | medium | weak | not-observed]
  discernment: [strong | medium | weak | not-observed]
  diligence: [strong | medium | weak | not-observed]
patterns: [pick 1-4 slugs from the vocab — must match what the original observed]
concepts: [3-6 topical kebab-case tags inferred from the original]
related: []
---

# [3-6 word title — reuse the original title's core noun phrase] — ${digest_date}

> [One line under 25 words capturing the punchline of the original digest. Self-contained.]

## The moment
[2-4 sentences. The defining decision from the original. If the original has a real user quote, use it (italicised). Otherwise paraphrase.]

## What you steered
[Max 3 bullets in second person ("you"). Pull from the original "Redirects" section. Each bullet should embed a specific decision.]
- **[short verb phrase].** [original observation, rewritten in second person] → [what changed]

## What you let slide
[1-3 bullets from the original "Unchallenged" (and "Wrong calls" if substantive). Honest read.]
- [What was accepted → was the trust warranted? → consequence]

## The pattern
**[bold one-line pattern from the original "Pattern" section, rewritten in second person].** [1-2 sentences expanding on when this shows up.]

## Trajectory note
Standalone — no echo of recent sessions.

HARD RULES:
- Do not invent user quotes. Only italicise text that appears as a quote in the original.
- Do not invent facts. If the original is thin in a section, write less; don't pad.
- YAML must be valid. Use [] for empty lists. Lowercase enum values.
- Patterns MUST be from the vocab above.
- Preserve the original's honesty — if it called the user out for coasting, do the same.

ORIGINAL DIGEST:
${existing_content}
ENDPROMPT

  local raw_content
  raw_content=$(cat "$tmpfile" | "$CLAUDE_BIN" -p 2>> "$LOG")
  local claude_exit=$?
  rm -f "$tmpfile"

  if [[ "$claude_exit" -ne 0 || -z "$raw_content" ]]; then
    log "FAIL: $digest_name (claude exit=$claude_exit)"
    return 1
  fi

  # Strip common preambles: code fences, "Here's the reformatted digest:" intros,
  # and any leading lines before the first standalone --- (the frontmatter delimiter).
  local new_content
  new_content=$(echo "$raw_content" | awk '
    BEGIN { found=0 }
    /^---$/ && !found { found=1 }
    found { print }
  ')

  if [[ -z "$new_content" ]]; then
    log "FAIL: $digest_name (no frontmatter delimiter found in output)"
    mkdir -p "$CRUX_DIR/scripts/.backfill-failures"
    echo "$raw_content" > "$CRUX_DIR/scripts/.backfill-failures/${digest_name}.raw"
    return 1
  fi
  if ! echo "$new_content" | grep -q '## The moment'; then
    log "FAIL: $digest_name (missing 'The moment' section)"
    mkdir -p "$CRUX_DIR/scripts/.backfill-failures"
    echo "$raw_content" > "$CRUX_DIR/scripts/.backfill-failures/${digest_name}.raw"
    return 1
  fi

  echo "$new_content" > "$digest_path"
  log "OK: $digest_name"
}

if [[ -n "$TARGET" ]]; then
  reformat_one "$TARGET"
else
  log "=== backfill run starting ==="
  total=0
  ok=0
  failed=0
  skipped=0
  for f in "$DIGEST_DIR"/*.md; do
    [[ -f "$f" ]] || continue
    total=$((total + 1))
    if head -1 "$f" | grep -q '^---$'; then
      skipped=$((skipped + 1))
      continue
    fi
    if reformat_one "$f"; then
      ok=$((ok + 1))
    else
      failed=$((failed + 1))
    fi
  done
  log "=== done: total=$total ok=$ok failed=$failed already-new=$skipped ==="
fi
