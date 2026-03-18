
# Issue Quality Rubric

## Blocking failures

Do not post if any are true.

### B1. Missing structure
One or more required sections are missing.

### B2. No implementation surface
No exact file paths, modules, packages, or workflows are named.

### B3. Vague acceptance criteria
Acceptance criteria use words like:
- improve
- support
- clean up
- make better
without measurable conditions.

### B4. No verification commands
The issue gives no concrete way to validate the change.

### B5. Scope blob
The issue mixes unrelated workstreams that should be separate issues.

## Warnings

These do not block posting, but should be fixed when possible.

### W1. Assumptions are not labeled
Inferred facts look like confirmed facts.

### W2. Related work not linked
Adjacent issues or PRs are mentioned vaguely or not at all.

### W3. Non-goals are weak
The worker could still sprawl into adjacent cleanup.

### W4. Title is generic
Examples of weak titles:
- fix auth
- improve CI
- refactor utils

## Target quality bar

A strong issue should let another agent answer these immediately:
- where do I start?
- what files are likely in scope?
- what must not be changed?
- how do I know I’m done?
