---
name: decision-gate
description: Use when progress depends on user approval, delegated timeout behavior, late replies, or an irreversible decision such as publish, deploy, destructive change, or scope lock.
---

# decision-gate

## Purpose
Normalize decision handling across all routes, including delegated timeout autonomy.

## Use for
- approvals with TTL
- delegated decisions after timeout
- late override handling
- irreversible gates (publish, deploy, destructive ops, scope lock)

## Do not use for
- routine low-risk internal handoffs
- status updates
- reversible micro-decisions

## Inputs
- gate summary (what needs a decision)
- options (2-3 concrete choices)
- risks (per option)
- default path after TTL
- reversibility flag
- requested deadline
- current contract

## Outputs
- `decision-packet.json` in task directory
- `deadline_at` (ISO-8601)
- `fallback_action` (what happens if no reply)
- `resolved_decision`
- `late_override_policy`
- entry in `decision-log.jsonl`

## decision-packet.json schema
```json
{
  "schema_version": "1.0",
  "task_id": "tsk_...",
  "decision_id": "dec_...",
  "gate_type": "approval|deploy|publish|destructive|scope_lock",
  "reversible": false,
  "ttl_seconds": 3600,
  "fallback_action": "string",
  "late_override_policy": "supersede|next_wave|discard",
  "options": [],
  "resolved_decision": null,
  "deadline_at": "ISO-8601"
}
```

## TTL policy
| gate_type | default TTL | fallback |
|-----------|-------------|---------|
| approval | 3600s (1h) | proceed with conservative default |
| deploy | 1800s (30min) | hold, alert Sokrat |
| publish | 7200s (2h) | hold, do not publish |
| destructive | 900s (15min) | abort, preserve state |
| scope_lock | 86400s (24h) | proceed with original scope |

## Late override policy
- `supersede`: user reply overrides the auto-resolved decision (allowed within 2h of resolution)
- `next_wave`: user reply queued for next task cycle
- `discard`: too late, system has already acted irreversibly

## Required procedure
1. Classify the decision by reversibility and risk.
2. Set TTL and fallback action according to policy table above.
3. Present to Юра via Sokrat: concise options + default path clearly stated.
4. Write `decision-packet.json` to task directory.
5. If no answer arrives before TTL: resolve using delegated operator rules, log as `resolution_mode: "delegated_timeout"`.
6. If late answer arrives: apply supersede/next-wave/discard policy.
7. Write resolved entry to `decision-log.jsonl`.
8. Update `status.json` next_action accordingly.

## decision-log.jsonl entry format
```json
{"decision_id":"dec_...","task_id":"tsk_...","gate_type":"deploy","resolved_by":"delegated_timeout","resolved_at":"ISO-8601","resolution_mode":"delegated_timeout","summary":"No reply in 30min — held deploy, alerted Sokrat"}
```

## Boundaries
- Must not let downstream agents negotiate directly with the user.
- Must not turn every minor uncertainty into a human gate.
- Must not block indefinitely — always has TTL + fallback.

## Handoff contract
- Resolved decisions mutate contract/state and become canonical truth for downstream steps.
- CI, deploy, publish start only after this gate resolves.

## Source: ao-v8.2 bundle
- ~/clawd/docs/ao-v8.2/03-skills/decision-gate.SKILL.md
