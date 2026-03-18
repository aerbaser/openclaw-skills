# Build Differences

## Rule: verify live CLI first

Never trust old runbooks blindly. Start with:

```bash
ao --help
ao session --help
ao review-check --help
```

## Current observed difference

Older memory/runbooks referred to:

```bash
ao lifecycle start
```

Current Dors AO build actually uses:

```bash
ao lifecycle-worker <project> --interval-ms 30000
```

If you use the wrong command, AO may look "unmonitored" even though a worker already exists.

## Agent/runtime differences

AO may run different agent plugins across projects/builds:
- Codex
- Claude
- others later

Do not hardcode assumptions about:
- orchestrator behavior loop,
- exact tmux naming,
- lifecycle command spelling,
- dashboard port,
- merge/reaction behavior.

Verify from:
1. project config (`agent-orchestrator.yaml`)
2. live `ao --help`
3. `ao status`
4. runtime/tmux/process state

## Dashboard port

The dashboard port is config-driven. Check project config before trusting a browser tab.

For current Dors arb-engine config:
- `agent-orchestrator.yaml` contains `port: 3001`

If `3000` and `3001` both exist, assume duplication/stale stack until proven otherwise.
