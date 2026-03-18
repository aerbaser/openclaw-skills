---
name: github-issue-forge
description: Draft or rewrite GitHub issues from real repository analysis. Use when creating feature, bug, refactor, migration, CI, or tech-debt issues that an implementation agent should be able to execute directly without guessing scope, code paths, constraints, or verification commands.
license: MIT
compatibility: openclaw; gh, git, python3 recommended; works best inside a checked-out repository with local read access and optional GitHub CLI auth for issue/PR overlap search.
metadata:
  author: OpenAI
  version: "3.1.0"
  tags:
    - github
    - issues
    - triage
    - planning
    - agent-handoff
---

# GitHub Issue Forge

Create GitHub issues that are good enough for a coding agent to execute directly —
not just good enough for a human to "understand later."

## Read first

Before drafting the issue, read:
- `{baseDir}/references/ISSUE_BODY_TEMPLATE.md`
- `{baseDir}/references/ISSUE_QUALITY_RUBRIC.md`
- `{baseDir}/references/SEARCH_PATTERNS.md`

---

## Core workflow

### 1. Scan the repository first

```bash
python3 {baseDir}/scripts/repo_scan.py --repo-root . --format markdown
```

Focused scan (when the task names a subsystem):
```bash
python3 {baseDir}/scripts/repo_scan.py --repo-root . --focus "auth session refresh" --format markdown
```

Extract concrete paths, commands, docs, tests, manifests, and likely touch points.
Read the real files — not just directory names.

### 2. Check GitHub for overlap before writing

```bash
gh issue list --state all --search "auth session refresh in:title,body sort:updated-desc"
gh pr list --state all --search "auth session refresh sort:updated-desc"
```

Do not create a new issue if an open issue or active PR already covers the same work.
If there is overlap: comment on the existing issue/PR, or create a narrower follow-up with explicit boundaries.

See `{baseDir}/references/SEARCH_PATTERNS.md` for full overlap search strategy.

### 3. Inspect the implementation area

- Read the real files, not just directory names.
- Identify the current behavior, missing behavior, architecture constraints, and test surface.
- Prefer exact file paths and command lines over vague descriptions.

### 4. Decide the issue shape

- Keep one executable problem per issue.
- Split discovery work, migrations, and follow-up cleanups into separate issues if they can be merged independently.
- Put non-goals in the issue body so the worker does not expand scope.

### 5. Draft with the canonical template

Use the exact section order from `{baseDir}/references/ISSUE_BODY_TEMPLATE.md`.
Make the body self-sufficient: include context the worker would otherwise need to rediscover.
Front-load the problem, desired outcome, affected areas, constraints, and verification.

### 6. Lint before posting

```bash
python3 {baseDir}/scripts/issue_lint.py \
  --title "feat: harden session refresh path" \
  --body-file /tmp/issue.md
```

Fix every blocking error before creating the issue.

### 7. Create the issue

```bash
gh issue create \
  --title "feat: harden session refresh path" \
  --label "enhancement" \
  --body-file /tmp/issue.md
```

Add labels and assignee when you have enough signal.
If the user asked only for a draft, return the final title, labels, and body instead of posting.

---

## Creation pattern (full example)

```bash
# 1 — Scan
python3 {baseDir}/scripts/repo_scan.py --focus "auth login session" --format markdown

# 2 — Check overlap
gh issue list --state all --search "auth login session in:title,body sort:updated-desc"
gh pr list --state all --search "auth login session sort:updated-desc"

# 3 — Draft body using ISSUE_BODY_TEMPLATE.md, save to /tmp/issue.md

# 4 — Lint
python3 {baseDir}/scripts/issue_lint.py \
  --title "feat: harden session refresh path" \
  --body-file /tmp/issue.md

# 5 — Post
gh issue create \
  --title "feat: harden session refresh path" \
  --label "enhancement,auth" \
  --body-file /tmp/issue.md
```

---

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
   A strong issue tells the agent what NOT to touch.

---

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
- stack or area labels already used by the repo (check with `gh label list`)

---

## Final check before posting

Do not create the issue until all answers are "yes":
- [ ] Is the scope atomic (one merge = one problem solved)?
- [ ] Does the body name the real code paths?
- [ ] Are duplicates and related PRs linked?
- [ ] Are non-goals explicit?
- [ ] Are acceptance criteria testable (checkboxes with observable outcomes)?
- [ ] Are verification commands real for this repository (not invented)?
- [ ] Is the Agent context section filled in (complexity, model hint, target branch)?
