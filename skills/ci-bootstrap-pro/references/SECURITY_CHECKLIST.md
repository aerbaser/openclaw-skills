
# Security Checklist

## Mandatory

- top-level `permissions` exists
- top-level `concurrency` exists
- `pull_request` is used for untrusted code
- `pull_request_target` is not used to checkout or execute attacker-controlled code
- deploy or publish steps are not mixed into untrusted PR execution
- secrets are not echoed or needlessly exposed

## Strongly recommended

- first-party setup actions where possible
- pinned major versions at minimum; full commit pinning for high-risk third-party actions when warranted
- environment protection for deployment workflows
- OIDC instead of long-lived cloud credentials where the platform supports it

## Smells

- `permissions: write-all`
- missing `permissions`
- missing `concurrency`
- `pull_request_target` with checkout of `${{ github.event.pull_request.head.sha }}`
- third-party action pinned to `main`, `master`, or another floating branch
- unnecessary `contents: write`
