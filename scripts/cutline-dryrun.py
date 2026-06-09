#!/usr/bin/env python3
"""Cut-line dry run: log-only classifier over Claude Code transcripts.

Day-1 of the Trail wedge. Answers ONE question before any hook ever fires:
is "irreversible" mechanically separable from "routine" on this user's real
sessions, at a precision that wouldn't get the hook disabled within a day?

Reads every main-session transcript under ~/.claude/projects, matches Bash
tool commands against taxonomy/cutlines.yml, and writes:

  <outdir>/matches.jsonl   one record per match, full context
  <outdir>/report.md       summary stats + per-rule samples for FP review

Strictly read-only over the transcripts. No hooks, no prompts, no capture.

Usage:
  python3 scripts/cutline-dryrun.py [--projects-dir ~/.claude/projects]
                                    [--outdir ./cutline-dryrun]
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import yaml

# Annotation heuristics — these never exclude a match, they label it so the
# human reviewing the report can judge the false-positive boundary.
ROUTINE_RM_TARGETS = re.compile(
    r"(/tmp\b|/private/tmp|\btmp/|node_modules|\bdist\b|\bbuild/|\.cache|"
    r"coverage|__pycache__|\bvenv\b|\.claude/worktrees|\btarget/)",
    re.IGNORECASE,
)
RECLONE = re.compile(r"rm\s+-[a-z]*r[a-z]*f?\s+(\S+).*?(?:git|gh)\s+(?:repo\s+)?clone\b",
                     re.IGNORECASE | re.DOTALL)
TEST_ENV = re.compile(r"RAILS_ENV=test\b")
PROD_HINTS = re.compile(r"(heroku|production|--prod\b|\bprod\b)", re.IGNORECASE)
MAIN_BRANCH = {"main", "master"}
HEREDOC = re.compile(r"<<-?\s*'?\"?(\w+)'?\"?.*?\n\1\b", re.DOTALL)


def strip_heredocs(command):
    """Remove heredoc bodies so text *mentioning* a destructive command
    (PR comments, commit messages, echo'd instructions) can't match."""
    return HEREDOC.sub("<<HEREDOC-STRIPPED", command)


def load_rules(path: Path):
    spec = yaml.safe_load(path.read_text())
    rules = []
    for r in spec["rules"]:
        rules.append({
            "id": r["id"],
            "tier": r["tier"],
            "why": r.get("why", ""),
            "rx": re.compile(r["pattern"], re.IGNORECASE),
        })
    return rules


def human_text(record):
    """Return stripped human-authored text from a user record, else None."""
    msg = record.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content
                 if isinstance(b, dict) and b.get("type") == "text"]
        text = "\n".join(parts).strip()
    else:
        return None
    if not text or text.startswith("<"):  # tool results / system-reminders / commands
        return None
    return text


def annotate(rule_id, command, branch):
    notes = []
    if rule_id == "rm-rf" and ROUTINE_RM_TARGETS.search(command):
        notes.append("likely-routine:tmp-or-build-path")
    if rule_id == "rm-rf" and RECLONE.search(command):
        notes.append("likely-routine:reclone-scratch")
    if rule_id in ("db-reset", "sql-destructive") and TEST_ENV.search(command):
        notes.append("likely-routine:test-env")
    if rule_id in ("git-force-push", "git-force-push-lease"):
        target_main = re.search(r"\b(origin|upstream)\s+\+?(main|master)\b", command)
        if target_main or (branch or "").lower() in MAIN_BRANCH:
            notes.append("targets-main")
        else:
            notes.append("own-branch")
    if rule_id == "sql-destructive" and not PROD_HINTS.search(command):
        notes.append("env-unclear")
    if PROD_HINTS.search(command):
        notes.append("prod-flagged")
    return notes


def scan_file(path: Path, rules, matches, stats):
    records = []
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    project = path.parent.name
    for idx, rec in enumerate(records):
        msg = rec.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for blk in content:
            if not (isinstance(blk, dict) and blk.get("type") == "tool_use"
                    and blk.get("name") == "Bash"):
                continue
            command = (blk.get("input") or {}).get("command") or ""
            stats["bash_commands"] += 1
            day = (rec.get("timestamp") or "")[:10]
            if day:
                stats["active_days"].add(day)
            sidechain = bool(rec.get("isSidechain"))
            stats["bash_sidechain" if sidechain else "bash_mainloop"] += 1

            matchable = strip_heredocs(command)
            for rule in rules:
                if not rule["rx"].search(matchable):
                    continue
                # nearest preceding human message = the justification proxy
                preceding = None
                for back in range(idx - 1, max(idx - 80, -1), -1):
                    prev = records[back]
                    if prev.get("type") == "user" and not prev.get("isSidechain"):
                        text = human_text(prev)
                        if text:
                            preceding = text[:200]
                            break
                matches.append({
                    "rule": rule["id"],
                    "tier": rule["tier"],
                    "command": command[:500],
                    "notes": annotate(rule["id"], command, rec.get("gitBranch")),
                    "sidechain": sidechain,
                    "sandbox_bypassed": bool((blk.get("input") or {}).get("dangerouslyDisableSandbox")),
                    "branch": rec.get("gitBranch"),
                    "project": project,
                    "session": rec.get("sessionId"),
                    "timestamp": rec.get("timestamp"),
                    "preceding_user_msg": preceding,
                })


def write_report(matches, stats, rules, outdir: Path):
    by_rule = defaultdict(list)
    for m in matches:
        by_rule[m["rule"]].append(m)

    hard_real = [m for m in matches if m["tier"] == "hard"
                 and not any(n.startswith("likely-routine") for n in m["notes"])]
    days = len(stats["active_days"]) or 1
    weeks = Counter(m["timestamp"][:10] for m in hard_real if m["timestamp"])

    # Decision events: retrying `gh pr merge 503` four times in one session is
    # one decision, four attempts. Group hard matches by (session, rule) within
    # a 30-minute window.
    events = []
    open_event = {}  # key -> (event dict, last timestamp)
    for m in hard_real:
        key = (m["session"], m["rule"])
        ts = m["timestamp"] or ""
        prev = open_event.get(key)
        within = False
        if prev and ts and prev[1]:
            delta = (datetime.fromisoformat(ts.replace("Z", "+00:00"))
                     - datetime.fromisoformat(prev[1].replace("Z", "+00:00"))).total_seconds()
            within = abs(delta) < 1800
        if within:
            prev[0]["attempts"] += 1
            open_event[key] = (prev[0], ts)
        else:
            ev = {**m, "attempts": 1}
            events.append(ev)
            open_event[key] = (ev, ts)

    lines = []
    w = lines.append
    w("# Cut-line dry run — log-only, no hooks fired")
    w("")
    w(f"> Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
      f"{stats['files']} transcripts · {stats['bash_commands']:,} Bash commands · "
      f"{len(stats['active_days'])} active days")
    w("")
    w("## Headline numbers")
    w("")
    w(f"- **Total matches:** {len(matches)} "
      f"({len([m for m in matches if m['tier'] == 'hard'])} hard tier, "
      f"{len([m for m in matches if m['tier'] == 'review'])} review tier)")
    w(f"- **Hard tier after routine-annotation:** {len(hard_real)} matches "
      f"→ **{len(events)} decision events** (retries grouped) — "
      f"**{len(events) / days:.2f} per active day** "
      f"(the would-have-fired rate for a capture hook)")
    pct = 100 * len(hard_real) / max(stats["bash_commands"], 1)
    w(f"- **Selectivity:** {pct:.2f}% of all Bash commands cross a hard cut-line "
      f"— everything else would stay frictionless")
    side = len([m for m in hard_real if m["sidechain"]])
    w(f"- **Delegated one-way doors:** {side}/{len(hard_real)} hard matches were "
      f"executed by a subagent, not the main loop — irreversible actions with "
      f"no human at the wheel (the cedes-responsibility measurement, for free)")
    sand = len([m for m in matches if m["sandbox_bypassed"]])
    if sand:
        w(f"- **Sandbox bypassed:** {sand} matches ran with the sandbox explicitly disabled")
    w("")
    w("## Per-rule breakdown")
    w("")
    w("| rule | tier | matches | sidechain | routine-annotated | prod-flagged |")
    w("|---|---|---|---|---|---|")
    for rule in rules:
        ms = by_rule.get(rule["id"], [])
        if not ms:
            continue
        routine = len([m for m in ms if any(n.startswith("likely-routine") for n in m["notes"])])
        prod = len([m for m in ms if "prod-flagged" in m["notes"]])
        sc = len([m for m in ms if m["sidechain"]])
        w(f"| {rule['id']} | {rule['tier']} | {len(ms)} | {sc} | {routine} | {prod} |")
    unfired = [r["id"] for r in rules if r["id"] not in by_rule]
    if unfired:
        w("")
        w(f"Rules with zero matches: {', '.join(unfired)}")
    w("")
    w("## Samples for false-positive review")
    w("")
    w("Eyeball each block: would you have wanted a half-second pause + one "
      "question at this moment? Mark the ones where the answer is plainly no — "
      "that set defines the precision number.")
    for rule in rules:
        ms = by_rule.get(rule["id"], [])
        if not ms:
            continue
        w("")
        w(f"### {rule['id']} ({rule['tier']}) — {len(ms)} matches")
        w(f"*{rule['why']}*")
        w("")
        for m in ms[:8]:
            flags = " ".join(f"`{n}`" for n in m["notes"]) or ""
            who = "subagent" if m["sidechain"] else "main"
            w(f"- `{m['command'][:160]}`")
            w(f"  — {m['project']} · {m['branch'] or '?'} · {who} "
              f"· {(m['timestamp'] or '')[:10]} {flags}")
            if m["preceding_user_msg"]:
                w(f"  — you, just before: *\"{m['preceding_user_msg'][:140]}\"*")
        if len(ms) > 8:
            w(f"- … {len(ms) - 8} more in matches.jsonl")
    w("")
    w("## Activity of hard matches over time")
    w("")
    for day in sorted(weeks):
        w(f"- {day}: {'█' * min(weeks[day], 40)} {weeks[day]}")
    w("")

    (outdir / "report.md").write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-dir", default=str(Path.home() / ".claude/projects"))
    ap.add_argument("--outdir", default="cutline-dryrun")
    ap.add_argument("--cutlines", default=str(Path(__file__).parent.parent / "taxonomy/cutlines.yml"))
    args = ap.parse_args()

    rules = load_rules(Path(args.cutlines))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in Path(args.projects_dir).rglob("*.jsonl")
                   if "subagents" not in p.parts)
    matches = []
    stats = {"files": 0, "bash_commands": 0, "bash_mainloop": 0,
             "bash_sidechain": 0, "active_days": set()}
    for path in files:
        stats["files"] += 1
        scan_file(path, rules, matches, stats)

    matches.sort(key=lambda m: m["timestamp"] or "")
    with open(outdir / "matches.jsonl", "w") as fh:
        for m in matches:
            fh.write(json.dumps(m) + "\n")
    write_report(matches, stats, rules, outdir)

    hard = len([m for m in matches if m["tier"] == "hard"])
    print(f"{stats['files']} transcripts · {stats['bash_commands']:,} bash commands "
          f"· {len(matches)} matches ({hard} hard) → {outdir}/report.md", file=sys.stderr)


if __name__ == "__main__":
    main()
