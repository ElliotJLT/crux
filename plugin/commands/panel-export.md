---
description: Export your crux panel counts to a file you can review and send
disable-model-invocation: true
---

Export the user's crux panel counts. Run this one command with the Bash tool and nothing else:

```
python3 "${CLAUDE_PLUGIN_ROOT}/bin/crux_panel.py" export --out "${CRUX_PANEL_DIR:-$HOME/.crux/panel}/export.json"
```

The command prints the path of the file it wrote. Then:

1. Show the user that path.
2. Read the file and show its contents, so they can see exactly what would be sent. It holds counts per ISO week and a random participant id. It never holds prompt text, command text, file paths or project names.
3. Tell the user they can send the file as they choose; nothing has been sent anywhere.

Do not summarise or interpret the numbers.
