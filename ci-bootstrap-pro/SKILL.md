---
name: ci-bootstrap-pro
description: Add or upgrade GitHub Actions CI from actual repository tooling. Use when a repo needs secure, fast, maintainable CI with correct install commands, minimal token permissions, safe pull_request handling, concurrency cancellation, caching, and repository-native lint/test/build steps.
license: MIT
compatibility: openclaw; gh optional; git and python3 recommended; designed for repositories using GitHub Actions under .github/workflows.
metadata:
  author: OpenAI
  version: "3.1.0"
  tags:
    - ci
    - github-actions
    - devops
    - automation
---

# CI Bootstrap Pro

Set up CI that is fast, deterministic, secure, and boring to maintain.

## When to use

Use this skill when the user wants to:
- add CI to a new repository
- replace weak or flaky CI with production-grade GitHub Actions
- normalize CI across multiple services or packages
- add lint, typecheck, test, build, artifact, or release gates
- debug why an existing workflow is slow, unsafe, or unreliable
- add CI for Solidity / smart contracts / Hardhat / Foundry
- add CI for React / Vite / Next.js

## Read first

Before editing workflows, read:
- `{baseDir}/references/CI_PLAYBOOK.md`
- `{baseDir}/references/SECURITY_CHECKLIST.md`
- `{baseDir}/references/STACK_COMMAND_MATRIX.md` (when choosing commands)

Use starter templates from:
- `{baseDir}/assets/workflows/`

---

## Core workflow

### 1. Detect the actual stack

```bash
python3 {baseDir}/scripts/ci_detect.py --repo-root .
```

Confirm: package manager, language runtime, lockfiles, workspace shape, and likely commands.
Read the actual manifests and scripts before choosing commands.

### 2. Use repository-native commands only

Reuse existing commands from `package.json`, `Makefile`, `justfile`, `pyproject.toml`, `cargo`, Gradle, Maven, or dotnet solution files.

Prefer deterministic installs:
- `npm ci`
- `pnpm install --frozen-lockfile`
- `yarn --immutable`
- `uv sync --frozen`
- `poetry install --no-interaction --sync`

### 3. Design the workflow shape

- Default to `push` + `pull_request` + optional `workflow_dispatch`
- Add top-level `permissions` with minimum needed access
- Add top-level `concurrency` so superseded runs are cancelled
- Keep fast PR gates in the default CI path
- Move slow integration, E2E, matrix explosion, or release work into separate workflows

### 4. Choose the right template

Start from the closest template in `assets/workflows/`.
Replace placeholders with real versions and commands from the repo.
Keep the workflow small and readable; split only when repository complexity justifies it.

Templates available:
- `node-ci.yml`, `react-ci.yml`
- `python-ci.yml`
- `go-ci.yml`
- `rust-ci.yml`
- `java-maven-ci.yml`, `java-gradle-ci.yml`
- `dotnet-ci.yml`
- `ruby-ci.yml`
- `solidity-hardhat-ci.yml`, `solidity-foundry-ci.yml`

### 5. Respect trust boundaries

- Do not use `pull_request_target` to build or execute untrusted pull request code
- Use plain `pull_request` for test/build on incoming code
- Keep privileged publish/deploy logic in protected branch workflows or separately-invoked workflows

### 6. Optimize for signal, not ceremony

- Run lint/typecheck/test/build only if the repo actually has them
- Use setup-action caching when supported
- Add artifacts only when they help debug failures or are part of release output
- Add a matrix only if the project claims multi-version or multi-OS support

### 7. Validate locally before declaring success

- Run the same commands outside CI when possible
- Check YAML structure
- Ensure every referenced script, file, and command exists
- If the repo already has CI, compare behavior and avoid duplicate or conflicting workflows

---

## Non-negotiable rules

1. **The workflow must match the repo.**
   Never ship boilerplate commands that do not exist locally.

2. **Permissions start restrictive.**
   Default to read-only `contents` unless a job truly needs more.

3. **Use one fast default path first.**
   A single reliable CI workflow beats a sprawling maze of half-maintained jobs.

4. **Cancel stale runs.**
   Use concurrency so a new push replaces the old run for the same branch or PR.

5. **Separate CI from deployment.**
   Build and test untrusted code with low privilege. Publish and deploy only from trusted refs or protected environments.

6. **Prefer first-party setup actions and built-in caching paths.**
   Use stack-native setup actions where available. Only pull in third-party actions when the value is clear.

7. **Document why the workflow exists.**
   Use clear job names and small comments around non-obvious decisions.

---

## Standard build order

Default order for most repositories:
1. install dependencies
2. lint / format check
3. typecheck or static analysis
4. unit tests
5. build
6. upload debug artifacts only if useful

---

## Common output files

- `.github/workflows/ci.yml` — always
- `.github/workflows/release.yml` — only if the user asked for publishing/deploy
- `.github/workflows/nightly.yml` — only for slow or flaky long-running suites

---

## Creation pattern

```bash
# 1 — Detect stack
python3 {baseDir}/scripts/ci_detect.py --repo-root .

# 2 — Pick closest template from {baseDir}/assets/workflows/
# 3 — Render into .github/workflows/ci.yml with repo-real values

# 4 — Verify
git diff -- .github/workflows
```

---

## Final check before completion

Do not stop until all answers are "yes":
- [ ] Does every command exist in this repository?
- [ ] Are permissions minimal?
- [ ] Does concurrency cancel stale runs?
- [ ] Is PR CI safe for forks (no `pull_request_target` with untrusted code)?
- [ ] Is caching configured through the proper setup action when supported?
- [ ] Would a new maintainer understand this workflow in one read?
