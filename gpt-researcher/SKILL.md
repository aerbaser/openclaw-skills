---
name: gpt-researcher
description: Deep web research via GPT Researcher. Use when you need comprehensive, source-backed research on any topic — news, technology, markets, people, products. Returns detailed reports with citations. NOT for simple factual lookups (use web_search). Best for multi-source synthesis that requires depth.
---

# GPT Researcher — Deep Research Skill

## Architecture

```
Agent (Аристотель)
  → HTTP POST localhost:8000/report/
    → GPT Researcher (FastAPI, uvicorn)
      → codex-proxy (localhost:8016)
        → Codex CLI → ChatGPT Pro (gpt-5.4)
      → DuckDuckGo (search, no API key)
      → HuggingFace embeddings (local, sentence-transformers/all-MiniLM-L6-v2)
```

## Services (systemd user)

| Service | Port | Purpose |
|---------|------|---------|
| `codex-proxy.service` | 8016 | Translates OpenAI API → Codex CLI → ChatGPT Pro |
| `gpt-researcher.service` | 8000 | GPT Researcher HTTP server + Web UI |

Check status: `systemctl --user status codex-proxy gpt-researcher`

## Quick Research (single report)

```bash
# Basic research report
curl -s -X POST http://127.0.0.1:8000/report/ \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Your research query here",
    "report_type": "research_report",
    "agent": "researcher"
  }' | python3 -m json.tool
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task` | string | required | Research query/topic |
| `report_type` | string | `research_report` | Type: `research_report`, `detailed_report`, `resource_report`, `outline_report`, `subtopic_report`, `multi_agents` |
| `agent` | string | `researcher` | Agent type |
| `report_source` | string | `web` | Source: `web` or `local` (local docs) |
| `source_urls` | list | `[]` | Specific URLs to research |
| `generate_in_background` | bool | `false` | Background generation |

### Report Types

- **`research_report`** — standard report (~1400 words), good balance of speed/depth
- **`detailed_report`** — comprehensive deep-dive with subtopics, slower but thorough
- **`resource_report`** — curated list of sources with summaries
- **`outline_report`** — structured outline with key points
- **`subtopic_report`** — focused on a specific subtopic

## Deep Research (recursive, high depth)

For complex topics requiring tree-like exploration:

```bash
curl -s -X POST http://127.0.0.1:8000/report/ \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Comprehensive analysis of DeFi yield strategies in 2026",
    "report_type": "detailed_report",
    "agent": "researcher"
  }' | python3 -m json.tool
```

Deep research parameters are configured in `.env`:
- `DEEP_RESEARCH_BREADTH=3` — parallel research paths
- `DEEP_RESEARCH_DEPTH=2` — sequential search iterations
- `DEEP_RESEARCH_CONCURRENCY=4` — concurrent operations

## Research on Specific URLs

```bash
curl -s -X POST http://127.0.0.1:8000/report/ \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Summarize the key findings",
    "report_type": "research_report",
    "source_urls": ["https://example.com/article1", "https://example.com/article2"]
  }' | python3 -m json.tool
```

## Background Research

For long-running research, use background mode:

```bash
# Start research in background
RESULT=$(curl -s -X POST http://127.0.0.1:8000/report/ \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Your query",
    "report_type": "detailed_report",
    "generate_in_background": true
  }')

RESEARCH_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['research_id'])")

# Check result later
curl -s http://127.0.0.1:8000/api/reports/$RESEARCH_ID | python3 -m json.tool
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/report/` | Generate research report |
| `GET` | `/api/reports` | List all reports |
| `GET` | `/api/reports/{id}` | Get specific report |
| `POST` | `/api/chat` | Chat with research context |
| `POST` | `/api/multi_agents` | Run multi-agent research |
| `GET` | `/` | Web UI |

## Response Format

```json
{
  "output": "# Research Report\n\n## Introduction\n...",
  "research_id": "task_1710000000_your_query",
  "sources": ["https://source1.com", "https://source2.com"],
  "costs": 0.0
}
```

The `output` field contains the full markdown report with inline citations.

## Troubleshooting

```bash
# Check services
systemctl --user status codex-proxy gpt-researcher

# Test codex-proxy health
curl -s http://127.0.0.1:8016/health

# Test GPT Researcher
curl -s http://127.0.0.1:8000/ | head -5

# Restart if needed
systemctl --user restart codex-proxy gpt-researcher

# Logs
journalctl --user -u gpt-researcher -n 50 --no-pager
journalctl --user -u codex-proxy -n 50 --no-pager
```

## Configuration

Config file: `/home/aiadmin/.openclaw/workspace-aristotle/projects/gpt-researcher/.env`

Key settings:
- LLMs: `FAST_LLM`, `SMART_LLM`, `STRATEGIC_LLM` — via codex-proxy (gpt-5.4)
- Search: `RETRIEVER=duckduckgo` (free, no key)
- Embeddings: `huggingface:sentence-transformers/all-MiniLM-L6-v2` (local)
- Language: `LANGUAGE=russian`
- Words: `TOTAL_WORDS=1400`

## Cost

All LLM calls go through Codex CLI → ChatGPT Pro subscription = **$0 marginal cost**.
Search via DuckDuckGo = **free**.
Embeddings via local HuggingFace = **free**.

## MCP (for ACP sessions)

MCP server config at `~/.openclaw/workspace-aristotle/.mcp.json`.
Available tools: `deep_research`, `quick_search`, `write_report`, `get_research_sources`, `get_research_context`.
Used when spawning ACP sessions (Codex/Claude Code) in Aristotle's workspace.
