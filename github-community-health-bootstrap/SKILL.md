
---
name: github-community-health-bootstrap
description: Use when creating or upgrading a public `.github` repository that supplies default community health files, issue intake forms, support information, security contacts, and a pull request template across many repositories.
license: MIT
compatibility: openclaw; best with GitHub CLI auth and permission to create or update the target `.github` repository.
metadata:
  author: OpenAI
  version: "4.0.0"
  tags:
    - github
    - community-health
    - templates
    - governance
    - bootstrap
---

# GitHub Community Health Bootstrap

Create the shared `.github` baseline once, then stop redoing the same templates in every repo.

## Trigger phrases

Activate when the user asks to:

- create a public `.github` repository
- set default issue / PR templates
- set default contribution / support / security docs
- standardize intake across many repos
- bootstrap shared GitHub defaults

## Read this first

Always read:

- `{baseDir}/references/DEFAULT_FILE_SCOPE.md`
- `{baseDir}/references/COMMUNITY_HEALTH_CHECKLIST.md`
- `{baseDir}/references/TEMPLATE_CHOOSER.md`

Starter files live in:

- `{baseDir}/templates/dot-github/`

Renderer:

```bash
python3 {baseDir}/scripts/render_dot_github.py \
  --src {baseDir}/templates/dot-github \
  --dest /tmp/dot-github \
  --owner-name "My Org" \
  --support-url "https://example.com/support" \
  --security-email "security@example.com"
```

## Workflow

### 1) Confirm shared baseline is the right layer

Use a public `.github` repo when:
- many repos need the same contribution and support defaults,
- you want one standard intake path,
- local overrides should be rare.

### 2) Render the templates

Replace placeholders with real org/account values.
Keep missing values obvious rather than inventing fake contacts.

### 3) Create or update the `.github` repo

Target repo name:
- `.github`

Populate:
- `README.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `SUPPORT.md`
- `.github/ISSUE_TEMPLATE/*.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/pull_request_template.md`

### 4) Keep repo-local overrides rare

Override in a specific repo only if:
- the repo truly has different contributors,
- the repo needs stack-specific intake,
- the shared defaults would create bad friction.

## Non-negotiables

- Do not create repo-local copies everywhere if shared defaults are sufficient.
- Do not invent fake support or security contacts.
- Keep forms concise and operational.
- Keep the shared repo public so GitHub can use the defaults.

## Verification

The bootstrap is good only if:
- the `.github` repo is public,
- all key files exist,
- issue forms / config are in `.github/ISSUE_TEMPLATE/`,
- the PR template is in a supported location,
- placeholders were intentionally resolved or left explicit.
