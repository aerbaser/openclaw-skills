
# Code Scanning Guide

## Decision rule

Prefer GitHub default setup when:
- admin rights are available,
- the repo is eligible,
- low maintenance is more valuable than workflow-level customization.

Use a committed CodeQL workflow when:
- settings-based setup is unavailable,
- the repo needs explicit workflow control,
- you need repo-local visibility of the scanning logic.

## Do not fake it
If you cannot enable default setup and do not add a workflow, do not claim code scanning is in place.
