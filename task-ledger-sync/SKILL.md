---
name: task-ledger-sync
description: Keep task ledger state consistent for autonomous delivery work. Use when creating or updating task records in ~/clawd/tasks, syncing status after artifact writes, appending canonical events, or answering status from status.json instead of chat memory.
---

# Task Ledger Sync (v8.2)

## Source of truth
- Canonical path: `~/clawd/tasks/<task_id>/`
- Contract: `contract.json` (v8.2 schema)
- State: `status.json` (v8.2 schema)
- Append-only event log: `events.ndjson`
- Delegated decisions: `decision-log.jsonl`

Never treat chat history, INBOX.md, or ad-hoc notes as the source of truth when task ledger files exist.

## Primary tools
- `node ~/clawd/scripts/task-store.js create --title "..." --route build_route --outcome app_release`
- `node ~/clawd/scripts/task-store.js transition <task_id> <state> --owner sokrat --next_action "..."`
- `node ~/clawd/scripts/task-store.js event <task_id> <EVENT_TYPE> '<json>'`
- `node ~/clawd/scripts/task-store.js decision <task_id> '<json>'`
- `node ~/clawd/scripts/status-synthesizer.js list|summary|blockers|stale`

## Canonical states (v8.2)
`INTAKE → CONTEXT → RESEARCH → DESIGN → PLANNING → SETUP → EXECUTION → REVIEW_PENDING → CI_PENDING → QUALITY_GATE → FINALIZING → DEPLOYING → OBSERVING → DONE`

Terminal: `DONE | FAILED | SUPERSEDED | CANCELLED`
Extended: `BLOCKED | WAITING_USER | WAITING_AGENT | IN_REWORK | STUCK | ROLLING_BACK | CONTRACT_LOCKED`

## Canonical routes (v8.2)
`artifact_route | build_route | diagnostic_route | publish_route | ops_route | incident_route | hybrid_route`

## Canonical outcome types (v8.2)
`strategy_doc | design_pack | website_release | app_release | bugfix_release | audit_pack | publish_asset | ops_change | incident_recovery`

## contract.json fields (v8.2)
```
schema_version, task_id, title, raw_request, outcome_type, delivery_mode,
route, full_solution, approval_policy, design_approval_mode,
required_gates[], owner_map{}, success_definition[], constraints[], created_at
```

## status.json fields (v8.2)
```
schema_version, task_id, state, current_owner, current_route,
last_event_id, blockers[], retries, deadline_at, updated_at, next_action
```

## events.ndjson entry format (v8.2)
```json
{"event_id":"evt_...","event_type":"STATE_CHANGED","task_id":"tsk_...","from_state":"INTAKE","to_state":"CONTEXT","actor":"sokrat","timestamp":"ISO-8601"}
```

Event types: `STATE_CHANGED | MESSAGE_ENQUEUED | REVIEW_COMPLETED | CI_COMPLETED | DEPLOY_COMPLETED | DECISION_RESOLVED`

## decision-log.jsonl entry format (v8.2)
```json
{"decision_id":"dec_...","task_id":"tsk_...","gate_type":"approval","resolved_by":"delegated_timeout","resolved_at":"ISO-8601","resolution_mode":"delegated_timeout","summary":"..."}
```

## Workflow

### 1) Create task only once
When a new autonomous task is accepted:
1. Create task directory via `task-store.js create`
2. Ensure `contract.json` and `status.json` exist with v8.2 fields
3. Move state forward explicitly; do not mutate files silently

### 2) Sync after every material change
After any of:
- new artifact created → `event` append
- owner changed → `transition` with `--owner`
- state changed → `transition`
- blocker appeared/cleared → `transition` with `--blockers`
- delegated decision taken → `decision` command

### 3) Answer status from ledger
When asked "what is the status?":
1. `status-synthesizer.js summary <task_id>` if task known
2. otherwise `status-synthesizer.js list` / `blockers` / `stale`
3. Report from ledger, not from memory

## Rules
- `events.ndjson` is append-only — never delete entries
- `status.json` must reflect current owner and next action
- `DONE` is invalid without evidence artifacts
- `WAITING_USER` should include `deadline_at`
- Handoff without ledger update is incomplete
- Keep `sessions_send` and `INBOX.md` — Phase 1 preserves existing delivery

## Runtime workers (cron, every 1 min)
- `decision-timeout-sweeper.js` — auto-resolves expired WAITING_USER tasks
- `mailbox-pump.js` — delivers mailbox envelopes (inbox→processing→done/deadletter)

## Source
- Canonical schemas: ~/clawd/docs/ao-v8.2/05-schemas/core-artifact-schemas.md
- Architecture: ~/clawd/docs/ao-v8.2/01-architecture/pipeline-flow-v8.2-unified.md
