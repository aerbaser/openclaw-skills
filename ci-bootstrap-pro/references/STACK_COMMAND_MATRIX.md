
# Stack Command Matrix

Use this as fallback guidance when the repo does not already define clear commands.

## Node / TypeScript
Install:
- `pnpm install --frozen-lockfile`
- `yarn --immutable`
- `npm ci`

Checks:
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`
- `pnpm build`

## Python
Install:
- `uv sync --frozen`
- `poetry install --no-interaction --sync`
- `python -m pip install -r requirements.txt`

Checks:
- `ruff check .`
- `mypy .`
- `pytest`

## Go
Checks:
- `go vet ./...`
- `go test ./...`
- `go build ./...`

## Rust
Checks:
- `cargo fmt --all --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --all-targets`
- `cargo build --workspace`

## Java
Maven:
- `mvn -B test`
- `mvn -B verify`

Gradle:
- `./gradlew test`
- `./gradlew build`

## .NET
Checks:
- `dotnet restore`
- `dotnet build --no-restore`
- `dotnet test --no-build`

## Ruby
Checks:
- `bundle install --jobs 4 --retry 3`
- `bundle exec rspec`

## Generic Make / just
Use:
- `make lint`
- `make test`
- `make build`
- `just lint`
- `just test`
- `just build`
only if the targets actually exist.
