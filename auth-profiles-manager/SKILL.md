---
name: auth-profiles-manager
description: >
  Manage OpenClaw auth profiles via Telegram inline buttons. Triggered by:
  (1) User sends /profiles command,
  (2) callback_data starts with "apr_" (auth profile button callbacks),
  (3) User asks to switch/reauth/add auth profiles.
  Shows current profiles, active account, expiry, allows switching primary/fallback and refreshing tokens.
metadata:
  { "openclaw": { "emoji": "🔑" } }
---

# Auth Profiles Manager

## Trigger Conditions

Activate this skill when:
- Message is exactly `/profiles` or starts with `/profiles`
- `callback_data` contains `apr_` prefix (button callbacks from this skill)
- User asks about "auth profiles", "switch account", "reauth", "Claude account"

---

## Step 1: Show Status Panel (`/profiles`)

Read auth-profiles.json and send formatted status with inline buttons.

```bash
python3 -c "
import json, base64, time
from datetime import datetime, timezone

f = '/home/aiadmin/.openclaw/agents/main/agent/auth-profiles.json'
d = json.load(open(f))
profiles = d.get('profiles', {})
order = d.get('order', {}).get('anthropic', [])
last_good = d.get('lastGood', {}).get('anthropic', 'unknown')

lines = ['🔑 Auth Profiles']
lines.append('')

# Anthropic profiles
lines.append('**Anthropic**')
for pid in order:
    p = profiles.get(pid)
    if not p:
        lines.append(f'  {pid}: ❌ missing')
        continue
    active = '✅ ACTIVE' if pid == last_good else ''
    ptype = p.get('type', '?')
    lines.append(f'  {pid}: {ptype} {active}')

# Codex JWT expiry
codex = profiles.get('openai-codex:default')
codex_token = (codex or {}).get('access') or (codex or {}).get('key')
if codex_token:
    try:
        parts = codex_token.split('.')
        payload = parts[1] + '=' * (-len(parts[1]) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload.encode()).decode())
        exp = data.get('exp', 0)
        now = int(time.time())
        days_left = (exp - now) // 86400
        exp_str = datetime.fromtimestamp(exp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        lines.append('')
        lines.append(f'**Codex JWT** expires {exp_str} ({days_left}d)')
    except Exception:
        lines.append('')
        lines.append('**Codex JWT** (parse error)')

# Gemini OAuth
gemini = profiles.get('google-gemini-cli:default')
if gemini:
    exp = gemini.get('expires', 0)
    if exp:
        now_ms = int(time.time() * 1000)
        if now_ms > exp:
            lines.append('**Gemini OAuth** ❌ expired')
        else:
            lines.append('**Gemini OAuth** ✅ valid')

print('\n'.join(lines))
"
```

Then send message with **inline buttons**:

```python
message(
  action="send",
  channel="telegram",
  target="473841722",
  message=<output from above>,
  buttons=[
    [
      {"text": "🔁 → yura (primary)", "callback_data": "apr_switch_yura"},
      {"text": "🔁 → dima (fallback)", "callback_data": "apr_switch_dima"}
    ],
    [
      {"text": "🔄 Refresh Codex JWT", "callback_data": "apr_refresh_codex"},
      {"text": "📊 Test all", "callback_data": "apr_test_all"}
    ],
    [
      {"text": "➕ Add profile", "callback_data": "apr_add_help"}
    ]
  ]
)
```

Reply with NO_REPLY after sending.

---

## Step 2: Handle Button Callbacks

When the message text matches a `apr_*` pattern, handle accordingly:

### `apr_switch_yura`
Switch active anthropic profile to `anthropic:yura`:

```python
python3 -c "
import json
f = '/home/aiadmin/.openclaw/agents/main/agent/auth-profiles.json'
d = json.load(open(f))
d['lastGood']['anthropic'] = 'anthropic:yura'
d['order']['anthropic'] = ['anthropic:yura', 'anthropic:dima']
json.dump(d, open(f, 'w'), indent=2)
print('Switched to anthropic:yura')
"
```

Then reply: `✅ Switched to **anthropic:yura** (primary, Max plan)`

No gateway restart needed — OpenClaw reads lastGood on next request.

---

### `apr_switch_dima`
Switch active anthropic profile to `anthropic:dima`:

```python
python3 -c "
import json
f = '/home/aiadmin/.openclaw/agents/main/agent/auth-profiles.json'
d = json.load(open(f))
d['lastGood']['anthropic'] = 'anthropic:dima'
d['order']['anthropic'] = ['anthropic:dima', 'anthropic:yura']
json.dump(d, open(f, 'w'), indent=2)
print('Switched to anthropic:dima')
"
```

Then reply: `✅ Switched to **anthropic:dima** (fallback)`

---

### `apr_refresh_codex`
Refresh Codex JWT token via OpenAI OAuth:

```javascript
node -e "
const https = require('https');
const fs = require('fs');

const auth = JSON.parse(fs.readFileSync('/home/aiadmin/.codex/auth.json'));
const refreshToken = auth.tokens.refresh_token;

const body = JSON.stringify({
  grant_type: 'refresh_token',
  client_id: 'app_EMoamEEZ73f0CkXaXp7hrann',
  refresh_token: refreshToken
});

const req = https.request({
  hostname: 'auth.openai.com',
  path: '/oauth/token',
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'Content-Length': body.length}
}, (res) => {
  let data = '';
  res.on('data', d => data += d);
  res.on('end', () => {
    const r = JSON.parse(data);
    if (r.access_token) {
      const parts = r.access_token.split('.');
      const payload = JSON.parse(Buffer.from(parts[1] + '==', 'base64').toString());
      const daysLeft = Math.floor((payload.exp - Date.now()/1000) / 86400);
      // Save to ~/.codex/auth.json
      auth.tokens.access_token = r.access_token;
      if (r.refresh_token) auth.tokens.refresh_token = r.refresh_token;
      auth.last_refresh = new Date().toISOString();
      fs.writeFileSync('/home/aiadmin/.codex/auth.json', JSON.stringify(auth, null, 2));
      // Sync to all agent auth-profiles
      for (const agent of ['main','archimedes','aristotle','herodotus']) {
        const p = \`/home/aiadmin/.openclaw/agents/\${agent}/agent/auth-profiles.json\`;
        try {
          const d = JSON.parse(fs.readFileSync(p));
          if (d.profiles?.['openai-codex:default']) {
            d.profiles['openai-codex:default'].key = r.access_token;
            fs.writeFileSync(p, JSON.stringify(d, null, 2));
          }
        } catch(e) {}
      }
      console.log('OK:' + daysLeft);
    } else {
      console.log('ERR:' + JSON.stringify(r).substring(0,100));
    }
  });
});
req.write(body);
req.end();
"
```

Parse output:
- If `OK:N` → reply: `✅ Codex JWT refreshed — valid for **N days**`
- If `ERR:...` → reply: `❌ Refresh failed: [error]. Run \`codex auth login\` manually in terminal.`

---

### `apr_test_all`
Test all anthropic profiles with a minimal API call:

```bash
for profile in "yura" "dima"; do
  # Get token for profile
  python3 -c "
import json, sys
f = '/home/aiadmin/.openclaw/agents/main/agent/auth-profiles.json'
d = json.load(open(f))
p = d['profiles'].get(f'anthropic:{sys.argv[1]}', {})
t = p.get('token') or p.get('key', '')
print(t)
" $profile 2>/dev/null | head -c 100
done
```

Then test each token via curl:
```bash
TOKEN="<token>"
curl -s -o /dev/null -w "%{http_code}" \
  -H "x-api-key: $TOKEN" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-haiku-4-5","max_tokens":5,"messages":[{"role":"user","content":"Hi"}]}' \
  https://api.anthropic.com/v1/messages
```

Report:
- 200 → ✅ working
- 401 → ❌ invalid/expired
- 429 → ⚠️ rate limited (but valid)
- Other → ❓ unknown

Reply with summary table:
```
🧪 Auth Test Results:

anthropic:yura — [status]
anthropic:dima — [status]
openai-codex:default — [not tested via API, JWT expires in N days]
```

---

### `apr_add_help`

Reply with instructions:
```
➕ Add Auth Profile

To add a new profile, run in terminal:

**New Anthropic OAuth (Max plan):**
openclaw models auth login

**New token:**
openclaw models auth token anthropic --profile-id anthropic:newname

**After adding** — send /profiles to refresh the view.
```

---

## Notes

- After switching profiles: gateway picks up on next request (no restart needed for lastGood change)
- Codex JWT: auto-refresh runs every 6h via cron `codex-token-sync`
- All auth-profiles changes sync to all 4 agents automatically in this skill
- DO NOT display full token values in responses — security
- All auth-profiles changes sync to all 4 agents automatically in this skill
- DO NOT display full token values in responses — security
