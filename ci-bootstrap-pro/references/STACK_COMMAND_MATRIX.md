# Stack Command Matrix

## Node / React
Install:
- `npm ci`
- `pnpm install --frozen-lockfile`
- `yarn --immutable`

Common checks:
- `npm run lint`
- `npm run typecheck`
- `npm test -- --runInBand` (Jest/CRA)
- `npx vitest run` (Vite projects)
- `npm run build`

React-specific notes:
- Set `CI=true` env var when running Jest — makes warnings into errors
- For Vite: prefer `vitest` over Jest; detect via `"vitest"` in devDependencies
- Template: `react-ci.yml`

## Solidity (Hardhat)
Install:
- `npm ci`

Common checks:
- `npx hardhat compile`
- `npx hardhat test`
- `npx hardhat coverage` (optional, slow)
- `npx solhint 'contracts/**/*.sol'`

Notes:
- Hardhat runs on Node; treat as Node repo for install steps
- Keep compile + test in one job; coverage as separate optional job
- Template: `solidity-hardhat-ci.yml`

## Solidity (Foundry)
Install:
- `foundry-rs/foundry-toolchain@v1` GitHub Action (installs forge, cast, anvil)
- Submodules: `actions/checkout@v4` with `submodules: recursive`

Common checks:
- `forge fmt --check`
- `forge build --sizes`
- `forge test -vvv`
- `forge coverage --report summary` (optional)
- `solhint 'src/**/*.sol'` (separate lint job)

Notes:
- Foundry is self-contained; no npm install needed unless you mix with Hardhat scripts
- `foundry.toml` is the config file — check for custom remappings
- Template: `solidity-foundry-ci.yml`

## Python
Install:
- `pip install -r requirements.txt`
- `uv sync --frozen`
- `poetry install --no-interaction --sync`

Common checks:
- `ruff check .`
- `pytest`
- `mypy .`

## Go
Install: (modules auto-downloaded)
Common checks:
- `go vet ./...`
- `go test ./...`
- `golangci-lint run` (if configured)

## Rust
Install: (cargo auto-downloads)
Common checks:
- `cargo fmt --check`
- `cargo clippy --all-targets -- -D warnings`
- `cargo test --all-features`

## Java (Maven)
Install:
- `mvn -B dependency:resolve` (optional, cached via actions/setup-java)

Common checks:
- `mvn -B verify` (compile + test + package)
- `mvn -B test` (tests only)
- `mvn -B checkstyle:check` (if configured)

## Java (Gradle)
Install:
- `./gradlew dependencies` (optional)

Common checks:
- `./gradlew build`
- `./gradlew test`
- `./gradlew check`

## Ruby
Install:
- `bundle install` (or bundler-cache: true in setup-ruby)

Common checks:
- `bundle exec rake test`
- `bundle exec rspec`
- `bundle exec rubocop`
