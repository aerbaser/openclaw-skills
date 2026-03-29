---
name: agent-orchestrator-ops
description: Operate, verify, diagnose, and recover Agent Orchestrator (AO) for Dors. Use when starting/stopping AO, checking whether the orchestrator is really running, validating lifecycle worker/dashboard/terminal servers, handling stale or duplicate dashboard stacks, cleaning merged ghost sessions, reconciling AO UI vs GitHub, or running user-visible delivery around merge/deploy/code tasks. Applies across Codex and Claude AO builds; always verify live CLI/build differences before acting.
---

# Agent Orchestrator Ops (v0.2.2)

## Environment

| Item | Value |
|------|-------|
| AO binary | `ao` (`~/.npm-global/bin/ao`) |
| AO version | `0.2.2` + local patch (`owner-first routing`) |
| AO config | `/home/aiadmin/tools/agent-orchestrator/agent-orchestrator.yaml` |
| AO data | `~/.agent-orchestrator/` |
| Worktrees | `~/.worktrees/` |
| Run from | `/home/aiadmin/tools/agent-orchestrator/` (**mandatory**) |
| Dashboard port | `3100` (config `port:`) |
| Terminal WS port | `14800` (auto, from `terminalPort:` or auto-detect) |
| Direct terminal WS | `14801` (from `directTerminalPort:` or `DIRECT_TERMINAL_PORT`) |
| Tailscale proxy | `debian.taildddc37.ts.net:3100 → 127.0.0.1:3100` |

> ⚠️ `ao` **must** run from the config dir — otherwise "No config found".

## Registered Projects

| Project ID | Repo | Local path | Session prefix |
|-----------|------|-----------|---------------|
| `ao-dashboard` | aerbaser/ao-dashboard | `/home/aiadmin/ao-dashboard` | `aodash` |
| `sokrat-core` | aerbaser/sokrat-core | `/home/aiadmin/projects/openclaw-platon/workspace/sokrat-core` | `sc` |

## Source of Truth (in order)

1. `ao status` — authoritative session/orchestrator state
2. Runtime: `tmux ls`, `ps aux | grep ao`, `ps aux | grep lifecycle`
3. Session metadata + GitHub: `ao session ls`, `gh pr view`
4. Dashboard UI/API — **last**, never declare state from UI alone

## Diagnostic Checklist (run before changing anything)

```bash
cd /home/aiadmin/tools/agent-orchestrator
ao --help                          # verify subcommand names (they change across versions!)
ao status                          # live session + orchestrator state
ao session ls                      # sessions + PR/CI status
ao session ls -p ao-dashboard      # filter by project
tmux ls                            # tmux sessions alive?
ps aux | grep 'lifecycle-worker'   # lifecycle workers running?
ss -tlnp | grep -E '3100|14800|14801'  # all 3 ports listening?
```

Only then decide: real failure / stale dashboard / duplicate stack / worker idle.

## Commands Reference

### Core Lifecycle

```bash
# Start project (orchestrator + dashboard + lifecycle worker)
ao start ao-dashboard              # full start (dashboard + orchestrator + lifecycle)
ao start ao-dashboard --no-dashboard    # orchestrator + lifecycle only
ao start sokrat-core --no-dashboard

# Stop
ao stop ao-dashboard               # stops everything for project
ao stop --all                      # stops all projects

# Status
ao status                          # all projects + sessions
ao status -p ao-dashboard          # filter
ao status --json                   # machine-readable
```

### Session Management

```bash
ao session ls                           # list all sessions
ao session ls -p ao-dashboard           # filter by project
ao session kill <session-id>            # kill + remove worktree
ao session kill <session-id> --keep-session     # keep mapped agent session
ao session kill <session-id> --purge-session    # delete mapped agent session
ao session cleanup                      # kill sessions where PR merged or issue closed
ao session cleanup -p ao-dashboard      # filter by project
ao session cleanup --dry-run            # preview only
ao session restore <session-id>         # restore crashed session in-place
ao session claim-pr <pr-number> [session]  # attach existing PR to session
ao session remap <session-id>           # re-discover OpenCode session mapping
ao session remap <session-id> --force   # force fresh remap
ao session attach <session-id>          # attach to tmux window
```

### Spawn Sessions

```bash
ao spawn <issue-number>                         # auto-detect project
ao spawn <issue-number> --open                  # + open in terminal
ao spawn <issue-number> --agent codex           # override agent runtime
ao spawn <issue-number> --claim-pr <pr>         # claim existing PR
ao spawn <issue-number> --decompose             # decompose into subtasks first
ao spawn <issue-number> --decompose --max-depth 2
ao batch-spawn 65 66 67                         # multiple issues, dedup
ao batch-spawn 65 66 67 --open
```

### Communicate with Sessions

```bash
ao send <session-id> "message text"             # send message (waits for idle)
ao send <session-id> "msg" --no-wait            # don't wait for idle
ao send <session-id> -f review-notes.md         # send file contents
ao send <session-id> "msg" --timeout 120        # custom idle timeout (default 600s)
```

### Dashboard

```bash
ao dashboard                      # standalone dashboard (⚠️ only starts Next.js, no WS servers!)
ao dashboard -p 3100              # custom port
ao dashboard --rebuild            # clean .next cache + restart
```

> ⚠️ **`ao dashboard` alone does NOT start terminal WebSocket servers.**
> Use `ao start <project>` for full stack (next + terminal-ws + direct-terminal-ws).
> Or start manually — see "Manual Dashboard Start" below.

### Review & Verify

```bash
ao review-check                   # check all projects for PR review comments
ao review-check ao-dashboard      # specific project
ao review-check --dry-run         # preview only

ao verify <issue-number>          # mark issue as verified on staging
ao verify <issue-number> --fail   # mark as failed
ao verify <issue-number> -c "Custom comment"
ao verify --list                  # list all merged-unverified issues
ao verify <issue> -p ao-dashboard # specify project
```

### Maintenance

```bash
ao doctor                         # health check (env, runtime, install)
ao doctor --fix                   # apply safe fixes
ao doctor --test-notify           # test all configured notifiers

ao update                         # fetch upstream, rebuild, smoke test
ao update --skip-smoke            # skip smoke tests
ao update --smoke-only            # only run smoke tests

ao setup openclaw                 # configure OpenClaw notifier integration
ao config-help                    # show full config schema reference
```

### Lifecycle Worker (internal)

```bash
# Usually auto-started by `ao start`. Manual start:
ao lifecycle-worker ao-dashboard --interval-ms 30000
```

Check if running:
```bash
ps aux | grep 'lifecycle-worker'
```

### Terminal (open sessions in tabs)

```bash
ao open <session-id>              # open session in terminal
ao open ao-dashboard              # open all sessions for project
ao open all                       # open everything
ao open <session-id> --new-window # open in new terminal window
```

## Dashboard Architecture (3 processes)

When started via `ao start` (dev mode), dashboard runs **3 concurrent processes**:

| Process | Script | Port | Purpose |
|---------|--------|------|---------|
| Next.js | `next dev -p ${PORT}` | 3100 | UI + API routes |
| terminal-websocket | `tsx watch server/terminal-websocket.ts` | 14800 (auto) | Legacy terminal WS |
| direct-terminal-ws | `tsx watch server/direct-terminal-ws.ts` | 14801 | Direct terminal WS (**required for DirectTerminal**) |

**`ao start` in dev mode** detects `server/` directory exists → runs `pnpm run dev` → concurrently starts all 3.

**`ao dashboard` standalone** only runs `npx next dev` → **missing WS servers** → terminal broken.

### Manual Dashboard Start (when `ao start` can't be used)

When Tailscale serve conflicts with `:::PORT` binding, start manually with `-H 127.0.0.1`:

```bash
cd /home/aiadmin/tools/agent-orchestrator/packages/web

# Kill any existing processes
pkill -f 'next.*dev.*3100' 2>/dev/null
pkill -f 'tsx.*terminal' 2>/dev/null

# Start all 3 with localhost binding (avoids Tailscale EADDRINUSE)
DIRECT_TERMINAL_PORT=14801 nohup npx concurrently \
  "npx next dev -p 3100 -H 127.0.0.1" \
  "npx tsx watch server/terminal-websocket.ts" \
  "DIRECT_TERMINAL_PORT=14801 npx tsx watch server/direct-terminal-ws.ts" \
  --names "next,terminal,direct-terminal" \
  > /tmp/ao-dash-full.log 2>&1 &
```

**Verify all 3 ports:**
```bash
ss -tlnp | grep -E '3100|14800|14801'
curl -s http://127.0.0.1:3100/api/sessions | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'ok: {len(d.get(\"orchestrators\",[]))} orchestrators')"
```

### Tailscale Conflict

Tailscale serve binds `100.x.x.x:3100` and `[fd7a:...]:3100`. Next.js default is `:::3100` (all interfaces) → EADDRINUSE.

**Fix:** Add `-H 127.0.0.1` to next dev command. Tailscale proxy still works (proxies to `127.0.0.1:3100`).

This is needed for manual starts. When using `ao start`, the `pnpm dev` script should inherit `HOSTNAME=127.0.0.1` env — but if it doesn't, start manually.

## Config Schema (key fields)

```yaml
# agent-orchestrator.yaml
dataDir: ~/.agent-orchestrator
worktreeDir: ~/.worktrees
port: 3100                        # Dashboard port
terminalPort: 14800               # Terminal WS (optional, auto-detect)
directTerminalPort: 14801         # Direct terminal WS (optional, auto-detect)
readyThresholdMs: 300000          # 5min before "ready" → "idle"

defaults:
  runtime: tmux                   # tmux | process
  agent: claude-code              # claude-code | aider | codex | opencode
  workspace: worktree             # worktree | clone
  notifiers: [openclaw]

projects:
  <project-id>:
    name: Display Name
    repo: owner/repo
    path: /absolute/path
    defaultBranch: main
    sessionPrefix: prefix
    agentRulesFile: .agent-rules.md    # rules passed to every session
    orchestratorRules: |               # orchestrator-specific rules
    agentConfig:
      permissions: auto                # auto | manual
      model: claude-sonnet-4-20250514
    scm:
      plugin: github                   # github | gitlab
    tracker:
      plugin: github                   # github | linear | gitlab
    postCreate: ["npm install"]
    symlinks: [.env]
    decomposer:
      enabled: false
      maxDepth: 3
      requireApproval: true
    orchestratorSessionStrategy: reuse # reuse | delete | ignore | kill-previous

notifiers:
  openclaw:
    plugin: openclaw
    url: http://127.0.0.1:18789/hooks/agent
    token: <token>
    projectOwnerMap:                   # owner-first routing (our local patch)
      ao-dashboard: platon
      sokrat-core: platon
    fallbackAgentId: main

reactions:
  ci-failed:       { auto: true, action: send-to-agent, retries: 2, escalateAfter: 2 }
  changes-requested: { auto: true, action: send-to-agent, escalateAfter: 30m }
  approved-and-green: { auto: false, action: notify, priority: action }
  agent-stuck:     { threshold: 10m, action: notify, priority: urgent }

notificationRouting:
  critical: [desktop, slack]
  high: [desktop]
  low: [desktop]
```

## Failure Modes

### 1. Stale Dashboard
**Symptom:** Dashboard empty / "no orchestrator" — but `ao status` shows active sessions
**Rule:** Trust `ao status` + runtime over dashboard UI
**Fix:** Restart dashboard (see Manual Dashboard Start). Don't kill sessions based on UI alone.

### 2. EADDRINUSE on :3100
**Symptom:** `ao start` or manual start fails with EADDRINUSE
**Check:**
```bash
ss -tlnp | grep 3100
lsof -i:3100 -P -n
```
**Common cause:** Tailscale serve binding on TS IP conflicts with `:::3100`
**Fix:** Use `-H 127.0.0.1` (see Tailscale Conflict section)
**Other cause:** Previous dashboard still running → `pkill -f 'next.*3100'`

### 3. Terminal WebSocket Error in Dashboard
**Symptom:** DirectTerminal shows WebSocket error, can't connect
**Check:** `ss -tlnp | grep 14801` — is direct-terminal-ws listening?
**Cause:** Dashboard started via `ao dashboard` (no WS) or `next dev` directly
**Fix:** Restart with full 3-process stack (see Manual Dashboard Start)

### 4. False "Session Stopped"
**Reality:** Agent finishes a turn and waits for input — NOT a crash
**Check:**
```bash
tmux ls                          # session still exists?
ao status                        # still registered?
ps aux | grep claude             # process alive?
```
**Probe before killing:**
```bash
ao send <session-id> "Report current status"
```

### 5. Merged Session Still Active
**Check:** `gh pr view <number>` — confirm merged in GitHub first
**Fix:** `ao session cleanup -p <project>` (or `--dry-run` first)

### 6. Orchestrator in "stuck" / "needs_input" Status
**Normal:** Orchestrator waits for input — this is its idle state. NOT an error.
**Real stuck:** No response to `ao send` for >10min
**Fix:** `ao session kill <session>` → `ao start <project> --no-dashboard`

### 7. Lifecycle Worker Dead
**Check:** `ps aux | grep lifecycle-worker`
**Fix:** Restart project: `ao stop <project> && ao start <project> --no-dashboard`
Or manual: `ao lifecycle-worker <project> --interval-ms 30000 &`

### 8. Ghost Sessions After Service Restart
**Symptom:** `ao status` shows sessions as "unknown", tmux sessions gone
**Fix:**
```bash
ao session cleanup -p <project> --dry-run   # preview
ao session cleanup -p <project>              # clean
# Then restart orchestrators:
ao start ao-dashboard --no-dashboard
ao start sokrat-core --no-dashboard
```

### 9. Wrong Subcommand Name
**Cause:** Subcommand names change across AO versions
**Fix:** Always `ao --help` first, never trust memory

### 10. "No config found"
**Fix:** `cd /home/aiadmin/tools/agent-orchestrator && ao status`

## Updating AO

```bash
cd /home/aiadmin/tools/agent-orchestrator

# Option A: built-in update (fast-forward + rebuild + smoke)
ao update
ao update --skip-smoke

# Option B: manual (when local patches exist)
ao stop --all
git fetch origin
git rebase origin/main            # resolve conflicts in local patches
pnpm install
pnpm build
ao start ao-dashboard --no-dashboard
ao start sokrat-core --no-dashboard
# Then start dashboard manually (see above)
```

**Current local patch:** `feat(notifier-openclaw): owner-first routing via projectOwnerMap`
Must be rebased on each update. Conflict likely in `packages/plugins/notifier-openclaw/src/index.ts`.

## Delivery Protocol

### Report to Сократ
Use `sessions_send` with session key: `agent:main:telegram:group:-1003692383088:topic:121`

### Report to Юра
Use `message` tool:
```
message(action=send, accountId=archimedes, channel=telegram, target=-1003692383088, threadId=122, message="...", buttons=[])
```

### Format: 1–3 lines
1. What changed
2. Status: `PASS` / `FAIL` / `BLOCKED` / `IN_PROGRESS`
3. Next step

### Mandatory Report Moments

| Moment | Include |
|--------|---------|
| Task start | ACK + objective |
| Orchestrator start/stop | Service + PASS/FAIL |
| Session spawned | Issue # + session name |
| PR opened | PR URL + summary |
| PR merged | PR # + next step |
| Dashboard restart | Ports + verification |
| Blocked | Dominant blocker |

## Quick Verification After Any Change

```bash
cd /home/aiadmin/tools/agent-orchestrator
ao status                                    # orchestrators + sessions
tmux ls                                      # tmux alive
ss -tlnp | grep -E '3100|14800|14801'       # all 3 dashboard ports
curl -s http://127.0.0.1:3100/api/sessions | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'orchestrators: {[o[\"id\"] for o in d.get(\"orchestrators\",[])]}')
print(f'sessions: {d[\"stats\"][\"totalSessions\"]}')
"
```
