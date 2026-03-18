# Canonical Issue Body Template

Use this exact structure unless the repository already enforces a stronger local format.

## Summary
One short paragraph. State the work item in plain engineering language.

## Problem
What is broken, missing, risky, or unnecessarily complex right now?

Include:
- current behavior or current gap
- why it matters now
- user, product, or maintenance impact
- evidence from code, tests, logs, docs, or issue history when available

## Desired Outcome
Describe the end state in observable terms.

## Scope
- What should change
- What should be added, removed, or refactored
- Which layers are in scope: API, UI, data, tests, docs, CI, migrations, config

## Out of Scope
- Explicit non-goals
- Follow-up ideas that should **not** be folded into this issue

## Affected Areas
List concrete files, packages, modules, workflows, or directories.

Example:
- `packages/core/src/auth/session.ts`
- `packages/web/app/api/auth/route.ts`
- `tests/auth/session.test.ts`

## Constraints / Implementation Notes
Capture facts that should guide implementation:
- architecture limits
- backward-compatibility requirements
- performance constraints
- rollout or migration limits
- API contracts
- naming conventions
- "do not change X in this issue"

## Acceptance Criteria
Use checkboxes. Each line should be independently testable.

Example:
- [ ] Refresh token failures no longer leave the session store in a partially-updated state.
- [ ] Existing successful refresh flows still pass current unit and integration tests.
- [ ] The worker adds or updates tests covering the failure and success paths.
- [ ] No public API shape changes are introduced.

## Verification
List the exact commands a worker should run.

```bash
# replace with repo-real commands
pnpm test --filter auth
pnpm lint
pnpm build
```

Also add one sentence describing what "green" means for this issue.

## Related Context
Link anything adjacent:
- related issues
- closed issues
- active PRs
- docs
- design notes
- incidents
- migrations
- code comments worth preserving

If nothing relevant exists, say `None found after repo/GitHub search.`

## Risks / Edge Cases
Call out the failure modes or subtleties the worker must not miss.
