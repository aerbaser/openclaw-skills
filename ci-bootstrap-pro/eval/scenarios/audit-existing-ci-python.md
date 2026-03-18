# Scenario: harden existing Python CI

User request:
"Our Python repo already has CI but it is flaky and too permissive."

Expected behavior:
- reads existing workflows
- detects current commands from pyproject / requirements
- narrows permissions
- keeps privileged deploy logic separate
- preserves useful behavior while removing duplication
