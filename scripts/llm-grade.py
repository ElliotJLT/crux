#!/usr/bin/env python3
"""LLM-graded diligence measurement.

The regex scan can't tell "verified the AI's substance" from "steered its
process". This grades a random sample of real turns with an LLM judge against
a fixed codebook, so the headline number is defensible.

Codebook (one PRIMARY label per human turn that responds to AI output):
  VERIFY  — checks/challenges whether the AI's output is CORRECT/TRUE: asks it
            to justify, points out an error, questions the reasoning, asks
            "are you sure / did you test / how do you know", validates a claim.
            (Discernment + Diligence on substance.)
  STEER   — redirects approach / scope / style / presentation, or corrects the
            AI's process, WITHOUT checking whether its claims are true.
            (Engaged on voice/process, not substance.)
  DIRECT  — a new instruction or task, not an evaluation of the prior output.
  ACCEPT  — approves / continues / moves on without scrutiny.

Read-only over transcripts. Message text is scrubbed of secrets/emails before
it leaves the machine. Aggregates are publishable; the labelled sample is local.

Usage: python3 scripts/llm-grade.py [--n 150] [--model claude-haiku-4-5-20251001]
"""

import argparse, json, re, random, subprocess, sys, math
from pathlib import Path

SECRET = re.compile(r"(\b\d{8,10}:[A-Za-z0-9_-]{30,}\b|\bsk-[A-Za-z0-9_-]{20,}\b|\b[A-Za-z0-9_\-]{32,}\b)")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

def scrub(t):
    t = EMAIL.sub("[email]", t)
    t = SECRET.sub("[redacted]", t)
    return t

def human_text(rec):
    if rec.get("type") != "user" or rec.get("isSidechain"): return None
    c = (rec.get("message") or {}).get("content")
    if isinstance(c, str): t = c.strip()
    elif isinstance(c, list):
        t = "\n".join(b.get("text","") for b in c if isinstance(b,dict) and b.get("type")=="text").strip()
    else: return None
    if not t or t[0] in "</" or t.startswith("[Request") or t.startswith("Caveat"): return None
    return t

def asst(rec):
    if rec.get("type") != "assistant" or rec.get("isSidechain"): return "",0,0
    c = (rec.get("message") or {}).get("content")
    if not isinstance(c, list): return "",0,0
    txt = "".join(b.get("text","") for b in c if isinstance(b,dict) and b.get("type")=="text")
    ed = sum(1 for b in c if isinstance(b,dict) and b.get("type")=="tool_use" and b.get("name") in ("Edit","Write","MultiEdit","NotebookEdit"))
    return txt, len(txt), ed

def collect(projects_dir):
    turns = []
    files = sorted(p for p in Path(projects_dir).rglob("*.jsonl") if "subagents" not in p.parts)
    for path in files:
        recs = []
        with open(path, errors="replace") as fh:
            for line in fh:
                try: recs.append(json.loads(line))
                except json.JSONDecodeError: pass
        tail=""; ch=ed=0
        for rec in recs:
            at,ac,ae = asst(rec); tail = (tail+at)[-1200:] if at else tail; ch+=ac; ed+=ae
            ht = human_text(rec)
            if ht is None: continue
            if ch>0 or ed>0:
                turns.append({"ai_tail": scrub(tail[-550:]), "ai_chars": ch, "ai_edits": ed,
                              "human": scrub(ht[:380])})
            tail=""; ch=ed=0
    return turns

CODEBOOK = """You are coding turns from a developer's real AI-coding sessions to measure epistemic engagement (the AI Fluency Index's Discernment + Diligence dimensions).

Each turn shows the TAIL of the AI's preceding output, then the HUMAN's reply. Assign exactly ONE primary label to the human reply:

VERIFY = checks or challenges whether the AI's output is CORRECT or TRUE — asks it to justify/prove/explain why, points out an error or flaw, questions the reasoning, asks "are you sure / did you test / how do you know", or validates a claim independently.
STEER = redirects the approach, scope, style, or presentation, or corrects the AI's process — but does NOT check whether the AI's claims are true.
DIRECT = a new instruction or task, not an evaluation of the prior output.
ACCEPT = approves, continues, or moves on without scrutiny ("ok", "do it", "great", "next", "yh").

Return ONLY a compact JSON array, one object per turn, no prose:
[{"i":1,"label":"VERIFY"},{"i":2,"label":"STEER"}]"""

def grade_batch(batch, model):
    lines = [CODEBOOK, "", f"Classify these {len(batch)} turns:", ""]
    for k, t in enumerate(batch, 1):
        lines.append(f"### Turn {k}  (AI wrote {t['ai_chars']} chars / {t['ai_edits']} edits)")
        lines.append(f"AI(tail): {t['ai_tail']}")
        lines.append(f"HUMAN: {t['human']}")
        lines.append("")
    prompt = "\n".join(lines)
    out = subprocess.run(["claude","-p","--model",model], input=prompt,
                         capture_output=True, text=True, timeout=120).stdout
    # robust: pull every {...} object in order, take labels positionally
    labels = []
    for o in re.findall(r"\{[^{}]*\}", out, re.DOTALL):
        try:
            lab = json.loads(o).get("label", "").upper()
            if lab: labels.append(lab)
        except json.JSONDecodeError:
            pass
    return labels

def wilson(p, n):
    if n==0: return (0,0)
    z=1.96; ph=p
    d=1+z*z/n
    c=(ph+z*z/(2*n))/d
    h=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--projects-dir", default=str(Path.home()/".claude/projects"))
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch", type=int, default=12)
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    ap.add_argument("--outdir", default="llm-grade")
    a=ap.parse_args()
    out=Path(a.outdir); out.mkdir(parents=True, exist_ok=True)

    turns=collect(a.projects_dir)
    random.seed(7); random.shuffle(turns)
    sample=turns[:a.n]
    print(f"collected {len(turns)} AI-responding turns; grading {len(sample)} with {a.model}", file=sys.stderr)

    labels=[]
    for s in range(0, len(sample), a.batch):
        batch=sample[s:s+a.batch]
        res=grade_batch(batch, a.model)  # list of labels, positional
        if len(res) != len(batch):       # one retry on count mismatch
            res=grade_batch(batch, a.model)
        for k,t in enumerate(batch):
            lab=res[k] if k < len(res) else "UNKNOWN"
            if lab not in ("VERIFY","STEER","DIRECT","ACCEPT"): lab="UNKNOWN"
            t["label"]=lab; labels.append(lab)
        print(f"  graded {min(s+a.batch,len(sample))}/{len(sample)}", file=sys.stderr)

    from collections import Counter
    c=Counter(labels); n=len([l for l in labels if l!="UNKNOWN"]) or 1
    def pct(k): return 100*c[k]/n
    lo,hi=wilson(c['VERIFY']/n, n)
    L=[]; w=L.append
    w("# LLM-graded diligence — verification vs steering vs accepting")
    w("")
    w(f"> {len(sample)} randomly-sampled human turns that responded to AI output · judge: {a.model}")
    w(f"> Codebook in scripts/llm-grade.py. Unparseable: {c['UNKNOWN']}.")
    w("")
    w("## Result")
    w(f"- **VERIFY** (checked the AI was right): **{pct('VERIFY'):.0f}%**  (95% CI {100*lo:.0f}–{100*hi:.0f}%)")
    w(f"- **STEER** (redirected process/voice, didn't verify): **{pct('STEER'):.0f}%**")
    w(f"- **DIRECT** (new instruction): {pct('DIRECT'):.0f}%")
    w(f"- **ACCEPT** (waved it through): **{pct('ACCEPT'):.0f}%**")
    w("")
    sv = c['STEER']/max(c['VERIFY'],1)
    w(f"- **Steer : verify ratio = {sv:.1f} : 1** — for every time the substance got checked, the process got steered {sv:.1f}×.")
    w(f"- Engaged-but-unverified (STEER+ACCEPT): {pct('STEER')+pct('ACCEPT'):.0f}%")
    (out/"report.md").write_text("\n".join(L))
    with open(out/"labelled.jsonl","w") as fh:
        for t in sample: fh.write(json.dumps(t)+"\n")
    print("\n".join(L))

if __name__=="__main__":
    main()
