# Issue Quality Rubric

Score every draft before posting. Use 0–2 per category (10+ points = acceptable; 12+ = good).

---

## 1. Scope clarity
- 0 = broad / mushy / multi-project
- 1 = mostly scoped but still leaks
- 2 = atomic and mergeable in one PR

## 2. Codebase grounding
- 0 = generic, no paths
- 1 = mentions areas loosely
- 2 = exact files / modules / workflows named

## 3. Acceptance criteria
- 0 = subjective or vague
- 1 = partly testable
- 2 = crisp, observable, complete checkboxes

## 4. Verification
- 0 = missing
- 1 = generic commands
- 2 = repo-real commands with expected outcome

## 5. Constraint handling
- 0 = ignores architecture / compatibility limits
- 1 = partial
- 2 = explicit and useful non-goals / constraints

## 6. Handoff quality
- 0 = worker will ask follow-ups immediately
- 1 = mostly self-sufficient
- 2 = implementation-ready, no basic follow-ups needed

---

## Blocking failures (automatic lint rejection)

Any of these fails the issue regardless of score:
- missing `Affected Areas`
- missing `Non-goals`
- missing `Acceptance Criteria`
- missing `Verification`
- zero checkboxes in acceptance criteria
- no file paths or modules named
- body < 3 meaningful sentences
- obvious duplicate exists and is not addressed
- title is vague: "fix stuff", "cleanup", "improve"

---

## Complexity heuristic

| Label  | Signals |
|--------|---------|
| small  | 1–2 files, no schema changes, <2h, existing tests cover it |
| medium | 3–7 files, possible API/schema changes, new tests needed |
| large  | cross-cutting, >7 files, migration, new subsystem, agent needs to plan first |

---

## Common vague verbs to replace

| Vague | Better |
|-------|--------|
| clean up | extract / remove / rename / consolidate |
| improve | reduce latency from X to Y / increase coverage to 80% |
| support | add endpoint / add field / add flag |
| handle properly | return 400 when / log and retry when / skip when |
| make better | shrink bundle by / reduce queries from N to 1 |
