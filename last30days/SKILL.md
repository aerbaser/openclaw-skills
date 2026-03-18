---
name: last30days
description: Research any topic from the last 30 days across Reddit, X, and web. Become an expert and write prompts.
---

# last30days: Two-Agent Research System

Research ANY topic across Reddit, X, and the web using a **two-agent architecture**:

- **Agent 1 (Explore)** — spawned subagent that collects raw data from all sources
- **Agent 2 (Research)** — main agent that synthesizes collected data and delivers results

This separation lets Explore go deep (more pages, more sources) while Research gets clean data for analysis.

---

## Architecture

```
User: "research [topic]"
        │
        ▼
  Main Agent (you)
  ├─ Parse intent (topic, query type, target tool)
  ├─ Spawn → Explore Agent
  │       ├─ Python script (Reddit/X API)
  │       ├─ web_search (multiple queries)
  │       ├─ web_fetch (top pages)
  │       └─ Saves → ~/clawd/data/research/raw/[slug]-[date].md
  │
  ├─ [wait for spawn to complete]
  │
  └─ Research Agent (you, after spawn returns)
          ├─ Read raw data file
          ├─ Judge: weight sources, find patterns
          ├─ Synthesize results
          └─ Deliver to user
```

---

## Step 1: Parse User Intent

Before doing anything, extract:

1. **TOPIC**: What they want to learn about
2. **TARGET_TOOL** (if specified): Where they'll use the prompts
3. **QUERY_TYPE**:
   - **PROMPTING** — "X prompts", "prompting for X" → techniques + copy-paste prompts
   - **RECOMMENDATIONS** — "best X", "top X" → LIST of specific things
   - **NEWS** — "what's happening with X", "X news" → current events
   - **GENERAL** — anything else → broad understanding

**IMPORTANT: Do NOT ask about target tool before research.** Research first, ask after.

---

## Step 2: Spawn Explore Agent

Spawn a subagent with the explore task. The explore agent does ALL data collection.

**Spawn call:**
```
sessions_spawn({
  task: <see template below>,
  thinking: "high",
  label: "explore-[topic-slug]"
})
```

**Explore Agent task template — COPY THIS EXACTLY, fill in variables:**

```
# Explore Agent: Collect Research Data

## Your Mission
You are the Explore Agent. Your ONLY job is to collect raw research data and save it to a file. Do NOT synthesize or summarize — just collect.

## Topic: [TOPIC]
## Query Type: [QUERY_TYPE]
## Target Tool: [TARGET_TOOL or "unknown"]

## Steps

### 1. Run the Python research script
```bash
python3 ~/.openclaw/skills/last30days/scripts/last30days.py "[TOPIC]" --emit=compact 2>&1
```
Save the FULL output. Note the mode (both/reddit-only/x-only/web-only).

### 2. Run web_search queries

Based on query type [QUERY_TYPE], run these searches:

**If RECOMMENDATIONS:**
- `best [TOPIC] recommendations`
- `[TOPIC] list examples`
- `most popular [TOPIC]`
- `[TOPIC] reddit recommendations`

**If NEWS:**
- `[TOPIC] news 2026`
- `[TOPIC] announcement update`
- `[TOPIC] latest developments`

**If PROMPTING:**
- `[TOPIC] prompts examples 2026`
- `[TOPIC] techniques tips`
- `[TOPIC] best practices prompting`

**If GENERAL:**
- `[TOPIC] 2026`
- `[TOPIC] discussion`
- `[TOPIC] guide overview`

For ALL: use the user's EXACT terminology. Do NOT substitute or add terms.
Run at least 4 web_search queries. Use freshness="pm" for recent results.

### 3. Fetch top pages with web_fetch

For the top 5-8 most promising URLs from web_search results:
- Use web_fetch to get full content
- Save title, URL, and key content (first 2000 chars)
- Skip pages that fail or return garbage

### 4. Save EVERYTHING to file

Save ALL collected data to:
`~/clawd/data/research/raw/[TOPIC-SLUG]-[YYYY-MM-DD].md`

Use this EXACT format:
```markdown
# Raw Research: [TOPIC]
Date: [YYYY-MM-DD]
Query Type: [QUERY_TYPE]
Target Tool: [TARGET_TOOL]
Mode: [both/reddit-only/x-only/web-only]

## Python Script Output
[FULL output from last30days.py]

## Web Search Results
### Query: "[query1]"
1. [Title] — [URL]
   Snippet: [snippet]
2. ...

### Query: "[query2]"
1. ...

## Fetched Pages
### [Title] — [URL]
[Content excerpt, max 2000 chars per page]

### [Title] — [URL]
[Content excerpt]

## Stats
- Script sources: Reddit {n} threads, X {n} posts
- Web searches: {n} queries, {n} total results
- Pages fetched: {n} successful, {n} failed
```

### 5. Report completion

Your final message must be EXACTLY:
```
DONE: ~/clawd/data/research/raw/[TOPIC-SLUG]-[YYYY-MM-DD].md
Stats: Reddit {n} | X {n} | Web searches {n} | Pages fetched {n}
```

## Rules
- Do NOT summarize or synthesize. Just collect raw data.
- Do NOT skip web_fetch — the Research Agent needs full page content.
- Do NOT output results to chat — only save to file.
- If a source fails, note it and continue. Don't stop.
- More data = better. Err on the side of collecting too much.
```

---

## Step 3: Wait & Read Results

When the Explore spawn completes:

1. Read the raw data file: `~/clawd/data/research/raw/[slug]-[date].md`
2. If spawn failed or file is missing — fall back to single-agent mode (do research yourself)

---

## Step 4: Research Agent — Synthesize

Now YOU are the Research Agent. You have all the raw data.

### Judge: Weight Sources

1. **Reddit/X sources → HIGHER weight** (engagement signals: upvotes, likes)
2. **Web sources → LOWER weight** (no engagement data)
3. **Cross-source patterns → STRONGEST signal** (mentioned in 2+ source types)
4. Note contradictions between sources
5. Extract top 3-5 actionable insights

### Ground in ACTUAL Research

**CRITICAL: Use what the sources SAY, not your pre-existing knowledge.**

- Read exact product/tool names mentioned
- Use specific quotes and insights from sources
- If research says "ClawdBot", don't write "Claude Code"

### For RECOMMENDATIONS queries

Extract SPECIFIC NAMES, not generic patterns:
- Scan for product/tool/project names
- Count mentions across sources
- List by popularity

**BAD:** "Skills are powerful. Keep them under 500 lines."
**GOOD:** "Most mentioned: /commit (5x), remotion (4x), git-worktree (3x)"

### For all queries

Identify from ACTUAL research output:
- **PROMPT FORMAT** — JSON, structured, natural language, keywords?
- Top 3-5 patterns/techniques across multiple sources
- Specific keywords and approaches FROM THE SOURCES
- Common pitfalls FROM THE SOURCES

---

## Step 5: Show Results

**Display in this EXACT sequence:**

### 1. What I learned

**If RECOMMENDATIONS:**
```
Most mentioned:
• [Name] — {n}x (r/sub, @handle, blog.com)
• [Name] — {n}x (sources)
• [Name] — {n}x (sources)

Notable mentions: [others with 1-2 mentions]
```

**If PROMPTING/NEWS/GENERAL:**
```
What I learned:

[2-4 sentences from ACTUAL research, not generic knowledge]

Key patterns:
• [Pattern from research]
• [Pattern from research]
• [Pattern from research]
```

### 2. Stats

For **full/partial mode** (has API keys):
```
---
Explore agent complete:
• Reddit: {n} threads | {sum} upvotes | {sum} comments
• X: {n} posts | {sum} likes | {sum} reposts
• Web: {n} pages | {domains}
• Top voices: r/{sub1}, r/{sub2} | @{handle1}, @{handle2}
```

For **web-only mode**:
```
---
Explore agent complete:
• Web: {n} pages | {domains}
• Top sources: {author1} on {site1}, {author2} on {site2}
```

### 3. Invitation
```
---
Share your vision for what you want to create and I'll write a prompt for {TARGET_TOOL}.
```

**SELF-CHECK:** Does your "What I learned" match the research? Rewrite if you're projecting knowledge.

**If TARGET_TOOL unknown**, ask now (not before research).

**STOP and WAIT for user response.**

---

## Step 6: Write Prompts (after user shares vision)

When user says what they want to create → write ONE tailored prompt.

### Match research-recommended FORMAT
- Research says JSON → write JSON
- Research says structured → use key: value
- Research says natural language → prose

### Output:
```
Prompt for {TARGET_TOOL}:

---
[The prompt in the format research recommends]
---

Uses: [1-line explanation of which research insight you applied]
```

### Quality checklist:
- FORMAT matches what research recommends
- Addresses what user wants to create
- Uses patterns/keywords from research
- Ready to paste (minimal placeholders)

If user asks for more → provide 2-3 variations. Otherwise one is enough.

---

## After Each Prompt

```
---
Expert in: {TOPIC} for {TARGET_TOOL}
Based on: {n} Reddit + {n} X + {n} web pages

Want another prompt? Tell me what you're creating.
```

---

## Context Memory

After research completes, you're an EXPERT. For follow-ups:
- Do NOT run new searches — answer from collected data
- Cite Reddit threads, X posts, web sources
- Only re-research if user asks about a DIFFERENT topic

---

## Caching

Raw data: `~/clawd/data/research/raw/[slug]-[date].md` (saved by Explore)
Synthesis: `~/clawd/data/research/[slug]-[date].md` (save after delivering results)

```bash
mkdir -p ~/clawd/data/research/raw
```

**After delivering results, save synthesis:**
```
# Research: [TOPIC]
Date: [YYYY-MM-DD]
Query Type: [QUERY_TYPE]
Target Tool: [TARGET_TOOL]

## Summary
[Your synthesis]

## Key Patterns
- [Pattern 1]
- [Pattern 2]
- [Pattern 3]

## Stats
[from explore agent]

## Top Sources
[top 5-10 sources with engagement data]
```

---

---

## Fallback

If spawn fails or takes >5 minutes:
- Read whatever data was saved
- Fall back to single-agent: run web_search + web_fetch yourself
- Still deliver results, just note fewer sources

---

## Quick Reference

| Tool | Use |
|------|-----|
| `exec` | Run Python script |
| `web_search` | Brave Search (in Explore agent) |
| `web_fetch` | Fetch page content (in Explore agent) |
| `sessions_spawn` | Spawn Explore agent |
| `Read` | Read raw data file (in Research phase) |
