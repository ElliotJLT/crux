#!/usr/bin/env python3
"""Generate plugin/cutlines.json from taxonomy/cutlines.yml.

The panel plugin must run on stdlib only, so it cannot read YAML. This script
flattens the hard tier (id, pattern, why) into JSON. tests/test_panel.py
asserts the two files are in sync; rerun this script after editing the YAML.

Usage:
  python3 scripts/build-cutlines-json.py [--check]
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "taxonomy" / "cutlines.yml"
DST = ROOT / "plugin" / "cutlines.json"


def build():
    spec = yaml.safe_load(SRC.read_text())
    rules = [
        {"id": r["id"], "pattern": r["pattern"], "why": r.get("why", "")}
        for r in spec["rules"]
        if r.get("tier") == "hard"
    ]
    return json.dumps({"rules": rules}, indent=2, ensure_ascii=False) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if plugin/cutlines.json is out of date")
    args = ap.parse_args()
    text = build()
    if args.check:
        if not DST.exists() or DST.read_text() != text:
            print("plugin/cutlines.json is out of sync with taxonomy/cutlines.yml", file=sys.stderr)
            return 1
        return 0
    DST.write_text(text)
    print(f"wrote {DST.relative_to(ROOT)} ({text.count(chr(34) + 'id' + chr(34))} hard rules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
