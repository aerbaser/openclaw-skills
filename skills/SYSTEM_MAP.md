
# System Map

## Routing layer

### github-platform-steward
Входная точка для полного GitHub ops flow.

Режимы:
- `portfolio-cleanup`
- `org-baseline-bootstrap`
- `repo-hardening`
- `issue-intake`
- `maintenance`

## Deep worker skills

### github-repo-steward
Когда проблема на уровне портфеля:
- inventory
- classification
- cleanup plan
- archive/delete dry-run
- optional apply

### github-community-health-bootstrap
Когда нужен org/user-level shared baseline через public `.github` repo:
- default community health files
- issue forms / templates
- PR template
- support/security/contributing docs

### github-governance-baseline
Когда живой repo надо довести до managed state:
- description
- topics
- README minimum
- CODEOWNERS
- labels
- ruleset target state

### github-security-baseline
Когда нужно включить supply-chain и Actions security baseline:
- Dependabot
- dependency review
- code scanning / CodeQL path
- audit workflow risks

### ci-bootstrap-pro
Когда нужно сделать хороший CI:
- stack detection
- repo-native commands
- workflow templates
- sanity audit

### github-issue-forge
Когда issue должен быть execution-grade:
- repo scan
- overlap search
- split decision
- structured issue body
- lint before posting

## Recommended sequences

### Portfolio cleanup
1. `github-platform-steward`
2. `github-repo-steward`
3. `github-community-health-bootstrap`
4. `github-governance-baseline`
5. `github-security-baseline`
6. `ci-bootstrap-pro`

### New repo hardening
1. `github-governance-baseline`
2. `github-security-baseline`
3. `ci-bootstrap-pro`

### Agent-ready execution
1. `github-issue-forge`
2. implementation agent
3. PR review / merge gates from governance + CI + security baseline
