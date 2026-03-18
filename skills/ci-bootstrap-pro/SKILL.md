
---
name: ci-bootstrap-pro
description: Use when adding or upgrading GitHub Actions CI from the actual repository tooling so workflows are secure, fast, maintainable, and based on real install/lint/test/build commands instead of boilerplate.
license: MIT
compatibility: openclaw; works best in a checked-out repository using GitHub Actions.
metadata:
  author: OpenAI
  version: "4.0.0"
  tags:
    - ci
    - github-actions
    - devops
    - automation
    - security
---

# CI Bootstrap Pro

Build boring, correct CI.

## Trigger phrases

Activate when the user asks to:

- add CI
- fix weak or flaky CI
- standardize GitHub Actions
- add lint / typecheck / test / build gates
- harden workflow permissions
- split untrusted PR CI from privileged deployment flows

## Read this first

Always read:

- `{baseDir}/references/CI_PLAYBOOK.md`
- `{baseDir}/references/SECURITY_CHECKLIST.md`
- `{baseDir}/references/WORKFLOW_SHAPES.md`

Read command selection guidance from:

- `{baseDir}/references/STACK_COMMAND_MATRIX.md`

Use starter templates from:

- `{baseDir}/assets/workflows/`

Audit existing workflows with:

```bash
python3 {baseDir}/scripts/workflow_sanity.py --root . --format pretty
```

## Workflow

### 1) Detect the actual stack

Run:

```bash
python3 {baseDir}/scripts/ci_detect.py --format pretty
```

Read the real manifests before selecting any command.

### 2) Prefer repository-native commands only

Look first in:
- `package.json`
- `Makefile` / `justfile`
- `pyproject.toml`
- `Cargo.toml`
- `go.mod`
- `pom.xml`
- `build.gradle(.kts)`
- `*.sln` / `*.csproj`
- `Gemfile`

Do not invent commands the repo does not use.

### 3) Choose the smallest sensible workflow shape

Default fast path:
- install
- lint / format check
- typecheck / static analysis
- unit tests
- build

Split out:
- deployment
- release
- heavy matrix jobs
- slow integration / E2E
when they would otherwise pollute PR signal.

### 4) Respect trust boundaries

Use `pull_request` for untrusted incoming code.
Do not use `pull_request_target` to checkout and execute untrusted PR code.

Keep privileged publish/deploy logic out of the main PR workflow.

### 5) Start from the nearest template

Pick the closest starter from `assets/workflows/`.
Then replace placeholders with repo-real values:
- runtime version
- package manager
- install command
- validation commands

### 6) Sanity-check the final workflow

Run:

```bash
python3 {baseDir}/scripts/workflow_sanity.py --root . --format pretty
```

Fix:
- missing top-level `permissions`
- missing `concurrency`
- risky triggers
- obviously broad write permissions
- suspicious action pinning

## Non-negotiable standards

- No boilerplate commands detached from the repo.
- No write permissions unless they are actually required.
- No privileged deployment logic in the same path as untrusted PR execution.
- No matrix explosion by default.
- No noisy ceremonial jobs that do not affect merge quality.

## Verification

CI is acceptable only if all answers are yes:

- Does every command exist in this repository?
- Is `permissions` intentionally minimal?
- Does `concurrency` cancel stale runs?
- Is PR CI safe for forked contributions?
- Is caching stack-native or clearly justified?
- Can a maintainer understand the workflow in one read?

## Failure modes

If the stack is ambiguous:
- stay in audit mode,
- list candidate commands and why,
- do not fabricate a fake workflow.

If CI already exists:
- improve incrementally,
- avoid duplicate workflows with overlapping triggers.
