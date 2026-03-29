# Build Notes (v0.2.2)

## Rule: Verify Live CLI First

Never trust old runbooks. Start every AO operation with:
```bash
cd /home/aiadmin/tools/agent-orchestrator
ao --help
ao status
```

## Current Version

- **Installed:** 0.2.2 (git-based monorepo install)
- **Local patch:** `owner-first routing via projectOwnerMap` (1 commit over origin/main)
- **Packages:** `@composio/ao-cli`, `@composio/ao-core`, `@composio/ao-web`, plugins
- **Node:** v22.22.0

## Subcommands (current)

| Command | Notes |
|---------|-------|
| `ao start <project>` | Full start (orchestrator + dashboard + lifecycle) |
| `ao stop <project>` | Full stop |
| `ao status` | Authoritative state view |
| `ao spawn <issue>` | Auto-detects project |
| `ao batch-spawn <issues...>` | Multiple issues with dedup |
| `ao send <session> "msg"` | With busy detection + retry |
| `ao session ls / kill / cleanup / restore / claim-pr / remap / attach` | Session management |
| `ao review-check` | Check PRs for review comments |
| `ao verify <issue>` | Post-merge verification |
| `ao doctor` | Health checks |
| `ao update` | Upstream sync + rebuild |
| `ao setup openclaw` | Notifier integration |
| `ao dashboard` | Standalone dashboard (⚠️ no WS) |
| `ao open <target>` | Open sessions in terminal |
| `ao lifecycle-worker <project>` | Internal polling worker |
| `ao config-help` | Config schema reference |

## Dashboard Start Modes

| Mode | Command | Processes | WS Servers |
|------|---------|-----------|------------|
| **Full (via ao start)** | `ao start <project>` | next + terminal-ws + direct-terminal-ws | ✅ Yes |
| **Standalone** | `ao dashboard` | next only | ❌ No |
| **Manual** | `npx concurrently ...` | next + terminal-ws + direct-terminal-ws | ✅ Yes |

`ao start` in dev mode detects `server/` directory → runs `pnpm run dev` (concurrently).
`ao dashboard` standalone runs `npx next dev` only.

## Agent Runtimes

Available: `claude-code`, `aider`, `codex`, `opencode`
Default: `claude-code` (configured in yaml `defaults.agent`)

## Do NOT Hardcode

- Exact tmux session naming (includes random hash prefix like `ad80e6c2be93-`)
- Lifecycle command spelling
- Dashboard port (read from config)
- Terminal WS ports (auto-detected or from config)
- Merge behavior (configured in `reactions.approved-and-green`)

## Config Location

```
/home/aiadmin/tools/agent-orchestrator/agent-orchestrator.yaml
```

Projects, ports, runtime, agent, reactions, notifiers, routing — all here.

## Local Patch Management

Current patch: `feat(notifier-openclaw): owner-first routing via projectOwnerMap`
- File: `packages/plugins/notifier-openclaw/src/index.ts`
- Adds: `resolveAgentId()`, `projectOwnerMap`, `fallbackAgentId` config
- Must rebase on each `ao update` or manual `git fetch + rebase`
- Typical conflict: in the same file around function declarations

Rebase flow:
```bash
git fetch origin
git rebase origin/main
# If conflict in notifier-openclaw/src/index.ts:
# Keep BOTH upstream's resolveEnvVarToken AND our resolveAgentId
git add <conflicted-file>
git rebase --continue
pnpm install && pnpm build
```
