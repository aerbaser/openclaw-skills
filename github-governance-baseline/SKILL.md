
---
name: github-governance-baseline
description: Use when a live repository needs to become a managed repository with consistent metadata, topics, README minimum, CODEOWNERS, labels, and a reusable ruleset target state.
license: MIT
compatibility: openclaw; works best in a checked-out repo with optional GitHub CLI auth for metadata and labels sync.
metadata:
  author: OpenAI
  version: "4.0.0"
  tags:
    - github
    - governance
    - codeowners
    - labels
    - rulesets
---

# GitHub Governance Baseline

Bring one live repository up to managed state.

## Trigger phrases

Activate when the user asks to:

- standardize repository governance
- add CODEOWNERS
- normalize labels
- set repo metadata and topics
- define ruleset or branch protection target state
- make the repo ready for team + agent work

## Read this first

Always read:

- `{baseDir}/references/CODEOWNERS_GUIDE.md`
- `{baseDir}/references/LABEL_TAXONOMY.md`
- `{baseDir}/references/RULESET_TARGET_STATE.md`
- `{baseDir}/references/README_MINIMUM.md`

Templates:
- `{baseDir}/templates/CODEOWNERS`
- `{baseDir}/templates/labels.json`
- `{baseDir}/templates/rulesets/repository-ruleset.json`

Helpers:
- `{baseDir}/scripts/repo_baseline_check.py`
- `{baseDir}/scripts/ruleset_payload.py`
- `{baseDir}/scripts/labels_sync.py`

## Workflow

### 1) Audit the current repo baseline

```bash
python3 {baseDir}/scripts/repo_baseline_check.py --root . --format pretty
```

### 2) Normalize metadata

Target baseline:
- description that says what the repo is for
- topics that help classify stack and purpose
- README with purpose / setup / commands / owner

### 3) Add CODEOWNERS

Use the template and then replace placeholders with real owners.
At minimum protect:
- `*`
- `.github/workflows/`
- infra / deployment paths if they exist

### 4) Sync labels

Preview or apply:

```bash
python3 {baseDir}/scripts/labels_sync.py --repo OWNER/REPO --labels-file {baseDir}/templates/labels.json
python3 {baseDir}/scripts/labels_sync.py --repo OWNER/REPO --labels-file {baseDir}/templates/labels.json --apply
```

### 5) Generate ruleset target state

```bash
python3 {baseDir}/scripts/ruleset_payload.py \
  --checks ci \
  --checks dependency-review \
  --default-branch main \
  --format pretty
```

Use the generated JSON as the source of truth for repo-level ruleset creation or import.

## Non-negotiables

- No empty or meaningless description.
- No generic label sprawl.
- No missing owner coverage for `.github/workflows/`.
- No repo-local template overrides unless the shared `.github` baseline is insufficient.
- No ruleset target state that ignores CI checks.

## Verification

Governance baseline is acceptable only if:
- repo purpose is obvious from metadata,
- README minimum exists,
- CODEOWNERS covers critical paths,
- labels are coherent,
- the ruleset target state is explicit and reviewable.
