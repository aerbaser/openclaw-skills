# Deployment Profile System v1

## Зачем это нужно

Поддерживающие файлы для `deploy-and-observe` нельзя держать в виде единичного набора заметок под один сервер.
Это сразу делает skill непереносимым и вынуждает каждый раз переписывать:
- release policy,
- smoke checks,
- observe rules,
- rollback steps,
- release evidence.

Правильная модель — profile-driven.

## Концепция

Есть 4 слоя:

1. **Canonical skill** — `deploy-and-observe.SKILL.md`
2. **Base templates** — шаблонные playbook-файлы, общие для всех deployment classes
3. **Deployment profile** — YAML с параметрами и release semantics под конкретный тип инфраструктуры
4. **Overrides** — узкие project/environment overrides без fork-а skill-а

## Нормативная иерархия файлов

```text
03-skills/support/deploy-and-observe/
  README.md
  profile-selection-matrix.md
  extension-rules.md
  base/
    environment-policy.template.md
    smoke-checks.template.md
    rollback-playbook.template.md
    observe-window-policy.template.md
    release-evidence-schema.md
  profiles/
    single-server-systemd.yaml
    single-host-docker-compose.yaml
    kubernetes-cluster.yaml
    static-site-cdn.yaml
    serverless-edge.yaml
05-schemas/
  deployment-profile.schema.yaml
```

## Что является profile, а что override

### Это profile
- другой deploy primitive;
- другой rollback primitive;
- другой promotion model;
- другая сущность health/observe контроля;
- другой механизм публикации артефакта.

### Это override
- имена сервисов;
- URL/домены;
- порты;
- health endpoints;
- конкретные smoke commands;
- длительность observe window;
- включение или пропуск staging;
- имена unit/stack/deployment/function.

## Baseline profiles

### 1. `single-server-systemd`
Когда есть один Linux-хост, systemd units, прямой rollout и rollback через бинарь/директорию/юнит.

### 2. `single-host-docker-compose`
Когда release делается через compose stack/compose services на одном хосте.

### 3. `kubernetes-cluster`
Когда release primitive — rollout deployment/statefulset/job, rollback через revision history.

### 4. `static-site-cdn`
Когда release — публикация статических артефактов с invalidation/preview URLs и публикацией в production.

### 5. `serverless-edge`
Когда release — version/alias/function/edge deployment, а health контролируется через endpoint/invocation metrics.

## Unified release algorithm

Независимо от профиля, `deploy-and-observe` делает одно и то же:
1. Resolve profile.
2. Load base templates.
3. Apply profile and overrides.
4. Validate release guard.
5. Execute deploy primitive.
6. Execute smoke suite.
7. Observe health window.
8. Roll back first if guard fails.
9. Emit `release-evidence.json`.
10. Handoff to `finalize-outcome` and `status-synthesizer`.

## Правила расширения

- Нельзя вводить новый profile ради удобства одной команды.
- Сначала проверяется, можно ли решить задачу override-ом.
- Новый profile обязан получить хотя бы:
  - profile YAML,
  - selection rule,
  - smoke/rollback/observe examples,
  - scenario tests,
  - one shadow deployment dry run.

## Рекомендуемая проектная привязка

В каждом проекте хранить минимум:

```text
ops/deploy/profile.yaml
ops/deploy/environments/preview.override.yaml
ops/deploy/environments/prod.override.yaml
ops/deploy/smoke.custom.md
```

Если staging реально существует, добавляется `staging.override.yaml`.

## Что это даёт

- не надо переписывать supporting docs под каждый сервер;
- skill остаётся один;
- разница между инсталляциями выражается через данные, а не через новый текст;
- появление нового класса инфраструктуры не ломает остальную архитектуру.
