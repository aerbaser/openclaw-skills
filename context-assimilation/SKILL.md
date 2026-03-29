---
name: context-assimilation
description: Use when work must start on an existing repo, product, brand, workflow, or system and the agent needs a factual context pack before research, design, or execution.
---

# context-assimilation

## Purpose
Extract facts before interpretation so brainstorm/research/design start from reality, not assumptions.

## Use for
- existing repo or product
- existing docs / brand / design system
- bugfix / improve-existing routes
- hybrid routes before full brainstorming

## Do not use for
- solution design
- tradeoff decisions
- prioritization
- rewriting the contract

## Inputs
- contract.json (from contract-router)
- repo tree (if build/improve route)
- docs, CLAUDE/AGENTS/memory files
- runtime inventory
- brand/product artifacts

## Outputs
- `context-pack.json` in task directory
- known constraints
- existing stack
- existing assets
- contradictions / unknowns
- reusable building blocks

## Scan order (deterministic)
1. Repo tree (`find . -name '*.md' -o -name 'package.json' -o -name 'Dockerfile' | head -50`)
2. Key docs (README, AGENTS.md, ARCHITECTURE.md if present)
3. Memory files (MEMORY.md, working-buffer.json)
4. Runtime inventory (systemctl --user list-units, ports)
5. Brand/assets (if design route)

## context-pack.json schema
```json
{
  "task_id": "tsk_...",
  "generated_at": "ISO-8601",
  "facts": [],
  "inferred_patterns": [],
  "unknowns": [],
  "contradictions": [],
  "reusable_building_blocks": [],
  "blockers": []
}
```

## Boundaries
- This is a factual layer, not a design layer.
- Must not duplicate brainstorming or external research.
- Must not silently hide contradictions — surface them explicitly.
- Separate facts (with evidence), inferred patterns (with basis), and unknowns.

## Required procedure
1. Read contract.json from task directory.
2. Scan in deterministic order above.
3. Capture evidence-backed facts only.
4. Separate facts, inferred patterns, unknowns.
5. Write context-pack.json to `~/clawd/tasks/<task_id>/context-pack.json`.
6. Update task status: `node ~/clawd/scripts/task-store.js transition <task_id> CONTEXT --owner Sokrat --next_action "brainstorm or research"`
7. Escalate only genuine blockers or contradictions.

## Handoff contract
- Brainstorming and research consume `context-pack.json` as preflight input.
- Never skip this step for improve/bugfix routes.

## Source: ao-v8.2 bundle
- ~/clawd/docs/ao-v8.2/03-skills/context-assimilation.SKILL.md
