
# Search Patterns

Use GitHub search before creating a new issue when `gh` auth is available.

## Generic overlap search

```bash
gh issue list --state all --search "<keywords> in:title,body sort:updated-desc"
gh pr list --state all --search "<keywords> sort:updated-desc"
```

## Bug-oriented search terms
Search by:
- user-visible symptom
- error message
- subsystem name
- affected endpoint / workflow / command

Example:

```bash
gh issue list --state all --search "refresh token expired in:title,body sort:updated-desc"
gh pr list --state all --search "refresh token expired sort:updated-desc"
```

## Feature-oriented search terms
Search by:
- desired behavior
- product term
- domain term
- existing architecture noun

Example:

```bash
gh issue list --state all --search "session rotation in:title,body sort:updated-desc"
```

## Refactor / tech-debt search terms
Search by:
- module name
- obsolete dependency
- migration target
- performance bottleneck name

## Split detection

Consider splitting if the search reveals:
- an already-open discovery issue,
- an active implementation PR,
- a broad epic that needs a narrower executable child issue.
