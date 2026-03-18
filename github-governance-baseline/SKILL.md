---
name: github-governance-baseline
description: Normalize live repositories into a managed baseline. Use when a repo needs metadata, topics, CODEOWNERS, labels, intake files, and a ruleset policy strong enough for multi-agent work.
license: MIT
compatibility: openclaw; gh and python3 recommended.
metadata:
  author: OpenAI
  version: "3.0.0"
  tags:
    - github
    - governance
    - labels
    - codeowners
    - repo-baseline
---

# GitHub Governance Baseline

Use this skill on repos that should stay alive.

## Read first

- `{baseDir}/references/LABEL_TAXONOMY.md`
- `{baseDir}/references/RULESET_POLICY.md`

## Workflow

### 1) Check drift

```bash
python3 {baseDir}/scripts/repo_baseline_check.py --repo-root .
```

### 2) Scaffold missing repo-local files

```bash
python3 {baseDir}/scripts/scaffold_repo_baseline.py --dest .
```

### 3) Set metadata

```bash
python3 {baseDir}/scripts/apply_repo_metadata.py --repo OWNER/REPO --description "..." --topics managed,github,ci
```

### 4) Sync labels

```bash
python3 {baseDir}/scripts/label_sync.py --repo OWNER/REPO --labels-file {baseDir}/templates/labels.json
```

### 5) Define the branch / ruleset policy

Use `{baseDir}/references/RULESET_POLICY.md` as the target contract.
Apply via GitHub UI or `gh api` if you have admin rights and a ready ruleset payload.

## What this skill owns

- description
- topics
- CODEOWNERS
- labels
- repo-local intake files when needed
- ruleset target state

## Non-negotiables

- Do not call a repo managed without CODEOWNERS.
- Do not keep label taxonomy random.
- Do not leave critical workflow paths ownerless.
