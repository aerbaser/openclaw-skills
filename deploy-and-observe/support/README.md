# deploy-and-observe support pack

Это не отдельные skills. Это data + template layer для `deploy-and-observe`.

## Принцип

Один skill обслуживает разные типы инфраструктуры через:
- base templates;
- baseline deployment profiles;
- project/environment overrides.

## Как использовать

1. Выбрать `deployment_profile`.
2. Загрузить базовые шаблоны.
3. Наложить profile YAML.
4. Наложить project override и environment override.
5. Выполнить один и тот же release algorithm.
6. Выписать `release-evidence.json`.

## Что нельзя делать

- нельзя копировать эти файлы и переписывать под каждый проект;
- нельзя плодить профиль под каждое имя сервиса;
- нельзя менять release semantics через свободный текст в issue.

## Базовые профили

- `single-server-systemd`
- `single-host-docker-compose`
- `kubernetes-cluster`
- `static-site-cdn`
- `serverless-edge`

## Минимальная проектная структура

```text
ops/deploy/profile.yaml
ops/deploy/environments/preview.override.yaml
ops/deploy/environments/prod.override.yaml
ops/deploy/smoke.custom.md
```

Staging добавляется только если реально существует.
