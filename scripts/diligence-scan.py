#!/usr/bin/env python3
"""Diligence scan: measure epistemic engagement with AI output over time.

Grounded in Anthropic's AI Fluency Index (Discernment + Diligence) and the
artifact paradox, rather than the operational one-way-door seam the cut-line
dry run measures. Read-only over ~/.claude/projects transcripts.

For every human-authored message it asks: did you engage your judgment on the
AI's substance (challenge / verify / correct), or coast (bare approval)? Then:

  1. Overall engagement vs coasting rate.
  2. The artifact-paradox test: is your challenge rate LOWER right after the AI
     produces a big / polished output (long text or multiple edits)?
  3. The trend by month — is engagement declining (the compounding claim)?

Heuristic, transparent, and conservative. Numbers are proxies, not gospel; a
validation sample is written for eyeballing. Aggregates are publishable; the
sample stays local.

Usage:
  python3 scripts/diligence-scan.py [--projects-dir ~/.claude/projects]
                                    [--outdir ./diligence-scan]
"""

import argparse, json, re, random
from collections import Counter, defaultdict
from pathlib import Path

VERIFY = re.compile(r"\b(why\b|are you sure|how do (you|we) know|prove\b|verif|double[- ]?check|fact[- ]?check|sanity check|did you (check|test|verif|confirm)|have you (check|test|verif)|is that (right|correct|true|accurate)|are we sure|is this (right|correct|true)|does that (actually|really)|what makes you|justif|explain (why|your|the reasoning|how)|can you confirm|where did (you|this|that)|show me (why|how|the))", re.I)
CORRECT = re.compile(r"(\bno,|\bnope\b|\bdon'?t\b|\bdo not\b|\bactually\b|\binstead\b|that'?s (wrong|not right|incorrect|not what)|that isn'?t|\brevert\b|\bundo\b|roll ?back|\bstop\b|\bwait\b|hold on|back up|you'?re wrong|that'?s wrong|\bincorrect\b|rethink|reconsider|i disagree|i don'?t think|not (sure|convinced) (that|this|about)|that'?s not|misunderstood|you missed|not quite|that'?s not what)", re.I)
CHALLENGE_SOFT = re.compile(r"(\?|\bbut\b|\bhowever\b|concern|\brisk\b|edge case|what if|are there|is there a (risk|problem|issue)|won'?t that|wouldn'?t that)", re.I)
APPROVAL = re.compile(r"^\s*(go for it|go ahead|go|do it|just do it|ship it|send it|yes+|yep+|yeah|ya|ok(ay)?|sure|sounds? good|perfect|great|nice|cool|lgtm|looks good|please( do)?( it)?|thanks?( so much)?|thank you|ty|continue|proceed|carry on|next|keep going|crack on|all good|do that|merge it|push it|ship|agreed|makes sense|good|love it|amazing|awesome)[\s.!👍]*$", re.I)


def human_text(record):
    if record.get("type") != "user" or record.get("isSidechain"):
        return None
    msg = record.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        text = "\n".join(parts).strip()
    else:
        return None
    if not text or text[0] in "</" or text.startswith("[Request") or text.startswith("Caveat"):
        return None
    return text


def assistant_size(record):
    """(text_chars, edit_count) contributed by an assistant record."""
    if record.get("type") != "assistant" or record.get("isSidechain"):
        return 0, 0
    content = (record.get("message") or {}).get("content")
    if not isinstance(content, list):
        return 0, 0
    chars = sum(len(b.get("text", "")) for b in content if isinstance(b, dict) and b.get("type") == "text")
    edits = sum(1 for b in content if isinstance(b, dict) and b.get("type") == "tool_use"
                and b.get("name") in ("Edit", "Write", "MultiEdit", "NotebookEdit"))
    return chars, edits


def classify(text):
    if VERIFY.search(text):
        return "engaged", "verify"
    if CORRECT.search(text):
        return "engaged", "correct"
    if APPROVAL.match(text):
        return "coasting", "approval"
    if len(text.split()) <= 3 and "?" not in text:
        return "coasting", "approval"
    if CHALLENGE_SOFT.search(text):
        return "engaged", "challenge"
    return "neutral", "directive"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-dir", default=str(Path.home() / ".claude/projects"))
    ap.add_argument("--outdir", default="diligence-scan")
    args = ap.parse_args()
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in Path(args.projects_dir).rglob("*.jsonl") if "subagents" not in p.parts)

    cats = Counter(); subs = Counter()
    by_month = defaultdict(Counter)
    # artifact-paradox buckets: response engagement after big vs small AI output
    para = {"big_edit": Counter(), "small_edit": Counter(), "big_text": Counter(), "small_text": Counter()}
    per_session_engaged = []
    sample = []
    sessions = 0; total_msgs = 0

    for path in files:
        recs = []
        with open(path, errors="replace") as fh:
            for line in fh:
                try: recs.append(json.loads(line))
                except json.JSONDecodeError: continue
        if not recs: continue
        sessions += 1
        acc_chars = acc_edits = 0
        sess_eng = sess_tot = 0
        for rec in recs:
            ac, ae = assistant_size(rec)
            acc_chars += ac; acc_edits += ae
            ht = human_text(rec)
            if ht is None:
                continue
            cat, sub = classify(ht)
            total_msgs += 1; sess_tot += 1
            cats[cat] += 1; subs[sub] += 1
            engaged = cat == "engaged"
            if engaged: sess_eng += 1
            month = (rec.get("timestamp") or "")[:7]
            if month: by_month[month][cat] += 1
            # artifact paradox: only count responses that follow real AI output
            if acc_chars > 0 or acc_edits > 0:
                para["big_edit" if acc_edits >= 2 else "small_edit"]["eng" if engaged else "no"] += 1
                para["big_text" if acc_chars >= 2000 else "small_text"]["eng" if engaged else "no"] += 1
            if len(sample) < 400:
                sample.append({"cat": cat, "sub": sub, "ai_chars": acc_chars, "ai_edits": acc_edits, "text": ht[:160]})
            acc_chars = acc_edits = 0
        if sess_tot >= 3:
            per_session_engaged.append(sess_eng / sess_tot)

    def rate(c, k):
        t = sum(c.values()); return (100 * c[k] / t) if t else 0

    eng = cats["engaged"]; coast = cats["coasting"]; neut = cats["neutral"]
    months = sorted(by_month)

    L = []; w = L.append
    w("# Diligence scan — epistemic engagement with AI output")
    w("")
    w(f"> {sessions} sessions · {total_msgs:,} human messages · {months[0] if months else '?'}–{months[-1] if months else '?'}")
    w("> Heuristic proxies for the AI Fluency Index's Discernment + Diligence. Conservative; eyeball sample.jsonl.")
    w("")
    w("## Engagement vs coasting")
    w(f"- **Engaged** (challenge / verify / correct the AI): {eng:,} = **{100*eng/total_msgs:.0f}%**")
    w(f"- **Coasting** (bare approval / continue): {coast:,} = **{100*coast/total_msgs:.0f}%**")
    w(f"- **Neutral** (new instruction, no scrutiny either way): {neut:,} = {100*neut/total_msgs:.0f}%")
    w(f"- Of engaged: verify {subs['verify']:,} · correct {subs['correct']:,} · soft-challenge {subs['challenge']:,}")
    w(f"- **Verification specifically** (asking the AI to justify/prove/explain *why*): {subs['verify']:,} = **{100*subs['verify']/total_msgs:.1f}%** of all messages")
    w("")
    w("## The artifact paradox, in your own data")
    w("> Do you scrutinise less right after the AI produces a big / polished output?")
    for label, key in [("after ≥2 edits", "big_edit"), ("after <2 edits", "small_edit"),
                       ("after ≥2000 chars of AI text", "big_text"), ("after <2000 chars", "small_text")]:
        c = para[key]; tot = c["eng"] + c["no"]
        w(f"- {label}: engaged on **{100*c['eng']/tot:.0f}%** of responses ({tot:,} responses)" if tot else f"- {label}: n/a")
    be = para["big_edit"]; se = para["small_edit"]
    bt = be["eng"]+be["no"]; st = se["eng"]+se["no"]
    if bt and st:
        delta = (100*be["eng"]/bt) - (100*se["eng"]/st)
        w(f"- **Δ engagement (big-edit minus small-edit): {delta:+.0f}pp.** Negative = the artifact paradox showing up: bigger output, less scrutiny.")
    w("")
    w("## Trend by month (the compounding check)")
    w("| month | msgs | engaged % | coasting % |")
    w("|---|---|---|---|")
    for m in months:
        c = by_month[m]; t = sum(c.values())
        if t < 10: continue
        w(f"| {m} | {t} | {100*c['engaged']/t:.0f}% | {100*c['coasting']/t:.0f}% |")
    w("")
    if per_session_engaged:
        per_session_engaged.sort()
        med = per_session_engaged[len(per_session_engaged)//2]
        w(f"Per-session engaged rate: median {100*med:.0f}% across {len(per_session_engaged)} sessions (≥3 msgs).")
    (outdir / "report.md").write_text("\n".join(L))
    random.seed(7); random.shuffle(sample)
    with open(outdir / "sample.jsonl", "w") as fh:
        for s in sample[:120]: fh.write(json.dumps(s) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
