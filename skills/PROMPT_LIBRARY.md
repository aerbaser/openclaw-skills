
# Prompt Library

Ниже короткие prompts, которые можно отдавать DevOps-агенту.

## Full GitHub cleanup

```text
Use github-platform-steward.
Audit my GitHub portfolio, classify every repository, identify archive/delete/template candidates, and return a phased cleanup plan. Stay in audit mode unless I explicitly ask for apply.
```

## Apply archive/delete after audit

```text
Use github-repo-steward.
Apply archive to confirmed archive candidates and delete only the explicitly approved parking repositories. Show the exact repos before execution.
```

## Bootstrap shared .github baseline

```text
Use github-community-health-bootstrap.
Create or update the public .github repository with shared community health files, issue forms, and a PR template. Use conservative wording and placeholders where owner-specific info is missing.
```

## Harden one repository

```text
Use github-platform-steward.
Harden this repository into managed state: governance baseline, security baseline, and CI. Prefer repo-native commands and keep changes minimal but production-grade.
```

## Create execution-ready issue

```text
Use github-issue-forge.
Analyze this repository and draft a GitHub issue for [feature/bug/refactor]. It must be executable by an implementation agent without follow-up questions.
```

## Build CI

```text
Use ci-bootstrap-pro.
Inspect the repository, detect the real stack, and add a secure GitHub Actions CI workflow with minimal permissions, concurrency cancellation, caching, and repository-native commands only.
```

## Sync repo labels and CODEOWNERS

```text
Use github-governance-baseline.
Normalize metadata, labels, CODEOWNERS, and ruleset target state for this repo. Do not add repo-local template overrides unless the shared .github defaults are insufficient.
```

## Add security baseline

```text
Use github-security-baseline.
Audit workflows for risky patterns, add Dependabot, dependency review, and a code scanning path that matches the repo and permissions available.
```
