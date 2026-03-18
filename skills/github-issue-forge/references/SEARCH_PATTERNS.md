# GitHub Search Patterns

Use these patterns with `gh` before posting a new issue.
Always search before creating — a duplicate wastes the coding agent's time and creates merge conflicts.

---

## Duplicate and overlap search

```bash
gh issue list --state all --search "auth refresh in:title,body sort:updated-desc"
gh pr list --state all --search "auth refresh sort:updated-desc"
```

## Area-focused search
Search by package, path, or subsystem naming used in the repo.

```bash
gh issue list --state all --search "packages/core auth in:title,body"
gh issue list --state all --search "session store in:title,body"
```

## Regression search
Look for previous fixes, rollbacks, or incidents.

```bash
gh issue list --state all --search "regression auth in:title,body"
gh pr list --state all --search "revert auth sort:updated-desc"
```

## CI and workflow search

```bash
gh issue list --state all --search "workflow ci actions in:title,body"
gh pr list --state all --search ".github/workflows sort:updated-desc"
```

## Local code search

```bash
# Find all references in source
rg "<keywords>" --type ts --type js --type py -l

# Check recent git history touching the area
git log --oneline --since="30 days ago" -- <path/to/area/>

# Check open PRs touching the same files
gh pr list --state open --search "<keywords>"
```

---

## Search heuristics

Prefer these query ingredients:
- subsystem name
- user-facing symptom
- core file or package name
- external system name
- architecture term used by the repo
- one narrow query first, then one broad query

Do not trust only titles. Search `in:title,body`.

---

## Decision matrix

| Situation | Action |
|-----------|--------|
| Exact duplicate exists (open) | Comment with additional context; do NOT create new issue |
| Exact duplicate exists (closed/fixed) | Verify fix is complete; if regression → create new with reference |
| Related issue exists (partial overlap) | Create new issue with explicit boundary + link to related |
| Active PR covers the work | Comment on PR instead of creating issue |
| Stale issue (>60 days, no activity) | Create fresh issue; link stale one for history |
| No overlap found | Proceed to draft |
