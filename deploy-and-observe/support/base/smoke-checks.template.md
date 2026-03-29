# smoke-checks.template.md

## Purpose
Базовый шаблон smoke suite. Проект подставляет реальные команды/URLs через override.

## Minimal categories

1. **Reachability**
   - service/process is up
   - endpoint responds

2. **Correct version/build**
   - version endpoint or build stamp matches expected release

3. **Critical path**
   - one minimal happy-path request or UI route succeeds

4. **Dependency sanity**
   - DB/cache/queue/external config reachable if required by route

5. **Error budget smoke**
   - no sudden surge of 5xx / crash / restart loop during initial observe window

## Template fields

- `smoke_suite_id`: {{name}}
- `timeout_seconds`: {{number}}
- `commands_or_checks`:
  - {{check_1}}
  - {{check_2}}
- `hard_fail_conditions`:
  - deploy unit not running
  - version mismatch
  - critical endpoint failure
- `warn_only_conditions`:
  - elevated latency without error rate change
  - non-critical route degraded
