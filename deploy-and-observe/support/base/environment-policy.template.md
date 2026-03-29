# environment-policy.template.md

## Purpose
Определяет environment rings, promotion rules, irreversible gates и required evidence.

## Template

- `environment_name`: {{environment_name}}
- `ring`: {{preview|staging|prod}}
- `is_optional`: {{true|false}}
- `approval_mode`: {{auto|delegated_timeout|explicit}}
- `irreversible`: {{true|false}}
- `promotion_from`: {{source_ring}}
- `rollback_target`: {{rollback_target}}
- `required_evidence`:
  - build artifact present
  - smoke pass
  - health window pass
  - reviewer gate pass if configured
  - secrets/config validation pass
- `blocked_if`:
  - open critical incident
  - unresolved critical finding
  - unknown deploy artifact
  - missing rollback target

## Notes
- `staging` можно пропускать только если профиль или override помечает его отсутствующим.
- Для current single-server setup обычно используется `preview -> prod`.
