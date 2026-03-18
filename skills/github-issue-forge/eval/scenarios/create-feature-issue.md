# Scenario: create feature issue

User request:
"Scan this repo and open an issue to add workspace-level billing alerts."

Expected behavior:
- scans the repo first
- checks related issues / PRs if `gh` is available
- drafts an issue using the canonical section structure
- includes exact code paths and verification commands
- avoids mixing billing alerts with unrelated notification cleanup
