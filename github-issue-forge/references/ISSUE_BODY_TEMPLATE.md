
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

## Non-Goals
- explicit things the worker should not change
- adjacent cleanups that are intentionally excluded
- future enhancements that belong in separate follow-up issues

## Acceptance Criteria
- [ ] criterion 1 is observable and specific
- [ ] criterion 2 is testable
- [ ] criterion 3 mentions the user-visible or system-visible outcome

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
- related issue / PR / ADR / docs links
- duplicate search results if relevant
- follow-up issues if the work was split

## Open Questions
- only include if a real ambiguity remains after scanning
```
