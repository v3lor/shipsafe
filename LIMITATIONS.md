# ShipSafe — actual limitations

This document records the genuine boundaries of the rehearsal runner, identified
by code audit on 2026-09-25. All statements are verified against the source.

## What the rehearsal actually does

- Creates one fresh temporary SQLite database per run in a `tempfile.TemporaryDirectory`.
- Seeds five deterministic synthetic orders via `seed.py`; no real or production data.
- Applies the candidate SQL with `sqlite3.executescript`. A real SQLite error causes a real
  FAIL; no fake BLOCK is hardcoded.
- Runs five gates in order on **the same database throughout**: migration, preservation,
  old-version, new-version, rollback. Every gate calls live Python functions that execute
  real parameterized SQL against that database.
- Any FAIL or SKIP result forces verdict `BLOCK`. `GO` requires all five gates to pass
  and the gate list to be exactly `GATES` in order (verified by `decision()`).
- Cleans up the temporary directory at exit regardless of outcome.

## What it does NOT do

- **Not a production test.** The database is synthetic and local. No production, staging,
  or real-application database is ever read or written.
- **Not a migration dry-run against production.** SQLite and production RDBMS (Postgres,
  MySQL, etc.) behave differently. This tool cannot substitute for a real migration plan.
- **No row-level data preservation beyond the five seeded rows.** The preservation gate
  only checks that the five seed records are identical after migration. It does not
  enumerate or validate any other rows.
- **No concurrent-access or transaction-isolation testing.** All gates run single-threaded
  on a single connection per operation.
- **No performance measurement.** Elapsed seconds reflect local wall-clock time on an
  idle machine; they measure tool overhead, not migration speed or database performance.
  The report explicitly labels them "measured locally" and does not claim anything about
  production speed.
- **No schema round-trip beyond what `app_v1`/`app_v2` explicitly SELECT.** Both apps
  use column-explicit queries. The rollback gate now records observed column names via
  `PRAGMA table_info`, but does not assert anything beyond their presence.
- **No per-statement execution feedback.** `sqlite3.executescript` returns `rowcount=-1`
  and no per-statement metadata. `migrate()` counts non-empty semicolon-delimited
  segments of the input text and reports them as `statements_in_script` — a property of
  the SQL text before execution, not a count of statements actually executed by SQLite.
  This count is approximate for SQL containing semicolons inside string literals or
  block comments.

## Fabricated-claim audit (2026-09-25)

The following defects were found and fixed in this session:

### Fixed: `rollback()` returned `"schema_unchanged": True` (hardcoded)

**Before:** `rollback()` returned `{"...", "schema_unchanged": True}` unconditionally.
No schema inspection was performed. This was an invented claim.

**After:** `rollback()` now reads `PRAGMA table_info(orders)` and returns
`"orders_columns": [<observed column names>]`. The caller can verify schema presence;
no assertion about "unchanged" is made by the tool itself.

### Fixed: `migrate()` returned a hardcoded summary string, then a misleading key name

**Before (first):** `migrate()` returned `{"summary": "SQLite executed the candidate SQL"}` —
a static string regardless of what SQL ran.

**Before (second):** An intermediate key `statements_executed` implied SQLite reported
per-statement execution counts, but `sqlite3.executescript` returns `rowcount=-1` and
provides no such feedback.

**After:** `migrate()` returns `{"statements_in_script": N}` where N is the count of
non-empty semicolon-delimited segments of the SQL text. The key name is explicit that
this is a property of the input text, not a measurement of what SQLite executed.

### Fixed: markdown report printed `None` for skipped-gate elapsed seconds

**Before:** `report.py` emitted `"Measured seconds: None"` for SKIP gates, which is
misleading (implies a measurement of zero was taken).

**After:** SKIP gates display `"Measured seconds: not measured (gate skipped)"`.

## Verified correct behaviors

- Every gate invokes real SQLite operations; no gate result is hardcoded.
- `decision()` blocks on any SKIP gate (not only FAIL), verified by 10 parameterized tests.
- Rollback and new-version gates operate on the same database path (passed by closure
  over `db_path` in `rehearse()`), verified by `test_orchestration_go_with_test_only_schema`.
- Temp directories are deleted after each run, verified by
  `test_repeatability_fixture_unchanged_and_temp_cleanup`.
- FAIL gate stops execution; all later gates are SKIP, verified by
  `test_real_gate_failures_propagate` for four different failure cases.
- The CLI returns exit code 1 for BLOCK and 0 for GO.
- No scope text in any report claims production safety.
