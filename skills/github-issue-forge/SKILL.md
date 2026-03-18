
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
