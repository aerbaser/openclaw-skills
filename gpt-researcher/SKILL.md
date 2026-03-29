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
      → codex-proxy (localhost:8016) → ChatGPT Pro (gpt-5.4, reasoning=high)
      → Tavily/Serper/ArXiv/PubMed/SemanticScholar (search)
      → HuggingFace embeddings (BAAI/bge-large-en-v1.5, local)
```

## Services (systemd user)

| Service | Port |
|---------|------|
| `codex-proxy.service` | 8016 |
| `gpt-researcher.service` | 8000 |

Check: `systemctl --user status codex-proxy gpt-researcher`

---

## Understanding User Intent (CRITICAL)

Users write in Russian or mixed language. Parse their request into 5 dimensions:

### 1. Research Type (preset)

| Пользователь пишет | report_type | Время |
|---------------------|-------------|-------|
| "ресёрч", "исследование", "отчёт", "разберись", "проанализируй" | `research_report` | 6-8 мин |
| "глубокий ресёрч", "детальный", "подробный", "копай глубоко" | `detailed_report` | 15-25 мин |
| "быстрый ресёрч", "кратко", "обзор", "overview" | `research_report` (reduced params) | 3-4 мин |
| "найди источники", "собери ссылки", "что пишут про" | `resource_report` | 4-5 мин |

### 2. Depth / Source Count

| User says | max_search_results | max_subtopics | max_urls_to_scrape |
|-----------|-------------------|--------------|-------------------|
| nothing (default) | 5 | 3 | 12 |
| "20 источников" | 5 | 4 | 20 |
| "50 источников" | 10 | 5 | 50 |
| "100 источников" | 15 | 7 | 100 |
| "как можно больше" | 15 | 10 | 100 |

### 3. Domain Preferences (query_domains)

Restricts search to ONLY specified domains. Use when user asks for specific platforms:

| Keyword | query_domains |
|---------|--------------|
| "на реддите", "reddit" | `["reddit.com"]` |
| "на твиттере", "в X" | `["twitter.com", "x.com", "nitter.net"]` |
| "на гитхабе" | `["github.com"]` |
| "на пабмеде", "pubmed" | `["pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov"]` |
| "научные статьи" | `["pubmed.ncbi.nlm.nih.gov", "scholar.google.com", "arxiv.org", "nature.com"]` |
| "крипто", "DeFi" | `["defillama.com", "dune.com", "messari.io", "theblock.co", "coingecko.com"]` |
| "новости" | `["reuters.com", "bloomberg.com", "techcrunch.com"]` |

**"в основном X"** = use query_domains BUT add 1-2 broad domains to catch important results outside the primary source.

### 4. Specialized Retrievers

GPT Researcher has built-in retrievers for specific source types. Use when the topic matches:

| Keyword | retrievers value | API key needed? |
|---------|-----------------|----------------|
| "научные статьи", "academic", "arxiv" | `tavily,arxiv` | No (arxiv free) |
| "медицина", "БАДы", "пабмед", "health" | `tavily,pubmed_central` | No (PubMed free) |
| "академические работы", "semantic scholar" | `tavily,semantic_scholar` | No (free) |
| "научный ресёрч" (broad) | `tavily,arxiv,pubmed_central,semantic_scholar` | No |
| default (anything else) | Don't set (uses .env default = tavily) | — |

**IMPORTANT:** Always include `tavily` (or `serper` if tavily quota exhausted) alongside specialized retrievers. They complement each other — Tavily finds web content, specialized retrievers find academic/domain sources.

**Available retrievers:** `tavily`, `serper`, `duckduckgo`, `arxiv`, `pubmed_central`, `semantic_scholar`, `exa`, `bing`, `google`, `searchapi`, `serpapi`, `searx`

### 5. Specific URLs

User can provide URLs directly:
- "проанализируй эту статью: https://..." → `source_urls: ["https://..."]`

---

## Combining Dimensions — Examples

| User request | Parameters |
|-------------|-----------|
| "ресёрч про магний для сна, ищи на пабмеде, 50 источников" | `report_type: research_report, retrievers: "tavily,pubmed_central", query_domains: ["pubmed.ncbi.nlm.nih.gov"], max_urls_to_scrape: 50` |
| "быстрый обзор что на реддите думают про Solana" | `report_type: research_report, query_domains: ["reddit.com"], total_words: 1000, max_search_results: 3` |
| "глубокий научный ресёрч про longevity" | `report_type: detailed_report, retrievers: "tavily,arxiv,pubmed_central,semantic_scholar", total_words: 5000` |
| "что на гитхабе нового по AI agents" | `report_type: research_report, query_domains: ["github.com"]` |
| "детальный ресёрч Hyperliquid vs dYdX, 30 источников" | `report_type: detailed_report, max_urls_to_scrape: 30` |

---

## Preset Parameters

**Quick:** ~1000 слов, 3-4 мин
```json
{"report_type": "research_report", "total_words": 1000, "max_search_results": 3, "max_subtopics": 1}
```

**Standard:** ~2500 слов, 6-8 мин — DEFAULT
```json
{"report_type": "research_report"}
```

**Deep:** ~5000+ слов, 15-25 мин
```json
{"report_type": "detailed_report", "total_words": 5000, "max_search_results": 8, "max_subtopics": 5}
```

**Sources:** список с описанием, 4-5 мин
```json
{"report_type": "resource_report"}
```

---

## API Reference

```bash
curl -s -X POST http://127.0.0.1:8000/report/ \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research query",
    "report_type": "research_report",
    "tone": "Analytical",
    "retrievers": "tavily,pubmed_central",
    "query_domains": ["reddit.com"],
    "max_urls_to_scrape": 50
  }' --max-time 900
```

### All Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task` | string | **required** | Research query/topic |
| `report_type` | string | `research_report` | `research_report`, `detailed_report`, `resource_report`, `outline_report` |
| `report_source` | string | `web` | `web` or `local` |
| `tone` | string | `Analytical` | `Objective`, `Formal`, `Analytical`, `Persuasive`, `Informative`, `Explanatory` (**capitalized!**) |
| `source_urls` | list | `null` | Specific URLs to analyze |
| `query_domains` | list | `null` | Restrict search to these domains |
| `retrievers` | string | `null` | Comma-separated retrievers: `"tavily,arxiv,pubmed_central"` |
| `max_search_results` | int | 5 | Search results per sub-query (3-15) |
| `max_subtopics` | int | 3 | Sub-questions to explore (1-10) |
| `max_urls_to_scrape` | int | 12 | Max pages to download and read (5-100) |
| `total_words` | int | 2500 | Target word count |

---

## After EVERY Research — MUST DO

### 1. Show Statistics
```
📊 Статистика:
• Источников: X
• Посещено URL: Y
• Время: ~N мин
• Retrievers: tavily, arxiv
• Топ-5 источников: [list with titles]
```

### 2. Publish to GitHub
```bash
SLUG="topic-name"
DATE=$(date +%Y-%m-%d)
cd /tmp/research && git pull --rebase 2>/dev/null
cat > "reports/${DATE}-${SLUG}.md" << 'REPORT'
<markdown report>
REPORT
git add reports/ && git commit -m "research: ${SLUG}" && git push
```

### 3. Send to User
- GitHub link: `https://github.com/aerbaser/research/blob/main/reports/YYYY-MM-DD-slug.md`
- Key findings (3-5 bullet points)
- Stats

**Repo:** https://github.com/aerbaser/research

---

## How Depth Works

| Parameter | What it controls | Effect on time |
|-----------|-----------------|---------------|
| `max_subtopics` | LLM splits topic into N sub-questions | +30s per subtopic |
| `max_search_results` | Results fetched per sub-question per retriever | +5s per result |
| `max_urls_to_scrape` | Pages actually downloaded and read | +10s per page |
| `retrievers` | Which search backends to query | +20s per extra retriever |
| `detailed_report` | Tree exploration: breadth×depth iterations | 2-3x longer |
| `CURATE_SOURCES` | LLM filters weak sources (uses gpt-5.4-mini) | +30s |

**Time estimates:**
- Quick (1 subtopic, 3 results, 5 pages): ~3-4 min
- Standard (3 subtopics, 5 results, 12 pages): ~6-8 min
- Deep detailed (5 subtopics, 8 results, 50 pages): ~15-25 min
- Max (10 subtopics, 15 results, 100 pages): ~30-45 min

## Cost

All LLM calls via ChatGPT Pro = **$0**. Tavily: 1000 req/mo free. ArXiv/PubMed/SemanticScholar: **free**. Serper: 2500 free then $2.50/1000. Embeddings: local = **free**.

When Tavily quota exhausted → change RETRIEVER in .env from `tavily` to `serper` (SERPER_API_KEY already configured).

## Troubleshooting

```bash
systemctl --user status codex-proxy gpt-researcher
journalctl --user -u gpt-researcher -n 50 --no-pager
systemctl --user restart codex-proxy gpt-researcher
```
