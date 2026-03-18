
---
name: github-security-baseline
description: Use when a repository needs GitHub-native security hygiene for dependencies and workflows, including Dependabot, dependency review, code scanning or CodeQL path selection, and an audit of risky GitHub Actions patterns.
license: MIT
compatibility: openclaw; works best in a checked-out repository with optional GitHub CLI auth and repository admin rights for settings-based code scanning.
metadata:
  author: OpenAI
  version: "4.0.0"
  tags:
    - github
    - security
    - dependabot
    - codeql
    - actions
---

# GitHub Security Baseline

Add supply-chain and workflow hygiene without turning the repo into security theater.

## Trigger phrases

Activate when the user asks to:

- harden GitHub security baseline
- add Dependabot
- audit workflow security
- add dependency review
- add code scanning / CodeQL
- clean up risky GitHub Actions patterns

## Read this first

Always read:

- `{baseDir}/references/DEPENDABOT_POLICY.md`
- `{baseDir}/references/CODE_SCANNING_GUIDE.md`
- `{baseDir}/references/ACTIONS_SECURITY_AUDIT.md`
- `{baseDir}/references/SECRET_HANDLING.md`

Templates:
- `{baseDir}/templates/dependabot.yml`
- `{baseDir}/templates/dependency-review.yml`
- `{baseDir}/templates/codeql.yml`

Helpers:
- `{baseDir}/scripts/actions_audit.py`
- `{baseDir}/scripts/security_baseline_check.py`

## Workflow

### 1) Audit the current state

```bash
python3 {baseDir}/scripts/security_baseline_check.py --root . --format pretty
python3 {baseDir}/scripts/actions_audit.py --root . --format pretty
```

### 2) Add dependency hygiene

Baseline:
- `.github/dependabot.yml`
- dependency review workflow for PRs

### 3) Choose code scanning path

Preferred decision order:
1. if org/repo settings and permissions allow GitHub default setup cleanly, prefer that for low-maintenance repos
2. otherwise commit a `codeql.yml` workflow template and tune it to the languages in the repo

### 4) Fix workflow security smells

Common smells:
- missing or broad `permissions`
- unsafe `pull_request_target`
- floating third-party actions
- deploy logic mixed into PR CI

### 5) Re-audit after changes

Run the audit scripts again.

## Non-negotiables

- No `write-all`.
- No `pull_request_target` path that executes untrusted PR code.
- No fake code scanning setup claim if nothing was actually configured.
- No broad secrets exposure in normal PR CI.
- No security baseline that ignores the repo’s real languages or workflows.

## Verification

Security baseline is acceptable only if:
- Dependabot config exists or is intentionally handled elsewhere,
- dependency review exists for PRs,
- a code scanning path is explicit,
- workflow audit findings are reduced or explained,
- risky patterns are not left hidden.
