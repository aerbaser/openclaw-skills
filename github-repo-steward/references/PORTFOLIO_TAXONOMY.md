
# Portfolio Taxonomy

Use one class per repository.

## managed
Live repository where agents may open PRs.

Signals:
- active product or service
- non-trivial code
- should have README, CI, owners, and review rules

## template
Repository intentionally used to generate new repos.

Signals:
- template flag set
- name / topics mention template, starter, boilerplate, scaffold
- low direct feature churn, high reuse intent

## fork
Third-party fork kept intentionally.

Signals:
- `isFork`
- maybe used as patch fork, mirror, or vendor fork

## lab
Experiment, prototype, spike, playground, throwaway.

Signals:
- names like `lab`, `playground`, `poc`, `spike`, `scratch`, `demo`, `sandbox`
- narrow purpose
- low or temporary value

## archive
Historical read-only repo.

Signals:
- already archived
- explicitly retained for history or reference

## parking
Placeholder, empty repo, abandoned shell, or unclear leftover.

Signals:
- empty or near-empty
- no meaningful docs
- no recent activity
- no clear role

## Forbidden class names
Do not use:
- misc
- other
- unknown

If a repo feels ambiguous, gather more signals and force a decision.
