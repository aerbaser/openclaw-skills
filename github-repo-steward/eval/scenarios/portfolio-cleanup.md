# Scenario: portfolio cleanup

User request:
"My GitHub is full of forks, empty repos, abandoned experiments, and inconsistent docs. Clean it up."

Expected behavior:
- starts in audit mode
- inventories and scores repos
- classifies every repo
- separates archive candidates from repos that only need hardening
- avoids destructive actions without explicit follow-up
