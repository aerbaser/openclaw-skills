# Ruleset Policy

Target state for a managed repo:

- protect default branch;
- require pull request before merge;
- require passing status checks for CI and security jobs that matter;
- require conversation resolution before merge;
- block force-push unless intentionally allowed;
- block branch deletion on protected targets;
- require CODEOWNER review for critical paths when the repo has shared ownership.

Use evaluate mode first if you are rolling out across many repos.
