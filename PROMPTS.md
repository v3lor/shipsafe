# Copy-and-paste prompts

## Prompt A — Codex: build the scaffold, stop at a genuine failed rehearsal

```text
Build the ShipSafe hackathon project in this repository. Read README.md, PRD.md, ARCHITECTURE.md, TASKS.md, and DEMO.md first. Follow their MVP scope closely.

This is a developer release-rehearsal tool. Implement a tiny Python/SQLite order app with v1 and v2 code, synthetic seed orders, a deterministic CLI rehearsal runner, genuine database/app gates, JSON and Markdown output, and meaningful pytest tests. The candidate migration MUST initially be unsafe: ALTER TABLE orders ADD COLUMN delivery_window TEXT NOT NULL without a default on a populated table. Keep the same SQL in examples/unsafe.sql. It must fail naturally in SQLite and yield BLOCK with a real captured error. Do not fake a failure, hardcode a verdict, or implement the safe migration yet.

Use a fresh temporary database per rehearsal. Never modify a checked-in fixture. Include migration, preservation, old-version, new-version, and rollback checks; mark dependent gates SKIP when migration fails. The v1 and v2 operations must later be exercised against the same migrated database. Make the main CLI command and test command obvious in README.md. Put the synthetic dataset provenance in DATA.md.

Run the tests and CLI. Fix scaffold defects but deliberately leave the candidate migration unsafe for IBM Bob IDE to investigate and repair. When finished, give me: changed files, install/run commands, observed CLI verdict and underlying SQLite error, test results, and the exact handoff point for Bob. Stop before editing candidate.sql to a safe migration.
```

## Prompt B — IBM Bob IDE: the central investigation and fix

```text
You are the release engineer for ShipSafe. Read PRD.md, ARCHITECTURE.md, DATA.md, and the code. First run the documented release rehearsal and inspect its real output. Explain which gate fails and why from the actual code and SQLite result. Do not assume the intended fix is sufficient without testing it.

Plan and implement a safe additive rollout for the optional delivery_window field. Keep examples/unsafe.sql as a record of the original failed candidate. Repair migrations/candidate.sql and any app or test logic needed so that: seeded data survives; v1 works on the migrated database; v2 reads old orders and creates an order with a delivery window; and v1 works again after that v2 write. The rollback check switches app version on the same migrated database; it must not roll back the schema.

Run the rehearsal and all relevant tests. If any gate fails, investigate and fix it. Produce out/release-decision.md from actual result data, with GO or BLOCK, each gate's evidence, root cause of the original failure, exact remediation, and clear limitations of this local simulation. Keep commands reproducible. Finally review your own changes for false positives, fake evidence, skipped gates, or fixture mutation. Summarize what you changed and the real command outputs.
```

## Prompt C — IBM Bob IDE: final review, if time remains

```text
Review the ShipSafe repository as a skeptical release reviewer. Run from a clean temporary state. Check that every required gate actually invokes real code and real SQLite operations, uses the same migrated DB across rollout and rollback checks, and that any FAIL or SKIP forces BLOCK. Confirm no report contains invented speed improvements or claims about production safety. Fix concrete defects you find, rerun the tests and rehearsal, and document actual limitations.
```

## If you want a UI after the CLI is done

```text
Only after the CLI rehearsal, tests, and Bob evidence work: build a tiny read-only report page that loads the JSON produced by the CLI and shows the GO/BLOCK verdict, gate statuses, and evidence. Do not replace real CLI checks with mock results. Keep setup under five minutes and preserve the CLI as the source of truth.
```
