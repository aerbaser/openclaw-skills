
# CI Playbook

## Default target

The default CI workflow should answer one question:
Can this change merge safely?

That means:
- install is deterministic,
- fast checks run on every PR,
- failures are obvious,
- stale runs get canceled,
- permissions are narrow.

## Stack detection order

1. lockfile / package manager
2. manifest
3. existing scripts / targets
4. existing CI files
5. docs that declare supported versions

## Command selection order

Prefer:
1. explicit repo scripts / targets
2. existing documented commands
3. language-default commands only if the repo has no better signal

## Split rules

Keep in the default PR workflow:
- lint
- typecheck
- unit tests
- build

Move out:
- deploy
- publish
- release tagging
- long-running integration suites
- multi-OS or multi-version matrix unless truly needed

## Naming

Default workflow file names:
- `ci.yml`
- `integration.yml`
- `release.yml`

Do not create five nearly identical workflow files without a reason.
