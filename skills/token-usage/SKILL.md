---
name: token-usage
description: Show how many tokens each task (session), day or month used in Claude Code, and for Codex or OpenCode through ccusage. Use when the user asks about token usage, which conversation used the most, or what a long conversation costs.
---

# Token usage per task

All counting runs on this computer, from the log files the agents already keep. Nothing is uploaded. Costs are estimates, not a bill.

## Claude Code: `scripts/usage.py` (Python 3, nothing to install)

```bash
python skills/token-usage/scripts/usage.py              # heaviest sessions, with titles
python skills/token-usage/scripts/usage.py --by month   # or --by day, add --since 2026-11-01
python skills/token-usage/scripts/usage.py --json
```

It reads `~/.claude/projects` (sub-agents counted in their parent session, repeated log lines counted once, dates in the computer's own time zone). It shows tokens only. For a cost, pass `--prices prices.json` with the user's own rates per model, in USD per million tokens: no price is built in, so none can be out of date.

## Codex and OpenCode: ccusage

[ccusage](https://github.com/ccusage/ccusage) (MIT, a separate project) reads their logs. Pinned to the version this skill was written against:

```bash
npx ccusage@20.1.1 codex session
npx ccusage@20.1.1 opencode session
```

Defaults it reads: Codex `${CODEX_HOME:-~/.codex}`, OpenCode `${OPENCODE_DATA_DIR:-${XDG_DATA_HOME:-~/.local/share}/opencode}`. If a report is empty, set the variable to the real folder. Add `--json` for machine-readable output; `ccusage telemetry disable` turns off its small anonymous ping.

## Report

Give the user the total tokens, the heaviest sessions with their titles, and say plainly that in long conversations most tokens are cache reads of the growing context. Do not call any cost a bill.
