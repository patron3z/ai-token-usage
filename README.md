# ai-token-usage

An Agent Skill that answers "how many tokens did each task use?" for **Claude Code, Codex and OpenCode**, and a small script that puts a title next to each Claude Code session.

It does the counting with [ccusage](https://github.com/ccusage/ccusage) (MIT, by ryoppippi and contributors), which it runs as a separate program. This repository contains none of ccusage's code and is not affiliated with it. Everything runs on your computer and nothing is uploaded by this skill.

## What you get

- `skills/token-usage/SKILL.md`: tells the agent which ccusage command to run for each agent, and how to report the result.
- `skills/token-usage/scripts/session_titles.py`: lists your heaviest Claude Code sessions with their titles and dates (Python 3, standard library only).

Costs are estimates at API prices, not what a subscription plan charges.

## Install

1. Install ccusage (Node.js needed), or use `npx ccusage` instead:

```bash
npm install -g ccusage
ccusage telemetry disable   # optional: ccusage sends a small anonymous ping by default
```

2. Copy `skills/token-usage/` to your agent's skills folder:

| Agent | Folder | Report command |
|---|---|---|
| Claude Code | `~/.claude/skills/token-usage` | `ccusage session` |
| Codex | `~/.agents/skills/token-usage` | `ccusage codex session` |
| OpenCode | `~/.config/opencode/skills/token-usage` | `ccusage opencode session` |

Then ask your agent: "how many tokens did each of my sessions use?"

## Status

Tested with Claude Code on Windows. Not yet run inside Codex or OpenCode (neither is installed on the author's PC): their folders and commands come from ccusage's own documentation. If something differs on your machine, open an issue.

## License

MIT, see `LICENSE`. ccusage has its own MIT license.
