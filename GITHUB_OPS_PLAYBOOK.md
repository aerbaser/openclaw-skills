# GitHub Ops Playbook

This is the operating model for keeping a GitHub portfolio clean enough that coding agents can work fast without spraying chaos.

## The core principle

Do not let agents operate against an unclassified repo pool.

The portfolio should have three layers:

1. **Portfolio governance**
   - decide which repos are alive
   - archive or retire dead repos
   - set default community-health files in a public `.github` repository
   - standardize review and merge rules for repos that matter

2. **Per-repo baseline**
   - README
   - description + topics
   - CI
   - CODEOWNERS
   - PR / issue templates
   - SECURITY / CONTRIBUTING where relevant
   - branch rules or rulesets

3. **Work intake**
   - every task becomes an execution-grade issue with scope, non-goals, exact paths, and verification commands

If layer 1 is messy, layer 2 gets inconsistent.
If layer 2 is weak, layer 3 creates bad PRs.

## Recommended cadence

### Once per org/user
- Create a public `.github` repository with default `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, and baseline issue / PR templates.
- Create one or more **template repositories** for the stacks you actually use.
- Define the minimum ruleset/branch protection profile for managed repos.

### Weekly
- Review open PRs older than 7 days.
- Review repos with broken default branch CI.
- Review new forks and ad-hoc experimental repos created by agents or contractors.

### Monthly
- Run `github-repo-steward` audit mode.
- Archive obvious dead repos.
- Convert stable starter repos into templates.
- Remove duplicate playground repos and stale forks.

### Per new repo
- Start from a template when possible.
- Run `ci-bootstrap-pro`.
- Add owners and templates before the first serious PR.

### Per task
- Use `github-issue-forge`.
- Never let agents implement against vague titles and a one-line body.

## Repo classes

Use a small taxonomy. Avoid 12 categories nobody follows.

- **managed** — live repos where agents may open PRs
- **template** — source repo used to create new repos
- **fork** — third-party fork kept intentionally
- **lab** — experiment, prototype, throwaway
- **archive** — read-only historical repo
- **parking** — placeholder or empty repo; either promote or retire

Use description + topics to mark these. Do not mass-rename repos unless you have a strong reason.

## Baseline for a managed repo

Minimum:

- README with purpose, setup, commands, and owner
- CI on `push` and `pull_request`
- CODEOWNERS for critical paths and `.github/workflows`
- PR template
- issue templates
- ruleset / branch protection requiring passing checks
- Dependabot config
- repository description + topics

Recommended:

- SECURITY.md
- CONTRIBUTING.md
- Code scanning default setup where eligible
- environment protection for deployment repos

## Archive policy

Archive when all are true:

- not a canonical product repo
- no meaningful push activity for a long time
- not a required template
- not a dependency mirror you intentionally maintain
- no active PRs or open issues that still matter

Before archiving:
- close or move open issues/PRs
- update README and description so people know the repo is historical
- keep a link to the replacement repo if one exists

## Agent policy

Agents can:
- open PRs in **managed** repos
- harden CI
- create or rewrite issues
- produce audit reports

Agents should not automatically:
- archive repos
- rename repos
- transfer repos
- delete repos
- change visibility

Those actions should require an explicit user instruction after the audit report is reviewed.

## Golden rule

A chaotic GitHub portfolio is not just cosmetic debt.
It is context debt.
Every duplicate repo, abandoned fork, or undocumented skeleton repo creates false signal for the next agent.
