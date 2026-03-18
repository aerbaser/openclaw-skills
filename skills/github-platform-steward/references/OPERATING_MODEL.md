
# Operating Model

## Principle

The platform skill does not replace domain skills.
It routes into them.

## Safe sequencing

### Portfolio cleanup
1. inventory
2. classification
3. shared baseline
4. living repo hardening
5. issue intake for follow-up work

### Repo hardening
1. governance
2. security
3. CI

### Work intake
1. scan repo
2. check duplicates
3. draft execution-ready issue

## Decision points

### Audit vs apply
Default:
- audit

Require explicit approval for:
- archive
- delete
- rename
- transfer
- visibility changes

### Shared baseline vs local override
Default:
- shared `.github` baseline

Use repo-local overrides only if:
- the repo has genuinely different contributors,
- the repo needs a different review process,
- the repo requires stack-specific issue or PR intake.

## Failure mode control

If permissions are insufficient:
- keep planning accurate,
- do not fabricate applied changes,
- return exact next commands or API paths.
