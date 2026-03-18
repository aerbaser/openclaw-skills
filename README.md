# OpenClaw Skills

Custom skills for [OpenClaw](https://openclaw.io) — migrated from `~/clawd/skills/` and workspace skill directories.

## Skills (33 total)

| Skill | Description |
|-------|-------------|
| **agent-browser** | A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands. |
| **agent-orchestrator** | Meta-agent skill for orchestrating complex tasks through autonomous sub-agents. Decomposes macro tasks into subtasks, spawns specialized sub-agents with dynamically generated SKILL.md files, coordinates file-based communication, consolidates results, and dissolves agents upon completion. |
| **auth-profiles-manager** | Manage OpenClaw auth profiles via Telegram inline buttons. Triggered by `/profiles` command, `apr_` button callbacks, or requests to switch/reauth/add auth profiles. |
| **calendar** | Calendar management and scheduling. Create events, manage meetings, and sync across calendar providers. |
| **ci-bootstrap-pro** | Use when adding or upgrading CI in a repository. Detect the stack, choose repository-native build and test commands, and produce secure GitHub Actions workflows with minimal token permissions. |
| **clawddocs** | Clawdbot documentation expert with decision tree navigation, search scripts, doc fetching, version tracking, and config snippets for all Clawdbot features. |
| **crypto** | Cryptocurrency market data and price alert monitoring tool based on CCXT. Supports multiple exchanges, real-time price tracking, and configurable price/volatility alerts. |
| **email** | Email management and automation. Send, read, search, and organize emails across multiple providers. |
| **frontend-design-3** | Create distinctive, production-grade frontend interfaces with high design quality. Generates creative, polished code that avoids generic/boilerplate UI patterns. |
| **github-issue-forge** | Use when creating or rewriting GitHub issues from repository analysis. Inspect code, tests, docs, related issues and PRs, then produce execution-ready issues with scope, constraints, and verification steps. |
| **github-pr** | Fetch, preview, merge, and test GitHub PRs locally. Great for trying upstream PRs before they're merged. |
| **git-notes-memory** | Git-Notes-Based knowledge graph memory system. Branch-aware persistent memory using git notes. Handles context silently and automatically. |
| **gog** | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. |
| **humanizer** | Remove signs of AI-generated writing from text. Detects and fixes patterns including inflated symbolism, promotional language, em dash overuse, AI vocabulary words, and excessive conjunctive phrases. |
| **last30days** | Research any topic from the last 30 days across Reddit, X, and web. Become an expert and write prompts. |
| **marketing-mode** | Marketing Mode combining 23 comprehensive marketing skills covering strategy, psychology, content, SEO, conversion optimization, and paid growth. |
| **n8n-workflow-automation** | Designs and outputs n8n workflow JSON with robust triggers, idempotency, error handling, logging, retries, and human-in-the-loop review queues. |
| **new-agent** | *(empty directory — no SKILL.md yet)* |
| **ontology** | Typed knowledge graph for structured agent memory and composable skills. Use when creating/querying entities (Person, Project, Task, Event, Document), linking related objects, and enforcing constraints. |
| **price-monitor** | Track crypto and stock prices in real-time with configurable alerts and multi-currency support. |
| **proactive-agent** | Transform AI agents from task-followers into proactive partners that anticipate needs and continuously improve. Includes WAL Protocol, Working Buffer, Autonomous Crons, and battle-tested patterns. |
| **qmd** | Search markdown knowledge bases, notes, and documentation using QMD. Use when users ask to search notes, find documents, or look up information. |
| **racket-id-booking** | Book padel courts on racket.id. Supports court availability lookup and booking at Blue Padel and other venues. |
| **self-improving-agent** | Captures learnings, errors, and corrections to enable continuous improvement. Use when a command fails or user corrects Claude. |
| **skill-creator** | Guide for creating effective skills. Use when users want to create or update a skill that extends Claude's capabilities. |
| **summarize** | Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube). |
| **superpowers** | Spec-first, TDD, subagent-driven software development workflow. Triggers brainstorm → plan → subagent execution loop for building features, debugging, and completing branches. |
| **web-deploy-github** | Create and deploy single-page static websites to GitHub Pages with autonomous workflow. Use for portfolio sites, CV pages, and landing pages. |
| **webhook-gen** | Generate webhook handlers with retry logic using AI. Use when integrating Stripe, GitHub, or any webhook provider. |
| **web-search-plus** | Unified search skill with Intelligent Auto-Routing. Automatically selects between Serper (Google), Tavily (Research), and Exa (Neural) with confidence scoring. |
| **whoop-central** | WHOOP Central — OAuth + scripts to fetch WHOOP data (sleep, recovery, strain, workouts). |
| **withings-health** | Fetches health data from the Withings API including weight, body composition, activity, and sleep. |
| **yc-cold-outreach** | Expert in Y Combinator cold email outreach techniques based on Startup School principles. Use to draft, critique, or iterate on cold emails to customers, partners, or investors. |

## Migration Notes

- **Sources:** `~/clawd/skills/` (30 skills), `~/.openclaw/workspace-archimedes/skills/`, `~/.openclaw/workspace-platon/skills/`
- **Conflicts resolved:**
  - `superpowers`: clawd version (Mar 15) taken over archimedes (Feb 21) — clawd is newer
  - `github-issue-forge`: archimedes and platon versions were identical (Mar 17) — archimedes copy used
  - `last30days`: destination had broken symlink to `/home/gotvild/clawd/skills/last30days` — replaced with real copy from clawd
- **Workspace-only skills added:** `agent-orchestrator`, `ci-bootstrap-pro`, `github-issue-forge`

## Usage

Each skill lives in its own subdirectory with a `SKILL.md` file. Reference them in your OpenClaw config:

```
~/.openclaw/skills/<skill-name>/SKILL.md
```
