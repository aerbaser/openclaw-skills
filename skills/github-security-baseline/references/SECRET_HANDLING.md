
# Secret Handling

## Baseline rules

- do not expose secrets to untrusted PR runs
- prefer environment protection or trusted branch workflows for deploy
- prefer short-lived cloud auth or OIDC where the platform supports it
- keep PR CI low privilege

## Smells

- secrets passed into every job by default
- deploy keys or cloud credentials in general CI
- workflows that blur test and release paths together
