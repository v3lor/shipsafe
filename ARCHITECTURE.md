# Architecture and implementation contract

## Suggested stack

Python 3.11+ with standard-library `sqlite3`, `argparse`, `json`, `tempfile`, `subprocess` as needed; `pytest` for tests. FastAPI is optional: prefer small testable app functions if HTTP setup would delay the working rehearsal. No external AI API is required. **Bob IDE is the AI development tool** used to inspect, plan, modify, verify, and document the release workflow.

## Suggested repository tree

```text
shipsafe/
  README.md
  DATA.md
  PRD.md
  ARCHITECTURE.md
  TASKS.md
  PROMPTS.md
  DEMO.md
  pyproject.toml
  shipsafe/
    __init__.py
    __main__.py
    seed.py
    rehearse.py
    report.py
    app_v1.py
    app_v2.py
  migrations/
    candidate.sql
  examples/
    unsafe.sql
  tests/
    test_rehearsal.py
  bob_sessions/
    .gitkeep
  out/
    .gitkeep
```

`out/*.json` and `out/*.md` should be ignored by Git by default unless they are intentional demo evidence. Commit a small red report and a small green report under `evidence/` once each has been captured from actual runs; make filenames explicit.

## Rehearsal algorithm

1. Create a fresh temporary directory and SQLite database; seed deterministic synthetic v1 orders.
2. Capture baseline IDs, counts, and important field values.
3. Apply the selected migration to that temporary database through `sqlite3.executescript`. Record error if it fails. Never silently substitute a safe migration or continue with a misleading green verdict.
4. On success, run preservation, old-version, new-version, and rollback checks **in order on the same migrated database**. Capture meaningful errors and the state changes each check makes. Fail an affected gate if a prerequisite fails; mark later gates `SKIP` with a reason.
5. Build the decision from actual gate outcomes (`BLOCK` for FAIL or SKIP; `GO` only when all required gates PASS). Record elapsed time from the real run, not a constant.
6. Write JSON and Markdown from the same result object. Clean up temporary data automatically. Preserve sample input and any explicit output paths.

## Minimum app contract

- `app_v1.create_order(db_path, customer_label, address, status)` and `app_v1.get_order(db_path, order_id)` plus list or equivalent.
- `app_v2.create_order(db_path, customer_label, address, status, delivery_window=None)` and `app_v2.get_order(...)` plus list or equivalent.
- Both versions use parameterized SQL. The seed data is fictional and deterministic. Both versions validate necessary inputs enough for the demo.
- v1 cannot refer to `delivery_window`. v2 must handle legacy rows where `delivery_window` is NULL.
- The database path is injected, never hardcoded. Connections close reliably; writes commit.

## Bob's role in the actual workflow

Bob opens the working repository in the IDE, reads the real failed report and source, identifies the incompatible migration, proposes an additive rollout, edits the migration and any necessary v2 logic, reruns the rehearsal and tests, then writes a decision explaining evidence and limits. Bob may use Agent mode, Plan mode, code review, and subagents if available and useful. Do not describe these features as used unless they actually appear in the task evidence.

**Scope control:** Codex should not pre-implement the safe fix or fabricate Bob's findings. It builds the scaffold and honest failure; Bob performs the central repair. The program's CLI remains useful for repeated release rehearsals after the demo.
