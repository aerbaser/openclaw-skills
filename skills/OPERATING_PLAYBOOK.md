
# GitHub Ops Operating Playbook

## Core principle

Не позволяй агентам работать поверх неразмеченного repo-пула.

Сначала:
- inventory
- classification
- baseline
- intake

Потом:
- implementation

## Portfolio taxonomy

Используй маленькую и жесткую таксономию:

- **managed** — живой repo, где агентам можно работать через PR
- **template** — исходник для новых repos
- **fork** — осознанный fork
- **lab** — эксперимент / POC / playground
- **archive** — read-only historical repo
- **parking** — пустышка / placeholder / непонятный остаток

Запрещено оставлять `misc` или `other`.
Если repo нельзя классифицировать — значит аудит сделан плохо.

## Managed repo baseline

Минимум:
- description + topics
- README с purpose / setup / commands / owner
- CI
- CODEOWNERS
- PR template
- issue templates
- dependency hygiene
- ruleset / branch protection target state

## Destructive policy

Автоматически без явного apply-флага:
- не архивировать
- не удалять
- не менять visibility
- не делать transfer
- не rename

## Cadence

### Weekly
- просмотреть старые PR
- просмотреть broken CI
- просмотреть новые forks / labs / parking repos

### Monthly
- прогнать `github-repo-steward`
- архивировать очевидный хлам после ревью
- удалять confirmed parking repos
- пересмотреть template repos

### Per repo
- governance
- security
- CI
- issue intake discipline
