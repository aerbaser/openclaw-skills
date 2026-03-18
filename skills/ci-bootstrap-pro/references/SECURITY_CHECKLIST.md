# GitHub Actions Security Checklist

Use this every time you touch CI.

## Permissions

- Set top-level `permissions` explicitly on every workflow.
- Start with `contents: read`.
- Add writes only for jobs that truly need them.
- Never grant `write-all` or omit permissions in new workflows.

## Trigger safety

- Use `pull_request` for running build/test on incoming (untrusted) code.
- Avoid `pull_request_target` for executing PR code — it runs in the base branch context with full secrets access.
- Keep privileged jobs on trusted refs, protected branches, or protected environments.
- If `pull_request_target` is needed (e.g., labeling), do NOT checkout PR code in the same job.

## Secrets

- Do not echo secrets or print them to logs.
- Do not store cloud credentials as long-lived plaintext if OIDC can replace them.
- Mask non-secret sensitive values when needed.
- Secrets should not be required for normal PR validation from forks.

## Actions provenance

- Prefer first-party GitHub actions where they meet the need.
- For third-party actions, pin to a full commit SHA in hardened environments.
- Avoid random marketplace actions for simple shell tasks.
- Known safe third-party actions in our stack:
  - `dtolnay/rust-toolchain@stable`
  - `Swatinem/rust-cache@v2`
  - `foundry-rs/foundry-toolchain@v1`
  - `crytic/slither-action@v0.4.0`

## Concurrency

- Cancel stale runs for the same branch or PR.
- Prevent multiple deploys to the same environment from racing.
- Use `group: ci-${{ github.workflow }}-${{ github.ref }}` as the default group key.

## Artifacts and logs

- Upload only useful artifacts.
- Avoid dumping sensitive config into logs or artifacts.
- Do not commit build artifacts — use GitHub releases or registries.

## Runner assumptions

- Do not assume tool versions that the repo never declares.
- If the project depends on a runtime version, set it explicitly with the appropriate setup action.

## Solidity-specific

- Never store private keys or mnemonics for mainnet deploys in Actions secrets.
- Use a dedicated deployer wallet with minimum balance — never fund the deployer from CI.
- Slither SARIF upload requires `security-events: write` permission.
- Fork mainnet tests use `FORK_URL` secret → Anvil `--fork-url`; this is safe and should only run in `ci.yml`, not `deploy.yml`.
