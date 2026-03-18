---
name: github-community-health-bootstrap
description: Create or refresh a public `.github` repository with default community health files and default issue/PR templates for an organization or user. Use when you need one central intake and contribution baseline for many repositories.
license: MIT
compatibility: openclaw; gh and python3 recommended.
metadata:
  author: OpenAI
  version: "3.0.0"
  tags:
    - github
    - templates
    - community-health
    - intake
    - org-baseline
---

# GitHub Community Health Bootstrap

Use this skill to create the shared `.github` repo baseline.

## Read first

- `{baseDir}/references/WHY_DOT_GITHUB.md`

## Workflow

### 1) Ensure the `.github` repository exists

Example:
```bash
gh repo create YOUR_OWNER/.github --public --description "Default community health files and templates"
```

### 2) Scaffold defaults into a local checkout

```bash
python3 {baseDir}/scripts/scaffold_dot_github.py \
  --dest /path/to/local/.github-repo \
  --owner YOUR_ORG \
  --contact-email security@example.com \
  --maintainer your-github-handle
```

The script substitutes `{{ORG}}`, `{{EMAIL}}`, `{{MAINTAINER}}` in all templates automatically.

### 3) Review generated files

Verify substitutions landed correctly. Adjust anything specific to your repo structure.

### 4) Commit and push

Use one clean PR or direct commit if this repo is bootstrap-only.

## What this skill owns

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SUPPORT.md`
- `SECURITY.md`
- issue templates
- PR template

## Default policy

Prefer Markdown issue templates by default.
Only move to issue forms if you intentionally want GitHub form-schema maintenance.

## Done means

- `.github` repo exists and is public
- defaults are committed
- repos without local overrides inherit sane intake files
