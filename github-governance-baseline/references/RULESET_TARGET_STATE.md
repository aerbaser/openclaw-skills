
# Ruleset Target State

Repository ruleset target should usually require:

- pull request before merging to the default branch
- at least one approving review
- required status checks for the default CI path
- resolution of conversations before merge
- protection against direct pushes except for approved bypass roles or apps where justified

## Start conservative

Recommended default branch target:
- `main` or default branch
- required checks: `ci`
- require approval: yes
- require conversation resolution: yes

## Escalate only when needed
Add stricter commit, branch, or push rules when the repo actually needs them.
