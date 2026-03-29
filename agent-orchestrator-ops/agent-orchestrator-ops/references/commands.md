# AO Commands

## Run from project dir

```bash
cd /Users/admin/projects/demerzel/services/arb-engine
```

## Core

```bash
ao --help
ao status
ao start
ao start --no-dashboard
ao stop arb-engine
```

## Lifecycle / review

Check live help first:

```bash
ao lifecycle-worker --help
ao review-check arb-engine
```

Current Dors build:

```bash
ao lifecycle-worker arb-engine --interval-ms 30000
```

## Sessions

```bash
ao session ls
ao session cleanup -p arb-engine
ao session kill ae-5
ao session restore ae-5
ao session claim-pr 730 ae-5
```

## Messaging workers

```bash
ao send ae-5 "Fix the failing CI and report back"
ao send ae-orchestrator "Check all worker sessions, review open PRs, check CI. Fix failures, report status."
```

## Review / PR handling

```bash
ao review-check arb-engine
```

Then confirm with GitHub (`gh pr view`, `gh issue view`) when needed.

## Truth checks

```bash
ao status
tmux ls
ps aux | grep 'ao lifecycle-worker'
curl -s http://localhost:3001/api/sessions
```

## Cleanup discipline

Use cleanup only when GitHub/runtime confirms the session is truly terminal:

```bash
ao session cleanup -p arb-engine
```
