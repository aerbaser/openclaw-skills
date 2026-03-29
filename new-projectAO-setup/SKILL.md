---
name: new-projectAO-setup
description: "Add a new repo/project to Agent Orchestrator (AO). Covers all steps: clone → config → .agent-rules.md → systemd service → GitHub webhook → smoke test → notify Platon. Use when adding any new project to the AO pipeline."
triggers:
  - "add new project to AO"
  - "подключи новый проект"
  - "новый проект в систему"
  - "добавь репо в AO"
  - "onboard project"
  - callback_data starts with "ao_onboard_"
metadata:
  { "openclaw": { "emoji": "🏗️" } }
---

# new-projectAO-setup — Adding a New Project to Agent Orchestrator

**Owner:** Гефест (executes) + Сократ (coordinates)  
**Outcome:** New repo is registered in AO, hooks configured, smoke test passes, Платон notified.

---

## Prerequisites

Before running this skill, you need:
- `repo` — GitHub repo owner/name (e.g. `aerbaser/my-new-app`)
- `local_path` — where to clone locally (e.g. `~/projects/my-new-app`)
- `session_prefix` — short prefix for AO sessions (e.g. `myapp`)
- `default_branch` — usually `main` or `master`

---

## Checklist (run in order)

### 1. Clone the repo locally

```bash
git clone https://github.com/<owner>/<repo>.git <local_path>
```

### 1.5. Generate CI from actual stack

Read and follow the `ci-bootstrap-pro` skill for this repo.
CI must be generated from the real stack (package.json, Makefile, pyproject.toml, etc.) — not from boilerplate.
CI must exist and be pushed **before** `.agent-rules.md` and webhook setup.

### 2. Create `.agent-rules.md` in the repo

Template:

```markdown
# Agent Rules — <ProjectName>

## Core constraints
- Never rename the spawn branch after `ao spawn`.
- One issue = one branch = one PR.
- Before every push: run lint, typecheck, targeted tests.
- Do not touch migrations, secrets, CI, or infra unless the issue explicitly allows it.
- If CI fails twice, stop autopatching and post a root-cause summary.
- Use conventional commits (`feat:`, `fix:`, `chore:`) and reference the issue number.
- Do not force-push after reviewer comments unless rebasing is required.

## Forbidden services
- Check `~/clawd/memory/forbidden-services.json` before any systemctl start.
```

Commit and push:

```bash
cd <local_path>
git add .agent-rules.md
git commit -m "chore: add ao agent-rules.md"
git push
```

### 3. Add project to `agent-orchestrator.yaml`

File: `~/projects/sokrat-core/agent-orchestrator.yaml` (source of truth, symlinked to `~/tools/agent-orchestrator/`)

Add a new entry under `projects:`:

```yaml
  <project_key>:
    name: <Human Name>
    repo: <owner>/<repo>
    path: <local_path>
    defaultBranch: <main|master>
    sessionPrefix: <prefix>
    agentRulesFile: .agent-rules.md
    postCreate:
      - "npm install --frozen-lockfile"  # or relevant install command
    scm:
      plugin: github
      webhook:
        path: /api/webhooks/github
```

Commit and push:

```bash
cd ~/projects/sokrat-core
git add agent-orchestrator.yaml
git commit -m "config: add <project_key> to AO"
git push
```

### 4. Create GitHub webhook

Use the stable Tailscale Funnel URL:

```bash
cat > /tmp/ao-webhook.json << 'JSON'
{
  "name": "web",
  "active": true,
  "events": [
    "pull_request", "pull_request_review", "pull_request_review_comment",
    "issue_comment", "check_run", "check_suite", "status", "push"
  ],
  "config": {
    "url": "https://debian.taildddc37.ts.net:8443/api/webhooks/github",
    "content_type": "json",
    "insecure_ssl": "0"
  }
}
JSON

gh api -X POST repos/<owner>/<repo>/hooks --input /tmp/ao-webhook.json \
  --jq '{id, url: .config.url, active, events}'
```

Record the hook ID for cleanup if needed.

### 5. Reload AO config

AO reads config on demand — but restart the lifecycle worker to pick up the new project:

```bash
systemctl --user restart ao@sokrat-core.service
```

Verify the project appears:

```bash
AO_CONFIG_PATH=~/projects/sokrat-core/agent-orchestrator.yaml ao status
```

### 6. Smoke test

```bash
# Spawn a test session
AO_CONFIG_PATH=~/projects/sokrat-core/agent-orchestrator.yaml ao spawn <project_key> --message "Smoke test: create a file /tmp/ao-smoke-$(date +%s).txt with content 'AO smoke test OK', commit and push to a new branch, then open a PR."

# Check session
AO_CONFIG_PATH=~/projects/sokrat-core/agent-orchestrator.yaml ao status
```

Wait for the PR to appear in GitHub. Then kill the test session:

```bash
AO_CONFIG_PATH=~/projects/sokrat-core/agent-orchestrator.yaml ao session kill <session_id>
```

Close the test PR and delete the branch.

### 7. Notify Платон

Send via `sessions_send`:

```
Проект <ProjectName> (<owner>/<repo>) добавлен в AO.

- AO project key: <project_key>
- Webhook: active on https://debian.taildddc37.ts.net:8443/api/webhooks/github
- .agent-rules.md: present in repo root
- Smoke test: passed

Можешь создавать Issues — AO подхватит их.
```

---

## Quick Reference

| What | Where |
|------|-------|
| AO config | `~/projects/sokrat-core/agent-orchestrator.yaml` |
| Webhook URL | `https://debian.taildddc37.ts.net:8443/api/webhooks/github` |
| AO status | `AO_CONFIG_PATH=~/projects/sokrat-core/agent-orchestrator.yaml ao status` |
| AO spawn | `ao spawn <project_key> <issue_number>` |
| Reload AO | `systemctl --user restart ao@sokrat-core.service` |
| Add hook | `gh api -X POST repos/<owner>/<repo>/hooks --input /tmp/ao-webhook.json` |

---

## Who does this

- **Сократ** — receives the request, validates inputs, coordinates
- **Гефест** — executes steps 1–6 (repo, config, hook, service, smoke test)
- **Платон** — receives notification in step 7, starts creating Issues

---

## Common errors

**"Project not found in AO"**
- Check `agent-orchestrator.yaml` has the project key exactly as used in `ao spawn`
- Restart `ao@sokrat-core.service`

**Webhook 403 from GitHub**
- Token needs `repo` scope with webhook write access
- Update PAT at `~/.config/gh/hosts.yml` or re-run `gh auth login`

**AO endpoint 404**
- `ao-dashboard.service` must be running: `systemctl --user status ao-dashboard.service`
- `ao-funnel.service` must be running: `systemctl --user status ao-funnel.service`

**Webhook not delivered**
- Verify Funnel is active: `tailscale funnel status`
- Tailscale daemon must be running: `systemctl status tailscaled`
