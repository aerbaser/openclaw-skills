
---
name: github-repo-steward
description: Use when repositories are duplicated, abandoned, undocumented, fork-heavy, empty, or inconsistent and you need a repeatable GitHub cleanup plan with inventory, classification, archive/delete candidates, and managed-repo hardening priorities.
license: MIT
compatibility: openclaw; best with authenticated GitHub CLI access to the target user or organization.
metadata:
  author: OpenAI
  version: "4.0.0"
  tags:
    - github
    - governance
    - portfolio
    - cleanup
    - repo-hygiene
---

# GitHub Repo Steward

Use this skill when the problem is the portfolio, not one repository.

## Trigger phrases

Activate when the user asks to:

- clean up GitHub repos
- audit all repos in an account or org
- classify forks / templates / archives / empties
- identify archive / delete candidates
- create a recurring repo hygiene process
- turn GitHub chaos into a governed portfolio

## Read this first

Always read:

- `{baseDir}/references/PORTFOLIO_TAXONOMY.md`
- `{baseDir}/references/REPO_BASELINE.md`
- `{baseDir}/references/ARCHIVE_POLICY.md`
- `{baseDir}/references/REVIEW_CADENCE.md`

Read this when org-wide defaults matter:

- `{baseDir}/references/ORG_DOT_GITHUB_BASELINE.md`

## Default mode

Default to **audit mode** first.

Do not archive, delete, rename, transfer, or change visibility without explicit user approval.

## Workflow

### 1) Build the inventory

Organization / user explicitly given:

```bash
python3 {baseDir}/scripts/repo_inventory.py --owner my-org --output /tmp/repos.json --format pretty
```

Authenticated viewer by default:

```bash
python3 {baseDir}/scripts/repo_inventory.py --output /tmp/repos.json --format pretty
```

### 2) Score and classify everything

```bash
python3 {baseDir}/scripts/repo_score.py --inventory /tmp/repos.json --output /tmp/repo-score.json --format pretty
```

Every repo must end up in exactly one class:
- managed
- template
- fork
- lab
- archive
- parking

No `misc`.
No `other`.
No “unclear” bucket left unresolved.

### 3) Produce a phased action plan

For each repo recommend one primary action:
- keep as managed
- keep and harden baseline
- convert to template
- keep as intentional fork
- archive candidate
- delete candidate

### 4) Separate safe from destructive

Safe:
- classification
- baseline recommendations
- missing `.github` defaults
- hardening priorities

Approval-required:
- archive
- delete
- rename
- transfer
- visibility change

### 5) Apply only when explicitly approved

Dry-run or command preview:

```bash
python3 {baseDir}/scripts/repo_apply.py --score-file /tmp/repo-score.json --archive-candidates
```

Actual apply:

```bash
python3 {baseDir}/scripts/repo_apply.py --score-file /tmp/repo-score.json --archive-candidates --apply
python3 {baseDir}/scripts/repo_apply.py --score-file /tmp/repo-score.json --delete-candidates --apply
```

## Required output

Every audit run must end with:
- portfolio summary
- repo-by-repo classification
- top archive candidates
- top delete candidates
- top hardening candidates
- missing shared baseline items
- next 10 actions in order

## Non-negotiables

- No repo left unclassified.
- No delete in implicit mode.
- No archive without a stated reason.
- No cleanup without a written plan.
