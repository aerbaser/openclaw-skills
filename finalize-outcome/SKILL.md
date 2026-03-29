---
name: finalize-outcome
description: Use when the system is about to claim a task is done, deliver outputs, close a route, or hand results to the user. Verifies completion with fresh evidence.
---

# finalize-outcome

## Purpose
Make DONE evidence-backed and route-aware. No task closes without proof.

## Use for
- Final delivery of any route
- Route closure (artifact, build, publish, ops, incident)
- PR-ready or release-ready claim verification
- Asset handoff to user
- Audit delivery

## Do not use for
- Intermediate progress updates
- Speculative previews labeled as drafts
- Mid-execution status checks (use status-synthesizer)

## Inputs
- `contract.json` (route, outcome_type, success_definition, required_gates)
- `status.json` (current state, must be FINALIZING or QUALITY_PASSED)
- `quality-report.json` (must exist and verdict != fail)
- Route-specific proof artifacts
- Verification evidence
- Unresolved risks (if any)

## Outputs
- `outcome-manifest.json` in `tasks/<task_id>/`
- Proof bundle references
- User-facing delivery note
- Residual risks (non-blocking)
- Task transition to DONE

## outcome-manifest.json schema
```json
{
  "schema_version": "1.0",
  "task_id": "tsk_...",
  "route": "artifact_route|build_route|publish_route|ops_route|incident_route|hybrid_route",
  "terminal_state": "DONE",
  "outcome_type": "strategy_doc|design_pack|website_release|app_release|bugfix_release|audit_pack|publish_asset|ops_change|incident_recovery",
  "delivered_artifacts": [
    {
      "name": "string",
      "path_or_url": "string",
      "type": "document|code|config|media|report"
    }
  ],
  "proof_bundle": [
    {
      "gate": "quality-report|code-review|ci|deploy|manual",
      "verdict": "pass",
      "ref": "path or id"
    }
  ],
  "verification_evidence": [
    {
      "check": "string",
      "result": "pass|skip|n/a",
      "detail": "string"
    }
  ],
  "residual_risks": [
    {
      "risk": "string",
      "severity": "low|medium",
      "mitigation": "string"
    }
  ],
  "final_verdict": "done|done_with_followups",
  "user_summary": "string",
  "completed_at": "ISO-8601"
}
```

## Required procedure

### Step 1: Gate verification
Check that ALL required_gates from contract.json have passed:
- `quality-report.json` exists → verdict is pass or revise (not fail)
- `review-findings/` → no open critical/major findings (if build_route)
- CI status → green (if build_route)
- Deploy evidence → stable (if deploy was required)

If any required gate is missing or failed → **BLOCK completion**. Do not proceed.

### Step 2: Evidence freshness
All evidence must be from the current execution, not stale from prior attempts:
- quality-report.json `generated_at` must be after last code/artifact change
- CI results must be for current commit/branch
- Deploy health must be within stable_health_window

### Step 3: Route completion matrix

#### artifact_route
- [ ] All success_definition items addressed
- [ ] quality-report.json verdict = pass
- [ ] Deliverable pack assembled in outputs/
- [ ] User summary prepared

#### build_route
- [ ] All issues implemented and reviewed
- [ ] CI green on current commit
- [ ] Deploy to target environment (preview/staging/prod per contract)
- [ ] Smoke tests pass
- [ ] Health window observed (if prod)
- [ ] Rollback path documented
- [ ] Release evidence recorded

#### publish_route
- [ ] Content reviewed and approved
- [ ] Published to target platform
- [ ] Sanity check (live link works, formatting correct)
- [ ] Analytics/tracking configured (if specified)

#### ops_route
- [ ] Change applied
- [ ] Rollback plan documented and tested
- [ ] Health verified post-change
- [ ] No regressions detected

#### incident_route
- [ ] Service restored
- [ ] Root cause identified
- [ ] Postmortem written (or remediation task created)
- [ ] System state verified stable

### Step 4: Assemble outcome-manifest.json
- List all delivered_artifacts with paths/URLs
- Reference all gate verdicts in proof_bundle
- Include verification_evidence for each route check
- Note any residual_risks (must be non-blocking)

### Step 5: Determine final verdict
- **done**: all gates pass, all evidence fresh, no open risks
- **done_with_followups**: all gates pass, but non-blocking improvements identified → create follow-up tasks in ledger

### Step 6: Write outcome-manifest.json
Save to `tasks/<task_id>/outcome-manifest.json`.

### Step 7: Transition to DONE
```bash
node ~/clawd/scripts/task-store.js transition <task_id> DONE --actor finalize-outcome
```

### Step 8: User delivery
Prepare concise delivery note for Сократ to send to user:
```
✅ <title> — готово

Результат: <1-2 строки что сделано>
Артефакты: <список ключевых deliverables>
Где: <ссылки/пути>
Следующие шаги: <если есть non-blocking followups>
```

### Step 9: Extract lessons (§20)
Review task history and write `tasks/<task_id>/lessons.json`:
```json
{
  "schema_version": "1.0",
  "task_id": "tsk_...",
  "recurring_failures": ["description of patterns that repeated"],
  "successful_patterns": ["what worked well and should be reused"],
  "useful_conventions": ["naming, structure, process conventions discovered"],
  "reusable_fixes": ["solutions that apply beyond this task"],
  "route_specific_improvements": ["improvements for this route type"],
  "extracted_at": "ISO-8601"
}
```

Sources for extraction:
- `events.ndjson` — retry_scheduled, rollback events, rework cycles
- `decision-log.jsonl` — overrides, escalations, blocked decisions
- `review-findings/` — recurring patterns in code review
- Duration analysis — was the task faster/slower than expected?

If no meaningful lessons → still write the file with empty arrays.
Feed into `~/.openclaw/skills/self-improving-agent/` for agent learning.

### Step 10: Log completion event
```bash
node ~/clawd/scripts/task-store.js event <task_id> TASK_COMPLETED --actor finalize-outcome --detail '{"verdict":"done","artifacts_count":N}'
```

## Boundaries
- Must not allow `PR ready` to masquerade as `release ready`
- Must not declare DONE on stale evidence
- Must not skip gate verification even if "everything looks fine"
- If contract says full_solution=true and result is partial → BLOCK
- Residual risks must be severity low or medium only — critical/major risks block completion

## Handoff contract
- Status becomes DONE only after this skill succeeds
- delivery-finalizer cron checks for tasks in FINALIZING and triggers this skill
- Failed finalization → task stays in FINALIZING with blocker reason in events

## Source
- ~/clawd/docs/ao-v8.2/03-skills/finalize-outcome.SKILL.md
- ~/clawd/docs/ao-v8.2/01-architecture/pipeline-flow-v8.2-unified.md §8
- ~/clawd/docs/ao-v8.2/05-schemas/core-artifact-schemas.md §8
