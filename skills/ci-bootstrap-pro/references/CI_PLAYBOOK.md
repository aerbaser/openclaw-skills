# CI Playbook

Use this decision tree when bootstrapping CI.

## 1. Pick the default trigger set

Default:
- `push` to the default branch
- `pull_request` to the default branch
- `workflow_dispatch` when manual reruns are useful

Use `paths` filters only when they materially reduce noise, especially in monorepos.

## 2. Keep the default CI lane fast

Target:
- lint / typecheck / unit tests / build on PRs
- finish quickly enough that maintainers trust the signal

Move these out of the fast lane unless the repo explicitly depends on them for every PR:
- large integration suites
- cross-platform or multi-version matrices
- browser E2E
- deployment checks
- slow security scans

## 3. Use repository-native install commands

Node:
- npm → `npm ci`
- pnpm → `pnpm install --frozen-lockfile`
- Yarn Berry → `yarn --immutable`

Python:
- uv → `uv sync --frozen`
- Poetry → `poetry install --no-interaction --sync`
- pip → install from pinned requirements or lockfiles where available

Go:
- use `go test ./...`, `go vet ./...`, and `gofmt` checks when applicable

Rust:
- use `cargo fmt --check`, `cargo clippy`, `cargo test`, and `cargo build`

Java:
- Maven → `mvn -B verify`
- Gradle → `./gradlew build` or `./gradlew test`

.NET:
- `dotnet restore`
- `dotnet build --no-restore`
- `dotnet test --no-build`

Ruby:
- `bundle install`
- repo-native lint/test commands such as `bundle exec rspec` and `bundle exec rubocop`

React:
- `npm ci && npm run lint && npm run typecheck && npm test && npm run build`
- Set `CI=true` env var so Jest turns warnings into hard errors
- Vitest projects: `npx vitest run` instead of `npm test`

Solidity (Hardhat):
- `npm ci && npx hardhat compile && npx hardhat test`
- Optional coverage: `npx hardhat coverage` (slow, separate job)
- Lint: `npx solhint 'contracts/**/*.sol'`

Solidity (Foundry):
- `forge fmt --check && forge build --sizes && forge test -vvv`
- Uses `foundry-rs/foundry-toolchain@v1` action (no npm needed)
- With submodules: `actions/checkout@v4` with `submodules: recursive`

## 4. Prefer built-in caching through setup actions

Good:
- `actions/setup-node` with `cache: npm|pnpm|yarn`
- `actions/setup-python` with `cache: pip`
- `actions/setup-java` with `cache: gradle|maven`
- `actions/setup-go`
- `actions/setup-dotnet`
- `ruby/setup-ruby` with Bundler cache where appropriate
- `Swatinem/rust-cache` for Rust

Only drop to raw cache keys when the setup action cannot express the repository's real cache behavior.

## 5. Use matrices intentionally

Use a matrix only when:
- the project officially supports multiple runtime versions
- the project officially supports multiple OS targets
- you can keep runtime and cost acceptable

Avoid matrices for:
- small internal services with one production runtime
- repositories with fragile or expensive integration suites

## 6. Split workflows at trust boundaries

Safe default:
- `ci.yml` for pull requests and pushes
- `release.yml` or `deploy.yml` only for trusted refs and protected environments

Do not mix untrusted PR execution with secret-heavy deployment logic.

## 7. Solidity-specific CI decisions

- **Test vs deploy are completely separate workflows** — never deploy from PR CI
- Fork mainnet for integration tests via Anvil `--fork-url` (use `FORK_URL` secret)
- Slither security scan → separate workflow (see `github-security-baseline` skill)
- Hardhat and Foundry can coexist in one repo — detect via `foundry.toml` + `hardhat.config.*`

## 8. Validation checklist

Before finishing:
- [ ] commands exist locally
- [ ] lockfile strategy is consistent
- [ ] no redundant jobs
- [ ] no duplicate workflows with overlapping triggers
- [ ] branch names and paths filters match the actual repository
- [ ] artifact names are clear
