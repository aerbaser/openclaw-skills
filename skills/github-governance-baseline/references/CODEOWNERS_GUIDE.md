
# CODEOWNERS Guide

## Minimum coverage

At minimum:
- `*` → default owner
- `.github/workflows/` → DevOps or platform owner
- infra / deployment dirs → DevOps or platform owner
- app or service roots → responsible team

## Principles

- keep ownership understandable
- do not create 40 hyper-granular patterns nobody maintains
- ensure workflow files are owned by someone who understands CI and permissions
- prefer teams over individuals where stable teams exist

## Smells

- no owner for workflow files
- only one person owns everything in a serious repo
- stale handles that no longer exist
