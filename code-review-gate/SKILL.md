---
name: code-review-gate
description: Use when a code task, issue, or implementation batch is complete and independent review is required before CI, merge, promotion, or further task execution. Part of the v8.2 pipeline gate chain for build_route and hybrid_route tasks.
---

# code-review-gate (v8.2)

## Purpose
Independent pre-CI review with structured findings and explicit verdicts. This gate is separate from Archimedes self-check — it must be performed by a different agent or Sokrat acting as reviewer.

## Activate when
- Archimedes/AO marks implementation as `REVIEW_PENDING`
- hotfix before CI on any production path
- code change after rework (returned from `IN_REWORK`)
- regression-sensitive diffs
- `build_route` or `hybrid_route` task reaching `REVIEW_PENDING` state

## Do not use for
- planning, strategy, or product decisions
- non-code artifacts (use `artifact-quality-gate`)
- nits without diff context
- issues still in EXECUTION

## Inputs (required)
- task_id (task ledger path: `~/clawd/tasks/<task_id>/`)
- diff or changed file list
- issue contract (`contract.json`)
- verification evidence (test results, smoke pass, self-check output)

## Outputs
- `review-findings.json` in the task directory
- verdict: `approve | changes_requested | blocked`
- if changes_requested: numbered rework checklist

## review-findings.json schema (v8.2 canonical)
```json
{
  "schema_version": "1.0",
  "task_id": "tsk_...",
  "issue_id": "gh_123",
  "reviewer": "sokrat | archimedes | external",
  "verdict": "approve | changes_requested | blocked",
  "findings": [
    {
      "id": "CR-001",
      "severity": "critical | major | minor",
      "file": "path/to/file.js",
      "summary": "one-line what's wrong",
      "evidence": "concrete proof (line, output, test result)",
      "required_fix": "what must change"
    }
  ],
  "rework_checklist": [],
  "reviewed_at": "ISO-8601",
  "approved_at": null
}
```

## Severity Matrix
| Severity | Meaning | Blocks merge? |
|---|---|---|
| `critical` | Correctness bug, security issue, contract violation, data loss risk | YES |
| `major` | Missing test, unsafe shortcut, non-trivial regression risk | YES |
| `minor` | Style, maintainability, sub-optimal but functional, cosmetic | NO |

## Procedure (strict order)

### Step 1 — Read contract first
```bash
cat ~/clawd/tasks/<task_id>/contract.json
cat ~/clawd/tasks/<task_id>/status.json
```
Understand: outcome_type, success_definition, required_gates, route.

### Step 2 — Review diff for spec conformance
Before style or aesthetics, check:
1. Does the code satisfy `success_definition[]` from contract?
2. Does it satisfy acceptance criteria from the issue?
3. Are there missing tests for new code paths?
4. Are there unsafe shortcuts or TODOs that block production?
5. Are there regressions in adjacent systems?
6. Is there contract drift (scope crept beyond what was contracted)?

### Step 3 — Write findings
Only actionable findings with IDs, severity, evidence, required fix.
No findings = approve.

### Step 4 — Emit verdict and log event
```bash
# Write review-findings.json to task dir
cat > ~/clawd/tasks/<task_id>/review-findings.json << 'JSON'
{...}
JSON

# Log event to task ledger
node ~/clawd/scripts/task-store.js event <task_id> REVIEW_COMPLETED \
  '{"verdict":"approve","reviewer":"sokrat","actor":"sokrat"}'

# If approve: transition to CI_PENDING
node ~/clawd/scripts/task-store.js transition <task_id> CI_PENDING \
  --actor sokrat --next_action "run CI suite"

# If changes_requested: transition to IN_REWORK
node ~/clawd/scripts/task-store.js transition <task_id> IN_REWORK \
  --actor sokrat --next_action "address review findings" \
  --blockers "CR-001: <description>"
```

### Step 5 — Post structured issue comment on GitHub
If the task has a linked GitHub issue, post findings as a structured comment:
```bash
# Build structured comment from review-findings.json
gh issue comment <issue_number> -R <owner/repo> --body "## Code Review — <task_id>

**Verdict:** changes_requested | approve | blocked
**Reviewer:** sokrat

### Findings
| ID | Severity | File | Summary | Required Fix |
|----|----------|------|---------|--------------|
| CR-001 | critical | src/foo.js | Missing null check | Add guard clause |
| CR-002 | major | src/bar.js | No test coverage | Add unit test |

### Rework Checklist
- [ ] CR-001: <required_fix>
- [ ] CR-002: <required_fix>

_Automated by code-review-gate v8.2_"
```
Skip this step if no GitHub issue is linked.

### Step 6 — Notify Archimedes if rework needed
Write to `~/.openclaw/workspace-archimedes/INBOX.md`:
```markdown
## [DATE] Review findings — <task_id>

Verdict: changes_requested

Rework checklist:
1. [CR-001] critical — <description> in <file>
   Fix: <required_fix>
2. ...

task-ledger: ~/clawd/tasks/<task_id>/review-findings.json
Expected: address all blocking/major findings, re-submit
```

Then `sessions_send(label="archimedes", message="Review returned changes_requested. Task: <task_id>. INBOX updated.")`

## Approve rules
- Approve ONLY when no blocking or major findings remain
- Minor/nit findings may be approved with a note
- `DONE` state is invalid without approve verdict in review-findings.json

## False positive handling
If a finding looks like a false positive:
- Mark with `"false_positive": true` in findings entry
- Document the reasoning in `evidence`
- Do not block merge on confirmed false positives

## Integration with task ledger
- Gate is complete when `review-findings.json` exists with a verdict
- AO may not proceed to `CI_PENDING` without this file
- Rework loop: `IN_REWORK → EXECUTION → REVIEW_PENDING → code-review-gate`

## Source
- Blueprint: ~/clawd/docs/ao-v8.2/03-skills/code-review-gate.SKILL.md
- Schemas: ~/clawd/docs/ao-v8.2/05-schemas/core-artifact-schemas.md
