# rollback-playbook.template.md

## Purpose
Шаблон rollback policy. Rollback first, diagnosis second.

## Required fields

- `rollback_unit`: {{artifact|service|stack|deployment|alias|site_version}}
- `rollback_trigger_conditions`:
  - smoke fail
  - health window fail
  - crash loop
  - release evidence incomplete
- `rollback_steps`:
  1. freeze further promotion
  2. revert to previous stable target
  3. confirm recovered version
  4. rerun minimal smoke
  5. emit rollback evidence
- `post_rollback_actions`:
  - incident note
  - attach logs/evidence
  - block redeploy until owner decision or new fix wave

## Hard rules
- rollback must be executable without writing new prose during incident;
- rollback target must exist before promotion;
- if rollback target is unknown, promotion is blocked.
