# Failure Modes

## 1) Stale dashboard on wrong port

### Symptom
- dashboard shows empty sessions / no orchestrator
- `ao status` still shows active workers

### Diagnosis
- compare `ao status` with `/api/sessions`
- check configured port in `agent-orchestrator.yaml`
- check listeners on `3000/3001/14800/14801`

### Rule
Trust CLI/runtime over dashboard.

## 2) Duplicate dashboard stacks / EADDRINUSE

### Symptom
- repeated `EADDRINUSE` on 3000/3001/14800/14801
- restarting one stack seems to respawn another

### Diagnosis
- inspect parent process tree
- look for `npm run dev`, `concurrently`, LaunchAgents, detached shells
- on Dors Mac a stale LaunchAgent existed:
  - `~/Library/LaunchAgents/local.ao-dashboard.plist`

### Fix
- kill the duplicate process tree
- unload the stale LaunchAgent if present
- leave one canonical stack only

## 3) False “orchestrator stopped”

### Symptom
- UI looks idle/stale
- human thinks orchestrator stopped

### Reality
Codex/Claude orchestrator can finish a turn and wait. That is not a crash.

### Check
- tmux session exists
- `ao status` returns active sessions
- lifecycle worker exists

## 4) Merged session still active in dashboard

### Symptom
- merged PR session still appears as active/working

### Check
- GitHub PR state
- local session metadata
- `ao session cleanup -p <project>` eligibility

### Fix
Run cleanup only after verifying terminal reality.

## 5) Wrong lifecycle command from stale memory

### Symptom
- operator says lifecycle is missing
- command errors with `unknown command`

### Cause
AO build changed subcommand names.

### Fix
Run `ao --help` first. On current Dors build use `ao lifecycle-worker ...`.

## 6) Dashboard API disagrees with CLI

### Rule
If these disagree:
- `ao status`
- tmux/process state
- GitHub PR/issue state
- dashboard API/UI

Treat dashboard as suspect until reconciled.
