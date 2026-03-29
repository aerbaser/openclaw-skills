---
name: contract-router
description: Use when a new request arrives and the system must classify outcome type, delivery mode, route family, required gates, and contract defaults before research, planning, or execution.
---

# contract-router

## Purpose
Turn a raw ask into a canonical contract envelope that the rest of the system can trust.

## Use for
- new user requests
- ambiguous asks that may become strategy/design/build/publish/audit/ops
- selecting `artifact_only / repo_build / hybrid / diagnostic / publish / ops_only`
- building the initial question batch

## Do not use for
- research synthesis
- brainstorming
- issue authoring
- execution planning

## Inputs
- raw user request
- known org/product context
- repo presence/absence
- operator defaults
- current runtime constraints

## Outputs
- `contract.json` draft (canonical schema — see schemas section below)
- `question_batch[]`
- `required_gates[]`
- `outcome_type`
- `delivery_mode`
- `route`
- `full_solution=true`
- `missing_context[]`

## Boundaries
- Must not invent product decisions.
- Must not start research before factual context requirements are known.
- Must not collapse non-code work into GitHub issue mode by default.

## Required procedure
1. Normalize the request into outcome language, not implementation language.
2. Decide whether the result is strategy, design, build, publish, audit, ops, or hybrid.
3. Select delivery mode and route family.
4. Apply full-solution defaults and default gates.
5. Generate a minimal high-value question batch; avoid sprawling interviews.
6. Write the first canonical contract draft.
7. Create task in ledger: `node ~/clawd/scripts/task-store.js create --title "<title>" --route <route> --outcome <outcome_type>`
8. Hand contract draft to Sokrat.

## Route taxonomy
| Route | When |
|-------|------|
| `artifact_route` | strategy doc, research, design pack, audit — no repo needed |
| `build_route` | new app, new feature, repo-based implementation |
| `diagnostic_route` | debug, root cause, performance analysis |
| `publish_route` | blog post, Twitter thread, content publication |
| `ops_route` | infra, deploy, service management |
| `incident_route` | live incident, rollback, emergency fix |
| `hybrid_route` | strategy + build, design + publish |

## Outcome taxonomy
`strategy_doc | design_pack | website_release | app_release | bugfix_release | audit_pack | publish_asset | ops_change | incident_recovery`

## Delivery modes
`artifact_only | repo_build | hybrid | diagnostic | publish | ops_only`

## Default gates by route
- `build_route`: context-assimilation, code-review-gate, CI, finalize-outcome
- `artifact_route`: context-assimilation, artifact-quality-gate, finalize-outcome
- `publish_route`: artifact-quality-gate, finalize-outcome
- `ops_route`: decision-gate (if irreversible), finalize-outcome
- `incident_route`: decision-gate, finalize-outcome

## contract.json schema
```json
{
  "schema_version": "1.0",
  "task_id": "tsk_...",
  "title": "string",
  "raw_request": "string",
  "outcome_type": "<see taxonomy>",
  "delivery_mode": "<see delivery modes>",
  "route": "<see route taxonomy>",
  "full_solution": true,
  "approval_policy": "delegated_timeout|explicit|mixed",
  "design_approval_mode": "delegated|explicit",
  "required_gates": [],
  "owner_map": {},
  "success_definition": [],
  "constraints": [],
  "created_at": "ISO-8601"
}
```

## Route owner enforcement

task-store.js enforces per-state owners automatically on transition. Default owners:

| State | Default Owner |
|-------|---------------|
| INTAKE, CONTRACT_LOCKED, QUALITY_GATE, FINALIZING, DONE | sokrat |
| CONTEXT, RESEARCH | aristotle |
| DESIGN | brainstorm |
| PLANNING | platon |
| SETUP, CI_PENDING, DEPLOYING, OBSERVING, ROLLING_BACK | hephaestus |
| EXECUTION, IN_REWORK | archimedes |
| REVIEW_PENDING | code-reviewer |

To override defaults for a specific task, set `owner_map` in contract.json:
```json
"owner_map": {
  "CONTEXT": "archimedes",
  "DESIGN": "aristotle"
}
```

Priority: explicit --owner CLI arg > contract.owner_map > DEFAULT_STATE_OWNERS

## Question minimization policy
- Ask only when confidence in route/outcome is <70%
- Max 3 clarifying questions per intake
- Never ask about timelines — AO is autonomous
- Never ask about cosmetic preferences before route is locked
- Do ask: realtime vs polling, who are the users, where to host (if build_route)

## Handoff contract
- Downstream agents only consume the contract; they do not reinterpret the original ask as source of truth.
- After contract.json is written, hand to context-assimilation (if build/improve) or directly to brainstorm (if strategy/design).

## Source: ao-v8.2 bundle
- ~/clawd/docs/ao-v8.2/03-skills/contract-router.SKILL.md
- ~/clawd/docs/ao-v8.2/01-architecture/pipeline-flow-v8.2-unified.md
