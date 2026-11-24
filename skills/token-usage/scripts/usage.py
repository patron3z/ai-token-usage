#!/usr/bin/env python3
"""Tokens used per session, day or month, from Claude Code's own log files.

Reads ~/.claude/projects/**/*.jsonl on this computer. Nothing is sent anywhere.
Standard library only. Costs are shown only if you give a prices file (see --prices):
no price is built in, so no number here can be out of date.

Examples:
  python usage.py                      # heaviest sessions, with titles
  python usage.py --by month
  python usage.py --by day --since 2026-11-01
  python usage.py --json
  python usage.py --prices prices.json # prices.json: {"model-name": {"input": 3, "output": 15, "cache_write": 3.75, "cache_read": 0.3}}  (USD per million tokens)
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def text_of(content):
    if isinstance(content, list):
        content = " ".join(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")
    return content.strip() if isinstance(content, str) else ""


def scan(root):
    """Yield one record per distinct assistant message: (session, timestamp, model, usage dict)."""
    seen = set()
    titles = {}
    paths = sorted(glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True))
    for path in paths:
        # a sub-agent file lives in <session>/subagents/...: count it under its parent session
        parts = os.path.normpath(path).split(os.sep)
        base = os.path.splitext(parts[-1])[0]
        session = parts[-3] if len(parts) >= 3 and parts[-2] == "subagents" else base
        with open(path, encoding="utf8", errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                t = d.get("type")
                if t in ("ai-title", "summary", "custom-title") and session == base:
                    titles[session] = d.get("aiTitle") or d.get("summary") or d.get("customTitle") or titles.get(session)
                elif t == "user" and not d.get("isMeta") and session == base and session not in titles:
                    first = text_of(d.get("message", {}).get("content"))
                    if first and not first.startswith("<"):
                        titles.setdefault("first:" + session, first[:90])
                if t != "assistant":
                    continue
                msg = d.get("message") or {}
                usage = msg.get("usage")
                if not isinstance(usage, dict):
                    continue
                key = (msg.get("id"), d.get("requestId"))
                if key != (None, None):
                    if key in seen:
                        continue
                    seen.add(key)
                yield session, d.get("timestamp") or "", msg.get("model") or "unknown", usage
    for s in list(titles):
        if s.startswith("first:"):
            titles.setdefault(s[6:], titles[s])
    scan.titles = titles


def local_day(ts):
    """Date of a UTC timestamp in the computer's own time zone (what a person calls 'that day')."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d")
    except ValueError:
        return ts[:10]


def cost(model, tot, prices):
    p = prices.get(model)
    if not p:
        return None
    return (tot["input_tokens"] * p.get("input", 0) + tot["output_tokens"] * p.get("output", 0)
            + tot["cache_creation_input_tokens"] * p.get("cache_write", 0)
            + tot["cache_read_input_tokens"] * p.get("cache_read", 0)) / 1_000_000


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--by", choices=("session", "day", "month"), default="session")
    ap.add_argument("--top", type=int, default=15, help="rows to show for --by session (default 15)")
    ap.add_argument("--since", default="", help="only messages from this date, YYYY-MM-DD")
    ap.add_argument("--root", default=os.path.join(os.path.expanduser("~"), ".claude", "projects"))
    ap.add_argument("--prices", help="JSON file of USD-per-million prices per model (optional)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    prices = {}
    if a.prices:
        with open(a.prices, encoding="utf8") as f:
            prices = json.load(f)

    groups = defaultdict(lambda: defaultdict(lambda: dict.fromkeys(KEYS, 0)))  # group -> model -> totals
    span = {}
    for session, ts, model, usage in scan(a.root):
        day = local_day(ts)
        if a.since and day < a.since:
            continue
        g = {"session": session, "day": day, "month": day[:7]}[a.by]
        for k in KEYS:
            groups[g][model][k] += int(usage.get(k) or 0)
        lo, hi = span.get(g, (day, day))
        span[g] = (min(lo, day), max(hi, day))
    titles = scan.titles

    rows = []
    for g, models in groups.items():
        tot = dict.fromkeys(KEYS, 0)
        c, unpriced = 0.0, False
        for m, t in models.items():
            for k in KEYS:
                tot[k] += t[k]
            v = cost(m, t, prices)
            if v is None:
                unpriced = True
            else:
                c += v
        row = {"group": g, **tot, "total_tokens": sum(tot.values()), "models": sorted(models),
               "first": span[g][0], "last": span[g][1]}
        if prices:
            row["cost_usd"] = round(c, 2)
            row["cost_complete"] = not unpriced
        if a.by == "session":
            row["title"] = titles.get(g) or titles.get("first:" + g) or ""
        rows.append(row)

    rows.sort(key=(lambda r: -r["total_tokens"]) if a.by == "session" else (lambda r: r["group"]))
    if a.by == "session":
        rows = rows[: a.top]
    if a.json:
        json.dump(rows, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return
    for r in rows:
        label = r["title"] or r["group"][:8] if a.by == "session" else r["group"]
        extra = f"  ~${r['cost_usd']:.2f}{'' if r['cost_complete'] else '+'}" if "cost_usd" in r else ""
        print(f"{r['total_tokens']:>16,} tok  out {r['output_tokens']:>10,}  cache-read {r['cache_read_input_tokens']:>15,}"
              f"  {r['first']}..{r['last']}  {label}{extra}")
    print(f"{sum(r['total_tokens'] for r in rows):>16,} tok  total of the rows shown")


if __name__ == "__main__":
    main()
