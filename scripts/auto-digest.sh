#!/bin/bash
# crux auto-digest — SessionEnd hook entry point
# Reads session metadata from stdin, saves it, then backgrounds the worker.

CRUX_DIR="${CRUX_DIR:-$HOME/crux}"
WORKER="$CRUX_DIR/scripts/digest-worker.sh"

# Dependency check
for dep in jq python3; do
  if ! command -v "$dep" &>/dev/null; then
    echo "crux: missing dependency: $dep" >&2
    exit 1
  fi
done

if ! command -v claude &>/dev/null; then
  echo "crux: claude CLI not found in PATH" >&2
  exit 1
fi

# Read hook event data from stdin immediately
INPUT=$(cat)

# Save to temp file for the worker
WORK_FILE=$(mktemp /tmp/dt-work-XXXXXX.json)
echo "$INPUT" > "$WORK_FILE"

# Background the worker (nohup so it survives session exit)
nohup "$WORKER" "$WORK_FILE" < /dev/null >> "$CRUX_DIR/scripts/auto-digest.log" 2>&1 &

exit 0
