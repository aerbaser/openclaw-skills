---
name: deploy-and-observe
description: Use when a release, deploy, environment promotion, smoke check, health window, rollback, or post-deploy observation step is required for a build or ops route.
---

# deploy-and-observe

## Purpose
Turn deployment from a shell command into a controlled release with evidence, rollback discipline, and profile-driven portability across different infrastructure classes.

## Use for
- Preview deploy (localhost, Tailscale)
- Production deploy
- Hotfix release
- Post-deploy smoke
- Rollback execution
- Incident stabilization
- Ops changes requiring health observation

## Do not use for
- Non-build/non-ops routes (strategy, design, publish — use artifact-quality-gate)
- Pure code review (use code-review-gate)
- Non-deployment testing

## Inputs
- `contract.json` (route, outcome_type, delivery_mode)
- Build artifact (commit SHA, branch, build output)
- Environment target (preview/staging/prod)
- Deployment profile (resolved from contract or environment class)
- Optional project/environment override
- Rollback plan
- Service/port configuration

## Profile-driven model (v8.3)
Different infrastructure = different profile, NOT rewriting the skill.

Resolve profile → load base templates → apply profile → apply overrides → execute.

Available profiles: `support/profiles/`
- `single-server-systemd` — current default (our setup)
- `single-host-docker-compose`
- `kubernetes-cluster`
- `static-site-cdn`
- `serverless-edge`

Selection: see `support/profile-selection-matrix.md`
Extension rules: see `support/extension-rules.md`
Schema: see `support/deployment-profile.schema.yaml`

## Outputs
- `release-evidence.json` in `tasks/<task_id>/`
- Environment deploy result
- Smoke check results
- Health window observation
- Rollback decision (if needed)

## release-evidence.json schema
```json
{
  "schema_version": "1.0",
  "task_id": "tsk_...",
  "environment": "preview|staging|prod",
  "topology": "single_server_tailscale|multi_env",
  "deploy_result": "success|failed|rolled_back",
  "commit_sha": "string",
  "branch": "string",
  "service_name": "string",
  "deploy_method": "systemd|docker|pm2|manual",
  "smoke_results": [
    {
      "check": "string",
      "result": "pass|fail|skip",
      "detail": "string",
      "timestamp": "ISO-8601"
    }
  ],
  "health_window": {
    "start": "ISO-8601",
    "end": "ISO-8601",
    "duration_minutes": 15,
    "checks_run": 0,
    "verdict": "pass|fail|in_progress",
    "rollback_readiness": true,
    "unresolved_warnings": [],
    "staging_used": false
  },
  "rollback_plan": {
    "method": "git_revert|service_restart|docker_rollback|manual",
    "command": "string",
    "tested": false
  },
  "rollback_ready": true,
  "recorded_at": "ISO-8601"
}
```

## Deployment topology

### single_server_tailscale (current default)
1. `preview_localhost` — localhost or Tailscale-only URL
2. `production` — same server, public or Tailscale-served

No staging. Production promotion requires:
- Extended smoke (all checks, not minimal)
- Rollback readiness verified
- Contract explicitly allows direct-to-prod

### multi_env (future)
1. `preview` → 2. `staging` → 3. `production`

## Release guard policy (embedded)

### Before any deploy
- [ ] Build passes locally
- [ ] CI green (if applicable)
- [ ] Code review gate passed (if build_route)
- [ ] Rollback plan documented and command available
- [ ] Target environment identified
- [ ] No conflicting deploys in progress

### Before production promotion
- [ ] Preview smoke passed
- [ ] Extended smoke completed (if no staging)
- [ ] Rollback command tested or verified
- [ ] Contract allows production deploy
- [ ] Decision gate cleared (if ops/destructive)

### Production rules
- Deploy without rollback instructions is **forbidden**
- stable_health_window is **mandatory** for production terminal state
- Failed health window → automatic rollback trigger

## Required procedure

### Step 1: Resolve deployment profile + environment path

**Profile resolution (mandatory, not optional):**
1. Check `contract.json` for explicit `deployment_profile` field
2. If absent → read `support/profile-selection-matrix.md` decision rules:
   - systemd units on single server? → `single-server-systemd`
   - docker-compose stack? → `single-host-docker-compose`
   - K8s workload? → `kubernetes-cluster`
   - static build to CDN? → `static-site-cdn`
   - serverless function/edge? → `serverless-edge`
3. Load profile YAML from `support/profiles/<profile>.yaml`
4. Read `default_promotion_path` from profile → sets environment path
5. Apply project override if `tasks/<task_id>/deploy-override.yaml` exists
6. Log resolved profile in events: `PROFILE_RESOLVED`

**Environment path from profile:**
- `single-server-systemd`: preview → prod (no staging)
- `single-host-docker-compose`: preview → prod
- `kubernetes-cluster`: preview → staging → prod
- `static-site-cdn`: preview → prod
- `serverless-edge`: preview → prod

### Step 2: Pre-deploy checklist
Verify release guard policy. All required items must be checked.
If any hard requirement fails → **BLOCK deploy**. Log reason in events.

### Step 3: Deploy to target
Execute deployment:
```bash
# Example for systemd service
systemctl --user restart <service>
# Or for Docker
docker compose up -d <service>
```

Record deploy method, command, timestamp.

### Step 4: Run smoke suite
Execute environment-appropriate smoke checks:

**Minimal smoke (preview):**
- Service is running (`systemctl is-active` or process check)
- HTTP endpoint responds (if web service)
- Basic functionality test

**Extended smoke (production without staging):**
- All minimal checks
- Key user flows work
- No error spikes in logs (tail last 30 lines)
- Resource usage normal (CPU, memory)

### Step 5: Start health window
For production deploys, observe for `stable_health_window`:
- Default duration: 15 minutes
- Check interval: every 2-5 minutes (via preview-health-check cron)
- Track: service uptime, error rate, response times

### Step 6: Handle failures
If any smoke or health check fails:
1. **Rollback first** — execute rollback plan immediately
2. **Diagnose second** — only after service is restored
3. **Record** — set `deploy_result: "rolled_back"` in release-evidence
4. **Event** — log DEPLOY_ROLLBACK event

### Step 7: Write release-evidence.json
Save to `tasks/<task_id>/release-evidence.json`.

### Step 8: Transition task state
```bash
# After successful deploy
node ~/clawd/scripts/task-store.js transition <task_id> DEPLOYING --actor hephaestus

# After health window pass
node ~/clawd/scripts/task-store.js transition <task_id> OBSERVING --actor hephaestus

# After stable observation
node ~/clawd/scripts/task-store.js transition <task_id> FINALIZING --actor deploy-and-observe

# On failure/rollback
node ~/clawd/scripts/task-store.js transition <task_id> ROLLING_BACK --actor deploy-and-observe
```

### Step 9: Log events
```bash
node ~/clawd/scripts/task-store.js event <task_id> DEPLOY_COMPLETED --actor hephaestus --detail '{"environment":"prod","result":"success"}'
```

## Boundaries
- No promotion without evidence — preview must pass before prod
- Current setup skips staging — this must be explicit, not accidental
- If health window fails at minute 14 of 15, the deploy fails
- Rollback is a valid outcome, not a failure of the skill
- deploy-and-observe does not decide whether to deploy — decision-gate does that

## Handoff contract
- finalize-outcome consumes release-evidence.json as part of proof_bundle
- preview-health-check cron monitors health window independently
- On completion, hand to finalize-outcome for task closure

## Supporting files (v8.3)
- `support/profile-selection-matrix.md` — which profile to use
- `support/extension-rules.md` — how to override/extend
- `support/deployment-profile.schema.yaml` — profile YAML schema
- `support/deployment-profile-system-v1.md` — architecture doc
- `support/base/` — environment, smoke, rollback, observe templates
- `support/profiles/` — 5 deployment profiles
- `support/examples/` — project override example

## Source
- ~/clawd/docs/ao-v8.3/sokrat-ao-bundle-v8.3-universal/03-skills/deploy-and-observe.SKILL.md
- ~/clawd/docs/ao-v8.3/sokrat-ao-bundle-v8.3-universal/01-architecture/deployment-profile-system-v1.md
- ~/clawd/docs/ao-v8.3/sokrat-ao-bundle-v8.3-universal/05-schemas/deployment-profile.schema.yaml
