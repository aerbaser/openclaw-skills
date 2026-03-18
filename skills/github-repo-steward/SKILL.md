---
name: github-repo-steward
description: Audit, classify, and clean up a messy GitHub portfolio. Use when repositories are duplicated, empty, abandoned, fork-heavy, undocumented, or inconsistent, and you need a repeatable inventory, scoring model, cleanup plan, and optional archive/delete apply path.
license: MIT
compatibility: openclaw; gh and python3 recommended; best with authenticated GitHub CLI access.
metadata:
  author: OpenAI
  version: "3.0.0"
  tags:
    - github
    - portfolio
    - cleanup
    - governance
    - repo-hygiene
---

# GitHub Repo Steward

Use this skill when the problem is the portfolio, not one repo.

## Read first

- `{baseDir}/references/PORTFOLIO_TAXONOMY.md`
- `{baseDir}/references/ARCHIVE_POLICY.md`
- `{baseDir}/references/REPO_BASELINE.md`

Read when setting org-wide defaults:
- `{baseDir}/references/ORG_DOT_GITHUB_BASELINE.md`

Read when defining recurring governance:
- `{baseDir}/references/REVIEW_CADENCE.md`

## Operating mode

Default: audit only.

Apply mode exists, but destructive actions stay off unless explicitly requested.

## Workflow

### 1) Build inventory

Personal account:
```bash
python3 {baseDir}/scripts/repo_inventory.py --owner YOUR_HANDLE --format markdown --out /tmp/repo_inventory.json
```

Org:
```bash
python3 {baseDir}/scripts/repo_inventory.py --owner YOUR_ORG --format markdown --out /tmp/repo_inventory.json
```

### 2) Score and classify

```bash
python3 {baseDir}/scripts/repo_score.py --inventory /tmp/repo_inventory.json --format markdown --out /tmp/repo_plan.csv
```

### 3) Review the plan

Every repo must end up in one class:
- managed
- template
- fork
- lab
- archive
- parking

Every repo must have one recommended action:
- keep_managed
- harden_baseline
- convert_to_template
- keep_fork
- archive_candidate
- delete_candidate
- promote_or_retire

### 4) Optional apply

Archive only:
```bash
python3 {baseDir}/scripts/apply_repo_actions.py --plan /tmp/repo_plan.csv --apply-archive
```

Archive and delete:
```bash
python3 {baseDir}/scripts/apply_repo_actions.py --plan /tmp/repo_plan.csv --apply-archive --apply-delete
```

## Required output

- portfolio summary
- repo-by-repo classification
- obvious archive candidates
- obvious delete candidates
- top managed repos to harden first
- missing org baseline items

## Non-negotiables

- No repo left as “misc”.
- No delete in implicit mode.
- No archive of repos with clear current value without saying why.
- No portfolio cleanup without a written plan.
