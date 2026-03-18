# GitHub Search Patterns

Use these patterns with `gh` before posting a new issue.

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

## Search heuristics

Prefer these query ingredients:
- subsystem name
- user-facing symptom
- core file or package name
- external system name
- architecture term used by the repo
- one narrow query first, then one broad query

Do not trust only titles. Search `in:title,body`.
