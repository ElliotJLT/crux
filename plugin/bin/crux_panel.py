#!/usr/bin/env python3
"""crux-panel: the measurement hooks for the crux research panel.

Stdlib only, Python 3.9+. No network. Everything is written to a local data
directory; only `export` produces anything meant to leave the machine, and it
contains counts only (see PANEL.md for the protocol).

Subcommands
  hook pretooluse         Trail: deny-once at hard cut-lines (Bash)
  hook userpromptsubmit   record justifications and sign-off responses
  hook stop               log sign-offs of autonomous runs
  export [--out FILE]     aggregate counts as JSON
  status                  human summary of this week

Hooks never crash Claude Code: any exception exits 0 silently and the
traceback goes to <data dir>/errors.log.
"""

import calendar
import json
import os
import re
import shlex
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROTOCOL_VERSION = "1.0"

# ---------------------------------------------------------------------------
# PRE-REGISTERED PARAMETERS
# Everything between these rules is pre-registered in PANEL.md. These values
# and marker lists must not change mid-study without a PROTOCOL_VERSION bump.
# ---------------------------------------------------------------------------
FIRE_WINDOW_SECONDS = 15 * 60          # justification validity / open-fire window
BLANK_MAX_WORDS = 4                    # fewer than this many words => blank
RUBBER_STAMPS = frozenset([            # whole-prompt match, lowercased, punctuation stripped
    "ok", "yes", "yep", "y", "go", "do it", "ship it", "just do it",
    "fine", "sure", "approved", "lgtm", "proceed",
])
STOP_MARKERS = (                       # whole-word/phrase match in a justification => withdrawn
    "no", "don't", "stop", "wait", "cancel", "hold on", "instead",
)
SIGNOFF_MIN_TOOL_CALLS = 8             # tool calls in one turn to count as an autonomous run
SIGNOFF_BUCKETS = (("8-19", 8, 19), ("20-49", 20, 49), ("50+", 50, None))
PUSHBACK_MARKERS = (                   # whole-word match => contest (also: ends with "?")
    "why", "wrong", "no", "not", "don't", "instead", "actually",
    "revert", "undo", "rather", "wait", "hmm",
)
ACCEPT_MAX_WORDS = 12                  # fewer than this many words, and an accept marker => accept
ACCEPT_MARKERS = (
    "thanks", "great", "nice", "perfect", "ship", "commit", "merge",
    "push", "lgtm", "good", "next", "done",
)
# Routine rm -rf exemption (rule rm-rf only). Ported verbatim from
# scripts/cutline-dryrun.py. An rm -rf invocation does not fire when every
# target matches ROUTINE_RM_TARGETS, or when RECLONE matches at that rm
# (delete-then-clone scratch). Nothing is logged for an exempt command.
ROUTINE_RM_TARGETS = re.compile(
    r"(/tmp\b|/private/tmp|\btmp/|node_modules|\bdist\b|\bbuild/|\.cache|"
    r"coverage|__pycache__|\bvenv\b|\.claude/worktrees|\btarget/)",
    re.IGNORECASE,
)
RECLONE = re.compile(r"rm\s+-[a-z]*r[a-z]*f?\s+(\S+).*?(?:git|gh)\s+(?:repo\s+)?clone\b",
                     re.IGNORECASE | re.DOTALL)
REDIRECT = re.compile(r"(\d*|&)[<>]+")     # >, 2>&1, &>, <<HEREDOC-STRIPPED are not targets
# ---------------------------------------------------------------------------

BUCKET_NAMES = [b[0] for b in SIGNOFF_BUCKETS]
KINDS = ("reasoned", "blank", "unanswered", "withdrawn")
RESPONSE_KINDS = ("contest", "accept", "neutral")

HEREDOC = re.compile(r"<<-?\s*'?\"?(\w+)'?\"?.*?\n\1\b", re.DOTALL)  # same as scripts/cutline-dryrun.py
SLASH_COMMAND = re.compile(r"^/[A-Za-z][\w:.-]*(\s|$)")
TAIL_BYTES = 1 << 20                   # hooks read only the tail of the event log


# --------------------------------------------------------------------------- time

def now():
    """Current UTC time. CRUX_PANEL_NOW (ISO, Z suffix) overrides it; tests only."""
    override = os.environ.get("CRUX_PANEL_NOW")
    if override:
        return parse_ts(override)
    return datetime.now(timezone.utc).replace(microsecond=0)


def ts_str(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s):
    return datetime.fromtimestamp(
        calendar.timegm(datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timetuple()), timezone.utc)


def iso_week(dt):
    y, w, _ = dt.isocalendar()[:3]
    return "%04d-W%02d" % (y, w)


# --------------------------------------------------------------------------- storage

def data_dir():
    d = Path(os.environ.get("CRUX_PANEL_DIR") or (Path.home() / ".crux" / "panel"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def participant_id(d):
    p = d / "participant.json"
    try:
        pid = json.loads(p.read_text()).get("participant_id")
        if pid:
            return pid
    except (OSError, ValueError, AttributeError):
        pass
    pid = str(uuid.uuid4())
    p.write_text(json.dumps({"participant_id": pid, "created": ts_str(now()),
                             "protocol_version": PROTOCOL_VERSION}) + "\n")
    return pid


def append_event(d, event):
    with open(d / "events.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def parse_lines(raw):
    out = []
    for line in raw.splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out


def read_events(d, tail_bytes=None):
    p = d / "events.jsonl"
    if not p.exists():
        return []
    with open(p, "rb") as fh:
        start = 0
        if tail_bytes:
            start = max(0, p.stat().st_size - tail_bytes)
            fh.seek(start)
        raw = fh.read().decode("utf-8", errors="replace")
    if start:
        raw = raw.split("\n", 1)[-1]  # drop the partial first line
    return parse_lines(raw)


def log_error(d):
    try:
        with open(d / "errors.log", "a", encoding="utf-8") as fh:
            fh.write("%s\n%s\n" % (ts_str(now()), traceback.format_exc()))
    except Exception:
        pass


# --------------------------------------------------------------------------- text classifiers

def normalise(text):
    return text.lower().replace("’", "'").replace("‘", "'")


def has_marker(text, markers):
    """Whole-word / whole-phrase match; apostrophes count as word characters."""
    pattern = r"(?<![a-z0-9'])(?:%s)(?![a-z0-9'])" % "|".join(re.escape(m) for m in markers)
    return re.search(pattern, normalise(text)) is not None


def word_count(text):
    return len(text.split())


def justification_kind(text):
    stripped = re.sub(r"[^\w\s']", "", normalise(text))
    stripped = " ".join(stripped.split())
    if word_count(text) < BLANK_MAX_WORDS or stripped in RUBBER_STAMPS:
        return "blank"
    return "reasoned"


def signoff_response_kind(text):
    if has_marker(text, PUSHBACK_MARKERS) or text.rstrip().endswith("?"):
        return "contest"
    if word_count(text) < ACCEPT_MAX_WORDS and has_marker(text, ACCEPT_MARKERS):
        return "accept"
    return "neutral"


def bucket_for(n):
    for name, lo, hi in SIGNOFF_BUCKETS:
        if n >= lo and (hi is None or n <= hi):
            return name
    return None


# --------------------------------------------------------------------------- cut-lines

def load_rules():
    path = Path(__file__).resolve().parent.parent / "cutlines.json"
    spec = json.loads(path.read_text(encoding="utf-8"))
    return [{"id": r["id"], "why": r.get("why", ""), "rx": re.compile(r["pattern"], re.IGNORECASE)}
            for r in spec["rules"]]


def strip_heredocs(command):
    return HEREDOC.sub("<<HEREDOC-STRIPPED", command)


def rm_all_routine(command, rule_rx):
    """True when every rm -rf invocation in `command` is routine (see ROUTINE_RM_TARGETS).

    An invocation with no parseable target is not routine, so the rule fires.
    """
    found = False
    for m in rule_rx.finditer(command):
        found = True
        rest = command[m.start():]
        if RECLONE.match(rest):
            continue
        seg = re.split(r"&&|\|\||[;|\n]", rest, maxsplit=1)[0]
        try:
            tokens = shlex.split(seg, comments=True)
        except ValueError:
            return False
        targets, skip = [], False
        for t in tokens[1:]:
            if skip:                       # file operand of a bare redirect operator
                skip = False
            elif REDIRECT.match(t):
                skip = REDIRECT.fullmatch(t) is not None
            elif not t.startswith("-"):
                targets.append(t)
        if not targets or not all(ROUTINE_RM_TARGETS.search(t) for t in targets):
            return False
    return found


# --------------------------------------------------------------------------- Measure 1: the Trail

def fire_states(events, session_id):
    """Per fire in this session: (fire event, justify event or None, executed?)."""
    fires, justifies, executed = {}, {}, set()
    for e in events:
        kind = e.get("e")
        if kind == "fire" and e.get("session_id") == session_id:
            fires[e["fire_id"]] = e
        elif kind == "justify" and e.get("session_id") == session_id:
            justifies.setdefault(e["fire_id"], e)
        elif kind == "executed":
            executed.add(e.get("fire_id"))
    return fires, justifies, executed


def rule_state(events, session_id, rule_id, t):
    """('justified', fire_id) | ('pending', fire_id) | ('none', None) for the latest fire of this rule."""
    fires, justifies, _ = fire_states(events, session_id)
    mine = [f for f in fires.values() if f.get("rule_id") == rule_id]
    if not mine:
        return "none", None
    latest = max(mine, key=lambda f: f["ts"])
    j = justifies.get(latest["fire_id"])
    if j is None:
        if (t - parse_ts(latest["ts"])).total_seconds() <= FIRE_WINDOW_SECONDS:
            return "pending", latest["fire_id"]
        return "none", None
    if j.get("stop"):
        return "none", None  # the user said stop: a retry is a new fire
    if (t - parse_ts(j["ts"])).total_seconds() <= FIRE_WINDOW_SECONDS:
        return "justified", latest["fire_id"]
    return "none", None


def hook_pretooluse(d, data):
    if data.get("tool_name") != "Bash":
        return None
    command = (data.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command:
        return None
    matchable = strip_heredocs(command)
    matched = [r for r in load_rules() if r["rx"].search(matchable)
               and not (r["id"] == "rm-rf" and rm_all_routine(matchable, r["rx"]))]
    if not matched:
        return None

    sid = data.get("session_id") or "unknown"
    t = now()
    events = read_events(d, TAIL_BYTES)
    _, _, executed = fire_states(events, sid)
    to_execute, blocked = [], []
    for rule in matched:
        state, fire_id = rule_state(events, sid, rule["id"], t)
        if state == "justified":
            to_execute.append(fire_id)
            continue
        if state == "none":  # a pending fire is denied again without a duplicate event
            append_event(d, {"e": "fire", "ts": ts_str(t), "session_id": sid,
                             "rule_id": rule["id"], "fire_id": uuid.uuid4().hex[:12]})
        blocked.append(rule)

    if not blocked:
        for fire_id in to_execute:
            if fire_id not in executed:
                append_event(d, {"e": "executed", "ts": ts_str(t), "session_id": sid, "fire_id": fire_id})
        return None

    doors = "; ".join("%s: %s" % (r["id"], r["why"]) for r in blocked)
    reason = ("crux trail: this is a one-way door (%s). Before running it, ask the user for a "
              "one-line reason it's right. Re-run only after they answer. "
              "Ask in plain text in your reply, then end your turn." % doors)
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def hook_userpromptsubmit(d, data):
    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return None
    sid = data.get("session_id") or "unknown"
    t = now()
    append_event(d, {"e": "prompt", "ts": ts_str(t), "session_id": sid})  # activity marker, no text

    text = prompt.strip()
    if text.startswith("<task-notification>") or SLASH_COMMAND.match(text):
        return None  # not the user answering

    events = read_events(d, TAIL_BYTES)
    fires, justifies, _ = fire_states(events, sid)
    pending = [f for f in fires.values()
               if f["fire_id"] not in justifies
               and (t - parse_ts(f["ts"])).total_seconds() <= FIRE_WINDOW_SECONDS]
    if pending:
        kind = justification_kind(text)
        stop = has_marker(text, STOP_MARKERS)
        for f in pending:
            append_event(d, {"e": "justify", "ts": ts_str(t), "session_id": sid,
                             "fire_id": f["fire_id"], "words": word_count(text),
                             "kind": kind, "stop": stop, "text": text[:2000]})
        return None  # this prompt answered a one-way door; it is not a sign-off response

    signoffs, answered = {}, set()
    for e in events:
        if e.get("session_id") != sid:
            continue
        if e.get("e") == "signoff":
            signoffs[e["signoff_id"]] = e
        elif e.get("e") == "signoff_response":
            answered.add(e.get("signoff_id"))
    open_signoffs = [s for sid_, s in signoffs.items() if sid_ not in answered]
    if open_signoffs:
        latest = max(open_signoffs, key=lambda s: s["ts"])
        append_event(d, {"e": "signoff_response", "ts": ts_str(t), "session_id": sid,
                         "signoff_id": latest["signoff_id"], "kind": signoff_response_kind(text)})
    return None


# --------------------------------------------------------------------------- Measure 2: sign-off

def _is_human_record(rec):
    if rec.get("type") != "user" or rec.get("isSidechain") or rec.get("isMeta"):
        return False
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        has_text = False
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_result":
                return False
            if b.get("type") == "text" and (b.get("text") or "").strip():
                has_text = True
        return has_text
    return False


def _tool_use_ids(rec):
    if rec.get("type") != "assistant" or rec.get("isSidechain"):
        return []
    content = (rec.get("message") or {}).get("content")
    if not isinstance(content, list):
        return []
    return [b.get("id") or object() for b in content
            if isinstance(b, dict) and b.get("type") == "tool_use"]


def count_turn_tool_calls(transcript_path):
    """Tool calls by the main agent since the last human prompt, or None if unknown.

    Transcript lines are JSON records. Human prompts are `user` records whose
    content is text (not tool_result), not isMeta, not sidechain. Subagent tool
    calls live in sidechain records and are not counted. Reads from the tail so
    large transcripts stay fast.
    """
    if not transcript_path or not os.path.isfile(transcript_path):
        return None
    size = os.path.getsize(transcript_path)
    chunk = TAIL_BYTES
    while True:
        start = max(0, size - chunk)
        with open(transcript_path, "rb") as fh:
            fh.seek(start)
            raw = fh.read().decode("utf-8", errors="replace")
        if start:
            raw = raw.split("\n", 1)[-1]
        recs = parse_lines(raw)
        for i in range(len(recs) - 1, -1, -1):
            if _is_human_record(recs[i]):
                ids = set()
                for r in recs[i + 1:]:
                    ids.update(_tool_use_ids(r))
                return len(ids)
        if start == 0 or chunk >= (128 << 20):
            return None
        chunk *= 4


def hook_stop(d, data):
    if data.get("stop_hook_active"):
        return None
    n = count_turn_tool_calls(data.get("transcript_path"))
    if n is None or n < SIGNOFF_MIN_TOOL_CALLS:
        return None
    sid = data.get("session_id") or "unknown"
    t = now()
    events = read_events(d, TAIL_BYTES)
    fires, justifies, _ = fire_states(events, sid)
    for f in fires.values():  # the turn ended at an open one-way door, not at a delivery
        if f["fire_id"] not in justifies and (t - parse_ts(f["ts"])).total_seconds() <= FIRE_WINDOW_SECONDS:
            return None
    append_event(d, {"e": "signoff", "ts": ts_str(t), "session_id": sid,
                     "signoff_id": uuid.uuid4().hex[:12], "tool_calls": bucket_for(n)})
    return None


# --------------------------------------------------------------------------- export

def _empty_week(label):
    return {
        "iso_week": label,
        "sessions_with_activity": 0,
        "fires": 0,
        "by_kind": {k: 0 for k in KINDS},
        "signoffs": 0,
        "signoff_responses": {"contest": 0, "accept": 0, "neutral": 0, "none": 0},
        "signoffs_by_bucket": {b: {"signoffs": 0, "contest": 0, "accept": 0, "neutral": 0, "none": 0}
                               for b in BUCKET_NAMES},
    }


def classify_fire(fire, justify, executed, t):
    """Outcome of one fire, or None while it is still open (window not yet closed)."""
    if justify is None:
        if (t - parse_ts(fire["ts"])).total_seconds() >= FIRE_WINDOW_SECONDS:
            return "unanswered"
        return None
    if justify.get("stop"):
        return "withdrawn"
    if fire["fire_id"] in executed:
        return justify.get("kind") if justify.get("kind") in ("reasoned", "blank") else "blank"
    if (t - parse_ts(justify["ts"])).total_seconds() >= FIRE_WINDOW_SECONDS:
        return "withdrawn"
    return None


def build_export(d):
    events = read_events(d)
    t = now()
    weeks, sessions = {}, {}

    def week(dt):
        label = iso_week(dt)
        if label not in weeks:
            weeks[label] = _empty_week(label)
            sessions[label] = set()
        return weeks[label]

    fires, justifies, executed = {}, {}, set()
    signoffs, responses = {}, {}
    for e in events:
        try:
            dt = parse_ts(e["ts"])
        except (KeyError, ValueError, TypeError):
            continue
        week(dt)
        if e.get("session_id"):
            sessions[iso_week(dt)].add(e["session_id"])
        kind = e.get("e")
        if kind == "fire":
            fires[e["fire_id"]] = e
        elif kind == "justify":
            justifies.setdefault(e["fire_id"], e)
        elif kind == "executed":
            executed.add(e["fire_id"])
        elif kind == "signoff":
            signoffs[e["signoff_id"]] = e
        elif kind == "signoff_response":
            responses.setdefault(e["signoff_id"], e)

    for fire in fires.values():
        outcome = classify_fire(fire, justifies.get(fire["fire_id"]), executed, t)
        if outcome:
            w = week(parse_ts(fire["ts"]))
            w["fires"] += 1
            w["by_kind"][outcome] += 1

    for sid, s in signoffs.items():
        w = week(parse_ts(s["ts"]))
        resp = (responses.get(sid) or {}).get("kind")
        resp = resp if resp in RESPONSE_KINDS else "none"
        bucket = s.get("tool_calls") if s.get("tool_calls") in BUCKET_NAMES else None
        w["signoffs"] += 1
        w["signoff_responses"][resp] += 1
        if bucket:
            w["signoffs_by_bucket"][bucket]["signoffs"] += 1
            w["signoffs_by_bucket"][bucket][resp] += 1

    out = []
    for label in sorted(weeks):
        weeks[label]["sessions_with_activity"] = len(sessions[label])
        out.append(weeks[label])
    return {
        "protocol_version": PROTOCOL_VERSION,
        "participant_id": participant_id(d),
        "generated_at": ts_str(t),
        "weeks": out,
    }


def _rate(num, den):
    return "n/a (no data)" if not den else "%d/%d = %.0f%%" % (num, den, 100.0 * num / den)


def status_text(d):
    export = build_export(d)
    label = iso_week(now())
    w = next((x for x in export["weeks"] if x["iso_week"] == label), _empty_week(label))
    k, r = w["by_kind"], w["signoff_responses"]
    lines = [
        "crux panel, protocol %s" % PROTOCOL_VERSION,
        "data dir: %s%s" % (d, "   (CRUX_PANEL=off: hooks are paused)"
                            if os.environ.get("CRUX_PANEL", "").lower() == "off" else ""),
        "weeks with data: %d" % len(export["weeks"]),
        "",
        "this week (%s)" % label,
        "  sessions with activity: %d" % w["sessions_with_activity"],
        "  one-way doors: %d  (reasoned %d, blank %d, unanswered %d, withdrawn %d)"
        % (w["fires"], k["reasoned"], k["blank"], k["unanswered"], k["withdrawn"]),
        "  blank-justification rate: %s" % _rate(k["blank"], k["reasoned"] + k["blank"]),
        "  autonomous-run sign-offs: %d  (contest %d, accept %d, neutral %d, no response %d)"
        % (w["signoffs"], r["contest"], r["accept"], r["neutral"], r["none"]),
        "  contest rate: %s" % _rate(r["contest"], w["signoffs"]),
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- entry points

HOOKS = {"pretooluse": hook_pretooluse, "userpromptsubmit": hook_userpromptsubmit, "stop": hook_stop}


def run_hook(name):
    if os.environ.get("CRUX_PANEL", "").strip().lower() == "off":
        return
    d = None
    try:
        d = data_dir()
        fn = HOOKS.get(name)
        data = json.loads(sys.stdin.read() or "{}")
        if fn is None or not isinstance(data, dict):
            return
        participant_id(d)
        result = fn(d, data)
        if result:
            sys.stdout.write(json.dumps(result))
            sys.stdout.flush()
    except Exception:
        if d is not None:
            log_error(d)
        else:
            try:
                log_error(Path.home())
            except Exception:
                pass


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "hook":
        run_hook(argv[2] if len(argv) > 2 else "")
        return 0
    if cmd == "export":
        out = None
        if "--out" in argv:
            i = argv.index("--out")
            out = argv[i + 1] if i + 1 < len(argv) else None
            if not out:
                print("export: --out needs a file path", file=sys.stderr)
                return 2
        text = json.dumps(build_export(data_dir()), indent=2) + "\n"
        if out:
            path = Path(out).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            print(str(path))
        else:
            sys.stdout.write(text)
        return 0
    if cmd == "status":
        print(status_text(data_dir()))
        return 0
    print(__doc__.strip().split("\n\n")[0] + "\n\nusage: crux_panel.py hook <pretooluse|userpromptsubmit|stop> | export [--out FILE] | status",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception:
        # Hooks must never surface a crash; interactive subcommands may.
        if len(sys.argv) > 1 and sys.argv[1] == "hook":
            sys.exit(0)
        raise
