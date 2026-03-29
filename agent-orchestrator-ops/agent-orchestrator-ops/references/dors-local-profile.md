# Dors Local Profile

## Canonical project

```bash
cd /Users/admin/projects/demerzel/services/arb-engine
```

Project ID:
- `arb-engine`

Config:
- `/Users/admin/projects/demerzel/services/arb-engine/agent-orchestrator.yaml`

## Current verified AO state

### Source of truth
- `ao status`
- runtime/tmux/process state
- GitHub state
- dashboard last

### Current dashboard port
- Configured dashboard port: `3001`
- Canonical local dashboard: `http://localhost:3001`

### Important anti-footgun
- A stale dashboard stack previously existed on `3000`
- Root cause found: `~/Library/LaunchAgents/local.ao-dashboard.plist`
- Do not trust `3000` unless explicitly reconfigured and verified

### Lifecycle worker
Current live build uses:

```bash
ao lifecycle-worker arb-engine --interval-ms 30000
```

A worker may already exist outside tmux. Verify with:

```bash
ps aux | grep 'ao lifecycle-worker arb-engine'
```

Observed live worker example:
- pid `9035`

### Orchestrator runtime
Current observed orchestrator tmux session:
- `cc86e61afd11-ae-orchestrator`

Standalone extra tmux session also present at times:
- `dmz-orchestrator`

Do not assume hashes are stable forever; discover dynamically via `ao status` and `tmux ls`.

## Canonical verification commands

```bash
ao --help
ao status
ps aux | grep 'ao lifecycle-worker arb-engine'
tmux ls
curl -s http://localhost:3001/api/sessions
```

## Current web/terminal ports
- `3001` — AO dashboard
- `14800` — terminal websocket
- `14801` — direct terminal websocket
- `3000` — treat as stale/invalid unless explicitly rebuilt and verified

## Known local pitfalls
- plain `lsof` / `netstat` may not be in PATH; use `/usr/sbin/lsof` and `/usr/sbin/netstat`
- duplicate `npm run dev` / `concurrently` trees can silently respawn stale stacks
- dashboard can be wrong while `ao status` remains correct

## Current delivery expectation
For user-impact tasks:
- status in topic:20
- short user-visible summary in topic:13
