# PRD — ShipSafe

## Problem and user

Small teams often test only the **new** application against the **new** database. During a rolling release, the old application may still run alongside the new one, and a rollback may put the old version back after the new version has written data. A migration that works for the new app can therefore still break production.

**User:** developer or release lead about to deploy an app plus a database change.

**Job:** run a local, repeatable release rehearsal and get an evidence-backed GO/BLOCK decision, then use IBM Bob IDE to fix a blocked release.

## One demo scenario

A tiny order API uses SQLite. Version 1 stores `orders(id, customer_label, address, status)`. It can create, fetch, and list orders. Version 2 adds an *optional* `delivery_window` (e.g., `9–12`) to orders. The provided fixture contains at least five fictional orders, including missing or unusual but valid field values. Neither passwords nor real customer details are needed.

The initial candidate migration is **unsafe**: it attempts `ALTER TABLE orders ADD COLUMN delivery_window TEXT NOT NULL` on a populated table without a default. SQLite rejects it. This is the visible failure to investigate. The desired solution is an **additive, compatible** migration: preexisting rows remain valid without a delivery window; the old app keeps working; the new app can create an order with a window; and the old app can still operate after a rollback. IBM Bob should discover and implement the specific safe fix.

For clarity, the app versions can be two small Python modules exposing functions and/or HTTP endpoints. The rehearsal must exercise the actual application code and a real SQLite database, not string-match files or print prewritten verdicts.

## Required gates

1. **Migration:** initialize a *fresh temporary copy* of the populated v1 database, run the candidate SQL, capture actual success/failure and stderr or exception details.
2. **Preservation:** count and read the seeded orders before and after migration. IDs, customer labels, addresses and statuses must remain intact.
3. **Old version during rollout:** on the migrated database, v1 can read an existing order and create a new order using its existing interface.
4. **New version after rollout:** on the same database, v2 reads an old order gracefully and creates an order with `delivery_window`; old orders may have no window.
5. **Rollback:** after v2 has written its order, v1 can list/read that order and create another one using the migrated database. Rollback means switching **application version**, not undoing the schema migration.
6. **Repeatability:** a second rehearsal starts with a clean database and produces the same result. Never mutate the checked-in fixture or a user's own DB.

Any failed gate means **BLOCK**. All gates passing means **GO for this simulated scenario**. The report must identify what was checked; it must not imply a production deployment is universally safe.

## Deliverables and acceptance

- `python -m shipsafe rehearse --migration migrations/candidate.sql --json out/report.json` runs the gates and exits nonzero on BLOCK; other CLI syntax is fine if documented and stable.
- A readable terminal table plus machine-readable JSON report with gate ID, result, evidence, summary, and actual timing. Exclude fake precision and invented time savings.
- A deterministic, synthetic seed fixture with provenance explained in `DATA.md` or README.
- A before/after artifact pair: unsafe candidate saved under `examples/unsafe.sql`; repaired migration at `migrations/candidate.sql`. The unsafe file remains an exhibit, not the migration selected for the final run.
- Meaningful tests for rehearsal logic and compatibility. A deliberate unsafe-migration test must remain red only in its expected-negative assertion, while the main final test suite passes.
- A short `out/release-decision.md` generated from actual gate results. Bob writes or improves the explanatory root-cause and remediation section after verifying the evidence.
- Evidence of Bob's actual work, including relevant task session screenshots in `bob_sessions/`.

## Out of scope for the 48-hour build

Production deployment, real cloud infrastructure, secrets, real customer data, arbitrary-language repository scanning, CI integrations, generic SQL migration analysis, LLM scoring of safety, a polished dashboard, authentication, and multiple example apps. A CLI and clear report are enough. If time remains, a minimal web report viewer may be added **after** all gates pass.

## Honest impact measurement

Record the baseline: the candidate migration fails with a real error and blocks the rehearsal. Record the final result: all required gates pass on a clean run. Report observed elapsed time if measured. Do not claim a measured productivity gain unless you actually run and document a comparable manual baseline.
