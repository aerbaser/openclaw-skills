---
name: artifact-quality-gate
description: Use when strategy, design, content, audit, or hybrid artifacts must be checked against a route-specific quality rubric before delivery, publication, or build handoff.
---

# artifact-quality-gate

## Purpose
Stop weak non-code outputs from being treated as complete. Every artifact must prove it meets route-specific quality standards before DONE.

## Use for
- Strategy docs, marketing plans, GTM
- Design packs, IA, UX flows, landing concepts
- Publish assets (blog, social, content packs)
- Audit reports (code, security, perf, UX, market)
- Hybrid pre-build packs (strategy+code or design+code)

## Do not use for
- Code review → use `code-review-gate`
- Deploy approvals → use `decision-gate`
- Generic proofreading without route context

## Inputs
- Artifact pack (all deliverables)
- `contract.json` (route, outcome_type, success_definition)
- Evidence from research/design phases (if relevant)

## Outputs
- `quality-report.json` in `tasks/<task_id>/`
- Per-criterion pass/fail/warning with evidence
- Blocking gaps list
- Revision brief (if verdict != pass)

## quality-report.json schema
```json
{
  "schema_version": "1.0",
  "task_id": "tsk_...",
  "route_type": "artifact|build|publish|audit|hybrid",
  "verdict": "pass|fail|revise",
  "scorecard": {
    "contract_fit": "pass|warn|fail",
    "completeness": "pass|warn|fail",
    "coherence": "pass|warn|fail",
    "handoff_readiness": "pass|warn|fail",
    "strategic_quality": "pass|warn|fail"
  },
  "criteria": [
    {
      "name": "string",
      "status": "pass|fail|warning",
      "evidence": "string"
    }
  ],
  "blocking_gaps": [
    {
      "gap_id": "QG-001",
      "area": "string",
      "description": "string",
      "severity": "critical|major|minor"
    }
  ],
  "revision_brief": [
    {
      "gap_id": "QG-001",
      "action": "string",
      "owner": "string"
    }
  ],
  "generated_at": "ISO-8601"
}
```

## Route-specific rubrics

### artifact_route (strategy, design, research)
1. **Contract fit** — outcome matches what was requested
2. **Completeness** — all success_definition items addressed
3. **Coherence** — no contradictions between sections/artifacts
4. **Actionability** — reader can act on recommendations without guessing
5. **Strategic quality** — differentiation, not generic advice
6. **Implementation readiness** — handoff to build is possible without re-research

### publish_route
1. **Contract fit** — matches requested format and audience
2. **Content quality** — no AI-slop markers, clear voice, value-dense
3. **Platform alignment** — format suits target platform (thread length, image specs, etc.)
4. **Brand coherence** — consistent with established voice/positioning
5. **CTA/purpose** — clear intent, not content for content's sake

### audit_route (diagnostic)
1. **Reproducibility** — findings can be independently verified
2. **Severity rationale** — each finding has justified severity, not arbitrary
3. **Remediation feasibility** — fixes are actionable, not vague
4. **Facts vs assumptions** — clearly separated
5. **Owner-assignable** — each remediation has a clear responsible party

### hybrid_route
Combines artifact_route + build-specific readiness checks:
1. All artifact_route criteria
2. **Spec precision** — enough detail for developer to implement without design questions
3. **Edge cases** — documented, not left implicit
4. **Data model** — defined if relevant
5. **Integration points** — external APIs, services clearly specified

## Required procedure

### Step 1: Load context
Read `contract.json` and identify route_type, outcome_type, success_definition.

### Step 2: Select rubric
Pick the rubric matching the route. For hybrid routes, merge rubrics.

### Step 3: Evaluate each criterion
Score every criterion as pass/fail/warning. Every score must have a concrete evidence string — no vague "looks good".

### Step 4: Identify blocking gaps
Separate blocking (fail) from non-blocking (warning). Assign gap IDs: QG-001, QG-002, etc.

### Step 5: Generate scorecard
Fill the 5-field scorecard (contract_fit, completeness, coherence, handoff_readiness, strategic_quality).

### Step 6: Verdict
- **pass**: zero fail criteria, zero blocking gaps
- **revise**: ≤2 blocking gaps, all fixable without re-research
- **fail**: >2 blocking gaps OR fundamental re-work needed

### Step 7: Write quality-report.json
Save to `tasks/<task_id>/quality-report.json`.

### Step 8: Handle verdict
- **pass** → transition task to FINALIZING, hand to finalize-outcome
- **revise** → write revision_brief, transition to QUALITY_REWORK, send brief to artifact owner
- **fail** → escalate to Сократ with gap summary

### Step 9: Event logging
```bash
# Log quality gate event
node ~/clawd/scripts/task-store.js event <task_id> QUALITY_GATE_COMPLETED --actor quality-gate --detail '{"verdict":"pass","gaps":0}'
```

## Boundaries
- Must not convert a failing artifact into a pass with vague caveats
- Must be route-specific, not one generic checklist for everything
- Zero blocking gaps = pass. One blocking gap = revise. Not negotiable.
- Must not evaluate code — code has its own gate (code-review-gate)

## Handoff contract
- `finalize-outcome` consumes quality-report.json; failed reports create revision loops, not silent partial completion
- DONE is impossible while quality-report.json has any `fail` criterion in a required category

## Source
- ~/clawd/docs/ao-v8.2/03-skills/artifact-quality-gate.SKILL.md
- ~/clawd/docs/ao-v8.2/01-architecture/pipeline-flow-v8.2-unified.md §7A
- ~/clawd/docs/ao-v8.2/05-schemas/core-artifact-schemas.md §6
