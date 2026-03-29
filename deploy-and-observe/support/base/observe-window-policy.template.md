# observe-window-policy.template.md

## Purpose
Шаблон наблюдения после релиза.

## Required fields

- `observe_window_minutes`: {{number}}
- `poll_interval_seconds`: {{number}}
- `signals`:
  - service health
  - restart/crash status
  - error rate
  - latency percentile if available
  - custom business heartbeat if available
- `pass_conditions`:
  - no hard failures
  - smoke remains green
  - no abnormal restart pattern
- `fail_conditions`:
  - repeated restarts
  - sustained 5xx spike
  - version drift
  - critical business path broken
- `escalate_conditions`:
  - uncertain signal quality
  - partial telemetry
  - degraded but non-fatal state

## Rule
If fail condition triggers inside observe window, rollback first.
