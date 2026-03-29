
---
name: github-issue-forge
description: Use when drafting or rewriting GitHub issues from real repository analysis so an implementation agent can execute directly without guessing scope, code paths, constraints, tests, or verification commands.
license: MIT
compatibility: openclaw; works best inside a checked-out repository with optional GitHub CLI auth for issue and PR overlap search.
metadata:
  author: OpenAI
  version: "4.0.0"
  tags:
    - github
    - issues
    - triage
    - planning
    - agent-handoff
---

# GitHub Issue Forge

Create issues that are executable, not aspirational.

## Trigger phrases

Activate when the user asks to:

- create a GitHub issue
- rewrite a vague issue
- turn repo analysis into an issue
- split work into agent-ready tasks
- de-duplicate or scope issues
- prepare bug / feature / refactor / migration / CI / tech-debt tasks for downstream execution

## Read this first

Always read:

- `{baseDir}/references/ISSUE_BODY_TEMPLATE.md`
- `{baseDir}/references/ISSUE_QUALITY_RUBRIC.md`
- `{baseDir}/references/SPLIT_DECISION_GUIDE.md`

Read this when searching overlap:

- `{baseDir}/references/SEARCH_PATTERNS.md`

## Workflow

### 1) Scan the real repo first

Run:

```bash
python3 {baseDir}/scripts/repo_scan.py --format pretty
```

If the request already points at a subsystem, rerun with focus:

```bash
python3 {baseDir}/scripts/repo_scan.py --focus "auth session refresh" --format pretty
```

Extract:
- exact file paths
- docs and ADRs
- tests and workflow touch points
- package manager and validation commands
- obvious architecture constraints

### 2) Check for overlap before drafting

If `gh` is authenticated:

```bash
gh issue list --state all --search "session refresh in:title,body sort:updated-desc"
gh pr list --state all --search "session refresh sort:updated-desc"
```

Do not create a fresh issue if an open issue or active PR already covers the same work.
Either:
- narrow the new issue, or
- attach findings to the existing thread.

### 3) Read the implementation area, not just filenames

Open the likely files.
Confirm:
- current behavior
- missing behavior
- constraints
- likely touch points
- probable verification surface

Mark anything unverified as an assumption.

### 4) Decide whether this should stay atomic

Split when:
- discovery is separate from implementation,
- migration and cleanup can merge independently,
- acceptance criteria get fuzzy,
- one part is blocked by another part.

### 5) Draft with the canonical template

Use the exact section order from `{baseDir}/references/ISSUE_BODY_TEMPLATE.md`.

Minimum required sections:
- Summary
- Problem
- Desired Outcome
- Affected Areas
- Constraints / Notes
- Non-Goals
- Acceptance Criteria
- Verification
- Related Context

### 6) Lint before posting

Save the body to a temporary file, then run:

```bash
python3 {baseDir}/scripts/issue_lint.py \
  --title "feat: harden session refresh path" \
  --body-file /tmp/issue.md \
  --format pretty
```

Fix every blocking error.

### 7) Create or return the issue

If the user wants a draft, return:
- title
- labels
- full body

If the user wants it posted:

```bash
gh issue create \
  --title "feat: harden session refresh path" \
  --body-file /tmp/issue.md
```

Add labels only when they improve routing.

## Non-negotiable standards

- Never post a title-only or context-light issue.
- Never use vague acceptance criteria.
- Always include exact code areas or modules.
- Always state non-goals.
- Always include real verification commands for this repo.
- Separate facts from assumptions.
- Keep one executable problem per issue.

## Verification

The issue is acceptable only if all answers are yes:

- Does it name exact paths or modules?
- Are acceptance criteria testable?
- Are non-goals explicit?
- Are verification commands real?
- Was duplicate / adjacent work checked when possible?
- Could another agent start implementation without basic follow-ups?

## Failure modes

If repo scan is incomplete:
- keep the issue draft-only unless explicitly asked to post,
- mark assumptions clearly.

If GitHub overlap search is unavailable:
- still draft the issue,
- note that duplicate search could not be confirmed.

---

## AO Pipeline v8.2 Extension

> This section adds AO-specific requirements on top of the base workflow above.
> When creating issues for AO execution (task_id present), apply ALL of these.

### Issue Contract Schema (AO-ready issue)

Every AO issue body must include these sections in order:

```markdown
## Summary
[1-2 sentences, outcome-focused]

## Problem / Context
[current state, why this matters]

## Desired Outcome
[concrete, measurable end state]

## Acceptance Criteria
- [ ] Criterion 1 (testable, specific)
- [ ] Criterion 2
- [ ] Criterion 3

## Verification Plan
Steps for the executing agent to verify completion:
1. `<exact command to run>`
2. Expected: `<what success looks like>`
3. Smoke test: `<URL or command>`

## Affected Areas
- `path/to/file.ts` — reason
- `path/to/other.ts` — reason

## Dependencies
- Blocked by: #<issue> (if any)
- Depends on: task_id `tsk_...` (if applicable)

## Non-Goals
- Not doing X in this issue
- Out of scope: Y

## Reviewer Handoff
After implementation, reviewer should check:
1. [specific thing to verify]
2. [second check]

## Rollback / Blast Radius
[only if relevant — what breaks if this goes wrong, how to revert]

## Constraints / Notes
- Stack: [exact tech]
- Do not change: [boundaries]
- Assumption: [anything unverified]

## task_id / contract_hash
- task_id: `tsk_...`
- contract_hash: [sha256 of contract.json, if available]
```

### Route type in issue
Include the task route in issue metadata (label or body):
- `route: build_route` / `artifact_route` / `diagnostic_route` / `publish_route` / `ops_route` / `incident_route` / `hybrid_route`

### GitHub Issue Types / Forms / Fields mapping
When the target repo has Issue Types enabled, set `type`:
- `Bug` for bugfix_release
- `Feature` for app_release, website_release
- `Task` for ops_change, strategy_doc, design_pack, audit_pack
- `Documentation` for publish_asset

When the repo has Issue Forms (`.github/ISSUE_TEMPLATE/*.yml`), use the matching form template. If no form exists, the AO Issue Contract Schema above serves as the body.

When the repo has custom Issue Fields (via Projects v2), populate:
- `Priority`: from contract approval_policy (delegated_timeout=medium, explicit=high)
- `Status`: from task state
- `Sprint`/`Milestone`: from contract if specified

### Validation rules (AO-specific, in addition to base linter)

An issue is **invalid** if any of these are missing:
- `Acceptance Criteria` with ≥1 testable checkbox
- `Verification Plan` with ≥1 concrete command
- `Affected Areas` with exact file paths
- `Non-Goals` (even if "none in this issue")

An issue is **invalid** if:
- Acceptance criteria are vague ("works correctly", "is fast")
- Verification plan has no runnable commands
- Scope covers work that could not merge independently

### One mergeable slice rule
One GitHub issue = one independently mergeable unit of work.
- Discovery tasks and implementation tasks must be separate issues
- Migration + cleanup can be one issue only if they deploy together
- When in doubt: split

### Mapping to task ledger
When creating issues for a known task:
1. Include `task_id` in issue body
2. After `gh issue create`, write issue URL to task events:
```bash
node ~/clawd/scripts/task-store.js event <task_id> ISSUE_CREATED \
  '{"issue_url":"https://github.com/org/repo/issues/N","actor":"platon"}'
```

### contract_hash propagation
When a contract.json exists:
```bash
CONTRACT_HASH=$(sha256sum ~/clawd/tasks/<task_id>/contract.json | awk '{print $1}')
```
Include in issue body under `## task_id / contract_hash`.
