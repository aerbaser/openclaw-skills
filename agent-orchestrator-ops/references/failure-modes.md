# Failure Modes (v0.2.2)

## 1. Stale Dashboard

**Symptom:** Dashboard empty / "no orchestrator" — but `ao status` shows active sessions
**Rule:** Trust `ao status` + runtime over dashboard UI
**Fix:** Restart dashboard (full 3-process stack). Don't kill sessions based on UI alone.

## 2. EADDRINUSE on :3100

**Symptom:** `ao start` or `pnpm dev` fails with EADDRINUSE
**Check:**
```bash
ss -tlnp | grep 3100
lsof -i:3100 -P -n
```
**Tailscale cause:** Tailscale serve binds `100.x.x.x:3100` + `[fd7a:]:3100`, conflicts with `:::3100`
**Fix:** Start next dev with `-H 127.0.0.1` (manual start) or set `HOSTNAME=127.0.0.1` env
**Other cause:** Old dashboard still running → `pkill -f 'next.*3100'`

## 3. Terminal WebSocket Error

**Symptom:** DirectTerminal in dashboard shows WebSocket error
**Check:** `ss -tlnp | grep 14801` — is direct-terminal-ws listening?
**Cause:** Dashboard started via `ao dashboard` (only starts next, not WS servers) or via bare `next dev`
**Fix:** Full 3-process start:
```bash
cd /home/aiadmin/tools/agent-orchestrator/packages/web
DIRECT_TERMINAL_PORT=14801 nohup npx concurrently \
  "npx next dev -p 3100 -H 127.0.0.1" \
  "npx tsx watch server/terminal-websocket.ts" \
  "DIRECT_TERMINAL_PORT=14801 npx tsx watch server/direct-terminal-ws.ts" \
  --names "next,terminal,direct-terminal" > /tmp/ao-dash-full.log 2>&1 &
```

## 4. False "Session Stopped"

**Reality:** Agent finishes a turn and waits — that is NOT a crash. "stuck"/"needs_input" is the idle state.
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

## 5. Merged Session Still Active

**Check:** `gh pr view <number>` — confirm merged in GitHub first
**Fix:** `ao session cleanup -p <project>` (use `--dry-run` first)

## 6. Ghost Sessions After Service Restart

**Symptom:** `ao status` shows sessions as "unknown", tmux sessions gone
**Fix:**
```bash
ao session cleanup -p <project>
ao start <project> --no-dashboard   # restart orchestrator + lifecycle
```

## 7. Lifecycle Worker Dead

**Check:** `ps aux | grep lifecycle-worker`
**Fix:** `ao stop <project> && ao start <project> --no-dashboard`
Or manual: `ao lifecycle-worker <project> --interval-ms 30000 &`

## 8. Session Stuck for >10 Minutes

**Check:** `ao send <session-id> "Report current status"`
**If no response in 5min:** `ao session kill <session-id>` → `ao spawn <issue>`
**Escalate** if respawn doesn't help.

## 9. Wrong Subcommand Name

**Cause:** Names change across versions
**Fix:** Always `ao --help` first

## 10. "No config found"

**Fix:** `cd /home/aiadmin/tools/agent-orchestrator && ao status`

## 11. Duplicate Dashboard Stacks

**Symptom:** Multiple next/tsx processes on same ports
**Check:**
```bash
ps aux | grep -E 'next.*3100|tsx.*terminal|concurrently' | grep -v grep
```
**Fix:** Kill all, start single stack:
```bash
pkill -f 'next.*dev.*3100'
pkill -f 'tsx.*terminal'
pkill -f 'concurrently.*agent-orchestrator'
# Then restart
```

## 12. Notifier Auth Failure (401)

**Symptom:** `[notifier-openclaw] rejected the auth token (HTTP 401)`
**Fix:** Check token in `agent-orchestrator.yaml` matches OpenClaw config:
```bash
grep token agent-orchestrator.yaml
cat ~/.openclaw/openclaw.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('hooks',{}).get('token','NOT SET'))"
```
Reconfigure: `ao setup openclaw`
