"""Extract condensed transcript from Claude Code JSONL session file."""
import json
import os
import sys

transcript_path = os.environ.get("DT_TRANSCRIPT", "")
if not transcript_path or not os.path.exists(transcript_path):
    sys.exit(0)

lines = open(transcript_path).readlines()
out = []
for line in lines:
    try:
        obj = json.loads(line)
        msg = obj.get("message", {})
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user" and isinstance(content, str):
            out.append(f"USER: {content[:2000]}")
        elif role == "assistant" and isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    text = c["text"][:2000]
                    out.append(f"ASSISTANT: {text}")
                elif isinstance(c, dict) and c.get("type") == "tool_use":
                    out.append(f"TOOL_CALL: {c.get('name', '?')}")
    except Exception:
        pass

print("\n---\n".join(out))
