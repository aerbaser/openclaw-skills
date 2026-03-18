
# Workflow Shapes

## Shape A: Single fast path
Use when:
- one runtime,
- one platform,
- one main package,
- CI needs to stay boring.

Contents:
- checkout
- setup runtime
- install
- lint
- typecheck
- test
- build

## Shape B: Fast path + integration split
Use when:
- integration tests are slow,
- external services are required,
- PR signal should stay under control.

Files:
- `ci.yml`
- `integration.yml`

## Shape C: Release split
Use when:
- publishing or deployment exists,
- trusted refs or environments are required.

Files:
- `ci.yml`
- `release.yml`

## Shape D: Matrix
Use only when:
- the project explicitly supports multiple OS or runtime versions,
- maintainers actually care about that support,
- the added time is worth it.

Do not create a matrix because it looks advanced.
