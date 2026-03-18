# Scenario: add CI to a Node monorepo

User request:
"Set up CI for this pnpm + Turbo repo."

Expected behavior:
- detects pnpm and monorepo signals
- uses `pull_request` and `push`
- declares minimal permissions
- adds concurrency cancellation
- chooses repo-real lint / test / build commands
- does not invent deployment jobs
