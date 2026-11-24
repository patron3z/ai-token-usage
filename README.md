# ai-token-usage

An Agent Skill that answers "how many tokens did each task use?" in **Claude Code, Codex and OpenCode**.

- **Claude Code:** `skills/token-usage/scripts/usage.py`, my own small script (Python 3, standard library only). It reads Claude Code's local log files and shows tokens per session (with the conversation's title), day or month.
- **Codex and OpenCode:** the skill tells the agent to run [ccusage](https://github.com/ccusage/ccusage) (MIT, by ryoppippi and contributors), a separate program. This repository contains none of its code and is not affiliated with it.

Everything runs on your computer and nothing is uploaded. Tokens are exact counts from the logs. The script shows no cost unless you give it your own prices.

## Check it

On the author's logs, month totals match ccusage's to the token (August to October compared; November was still growing while measured).

## Install

Copy `skills/token-usage/` to your agent's skills folder:

| Agent | Folder |
|---|---|
| Claude Code | `~/.claude/skills/token-usage` |
| Codex | `~/.agents/skills/token-usage` |
| OpenCode | `~/.config/opencode/skills/token-usage` |

Then ask your agent: "how many tokens did each of my sessions use?" Or run the script yourself:

```bash
python skills/token-usage/scripts/usage.py --top 10
python skills/token-usage/scripts/usage.py --by month
```

## Status

Tested on Windows with Claude Code. The Codex and OpenCode parts are untested here (neither is installed on the author's PC): their folders and ccusage commands come from ccusage's documentation. If something differs on your machine, open an issue.

## License

MIT, see `LICENSE`.
