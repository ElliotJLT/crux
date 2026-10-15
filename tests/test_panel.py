"""Tests for the crux panel plugin.

Hooks are exercised the way Claude Code runs them: JSON on stdin to
plugin/bin/crux_panel.py in a subprocess, with CRUX_PANEL_DIR pointing at a
temp dir. CRUX_PANEL_NOW pins the clock so the 15-minute window and ISO weeks
are testable.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugin" / "bin" / "crux_panel.py"
T0 = "2026-10-14T10:00:00Z"  # a Wednesday, ISO week 2026-W42

DOOR = "git push --force origin main"
SECRET_BRANCH = "SECRETBRANCH_zq91"
SECRET_CMD = "git push --force origin " + SECRET_BRANCH
SECRET_PROMPT = "because PLUMBUS_7731 customer asked for it today"
SECRET_CWD = "/Users/zq91/secret-project-xyzzy"


def load_module():
    spec = importlib.util.spec_from_file_location("crux_panel_mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def at(minutes, base=T0):
    from datetime import datetime, timedelta, timezone
    dt = datetime.strptime(base, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (dt + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


class Panel:
    def __init__(self, tmp_path):
        self.dir = tmp_path / "panel"
        self.tmp = tmp_path

    def run(self, args, stdin="", now=T0, env=None):
        e = dict(os.environ)
        e.pop("CRUX_PANEL", None)
        e["CRUX_PANEL_DIR"] = str(self.dir)
        e["CRUX_PANEL_NOW"] = now
        e.update(env or {})
        return subprocess.run([sys.executable, str(SCRIPT)] + args, input=stdin,
                              capture_output=True, text=True, env=e, timeout=30)

    def hook(self, name, payload, now=T0, env=None, raw=None):
        p = self.run(["hook", name], raw if raw is not None else json.dumps(payload), now, env)
        assert p.returncode == 0, p.stderr
        return p.stdout

    def bash(self, command, sid="s1", now=T0):
        out = self.hook("pretooluse", {"session_id": sid, "hook_event_name": "PreToolUse",
                                       "tool_name": "Bash", "tool_input": {"command": command},
                                       "cwd": SECRET_CWD}, now)
        return json.loads(out) if out else None

    def prompt(self, text, sid="s1", now=T0):
        return self.hook("userpromptsubmit", {"session_id": sid, "hook_event_name": "UserPromptSubmit",
                                              "prompt": text, "cwd": SECRET_CWD}, now)

    def stop(self, transcript, sid="s1", now=T0, **extra):
        payload = {"session_id": sid, "hook_event_name": "Stop", "transcript_path": str(transcript),
                   "stop_hook_active": False, "last_assistant_message": "done"}
        payload.update(extra)
        return self.hook("stop", payload, now)

    def events(self, kind=None):
        p = self.dir / "events.jsonl"
        if not p.exists():
            return []
        evs = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
        return [e for e in evs if kind is None or e["e"] == kind]

    def export(self, now=T0):
        p = self.run(["export"], now=now)
        assert p.returncode == 0, p.stderr
        return json.loads(p.stdout)

    def week(self, label="2026-W42", now=T0):
        for w in self.export(now)["weeks"]:
            if w["iso_week"] == label:
                return w
        return None


@pytest.fixture
def panel(tmp_path):
    return Panel(tmp_path)


def transcript(tmp_path, turns, name="t.jsonl"):
    """Write a Claude Code style transcript. turns: list of ('human', text) | ('tool', n) | other raw dicts."""
    lines = []
    for kind, val in turns:
        if kind == "human":
            lines.append({"type": "user", "message": {"role": "user", "content": val}})
        elif kind == "human_blocks":
            lines.append({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": val}]}})
        elif kind == "tool":
            for _ in range(val):
                tid = "toolu_" + uuid.uuid4().hex[:10]
                lines.append({"type": "assistant", "message": {"role": "assistant", "content": [
                    {"type": "tool_use", "id": tid, "name": "Bash", "input": {"command": "ls"}}]}})
                lines.append({"type": "user", "message": {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": tid, "content": "ok"}]}})
        elif kind == "sidechain_tool":
            for _ in range(val):
                lines.append({"type": "assistant", "isSidechain": True, "message": {"role": "assistant", "content": [
                    {"type": "tool_use", "id": "toolu_" + uuid.uuid4().hex[:10], "name": "Read", "input": {}}]}})
        elif kind == "meta":
            lines.append({"type": "user", "isMeta": True, "message": {"role": "user", "content": [
                {"type": "text", "text": "expanded skill body"}]}})
        elif kind == "assistant_text":
            lines.append({"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "text", "text": val}]}})
        elif kind == "raw":
            lines.append(val)
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(x) for x in lines) + "\n{not json\n")
    return p


# ----------------------------------------------------------------- build / config sync

def test_cutlines_json_in_sync_with_yaml():
    yaml = pytest.importorskip("yaml", reason="PyYAML is needed to check the cut-lines sync")
    spec = yaml.safe_load((ROOT / "taxonomy" / "cutlines.yml").read_text())
    expected = [{"id": r["id"], "pattern": r["pattern"], "why": r.get("why", "")}
                for r in spec["rules"] if r["tier"] == "hard"]
    got = json.loads((ROOT / "plugin" / "cutlines.json").read_text())
    assert got == {"rules": expected}
    assert len(expected) >= 10 and all(r["tier"] != "review" for r in spec["rules"] if r["id"] in
                                       {x["id"] for x in expected})


def test_build_script_check_passes():
    pytest.importorskip("yaml")
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "build-cutlines-json.py"), "--check"],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr


def test_manifests_are_wired():
    plugin = json.loads((ROOT / "plugin" / ".claude-plugin" / "plugin.json").read_text())
    assert plugin["name"] == "crux-panel"
    mkt = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert mkt["name"] == "crux"
    entry = mkt["plugins"][0]
    assert entry["name"] == plugin["name"]
    assert (ROOT / ".claude-plugin" / ".." / entry["source"] / ".claude-plugin" / "plugin.json").resolve().exists()
    hooks = json.loads((ROOT / "plugin" / "hooks" / "hooks.json").read_text())["hooks"]
    assert set(hooks) == {"PreToolUse", "UserPromptSubmit", "Stop"}
    assert hooks["PreToolUse"][0]["matcher"] == "Bash"
    for groups in hooks.values():
        cmd = groups[0]["hooks"][0]["command"]
        assert '"${CLAUDE_PLUGIN_ROOT}/bin/crux_panel.py"' in cmd
    assert (ROOT / "plugin" / "commands" / "panel-export.md").exists()


def test_panel_md_matches_coded_constants():
    mod = load_module()
    assert mod.PROTOCOL_VERSION == "1.0"
    text = (ROOT / "PANEL.md").read_text()
    assert "Protocol version: 1.0" in text
    for rule in json.loads((ROOT / "plugin" / "cutlines.json").read_text())["rules"]:
        assert rule["id"] in text, rule["id"]
    for hypothesis in (
        "H1 (descriptive): across participants, the blank-justification rate at one-way doors is above 25%.",
        "H2: within a participant, the blank-justification rate rises over the study period (12 weeks) rather than falling.",
        "H3: the sign-off contest rate is lower for long autonomous runs (50+ tool calls) than short ones (8-19).",
        "Kill criterion: if fewer than 15 participants export at least 4 weeks of data, the study reports as underpowered and makes no population claim.",
    ):
        assert hypothesis in text

    def listed(label):
        m = re.search(r"^- %s: (.+)$" % re.escape(label), text, re.M)
        assert m, label
        return [x.strip() for x in m.group(1).split(",")]

    assert set(listed("Rubber-stamp replies")) == set(mod.RUBBER_STAMPS)
    assert len(listed("Rubber-stamp replies")) == len(mod.RUBBER_STAMPS)
    assert listed("Stop markers") == list(mod.STOP_MARKERS)
    assert listed("Pushback markers") == list(mod.PUSHBACK_MARKERS)
    assert listed("Accept markers") == list(mod.ACCEPT_MARKERS)


# ----------------------------------------------------------------- Trail: PreToolUse

def test_non_door_command_is_silent(panel):
    assert panel.bash("ls -la && git status") is None
    assert panel.events("fire") == []


def test_non_bash_tool_is_ignored(panel):
    out = panel.hook("pretooluse", {"session_id": "s1", "tool_name": "Write",
                                    "tool_input": {"file_path": "x", "content": DOOR}})
    assert out == ""


def test_door_is_denied_with_documented_shape(panel):
    res = panel.bash(DOOR)
    hso = res["hookSpecificOutput"]
    assert hso["hookEventName"] == "PreToolUse"
    assert hso["permissionDecision"] == "deny"
    reason = hso["permissionDecisionReason"]
    assert reason.startswith("crux trail: this is a one-way door (git-force-push: ")
    assert "ask the user for a one-line reason it's right" in reason
    assert "Re-run only after they answer" in reason
    fires = panel.events("fire")
    assert len(fires) == 1 and fires[0]["rule_id"] == "git-force-push"
    assert set(fires[0]) == {"e", "ts", "session_id", "rule_id", "fire_id"}


def test_command_text_is_never_logged(panel):
    panel.bash(SECRET_CMD)
    assert SECRET_BRANCH not in (panel.dir / "events.jsonl").read_text()


def test_heredoc_body_mentioning_door_does_not_fire(panel):
    cmd = "git commit -F - <<'EOF'\nnote: never git push --force again\nEOF"
    assert panel.bash(cmd) is None
    assert panel.events("fire") == []


def test_repeat_while_pending_denies_without_duplicate_fire(panel):
    panel.bash(DOOR)
    res = panel.bash(DOOR, now=at(1))
    assert res["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert len(panel.events("fire")) == 1


def test_justified_rerun_is_allowed_and_logged_once(panel):
    panel.bash(DOOR)
    panel.prompt("the branch is merged and nobody else uses it", now=at(1))
    assert panel.bash(DOOR, now=at(2)) is None
    assert panel.bash(DOOR, now=at(3)) is None  # still within the window
    ex = panel.events("executed")
    assert len(ex) == 1 and ex[0]["fire_id"] == panel.events("fire")[0]["fire_id"]
    assert len(panel.events("fire")) == 1


def test_justification_expires_after_15_minutes(panel):
    panel.bash(DOOR)
    panel.prompt("the branch is merged and nobody else uses it", now=at(1))
    res = panel.bash(DOOR, now=at(17))
    assert res["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert len(panel.events("fire")) == 2


def test_justification_is_per_session_and_per_rule(panel):
    panel.bash(DOOR, sid="A")
    panel.prompt("the branch is merged and nobody else uses it", sid="A", now=at(1))
    assert panel.bash(DOOR, sid="B", now=at(2))["hookSpecificOutput"]["permissionDecision"] == "deny"
    other = panel.bash("git branch -D old-thing", sid="A", now=at(2))
    assert "git-branch-force-delete" in other["hookSpecificOutput"]["permissionDecisionReason"]


def test_two_rules_in_one_command_both_named(panel):
    res = panel.bash("git branch -D old && git push --force origin main")
    reason = res["hookSpecificOutput"]["permissionDecisionReason"]
    assert "git-branch-force-delete" in reason and "git-force-push" in reason
    assert len(panel.events("fire")) == 2
    panel.prompt("both are dead branches from the old release", now=at(1))
    assert len(panel.events("justify")) == 2
    assert panel.bash("git branch -D old && git push --force origin main", now=at(2)) is None
    assert len(panel.events("executed")) == 2


@pytest.mark.parametrize("text,kind", [
    ("ok", "blank"), ("Yes.", "blank"), ("LGTM!", "blank"), ("Do it!", "blank"),
    ("ship it", "blank"), ("just do it", "blank"), ("go ahead now", "blank"),  # < 4 words
    ("y", "blank"), ("proceed", "blank"), ("approved", "blank"),
    ("the old branch is dead", "reasoned"),
    ("yes, because the release shipped", "reasoned"),
    ("it is the stale remote", "reasoned"),
])
def test_justification_kind(panel, text, kind):
    panel.bash(DOOR)
    panel.prompt(text, now=at(1))
    j = panel.events("justify")[0]
    assert j["kind"] == kind
    assert j["words"] == len(text.split())
    assert j["text"] == text  # stored locally only


def test_slash_commands_and_task_notifications_are_not_justifications(panel):
    panel.bash(DOOR)
    panel.prompt("/crux-panel:panel-export", now=at(1))
    panel.prompt("<task-notification>\n<task-id>abc</task-id></task-notification>", now=at(1))
    assert panel.events("justify") == []


def test_stop_marker_justification_is_withdrawn_and_not_allowed(panel):
    panel.bash(DOOR)
    panel.prompt("no, don't do it, wait for the review", now=at(1))
    j = panel.events("justify")[0]
    assert j["stop"] is True
    res = panel.bash(DOOR, now=at(2))
    assert res["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert panel.events("executed") == []
    w = panel.week(now=at(2))
    assert w["by_kind"]["withdrawn"] == 1


@pytest.mark.parametrize("text", ["stop", "hold on a second please", "cancel that", "use rebase instead of force",
                                  "wait for the review first", "no"])
def test_each_stop_marker_withdraws(panel, text):
    panel.bash(DOOR)
    panel.prompt(text, now=at(1))
    assert panel.events("justify")[0]["stop"] is True


def test_ordinary_words_do_not_trip_stop_markers(panel):
    panel.bash(DOOR)
    panel.prompt("nothing depends on that branch, it is a note only", now=at(1))  # "nothing" != "no"
    assert panel.events("justify")[0]["stop"] is False


# ----------------------------------------------------------------- Trail: routine rm -rf exemption

@pytest.mark.parametrize("cmd", [
    "rm -rf node_modules",
    "rm -rf /tmp/x",
    "rm -fr dist build/",
    "rm -rf ./node_modules/.cache",
    "rm -rf ~/.cache/pip",
    "rm -r -f venv __pycache__",
    "rm -rf /private/tmp/scratch && echo done",
    "rm -rf node_modules; npm install",
    "rm -rf node_modules && rm -rf /tmp/y",
    "rm -rf src && git clone https://example.com/r.git src",   # RECLONE: delete-then-clone scratch
    "rm -rf node_modules # cleanup src",                         # shell comment is not a target
    "rm -rf node_modules > /dev/null 2>&1",
    "rm -rf node_modules >/tmp/out 2>&1",
    "rm -rf node_modules <<EOF\nrm -rf src\nEOF",               # heredoc body is stripped first
])
def test_routine_rm_rf_does_not_fire_and_logs_nothing(panel, cmd):
    assert panel.bash(cmd) is None
    assert not (panel.dir / "events.jsonl").exists() or panel.events() == []


@pytest.mark.parametrize("cmd", [
    "rm -rf src",
    "rm -rf node_modules src",
    "rm -rf src node_modules",
    "rm -rf /tmp/x /etc",
    "rm -rf node_modules && rm -rf src",
    'rm -rf "$HOME/project"',
    "rm -rf",
    "rm -rf 'unterminated",
    "cd /tmp && rm -rf data",
    "rm -rf src > /dev/null 2>&1",
])
def test_non_routine_rm_rf_fires(panel, cmd):
    res = panel.bash(cmd)
    assert res["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "rm-rf" in res["hookSpecificOutput"]["permissionDecisionReason"]
    assert [f["rule_id"] for f in panel.events("fire")] == ["rm-rf"]


def test_rm_exemption_does_not_cover_other_rules(panel):
    res = panel.bash("rm -rf node_modules; git push --force origin main")
    reason = res["hookSpecificOutput"]["permissionDecisionReason"]
    assert "git-force-push" in reason and "rm-rf" not in reason
    assert [f["rule_id"] for f in panel.events("fire")] == ["git-force-push"]


def test_routine_regexes_match_dryrun_and_panel_md():
    mod = load_module()
    text = (ROOT / "PANEL.md").read_text()
    assert mod.ROUTINE_RM_TARGETS.pattern in text
    assert mod.RECLONE.pattern in text
    assert mod.ROUTINE_RM_TARGETS.flags & re.IGNORECASE
    pytest.importorskip("yaml")
    spec = importlib.util.spec_from_file_location("dryrun", ROOT / "scripts" / "cutline-dryrun.py")
    dry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dry)
    assert mod.ROUTINE_RM_TARGETS.pattern == dry.ROUTINE_RM_TARGETS.pattern
    assert mod.ROUTINE_RM_TARGETS.flags == dry.ROUTINE_RM_TARGETS.flags
    assert mod.RECLONE.pattern == dry.RECLONE.pattern
    assert mod.RECLONE.flags == dry.RECLONE.flags


# ----------------------------------------------------------------- Trail: export outcomes

def test_outcomes_unanswered_withdrawn_blank_reasoned(panel):
    # reasoned + executed
    panel.bash(DOOR, sid="a")
    panel.prompt("the branch is merged and nobody else uses it", sid="a", now=at(1))
    panel.bash(DOOR, sid="a", now=at(2))
    # blank + executed
    panel.bash(DOOR, sid="b")
    panel.prompt("ok", sid="b", now=at(1))
    panel.bash(DOOR, sid="b", now=at(2))
    # justified, never executed -> withdrawn once the window closes
    panel.bash(DOOR, sid="c")
    panel.prompt("the branch is merged and nobody else uses it", sid="c", now=at(1))
    # no answer at all -> unanswered
    panel.bash(DOOR, sid="d")

    # inside the window the last two are still open and not counted yet
    w = panel.week(now=at(10))
    assert w["fires"] == 2
    assert w["by_kind"] == {"reasoned": 1, "blank": 1, "unanswered": 0, "withdrawn": 0}

    w = panel.week(now=at(30))
    assert w["fires"] == 4
    assert w["by_kind"] == {"reasoned": 1, "blank": 1, "unanswered": 1, "withdrawn": 1}
    assert w["sessions_with_activity"] == 4


def test_weeks_are_split_by_iso_week(panel):
    panel.bash(DOOR, sid="a")
    panel.prompt("ok", sid="a", now=at(1))
    panel.bash(DOOR, sid="a", now=at(2))
    later = "2026-10-21T10:00:00Z"
    panel.bash(DOOR, sid="b", now=later)
    panel.prompt("the branch is merged and nobody else uses it", sid="b", now=at(1, later))
    panel.bash(DOOR, sid="b", now=at(2, later))
    weeks = {w["iso_week"]: w for w in panel.export(now=at(60, later))["weeks"]}
    assert weeks["2026-W42"]["by_kind"]["blank"] == 1
    assert weeks["2026-W43"]["by_kind"]["reasoned"] == 1


# ----------------------------------------------------------------- sign-off

@pytest.mark.parametrize("n,bucket", [(8, "8-19"), (19, "8-19"), (20, "20-49"), (49, "20-49"),
                                      (50, "50+"), (73, "50+")])
def test_stop_logs_signoff_buckets(panel, tmp_path, n, bucket):
    t = transcript(tmp_path, [("human", "build the thing"), ("tool", n), ("assistant_text", "done")])
    assert panel.stop(t) == ""
    so = panel.events("signoff")
    assert len(so) == 1 and so[0]["tool_calls"] == bucket
    assert set(so[0]) == {"e", "ts", "session_id", "signoff_id", "tool_calls"}


def test_stop_below_threshold_logs_nothing(panel, tmp_path):
    t = transcript(tmp_path, [("human", "x"), ("tool", 7)])
    panel.stop(t)
    assert panel.events("signoff") == []


def test_stop_counts_only_the_last_turn_main_agent_real_tools(panel, tmp_path):
    t = transcript(tmp_path, [
        ("human", "first task"), ("tool", 30),
        ("human_blocks", "second task"), ("meta", None), ("tool", 5), ("sidechain_tool", 20), ("assistant_text", "ok"),
    ])
    panel.stop(t)
    assert panel.events("signoff") == []  # 5 main-agent calls in the last turn


def test_stop_duplicate_tool_use_ids_count_once(panel, tmp_path):
    dup = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "same", "name": "Bash", "input": {}}]}}
    t = transcript(tmp_path, [("human", "x")] + [("raw", dup)] * 20)
    panel.stop(t)
    assert panel.events("signoff") == []


def test_stop_defensive_inputs(panel, tmp_path):
    assert panel.stop(tmp_path / "missing.jsonl") == ""
    assert panel.hook("stop", {"session_id": "s1", "hook_event_name": "Stop"}) == ""
    t = transcript(tmp_path, [("human", "x"), ("tool", 12)])
    panel.stop(t, stop_hook_active=True)
    assert panel.events("signoff") == []


def test_stop_at_open_one_way_door_is_not_a_signoff(panel, tmp_path):
    panel.bash(DOOR)
    t = transcript(tmp_path, [("human", "x"), ("tool", 12)])
    panel.stop(t, now=at(1))
    assert panel.events("signoff") == []


def _signoff_then_reply(panel, tmp_path, reply, n=10):
    t = transcript(tmp_path, [("human", "x"), ("tool", n)])
    panel.stop(t)
    panel.prompt(reply, now=at(5))
    r = panel.events("signoff_response")
    return r[0]["kind"] if r else None


@pytest.mark.parametrize("reply,kind", [
    ("why did you change the schema?", "contest"),
    ("that's wrong", "contest"),
    ("no", "contest"),
    ("not what I asked", "contest"),
    ("don't touch the config", "contest"),
    ("undo the last commit", "contest"),
    ("Actually, keep the old behaviour", "contest"),
    ("hmm", "contest"),
    ("can you run the tests again?", "contest"),
    ("thanks", "accept"),
    ("great, ship it", "accept"),
    ("LGTM", "accept"),
    ("looks good, commit and push", "accept"),
    ("nice, next", "accept"),
    ("great but why so many files", "contest"),            # pushback wins over accept
    ("thanks, I will read it all properly over the weekend and tell you tomorrow", "neutral"),  # >= 12 words
    ("ok", "neutral"),
    ("now do the same for the other module please", "neutral"),
    ("knowledge is power", "neutral"),                      # "no" inside a word is not a marker
])
def test_signoff_response_kinds(panel, tmp_path, reply, kind):
    assert _signoff_then_reply(panel, tmp_path, reply) == kind


def test_only_next_prompt_classifies_a_signoff(panel, tmp_path):
    t = transcript(tmp_path, [("human", "x"), ("tool", 10)])
    panel.stop(t)
    panel.prompt("thanks", now=at(1))
    panel.prompt("why though", now=at(2))
    assert len(panel.events("signoff_response")) == 1


def test_prompt_with_no_signoff_logs_no_response(panel):
    panel.prompt("why is this slow")
    assert panel.events("signoff_response") == []


def test_prompt_answering_a_door_is_not_a_signoff_response(panel, tmp_path):
    t = transcript(tmp_path, [("human", "x"), ("tool", 10)])
    panel.stop(t)
    panel.prompt("thanks", now=at(1))      # classifies the signoff
    panel.bash(DOOR, now=at(2))
    panel.prompt("the branch is merged and nobody else uses it", now=at(3))
    assert len(panel.events("signoff_response")) == 1
    assert len(panel.events("justify")) == 1


def test_signoff_export_with_buckets_and_none(panel, tmp_path):
    for i, (n, reply) in enumerate([(10, "why?"), (12, "thanks"), (30, "why is that"), (60, "ok"), (55, None)]):
        sid = "s%d" % i
        t = transcript(tmp_path, [("human", "x"), ("tool", n)], name="t%d.jsonl" % i)
        panel.stop(t, sid=sid, now=at(i * 20))
        if reply:
            panel.prompt(reply, sid=sid, now=at(i * 20 + 1))
    w = panel.week(now=at(200))
    assert w["signoffs"] == 5
    assert w["signoff_responses"] == {"contest": 2, "accept": 1, "neutral": 1, "none": 1}
    b = w["signoffs_by_bucket"]
    assert b["8-19"] == {"signoffs": 2, "contest": 1, "accept": 1, "neutral": 0, "none": 0}
    assert b["20-49"] == {"signoffs": 1, "contest": 1, "accept": 0, "neutral": 0, "none": 0}
    assert b["50+"] == {"signoffs": 2, "contest": 0, "accept": 0, "neutral": 1, "none": 1}


# ----------------------------------------------------------------- export shape and privacy

def _full_session(panel, tmp_path):
    sid = "sess-" + SECRET_BRANCH
    panel.bash(SECRET_CMD, sid=sid)
    panel.prompt(SECRET_PROMPT, sid=sid, now=at(1))
    panel.bash(SECRET_CMD, sid=sid, now=at(2))
    t = transcript(tmp_path, [("human", "SECRET_PROMPT_IN_TRANSCRIPT"), ("tool", 12),
                              ("assistant_text", "SECRET_ASSISTANT_TEXT")])
    panel.stop(t, sid=sid, now=at(3), cwd=SECRET_CWD)
    panel.prompt("why did you touch SECRET_FILE_NAME.py", sid=sid, now=at(4))
    return sid, t


def test_export_contains_counts_only(panel, tmp_path):
    sid, t = _full_session(panel, tmp_path)
    p = panel.run(["export"], now=at(30))
    assert p.returncode == 0
    text = p.stdout
    for needle in [SECRET_BRANCH, SECRET_CMD, "PLUMBUS_7731", SECRET_PROMPT, SECRET_CWD, "secret-project",
                   "xyzzy", sid, str(t), str(tmp_path), "SECRET_", "git push", "--force", "/Users", ".py",
                   "force-push", "git-force"]:
        assert needle not in text, needle
    data = json.loads(text)
    assert set(data) == {"protocol_version", "participant_id", "generated_at", "weeks"}
    assert data["protocol_version"] == "1.0"
    uuid.UUID(data["participant_id"], version=4)
    assert len(data["weeks"]) == 1
    w = data["weeks"][0]
    assert set(w) == {"iso_week", "sessions_with_activity", "fires", "by_kind", "signoffs",
                      "signoff_responses", "signoffs_by_bucket"}

    def only_numbers(node):
        if isinstance(node, dict):
            for v in node.values():
                only_numbers(v)
        else:
            assert isinstance(node, int) and not isinstance(node, bool)
    for key in ("sessions_with_activity", "fires", "by_kind", "signoffs", "signoff_responses", "signoffs_by_bucket"):
        only_numbers(w[key])
    assert w["fires"] == 1 and w["by_kind"]["reasoned"] == 1
    assert w["signoffs"] == 1 and w["signoff_responses"]["contest"] == 1


def test_local_log_keeps_justification_text_but_not_commands(panel, tmp_path):
    _full_session(panel, tmp_path)
    log = (panel.dir / "events.jsonl").read_text()
    assert SECRET_PROMPT in log           # justification text stays local
    assert SECRET_CMD not in log and SECRET_BRANCH not in log.replace("sess-" + SECRET_BRANCH, "")
    assert "SECRET_PROMPT_IN_TRANSCRIPT" not in log and "SECRET_ASSISTANT_TEXT" not in log
    assert "SECRET_FILE_NAME" not in log  # sign-off responses are classified, never stored
    assert SECRET_CWD not in log


def test_export_out_file_and_empty_export(panel, tmp_path):
    out = tmp_path / "nested" / "export.json"
    p = panel.run(["export", "--out", str(out)])
    assert p.returncode == 0 and p.stdout.strip() == str(out)
    data = json.loads(out.read_text())
    assert data["weeks"] == [] and data["protocol_version"] == "1.0"


def test_participant_id_is_stable_uuid4(panel):
    a = panel.export()["participant_id"]
    b = panel.export()["participant_id"]
    assert a == b
    assert uuid.UUID(a).version == 4
    assert json.loads((panel.dir / "participant.json").read_text())["participant_id"] == a


def test_status_summary(panel, tmp_path):
    panel.bash(DOOR, sid="a")
    panel.prompt("ok", sid="a", now=at(1))
    panel.bash(DOOR, sid="a", now=at(2))
    panel.bash(DOOR, sid="b")
    panel.prompt("the branch is merged and nobody else uses it", sid="b", now=at(1))
    panel.bash(DOOR, sid="b", now=at(2))
    t = transcript(tmp_path, [("human", "x"), ("tool", 9)])
    panel.stop(t, sid="c", now=at(3))
    panel.prompt("why?", sid="c", now=at(4))
    p = panel.run(["status"], now=at(5))
    assert p.returncode == 0
    assert "blank-justification rate: 1/2 = 50%" in p.stdout
    assert "contest rate: 1/1 = 100%" in p.stdout
    assert "2026-W42" in p.stdout


def test_status_with_no_data(panel):
    p = panel.run(["status"])
    assert p.returncode == 0 and "n/a" in p.stdout


# ----------------------------------------------------------------- safety

def test_panel_off_does_nothing(panel, tmp_path):
    env = {"CRUX_PANEL": "off"}
    out = panel.hook("pretooluse", {"session_id": "s", "tool_name": "Bash", "tool_input": {"command": DOOR}}, env=env)
    assert out == ""
    panel.hook("userpromptsubmit", {"session_id": "s", "prompt": "ok"}, env=env)
    t = transcript(tmp_path, [("human", "x"), ("tool", 12)])
    panel.hook("stop", {"session_id": "s", "transcript_path": str(t)}, env=env)
    assert not panel.dir.exists()


@pytest.mark.parametrize("raw", ["", "not json", "[1,2]", "null", '{"tool_name": "Bash"}',
                                 '{"tool_name": "Bash", "tool_input": {"command": 5}}',
                                 '{"tool_name": "Bash", "tool_input": null}'])
@pytest.mark.parametrize("name", ["pretooluse", "userpromptsubmit", "stop"])
def test_hooks_survive_garbage_stdin(panel, name, raw):
    assert panel.hook(name, None, raw=raw) == ""


def test_hook_exceptions_exit_zero_and_log_error(panel):
    panel.dir.mkdir(parents=True)
    (panel.dir / "events.jsonl").write_text('{"e": "fire", "session_id": "s1"}\n')  # malformed fire: no ts/fire_id
    out = panel.hook("pretooluse", {"session_id": "s1", "tool_name": "Bash", "tool_input": {"command": DOOR}})
    assert out == ""  # fail open, silently
    assert "Traceback" in (panel.dir / "errors.log").read_text()


def test_corrupt_event_lines_are_skipped(panel):
    panel.bash(DOOR)
    with open(panel.dir / "events.jsonl", "a") as fh:
        fh.write("{broken\n\n[]\n")
    panel.prompt("the branch is merged and nobody else uses it", now=at(1))
    assert panel.bash(DOOR, now=at(2)) is None
    assert panel.export(now=at(3))["weeks"][0]["by_kind"]["reasoned"] == 1


def test_unwritable_data_dir_exits_zero(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    e = dict(os.environ, CRUX_PANEL_DIR=str(blocker / "sub"), HOME=str(tmp_path))
    e.pop("CRUX_PANEL", None)
    p = subprocess.run([sys.executable, str(SCRIPT), "hook", "pretooluse"],
                       input=json.dumps({"session_id": "s", "tool_name": "Bash",
                                         "tool_input": {"command": DOOR}}),
                       capture_output=True, text=True, env=e)
    assert p.returncode == 0 and p.stdout == ""


def test_hook_is_fast_with_large_log(panel):
    panel.dir.mkdir(parents=True)
    line = json.dumps({"e": "prompt", "ts": T0, "session_id": "old"}) + "\n"
    (panel.dir / "events.jsonl").write_text(line * 60000)  # ~3.5 MB
    import time
    start = time.time()
    panel.bash(DOOR)
    assert time.time() - start < 2.0


def test_runs_on_python39_syntax():
    import ast
    ast.parse(SCRIPT.read_text(), feature_version=(3, 9))


def test_script_imports_only_stdlib():
    tree = __import__("ast").parse(SCRIPT.read_text())
    mods = set()
    for n in __import__("ast").walk(tree):
        if isinstance(n, __import__("ast").Import):
            mods.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, __import__("ast").ImportFrom):
            mods.add(n.module.split(".")[0])
    assert mods <= set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else True
    assert "yaml" not in mods and "requests" not in mods
