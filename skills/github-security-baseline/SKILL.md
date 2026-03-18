---
name: github-security-baseline
description: Add a practical GitHub security baseline to a repository. Use when a repo needs Dependabot, dependency review, CodeQL workflow coverage, and an audit of risky GitHub Actions patterns such as missing permissions or unsafe pull_request_target usage.
license: MIT
compatibility: openclaw; python3 recommended; gh optional.
metadata:
  author: OpenAI
  version: "3.0.0"
  tags:
    - github
    - security
    - dependabot
    - codeql
    - actions
---

# GitHub Security Baseline

This skill handles repository-level security hygiene.

## Read first

- `{baseDir}/references/ACTIONS_SECURITY.md`

## Workflow

### 1) Audit current state

```bash
python3 {baseDir}/scripts/security_audit.py --repo-root .
```

### 2) Scaffold missing baseline files

```bash
python3 {baseDir}/scripts/scaffold_security_baseline.py --dest .
```

The script auto-detects the repo's package ecosystem and generates a matching `dependabot.yml`.
Supported: `npm`, `pip`, `gomod`, `cargo`, `maven`, `gradle`, `bundler`, `nuget`.
Always includes `github-actions`. Use `--force` to overwrite existing files.

### 3) Review workflow permissions and triggers

Fix:
- missing `permissions`
- `write-all`
- unsafe `pull_request_target`
- missing `concurrency` where stale runs hurt

### 4) Commit and push

Keep security automation separate from deployment secrets logic.

## What this skill owns

- `.github/dependabot.yml` (ecosystem-aware, auto-generated)
- `dependency-review.yml`
- `codeql.yml` (language matrix, uncomment what's needed)
- `slither.yml` (auto-scaffolded when Solidity is detected)
- workflow security audit

## Non-negotiables

- no blind trust of PR code from forks
- no broad token permissions without reason
- no repo called managed without dependency update path
