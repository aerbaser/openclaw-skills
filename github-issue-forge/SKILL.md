---
name: github-issue-forge
description: Use when creating or rewriting GitHub issues from repository analysis. Inspect code, tests, docs, related issues and PRs, then produce execution-ready issues with scope, constraints, verification steps, and acceptance criteria so downstream coding agents can implement without ambiguity.
version: 1.0.0
homepage: https://github.com/ComposioHQ/agent-orchestrator
author: OpenAI
license: MIT
metadata: {"openclaw":{"emoji":"🧩","requires":{"bins":["git","gh","rg","python3"]},"homepage":"https://github.com/ComposioHQ/agent-orchestrator"}}
---

# GitHub Issue Forge

Create GitHub issues that are good enough for a coding agent to execute directly, not just good enough for a human to "understand later."

## When to use

Use this skill when the user wants to:
- create a new GitHub issue from codebase analysis
- rewrite a vague issue into an implementation-ready issue
- triage a bug, refactor, feature, migration, or CI task into a scoped issue
- check whether an issue is a duplicate, overlaps another issue/PR, or should be split
- produce issues specifically intended for downstream agent execution

## Read first

Before drafting the issue, read:
- `{baseDir}/references/ISSUE_BODY_TEMPLATE.md`
- `{baseDir}/references/ISSUE_QUALITY_RUBRIC.md`
- `{baseDir}/references/SEARCH_PATTERNS.md`

## Core workflow

1. **Scan the repository first**
   - Run `python3 {baseDir}/scripts/repo_scan.py --format pretty`.
   - If the task already names a subsystem, rerun with `--focus "<keywords>"`.
   - Extract concrete paths, commands, docs, tests, manifests, and likely touch points.

2. **Check GitHub for overlap before writing**
   - Search issues and PRs with `gh issue list --state all --search ...` and `gh pr list --state all --search ...`.
   - Do not create a new issue if an open issue or active PR already covers the same work.
   - If there is overlap, either:
     - comment on the existing issue/PR, or
     - create a narrower follow-up issue with explicit boundaries.

3. **Inspect the implementation area**
   - Read the real files, not just directory names.
   - Identify the current behavior, missing behavior, architecture constraints, and test surface.
   - Prefer exact file paths and command lines over vague descriptions.

4. **Decide the issue shape**
   - Keep one executable problem per issue.
   - Split discovery work, migrations, and follow-up cleanups into separate issues if they can be merged independently.
   - Put non-goals in the issue body so the worker does not expand scope.

5. **Draft the issue body with the template**
   - Use the exact section structure from `ISSUE_BODY_TEMPLATE.md`.
   - Make the body self-sufficient: include context the worker would otherwise need to rediscover.
   - Front-load the problem, desired outcome, affected areas, constraints, and verification.

6. **Lint the issue before posting**
   - Save draft body to a temporary markdown file.
   - Run `python3 {baseDir}/scripts/issue_lint.py --title "<title>" --body-file /tmp/issue.md --format pretty`.
   - Fix every blocking error before creating the issue.

7. **Create the issue**
   - Prefer `gh issue create --title "<title>" --body-file /tmp/issue.md`.
   - Add labels and assignee when you have enough signal.
   - If the user asked only for a draft, return the final title, labels, and body instead of posting.

## Non-negotiable rules

1. **Never post a title-only or context-light issue.**
   The issue body must contain enough information for a worker to act without asking basic follow-ups.

2. **Acceptance criteria must be testable.**
   Use checkboxes and observable outcomes. Avoid "clean up", "improve", "support", or "make better" without measurable conditions.

3. **Prefer repository-native language.**
   Mirror the codebase's naming, directories, script names, package manager, and architecture vocabulary.

4. **Show the worker where to look.**
   Always include an `Affected Areas` section with exact paths, modules, packages, or workflows.

5. **Separate facts from assumptions.**
   If something is inferred rather than confirmed, mark it explicitly as an assumption or open question.

6. **State verification commands explicitly.**
   Include the exact commands the worker should run for local validation and the expected high-level outcome.

7. **Call out scope limits.**
   A strong issue tells the agent what not to touch.

## Good labels

Use only labels that materially help routing:
- `bug`
- `enhancement`
- `refactor`
- `ci`
- `docs`
- `tech-debt`
- `blocked`
- `breaking-change`
- stack or area labels already used by the repo

## Creation pattern

```bash
python3 {baseDir}/scripts/repo_scan.py --focus "auth login session" --format pretty
gh issue list --state all --search "auth login session in:title,body sort:updated-desc"
gh pr list --state all --search "auth login session sort:updated-desc"

# Draft the body in /tmp/issue.md using the skill template, then lint it
python3 {baseDir}/scripts/issue_lint.py --title "feat: harden session refresh path" --body-file /tmp/issue.md --format pretty

gh issue create   --title "feat: harden session refresh path"   --label "enhancement,auth"   --body-file /tmp/issue.md
```

## Final check before posting

Do not create the issue until all answers are "yes":
- Is the scope atomic?
- Does the body name the real code paths?
- Are duplicates and related PRs linked?
- Are non-goals explicit?
- Are acceptance criteria testable?
- Are verification commands real for this repository?
