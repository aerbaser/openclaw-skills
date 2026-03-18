# Actions Security Notes

## Minimum baseline
- explicitly set `permissions`;
- prefer `contents: read` unless a job genuinely needs more;
- treat `pull_request_target` as privileged;
- separate CI for untrusted PR code from deploy/write operations;
- use `concurrency` to cancel stale runs when appropriate.

## Solidity / Smart Contract specific
- Run **Slither** on every PR — catches reentrancy, access control, and other vuln classes statically.
- Never store private keys or mnemonics in Actions secrets for mainnet — use a dedicated deployer wallet.
- Fork mainnet for integration tests (`FORK_URL` secret → Anvil `--fork-url`); never test against live RPC in PR CI.
- Keep Hardhat/Foundry test networks isolated from deploy scripts in the same workflow.
- Separate `test` (safe, any PR) from `deploy` (protected branch only, manual trigger or workflow_dispatch).
- `crytic/slither-action` uploads SARIF to GitHub Security tab — requires `security-events: write`.

## React / Frontend specific
- Set `CI=true` for Jest — turns warnings into hard errors.
- Never expose `NEXT_PUBLIC_*` secrets with real values in PR CI; use placeholder values.
- Build artifact should not be deployed from untrusted PR workflows.
