
---
name: github-platform-steward
description: Use when the user wants one DevOps agent to clean up GitHub, standardize repositories, bootstrap shared defaults, harden living repos, or run recurring GitHub maintenance through a single entrypoint.
license: MIT
compatibility: openclaw; designed as a master skill that routes into specialized child skills.
metadata:
  author: OpenAI
  version: "4.0.0"
  tags:
    - github
    - governance
    - devops
    - orchestration
    - portfolio
---

# GitHub Platform Steward

This is the master skill.
It should route, not pretend to be every worker skill.

## Trigger phrases

Activate when the user asks to:

- clean up GitHub
- put GitHub in order
- standardize repos
- bootstrap GitHub governance
- set up the full GitHub operating system
- let one DevOps agent own the whole GitHub toolkit
- run recurring GitHub maintenance

## Read this first

Always read:

- `{baseDir}/references/OPERATING_MODEL.md`
- `{baseDir}/references/REQUEST_PATTERNS.md`
- `{baseDir}/references/DELIVERY_FORMAT.md`

## Choose the mode first

### 1) `portfolio-cleanup`
Use when the problem is portfolio-level chaos:
- duplicated repos
- stale forks
- empty repos
- lab / parking / archive candidates
- inconsistent baseline across many repos

Primary child skill:
- `github-repo-steward`

Secondary child skills after cleanup:
- `github-community-health-bootstrap`
- `github-governance-baseline`
- `github-security-baseline`
- `ci-bootstrap-pro`

### 2) `org-baseline-bootstrap`
Use when the user needs shared defaults for an org or account.

Primary child skill:
- `github-community-health-bootstrap`

Optional follow-up:
- `github-governance-baseline`

### 3) `repo-hardening`
Use when one live repo must be upgraded into managed state.

Run in this order:
1. `github-governance-baseline`
2. `github-security-baseline`
3. `ci-bootstrap-pro`

### 4) `issue-intake`
Use when the main need is execution-grade work intake.

Primary child skill:
- `github-issue-forge`

### 5) `maintenance`
Use for recurring hygiene without redesigning everything.

Typical sequence:
1. `github-repo-steward` in audit mode
2. `github-security-baseline` audit
3. `ci-bootstrap-pro` review where needed
4. `github-issue-forge` for follow-up tasks

## Workflow

### 1) Establish scope
Determine:
- personal account vs organization
- one repo vs many repos
- audit-only vs apply mode
- whether destructive actions are allowed

### 2) Route into the narrowest useful child skill
Do not solve portfolio chaos with a repo-local skill.
Do not solve a single issue draft with the portfolio skill.

### 3) Execute child skills in order
Prefer safe sequence:
- inventory / audit
- baseline
- hardening
- issue intake

### 4) Consolidate output
Always return:
- what was inspected
- what changed
- what is still blocked
- what needs explicit approval
- next 10 actions in order

## Non-negotiables

- Audit first.
- No destructive action without explicit approval.
- No repo left unclassified in portfolio mode.
- No repo-local override when the shared `.github` baseline is enough.
- No issue drafting before repo scan when repo access exists.
- No CI boilerplate detached from the real stack.

## Completion standard

The run is acceptable only if:
- the correct mode was chosen,
- the right child skills were invoked,
- the final output is phased and prioritized,
- destructive actions are separated from safe changes.
