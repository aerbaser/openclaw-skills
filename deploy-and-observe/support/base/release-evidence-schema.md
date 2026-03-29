# release-evidence-schema.md

## Required fields

- `task_id`
- `release_id`
- `deployment_profile`
- `environment`
- `artifact_ref`
- `deployed_version`
- `promotion_path`
- `deploy_started_at`
- `deploy_finished_at`
- `smoke_results`
- `observe_window_result`
- `rollback_performed`
- `rollback_target`
- `final_release_decision`
- `evidence_refs`
- `operator`

## Semantics

`final_release_decision` must be one of:
- `promoted`
- `held`
- `rolled_back`
- `aborted`

`evidence_refs` should point to:
- logs
- screenshots if UI route
- endpoint snapshots
- version stamps
- issue/PR/review refs if relevant
