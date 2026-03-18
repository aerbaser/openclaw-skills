
# Actions Security Audit

Audit for these first:

- missing top-level `permissions`
- `permissions: write-all`
- `pull_request_target` with checkout or attacker-controlled refs
- third-party actions pinned to floating refs
- release or deploy logic mixed with untrusted PR execution
- unnecessary secret use in CI

Then look for:
- stale workflows
- duplicate workflows
- dead environment assumptions
