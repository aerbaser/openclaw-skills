# Scenario: rewrite vague bug issue

User request:
"Rewrite issue #123, it just says sessions break randomly."

Expected behavior:
- reads the original issue
- inspects real session/auth code
- rewrites into a scoped, testable issue
- marks unknowns as open questions instead of pretending certainty
