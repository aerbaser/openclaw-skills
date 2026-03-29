
# Issue Body Template

Use this exact section order.

```md
## Summary
One short paragraph describing the change in repository-native language.

## Problem
Describe the current behavior, the gap, and why it matters.
Prefer concrete symptoms over abstract complaints.

## Desired Outcome
Describe the target behavior in observable terms.

## Affected Areas
- `path/to/file-or-dir`
- `another/path`
- module / package / workflow names if paths are not enough

## Constraints / Notes
- architecture limits
- compatibility requirements
- migration constraints
- sequencing notes
- assumptions that still need confirmation

## Layout Constraints _(UI/Frontend tasks only — omit for backend/infra)_
- Flex/Grid rules: e.g. `min-w-0` on text containers, `flex-wrap` behavior, overflow handling
- Responsive breakpoints: which breakpoints must be verified (mobile 375px / tablet 768px / desktop 1280px+)
- Typography: truncation rules (`truncate`, `line-clamp`), font-size floors
- Spacing system: Tailwind spacing units, no magic pixel values
- Container constraints: fixed vs fluid widths, sidebar/panel interaction
- Scroll regions: what scrolls independently, what clips
- Color/theme: dark mode, system preference, token usage

## Non-Goals
- explicit things the worker should not change
- adjacent cleanups that are intentionally excluded
- future enhancements that belong in separate follow-up issues

## Acceptance Criteria
- [ ] criterion 1 is observable and specific
- [ ] criterion 2 is testable
- [ ] criterion 3 mentions the user-visible or system-visible outcome

## Tests Required
- [ ] New test: `<describe what to test and where>`
- [ ] OR: existing test to update: `<path/to/test-file>`
- [ ] OR: no automated test possible — manual verification only (explain why)

## Verification
```bash
# exact commands the worker should run locally or in CI
```

Expected high-level result:
- tests pass
- lint passes
- behavior is covered
- no regressions in named paths

## Related Context
**Overlap check:** `gh issue list --state all --search "<keyword>"` → <result: "no overlap" OR "#N covers adjacent area — scope narrowed">
- Dependencies (must be done first): #N, #N
- Blocks: #N (this issue must be done before)
- Related PRs: #N
- Follow-up issues (intentionally excluded from scope): describe briefly

## Open Questions
- only include if a real ambiguity remains after scanning
```
