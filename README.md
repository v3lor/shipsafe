# ShipSafe

ShipSafe rehearses a database migration against a copy of realistic synthetic data before the release goes out. It checks five things in order on the same temporary SQLite database: whether the migration runs, whether existing rows survive, whether the old app version still works on the migrated data, whether the new app version works, and whether rolling back to the old app still works after the new app has written a row. Each gate produces a JSON evidence object. The final verdict is **GO** only when all five gates pass; any FAIL or SKIP produces **BLOCK**.

**IBM Bob IDE** investigated the failing migration, identified the root cause, designed and implemented the safe fix, reran all checks, and produced the release decision.

## Live demo

**[https://v3lor.github.io/shipsafe/](https://v3lor.github.io/shipsafe/)** · [About ShipSafe](https://v3lor.github.io/shipsafe/about.html)

Open the report viewer and click **"Load example (BLOCK → GO)"** to instantly see the full before/after comparison with the two committed demo reports.

## The scenario

The sample app (`shipsafe/app_v1.py`, `shipsafe/app_v2.py`) tracks delivery orders. A planned v2 adds a `delivery_window` column. The unsafe first attempt (`examples/unsafe.sql`) declares the column `NOT NULL` with no default, which SQLite rejects when existing rows have no value for it. All four dependent gates are skipped and the verdict is **BLOCK**.

The safe migration (`migrations/candidate.sql`) uses `ADD COLUMN … DEFAULT NULL`, which SQLite accepts for rows already in the table. The new app treats a `NULL` delivery window as "not yet assigned". The old app ignores the new column entirely. Rollback — switching back to v1 after v2 has written a row — still reads and writes correctly because v1's queries are column-explicit and never reference `delivery_window`.

## Five gates

| Gate | What it checks |
|------|---------------|
| **migration** | `sqlite3.executescript` applies the candidate SQL without error |
| **preservation** | All five seeded rows survive the migration unchanged |
| **old-version** | `app_v1.get_order` reads a seed row; `app_v1.create_order` writes a new one |
| **new-version** | `app_v2.get_order` reads a legacy row (NULL delivery_window); `app_v2.create_order` writes with a window value |
| **rollback** | `app_v1.get_order` reads the v2-written row; `app_v1.create_order` writes again; `PRAGMA table_info` records observed column names |

`decision()` in `shipsafe/rehearse.py` blocks on any FAIL or SKIP gate, verified by ten parameterised pytest cases.

## Genuine evidence

Both captured runs are committed verbatim in [`evidence/`](evidence/):

- [`evidence/red-run.json`](evidence/red-run.json) / [`evidence/red-run.md`](evidence/red-run.md) — BLOCK, `examples/unsafe.sql`, `OperationalError`
- [`evidence/green-run.json`](evidence/green-run.json) / [`evidence/green-run.md`](evidence/green-run.md) — GO, `migrations/candidate.sql`, all five gates PASS

The demo reports served by the live viewer are copies of these files (`demo/red.json`, `demo/green.json`).

Bob session screenshots (IBM Bob IDE task summaries) are in [`bob_sessions/`](bob_sessions/).

## Run the CLI yourself

```sh
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

python -m pip install -e ".[test]"
```

**Red run** — reproduce the original failure:

```sh
python -m shipsafe rehearse --migration examples/unsafe.sql --json out/unsafe.json
# exits 1 (BLOCK); migration gate FAIL, four gates SKIP
```

**Green run** — reproduce the repaired release:

```sh
python -m shipsafe rehearse --migration migrations/candidate.sql --json out/report.json
# exits 0 (GO); all five gates PASS
```

JSON is written to the path you specify. Markdown defaults to `out/release-decision.md` (override with `--markdown PATH`). Exit codes: `0` = GO, `1` = BLOCK, `2` = CLI/input/output error.

Every run creates a fresh temporary database, seeds five deterministic synthetic rows, runs the gates, then deletes the database. The `out/` directory is gitignored; load your generated files with the viewer's file pickers.

## Run the tests

```sh
python -m pytest -q
```

Twenty-three tests pass. The test suite includes a case that asserts `examples/unsafe.sql` genuinely fails with `OperationalError` (not a hardcoded result), parameterised tests that verify `decision()` blocks on each possible FAIL/SKIP combination, and integration tests that run real gates on a test-only schema.

## IBM Bob's role

Bob opened this repository in Bob IDE with the failing rehearsal already committed. Using the IDE's agent and plan modes, Bob:

1. Read the real `evidence/red-run.json` output and identified `OperationalError: Cannot add a NOT NULL column with default value NULL`.
2. Traced the failure to `examples/unsafe.sql`'s `ADD COLUMN delivery_window TEXT NOT NULL` declaration.
3. Designed the safe fix: `ADD COLUMN delivery_window TEXT DEFAULT NULL`, which SQLite accepts for existing rows.
4. Edited `migrations/candidate.sql`, reran the rehearsal, confirmed all five gates PASS, and verified the pytest suite still passes.
5. Audited the gate evidence objects for fabricated claims; found and fixed three issues (documented in `LIMITATIONS.md`).
6. Produced the committed green evidence and session screenshots.

Bob's task session screenshots are in `bob_sessions/`.

## Report viewer

Open [`report-viewer.html`](report-viewer.html) in a browser. For the **Load example** button, serve over HTTP:

```sh
python -m http.server 8000
# open http://localhost:8000/report-viewer.html
```

Opening the file directly (`file://`) still works for the file pickers.

## Limitations

ShipSafe is a local SQLite simulation, not a production migration plan. Full details in [`LIMITATIONS.md`](LIMITATIONS.md). Key points:

- The database is synthetic and temporary. No production data is ever read or written.
- SQLite behaviour differs from Postgres, MySQL, and other production RDBMS.
- The preservation gate checks only the five seeded rows.
- All gates run single-threaded; no concurrency or transaction-isolation testing.
- Elapsed seconds measure local wall-clock overhead, not database performance.
- `statements_in_script` counts non-empty semicolon-delimited segments of the SQL text before execution — a text property, not a count of statements SQLite actually ran.

## Repository layout

```
shipsafe/           Python package — rehearse.py, report.py, app_v1.py, app_v2.py, seed.py
migrations/         candidate.sql  — the safe, repaired migration
examples/           unsafe.sql     — the original unsafe migration (kept as regression exhibit)
tests/              test_rehearsal.py — 23 pytest cases
evidence/           captured red and green runs (JSON + Markdown)
demo/               red.json, green.json — copies served by the live viewer
bob_sessions/       IBM Bob IDE task session screenshots
out/                runtime output directory (gitignored)
```

## Hackathon

IBM Bob 2.0 Hackathon, September 25–27, 2026.
