# AO Commands (v0.2.2)

> Always run from `/home/aiadmin/tools/agent-orchestrator/`
> Always run `ao --help` first — subcommand names may change across versions.

## Core Lifecycle

```bash
ao start <project>                        # full start: orchestrator + dashboard + lifecycle
ao start <project> --no-dashboard         # orchestrator + lifecycle only
ao start <project> --no-orchestrator      # dashboard + lifecycle only
ao start <project> --rebuild              # clean .next cache before starting
ao stop <project>                         # stop all for project
ao stop --all                             # stop everything
ao status                                 # all projects + sessions
ao status -p <project>                    # filter by project
ao status --json                          # JSON output
```

## Session Management

```bash
ao session ls                             # list all sessions
ao session ls -p <project>                # filter by project
ao session attach <session>               # attach to tmux window
ao session kill <session>                 # kill + remove worktree
ao session kill <session> --keep-session  # keep mapped agent session
ao session kill <session> --purge-session # delete mapped agent session
ao session cleanup                        # kill merged/closed sessions
ao session cleanup -p <project>           # filter
ao session cleanup --dry-run              # preview
ao session restore <session>              # restore crashed session in-place
ao session claim-pr <pr> [session]        # attach existing PR to session
ao session remap <session>                # re-discover OpenCode session mapping
ao session remap <session> --force        # force fresh remap
```

## Spawn Sessions

```bash
ao spawn <issue>                          # auto-detect project from config
ao spawn <issue> --open                   # + open in terminal tab
ao spawn <issue> --agent codex            # override agent (codex|claude-code|aider|opencode)
ao spawn <issue> --claim-pr <pr>          # claim existing PR
ao spawn <issue> --decompose              # decompose issue into subtasks first
ao spawn <issue> --decompose --max-depth 2
ao spawn <issue> --assign-on-github       # assign claimed PR on GitHub
ao batch-spawn <issues...>                # multiple issues, with duplicate detection
ao batch-spawn 65 66 67 --open
```

## Communicate with Sessions

```bash
ao send <session> "message"               # send message (waits for idle first)
ao send <session> "msg" --no-wait         # don't wait for idle
ao send <session> -f review-notes.md      # send file contents
ao send <session> "msg" --timeout 120     # custom idle timeout (default 600s)
```

## Dashboard

```bash
ao dashboard                              # standalone (⚠️ no WS servers!)
ao dashboard -p 3100                      # custom port
ao dashboard --rebuild                    # clean + restart
ao dashboard --no-open                    # skip browser auto-open
```

> ⚠️ `ao dashboard` alone starts only Next.js — no terminal WebSocket servers.
> Use `ao start` for full 3-process stack.

## Review & Verify

```bash
ao review-check                           # check all projects for PR review comments
ao review-check <project>                 # specific project
ao review-check --dry-run                 # preview

ao verify <issue>                         # mark issue as verified on staging
ao verify <issue> --fail                  # mark as failed
ao verify <issue> -c "Custom comment"     # add comment
ao verify --list                          # list merged-unverified issues
ao verify <issue> -p <project>            # specify project
```

## Maintenance

```bash
ao doctor                                 # health check
ao doctor --fix                           # apply safe fixes
ao doctor --test-notify                   # test notifiers

ao update                                 # fetch upstream + rebuild + smoke test
ao update --skip-smoke                    # skip smoke tests
ao update --smoke-only                    # only run smoke tests

ao setup openclaw                         # configure OpenClaw notifier
ao config-help                            # full config schema reference
```

## Terminal

```bash
ao open <session>                         # open in terminal tab
ao open <project>                         # open all sessions for project
ao open all                               # open everything
ao open <session> --new-window            # new terminal window
```

## Lifecycle Worker (internal, auto-started by `ao start`)

```bash
ao lifecycle-worker <project> --interval-ms 30000
```

Check if running: `ps aux | grep lifecycle-worker`

## Verification (quick health check)

```bash
cd /home/aiadmin/tools/agent-orchestrator
ao status
ao session ls
tmux ls
ps aux | grep lifecycle-worker
ss -tlnp | grep -E '3100|14800|14801'
curl -s http://127.0.0.1:3100/api/sessions
```
