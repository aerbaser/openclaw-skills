# Profile selection matrix

| Profile | Use when | Deploy primitive | Rollback primitive | Typical targets |
|---|---|---|---|---|
| `single-server-systemd` | Один Linux-хост, systemd units, rollout как service restart/symlink switch/bin replace | systemd unit / artifact swap | previous symlink / previous artifact / previous unit config | app server, API server, worker host |
| `single-host-docker-compose` | Один хост, compose stack, контейнерный rollout | compose pull/up/recreate | previous image tag / previous compose state | small SaaS, internal tools |
| `kubernetes-cluster` | K8s deployment/statefulset rollout, service mesh, multiple replicas | rollout apply / deploy upgrade | rollout undo / previous revision | production clusters |
| `static-site-cdn` | Publish of static assets to hosting/CDN | upload/promote artifact | previous version pointer / alias rollback | landing pages, docs, marketing sites |
| `serverless-edge` | Functions/edge workers/versioned aliases | deploy version / alias switch | alias revert / previous version | APIs, edge handlers, event processors |

## Decision rules

1. Если есть один сервер и systemd — `single-server-systemd`.
2. Если rollout сущность — compose stack/service — `single-host-docker-compose`.
3. Если rollout сущность — K8s workload с revision history — `kubernetes-cluster`.
4. Если публикуется статический build на CDN/hosting — `static-site-cdn`.
5. Если основная release единица — function/version/alias — `serverless-edge`.

## Anti-rules

- Не создавать отдельный профиль `my-api-prod`.
- Не создавать профиль ради different hostnames.
- Не создавать профиль ради optional staging.
- Не создавать профиль ради другой smoke команды.

Это должны закрывать overrides.
