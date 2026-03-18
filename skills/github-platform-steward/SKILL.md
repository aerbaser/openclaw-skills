---
name: github-platform-steward
description: Orchestrate GitHub order end-to-end across a messy user or organization portfolio. Use when one DevOps agent should own repository cleanup, org defaults, repo baseline, security baseline, CI baseline, and execution-grade issue intake.
license: MIT
compatibility: openclaw; gh and python3 recommended; best with authenticated GitHub CLI access.
metadata:
  author: OpenAI
  version: "3.0.0"
  tags:
    - github
    - governance
    - platform
    - devops
    - orchestration
---

# GitHub Platform Steward

This is the top-level GitHub skill.
Use it when the request is broad and messy.

## Supported modes

Decide the mode first:

- `portfolio-cleanup`
- `org-baseline-bootstrap`
- `repo-hardening`
- `issue-intake`
- `maintenance`

Read:
- `{baseDir}/references/OPERATING_MODEL.md`
- `{baseDir}/references/REQUEST_PATTERNS.md`

## Mode routing

### 1) portfolio-cleanup

Use:
- sibling skill `github-repo-steward`
- then `github-community-health-bootstrap`
- then `github-governance-baseline`
- then `github-security-baseline`
- then `ci-bootstrap-pro`

Required output:
- inventory summary
- repo classification table
- archive/delete candidates
- `.github` baseline status
- rollout list for managed repos

### 2) org-baseline-bootstrap

Use:
- `github-community-health-bootstrap`
- `github-governance-baseline`

Goal:
create one sane baseline for all current and future repos.

### 3) repo-hardening

Use in this order:
1. `github-governance-baseline`
2. `github-security-baseline`
3. `ci-bootstrap-pro`

### 4) issue-intake

Use:
- `github-issue-forge`

### 5) maintenance

Repeatable operations:
- monthly `github-repo-steward` audit
- weekly `github-security-baseline` audit
- per-repo `ci-bootstrap-pro` only on change or drift
- `github-issue-forge` for every serious task handed to coding agents

## Execution rules

- Start in audit mode unless the user explicitly wants apply mode.
- Do not delete or archive repos silently.
- Do not call a repo “managed” unless it has an owner, baseline docs, and CI.
- Do not leave repos unclassified.

## Final response shape

Always return:
- what mode you ran
- what you changed
- what still requires admin rights or user intent
- next 10 actions
