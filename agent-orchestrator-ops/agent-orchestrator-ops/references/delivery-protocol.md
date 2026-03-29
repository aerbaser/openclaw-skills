# Delivery Protocol

## User-visible status

For user-impact code / merge / deploy tasks, send short visible updates:
- topic:20 — operational Dors lane
- topic:13 — user-visible summary lane

Keep each update to 1–3 lines:
1. what changed
2. status: PASS / FAIL / BLOCKED / IN_PROGRESS
3. next step (if any)

## Minimum moments to send

### Start
- acknowledge the task
- name the current blocker or objective
- include ETA

### Merge
- PR merged
- whether deploy is next or already done

### Deploy
- deployed SHA / PR
- PASS / FAIL / BLOCKED
- next verification step

### Verification
- final state
- if blocked, only the dominant blocker

## Post-merge / post-deploy notify runbook

If automation is not yet implemented:
- send manual status immediately after merge
- send manual status immediately after deploy
- send final verify result

If automation exists later, keep manual fallback when automation is degraded.

## Good examples

```text
PR #730 merged and deployed. PASS. Rechecking runtime health now.
```

```text
Binance spot loader fix in work. BLOCKED by spot→fapi misroute. ETA 45m.
```

```text
SPEC-0017 deployed and verified. PASS. No next step.
```
