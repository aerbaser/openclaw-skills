---
name: ontology
description: Typed knowledge graph for structured agent memory and composable skills. Use when creating/querying entities (Person, Project, Task, Event, Document), linking related objects, enforcing constraints, planning multi-step actions as graph transformations, or when skills need to share state. Trigger on "remember", "what do I know about", "link X to Y", "show dependencies", entity CRUD, or cross-skill data access.
---

# Ontology

A typed vocabulary + constraint system for representing knowledge as a verifiable graph.

## Core Concept

Everything is an **entity** with a **type**, **properties**, and **relations** to other entities. Every mutation is validated against type constraints before committing.

```
Entity: { id, type, properties, relations, created, updated }
Relation: { from_id, relation_type, to_id, properties }
```

## When to Use

| Trigger | Action |
|---------|--------|
| "Remember that..." | Create/update entity |
| "What do I know about X?" | Query graph |
| "Link X to Y" | Create relation |
| "Show all tasks for project Z" | Graph traversal |
| "What depends on X?" | Dependency query |
| Planning multi-step work | Model as graph transformations |
| Skill needs shared state | Read/write ontology objects |

## Core Types

```yaml
# Agents & People
Person: { name, email?, phone?, notes? }
Organization: { name, type?, members[] }

# Work
Project: { name, status, goals[], owner? }
Task: { title, status, due?, priority?, assignee?, blockers[] }
Goal: { description, target_date?, metrics[] }

# Time & Place
Event: { title, start, end?, location?, attendees[], recurrence? }
Location: { name, address?, coordinates? }

# Information
Document: { title, path?, url?, summary? }
Message: { content, sender, recipients[], thread? }
Thread: { subject, participants[], messages[] }
Note: { content, tags[], refs[] }

# Resources
Account: { service, username, credential_ref? }
Device: { name, type, identifiers[] }
Credential: { service, secret_ref }  # Never store secrets directly

# Meta
Action: { type, target, timestamp, outcome? }
Policy: { scope, rule, enforcement }
```

## Storage

Default: `memory/ontology/graph.jsonl`

```jsonl
{"op":"create","entity":{"id":"p_001","type":"Person","properties":{"name":"Alice"}}}
{"op":"create","entity":{"id":"proj_001","type":"Project","properties":{"name":"Website Redesign","status":"active"}}}
{"op":"relate","from":"proj_001","rel":"has_owner","to":"p_001"}
```

Query via scripts or direct file ops. For complex graphs, migrate to SQLite.

### Append-Only Rule

When working with existing ontology data or schema, **append/merge** changes instead of overwriting files. This preserves history and avoids clobbering prior definitions.

## Workflows

### Create Entity

```bash
python3 scripts/ontology.py create --type Person --props '{"name":"Alice","email":"alice@example.com"}'
```

### Query

```bash
python3 scripts/ontology.py query --type Task --where '{"status":"open"}'
python3 scripts/ontology.py get --id task_001
python3 scripts/ontology.py related --id proj_001 --rel has_task
```

### Link Entities

```bash
python3 scripts/ontology.py relate --from proj_001 --rel has_task --to task_001
```

### Validate

```bash
python3 scripts/ontology.py validate  # Check all constraints
```

## Constraints

Define in `memory/ontology/schema.yaml`:

```yaml
types:
  Task:
    required: [title, status]
    status_enum: [open, in_progress, blocked, done]
  
  Event:
    required: [title, start]
    validate: "end >= start if end exists"

  Credential:
    required: [service, secret_ref]
    forbidden_properties: [password, secret, token]  # Force indirection

relations:
  has_owner:
    from_types: [Project, Task]
    to_types: [Person]
    cardinality: many_to_one
  
  blocks:
    from_types: [Task]
    to_types: [Task]
    acyclic: true  # No circular dependencies
```

## Skill Contract

Skills that use ontology should declare:

```yaml
# In SKILL.md frontmatter or header
ontology:
  reads: [Task, Project, Person]
  writes: [Task, Action]
  preconditions:
    - "Task.assignee must exist"
  postconditions:
    - "Created Task has status=open"
```

## Planning as Graph Transformation

Model multi-step plans as a sequence of graph operations:

```
Plan: "Schedule team meeting and create follow-up tasks"

1. CREATE Event { title: "Team Sync", attendees: [p_001, p_002] }
2. RELATE Event -> has_project -> proj_001
3. CREATE Task { title: "Prepare agenda", assignee: p_001 }
4. RELATE Task -> for_event -> event_001
5. CREATE Task { title: "Send summary", assignee: p_001, blockers: [task_001] }
```

Each step is validated before execution. Rollback on constraint violation.

## Integration Patterns

### With Causal Inference

Log ontology mutations as causal actions:

```python
# When creating/updating entities, also log to causal action log
action = {
    "action": "create_entity",
    "domain": "ontology", 
    "context": {"type": "Task", "project": "proj_001"},
    "outcome": "created"
}
```

### Cross-Skill Communication

```python
# Email skill creates commitment
commitment = ontology.create("Commitment", {
    "source_message": msg_id,
    "description": "Send report by Friday",
    "due": "2026-01-31"
})

# Task skill picks it up
tasks = ontology.query("Commitment", {"status": "pending"})
for c in tasks:
    ontology.create("Task", {
        "title": c.description,
        "due": c.due,
        "source": c.id
    })
```

## Quick Start

```bash
# Initialize ontology storage
mkdir -p memory/ontology
touch memory/ontology/graph.jsonl

# Create schema (optional but recommended)
python3 scripts/ontology.py schema-append --data '{
  "types": {
    "Task": { "required": ["title", "status"] },
    "Project": { "required": ["name"] },
    "Person": { "required": ["name"] }
  }
}'

# Start using
python3 scripts/ontology.py create --type Person --props '{"name":"Alice"}'
python3 scripts/ontology.py list --type Person
```

## References

- `references/schema.md` — Full type definitions and constraint patterns
- `references/queries.md` — Query language and traversal examples

## Instruction Scope

Runtime instructions operate on local files (`memory/ontology/graph.jsonl` and `memory/ontology/schema.yaml`) and provide CLI usage for create/query/relate/validate; this is within scope. The skill reads/writes workspace files and will create the `memory/ontology` directory when used. Validation includes property/enum/forbidden checks, relation type/cardinality validation, acyclicity for relations marked `acyclic: true`, and Event `end >= start` checks; other higher-level constraints may still be documentation-only unless implemented in code.

---

## Pipeline v8.2 Canonical Vocabulary

> These enums are the authoritative vocabulary for all pipeline agents.
> Agents must use these values verbatim in contract.json, status.json, and events.ndjson.
> Any new route, gate, or outcome type must be added here before production use.

### Routes
- `artifact_route` — strategy doc, research, design pack, audit — no repo needed
- `build_route` — new app, new feature, repo-based implementation
- `diagnostic_route` — debug, root cause, performance analysis
- `publish_route` — blog post, Twitter thread, content publication
- `ops_route` — infra, deploy, service management
- `incident_route` — live incident, rollback, emergency fix
- `hybrid_route` — strategy + build, design + publish

### Outcome Types
- `strategy_doc` — research, analysis, strategic recommendation
- `design_pack` — UX/UI, system design, architecture
- `website_release` — website or landing page
- `app_release` — web/mobile app, service, API
- `bugfix_release` — bug fix or hotfix
- `audit_pack` — code audit, security review
- `publish_asset` — blog post, thread, content
- `ops_change` — infra change, service config
- `incident_recovery` — live incident resolution

### Delivery Modes
- `artifact_only` — research, docs, designs — no repo
- `repo_build` — code that lives in a repo
- `hybrid` — artifact + repo (design pack + implementation)
- `diagnostic` — analysis output, no deployable artifact
- `publish` — content destined for external publication
- `ops_only` — operational change, no code artifact

### Task States (v8.2 canonical)
- `INTAKE CONTEXT RESEARCH DESIGN PLANNING SETUP EXECUTION REVIEW_PENDING CI_PENDING QUALITY_GATE FINALIZING DEPLOYING OBSERVING DONE` — primary pipeline
- Terminal: `DONE FAILED SUPERSEDED CANCELLED`
- Extended: `BLOCKED WAITING_USER WAITING_AGENT CONTRACT_LOCKED IN_REWORK STUCK ROLLING_BACK`

### Required Gates by Route
- `build_route`: context-assimilation, code-review-gate, CI, finalize-outcome
- `artifact_route`: context-assimilation, artifact-quality-gate, finalize-outcome
- `publish_route`: artifact-quality-gate, finalize-outcome
- `ops_route`: decision-gate, finalize-outcome
- `incident_route`: decision-gate, finalize-outcome
- `hybrid_route`: context-assimilation, artifact-quality-gate, code-review-gate, finalize-outcome

### Approval Policies
- `delegated_timeout` — Sokrat decides after TTL (default)
- `explicit` — requires human confirmation
- `mixed` — explicit for destructive, delegated for reversible

### Gate Types (decision-gate)
- `approval` — TTL 1h, fallback: proceed conservative
- `deploy` — TTL 30min, fallback: hold
- `publish` — TTL 2h, fallback: hold
- `destructive` — TTL 15min, fallback: abort
- `scope_lock` — TTL 24h, fallback: proceed original scope

### Resolution Modes (decision-log)
- `delegated_timeout` — timer expired, Sokrat decided
- `user` — user replied explicitly
- `operator_override` — system rule applied
- `abort` — action aborted (destructive + no reply)

### Proof / Evidence Types (DONE gate)
- `url` — live URL accessible
- `test_pass` — CI/test suite green
- `artifact_file` — file exists and is valid
- `smoke_pass` — smoke test passed
- `review_approved` — code review approved
- `deploy_confirmed` — deployment confirmed active

### Risk Levels (issue contracts, decision gates)
- `low` — reversible, no user impact, internal tooling
- `medium` — limited blast radius, rollback possible within minutes
- `high` — user-facing impact, requires review gate
- `critical` — irreversible or money/security/data-loss risk, requires explicit approval

### Review Finding Severities (code-review-gate)
- `critical` — correctness bug, security issue, contract violation, data loss risk → blocks merge
- `major` — missing test, unsafe shortcut, non-trivial regression risk → blocks merge
- `minor` — style, maintainability, sub-optimal but functional, cosmetic → does not block

### Blocker Categories
- `missing_context` — need more info from user
- `waiting_agent` — delegated agent hasn't responded
- `external_dep` — third-party API/service unavailable
- `ci_failure` — CI broken
- `review_requested` — review pending
- `approval_timeout` — user hasn't responded to gate

### Synonyms → Canonical
- "strategy only" / "just research" / "analyse X" → `artifact_route` / `strategy_doc`
- "build X" / "make X" / "create X" / "implement" → `build_route` / `app_release`
- "fix bug" / "this is broken" / "hotfix" → `build_route` / `bugfix_release`
- "design" / "mockup" / "wireframe" / "UX" → `artifact_route` / `design_pack`
- "post about" / "write thread" / "publish" → `publish_route` / `publish_asset`
- "set up server" / "deploy" / "infra" → `ops_route` / `ops_change`
- "incident" / "down" / "rollback" → `incident_route` / `incident_recovery`
