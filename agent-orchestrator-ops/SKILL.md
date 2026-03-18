---
name: agent-orchestrator-ops
description: Operate, verify, diagnose, and recover Agent Orchestrator (AO) for Dors. Use when starting/stopping AO, checking whether the orchestrator is really running, validating lifecycle worker/dashboard/terminal servers, handling stale or duplicate dashboard stacks, cleaning merged ghost sessions, reconciling AO UI vs GitHub, or running user-visible delivery around merge/deploy/code tasks. Applies across Codex and Claude AO builds; always verify live CLI/build differences before acting.
---

# Agent Orchestrator Ops

Use this skill for AO operational work.

## Source of truth

Always trust these in order:
1. `ao status`
2. Live runtime/process state (`tmux`, `ps`, worker PID)
3. Session metadata / GitHub state
4. Dashboard UI/API last

Never declare “orchestrator stopped” from dashboard symptoms alone.

## Mandatory diagnostic order

Before changing anything:
1. Read `references/dors-local-profile.md` for current local paths/ports.
2. Run `ao --help` and `ao status` from the project directory.
3. Verify orchestrator tmux/runtime really exists.
4. Verify lifecycle worker command for the current build (see `references/build-differences.md`).
5. Verify dashboard/API on the configured port.
6. Only then decide whether this is:
   - real orchestrator failure,
   - stale dashboard,
   - duplicate dashboard stack,
   - stale merged session,
   - worker idle between tasks.

## Canonical workflow

### Start / verify
- Start AO from the project directory with `ao start` (or `ao start --no-dashboard` when intentionally skipping web UI).
- Immediately verify with:
  - `ao --help`
  - `ao status`
  - tmux/process checks
  - dashboard API on the configured port

### Lifecycle worker
- Do **not** assume the subcommand from memory.
- First inspect the live CLI build.
- On the current Dors build the worker is `ao lifecycle-worker <project> --interval-ms 30000`.
- A worker may already be running outside tmux; verify with `ps` before spawning another one.

### Dashboard truth model
- Dashboard is a derivative view.
- If UI and CLI disagree, trust `ao status` + runtime + GitHub.
- Duplicate dashboard stacks can create false emptiness or false “stopped” symptoms.

### Session hygiene
- For merged/closed/stale ghosts, use `ao session cleanup` only after checking GitHub/PR state.
- If a session is still active in reality, do **not** clean it up just because the UI looks wrong.

## User-visible delivery

For user-impact code/deploy tasks:
- send short status updates in topic:20,
- also send short user-visible status in topic:13,
- keep format to 1–3 lines: what changed / PASS|FAIL|BLOCKED / next step.

Read `references/delivery-protocol.md` before posting.

## References

- `references/commands.md` — canonical AO commands
- `references/build-differences.md` — build/version differences and live verification
- `references/failure-modes.md` — stale dashboard, wrong port, merged ghosts, duplicate stacks, false “stopped”
- `references/delivery-protocol.md` — topic:13/topic:20 status rules, merge/deploy notify
- `references/dors-local-profile.md` — current Dors local paths, ports, project IDs, and discovered pitfalls
