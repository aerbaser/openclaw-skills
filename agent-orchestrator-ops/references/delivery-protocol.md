# Delivery Protocol

## Report to Сократ

Use `sessions_send`:
```
sessions_send(sessionKey="agent:main:telegram:group:-1003692383088:topic:121", message="...")
```

## Report to Юра

Use `message` tool with Archimedes account:
```
message(action=send, accountId=archimedes, channel=telegram, target=-1003692383088, threadId=122, message="...", buttons=[])
```

> ⚠️ Always include `buttons=[]` — message tool requires it.
> ⚠️ threadId=122 is Архимед's topic. Don't post to 121 (Сократ's topic).

## Format

1–3 lines max:
1. What changed
2. Status: `PASS` / `FAIL` / `BLOCKED` / `IN_PROGRESS`
3. Next step

## Mandatory Report Moments

| Moment | Include |
|--------|---------|
| Task ACK | Acknowledge + objective (within 60s) |
| Orchestrator start/stop | Service + PASS/FAIL + verification |
| Session spawned | Issue # + session name |
| PR opened | PR URL + summary |
| PR merged | PR # + next step |
| Dashboard restart | Ports + verification result |
| AO update | Old version → new version + status |
| Blocked | Single dominant blocker |

## Examples

```
AO updated 0.1.0 → 0.2.2. Local patch rebased. Both orchestrators running. Dashboard :3100 + WS :14800/:14801. PASS.
```
```
aodash-orchestrator restarted. Claude Code session active. Dashboard API responding. PASS.
```
```
Spawned aodash-8 for issue #99. Session active in tmux. IN_PROGRESS.
```
```
PR #100 merged (fix/restore-kanban). Dashboard restarted. Pipeline page loads 3 tasks. PASS.
```
```
BLOCKED: ao session amber-shore not responding after 5min. Killing and respawning.
```
