# GitHub Actions Security Checklist

Use this every time you touch CI.

## Permissions
- Set top-level `permissions` explicitly.
- Start with `contents: read`.
- Add writes only for jobs that truly need them.

## Trigger safety
- Use `pull_request` for running build/test on incoming code.
- Avoid `pull_request_target` for executing PR code.
- Keep privileged jobs on trusted refs, protected branches, or protected environments.

## Secrets
- Do not echo secrets.
- Do not store cloud credentials as long-lived plaintext if OIDC can replace them.
- Mask non-secret sensitive values when needed.

## Actions provenance
- Prefer first-party GitHub actions where they meet the need.
- For third-party actions, pin to a full commit SHA in hardened environments.
- Avoid random marketplace actions for simple shell tasks.

## Concurrency
- Cancel stale runs for the same branch or PR.
- Prevent multiple deploys to the same environment from racing.

## Artifacts and logs
- Upload only useful artifacts.
- Avoid dumping sensitive config into logs or artifacts.

## Runner assumptions
- Do not assume tool versions that the repo never declares.
- If the project depends on a runtime version, set it explicitly with the appropriate setup action.
