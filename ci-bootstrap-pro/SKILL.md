---
name: ci-bootstrap-pro
description: Use when adding or upgrading CI in a repository. Detect the stack, choose repository-native build and test commands, and produce secure GitHub Actions workflows with minimal token permissions, concurrency control, caching, realistic validation, and clean separation between untrusted PR CI and privileged deployment flows.
version: 1.0.0
homepage: https://docs.github.com/actions
author: OpenAI
license: MIT
metadata: {"openclaw":{"emoji":"🛠️","requires":{"bins":["git","gh","rg","python3"]},"homepage":"https://docs.github.com/actions"}}
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

## Read first

Before editing workflows, read:
- `{baseDir}/references/CI_PLAYBOOK.md`
- `{baseDir}/references/SECURITY_CHECKLIST.md`

Use templates from:
- `{baseDir}/assets/workflows/`

## Core workflow

1. **Detect the stack**
   - Run `python3 {baseDir}/scripts/ci_detect.py --format pretty`.
   - Confirm the package manager, language runtime, lockfiles, workspace shape, and likely commands.
   - Read the actual manifests and scripts before choosing commands.

2. **Use repository-native commands**
   - Reuse existing commands from `package.json`, `Makefile`, `justfile`, `pyproject.toml`, `cargo`, Gradle, Maven, or dotnet solution files.
   - Prefer deterministic installs:
     - `npm ci`
     - `pnpm install --frozen-lockfile`
     - `yarn --immutable`
     - `uv sync --frozen`
     - `poetry install --no-interaction --sync`
     - language-equivalent frozen install modes

3. **Design the workflow shape**
   - Default to `push` + `pull_request` + optional `workflow_dispatch`.
   - Add top-level `permissions` with minimum needed access.
   - Add top-level `concurrency` so superseded runs are cancelled.
   - Keep fast PR gates in the default CI path.
   - Move slow integration, E2E, matrix explosion, or release work into separate workflows when needed.

4. **Choose the right template**
   - Start from the closest template in `assets/workflows/`.
   - Replace placeholders with real versions and commands from the repo.
   - Keep the workflow small and readable; split only when the repository complexity justifies it.

5. **Respect trust boundaries**
   - Do not use `pull_request_target` to build or execute untrusted pull request code.
   - Use plain `pull_request` for test/build on incoming code.
   - Keep privileged publish/deploy logic in protected branch workflows, protected environments, or separately-invoked workflows.

6. **Optimize for signal, not ceremony**
   - Run lint/typecheck/test/build only if the repo actually has them.
   - Use setup-action caching when supported.
   - Add artifacts only when they help debug failures or are part of release output.
   - Add a matrix only if the project claims multi-version or multi-OS support.

7. **Validate locally before declaring success**
   - Run the same commands outside CI when possible.
   - Check YAML structure.
   - Ensure every referenced script, file, and command exists.
   - If the repo already has CI, compare behavior and avoid duplicate or conflicting workflows.

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
   Use stack-native setup actions where available. Only pull in third-party actions when the repository needs them and the value is clear.

7. **Document why the workflow exists.**
   Use clear job names and small comments around non-obvious decisions.

## Standard build order

Default order for most repositories:
1. install dependencies
2. lint / format check
3. typecheck or static analysis
4. unit tests
5. build
6. upload debug artifacts only if useful

## Common files

Typical output files:
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml` only if the user asked for publishing/deploy
- `.github/workflows/nightly.yml` only for slow or flaky long-running suites

## Creation pattern

```bash
python3 {baseDir}/scripts/ci_detect.py --format pretty

# Read the nearest template in {baseDir}/assets/workflows/
# Render the template into .github/workflows/ci.yml
# Replace placeholders with repo-real values and commands

git diff -- .github/workflows
```

## Final check before completion

Do not stop until all answers are "yes":
- Does every command exist in this repository?
- Are permissions minimal?
- Does concurrency cancel stale runs?
- Is PR CI safe for forks?
- Is caching configured through the proper setup action when supported?
- Would a new maintainer understand this workflow in one read?
