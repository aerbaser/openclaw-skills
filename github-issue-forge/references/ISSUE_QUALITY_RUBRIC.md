# Issue Quality Rubric

Score every draft against this rubric before posting.

## 1. Executability
A good issue tells a worker exactly what to do next.

Pass when:
- the problem is concrete
- the desired outcome is observable
- the issue is not an umbrella or brainstorming note
- the worker can start from the body without asking for basics

Fail examples:
- "Investigate auth problems"
- "Improve performance"
- "Clean up the API layer"

## 2. Scope control
Pass when:
- the issue can plausibly ship as one PR
- non-goals are explicit
- hidden migrations or follow-up work are called out separately

Fail examples:
- bug fix + refactor + migration + docs rewrite in one issue
- "while you're here" scope creep

## 3. Code awareness
Pass when:
- the issue names real files, modules, commands, workflows, or tests
- it reflects how the repository is actually structured

Fail examples:
- generic references like "backend", "frontend", "the service layer"

## 4. Validation quality
Pass when:
- acceptance criteria are checkable
- verification commands are real for the repo
- tests or checks are mentioned explicitly

Fail examples:
- "works correctly"
- "looks good"
- no commands, no checks, no success definition

## 5. Adjacency handling
Pass when:
- duplicates were checked
- related PRs/issues are linked
- overlap is resolved with boundaries, not ignored

## 6. Honest uncertainty
Pass when:
- assumptions are labeled
- unresolved questions are explicit and minimal

Fail examples:
- stating guesses as facts
- hiding uncertainty in vague language

## Hard fail conditions

Do **not** post if any of these is true:
- no `Affected Areas`
- no `Acceptance Criteria`
- no `Verification`
- obvious duplicate exists
- the body depends on context that is not written down
