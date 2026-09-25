# ShipSafe — start here

## Run the scaffold (Python 3.11+)

From this repository root:

```sh
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest -q
python -m shipsafe rehearse --migration migrations/candidate.sql --json out/report.json
```

The initial CLI deliberately exits **1 (BLOCK)**. SQLite rejects the candidate
with `Cannot add a NOT NULL column with default value NULL`. Migration is FAIL;
preservation, old-version, new-version, and rollback are SKIP. The pytest suite
should pass: the negative test asserts the real failure, not a failed test run.
Tests use `examples/unsafe.sql`, so Bob can repair the candidate without removing
the regression test. No safe migration is included in this scaffold.

JSON defaults to `out/report.json`; Markdown defaults to `out/release-decision.md`
(override with `--markdown PATH`). Exit codes: 0 = all five gates PASS, 1 = BLOCK,
2 = CLI/input/output error. No verdict is emitted for an unreadable migration.
Every rehearsal seeds five synthetic records into a unique temporary database,
then deletes it. No production/fixture database path is accepted. Rollout and
rollback gates use the same database and invoke real app functions. Rollback
switches back to v1 without undoing schema changes. Outcomes are deterministic;
measured timings naturally vary. Run only trusted local migration SQL.

See `DATA.md` for provenance and `evidence/` for the captured initial red run.
Downstream tests use a test-only v2 schema to verify gate behavior, not a repaired
release migration or green release evidence.

## Exact handoff to IBM Bob IDE

Open this repository in Bob IDE, run the commands above, inspect the actual
`out/report.json` and `out/release-decision.md`, then use **Prompt B in PROMPTS.md**.
The first repair belongs in `migrations/candidate.sql`, which is still identical
to `examples/unsafe.sql`. Investigate and implement the compatible rollout;
retain the unsafe exhibit. Rerun tests and the CLI, capture genuine green evidence,
and document the verified root cause/remediation. Add actual Bob session screenshots
to `bob_sessions/`. No repair, green release report, or Bob session is fabricated here.

**Pitch:** ShipSafe rehearses a software release against a copy of realistic sample data. It checks whether the migration runs, whether the current and new app versions work during rollout, whether rollback still works, and whether data survives. IBM Bob IDE investigates failed checks, repairs the rollout, and produces an evidence-backed release decision.

**Hackathon:** IBM Bob 2.0, September 25–27, 2026. Official guide: https://lablab-ibm-bob-2-hackathon-guide.s3.us.cloud-object-storage.appdomain.cloud/index.html . Read the current event page for submission times and requirements: https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon .

## Do this first — your actions

1. Register for the hackathon and form/join your team on lablab.ai. Check the event's exact submission deadline in your account; do not infer it from the date range.
2. Accept the IBM Bob invitation sent to the registration email, make an IBMid if needed, and install the current Bob IDE. Sign in with the **hackathon-provisioned** account. Confirm you are in the hackathon account before spending Bobcoins. Bob IDE is mandatory; Bob Shell and watsonx are optional.
3. Make a **new public GitHub repository** named `shipsafe` (or similar). Do not place this inside your capstone or Luqmar repository. Keep the dataset synthetic and the code created for this event.
4. Open the repository in Codex. Give Codex the six Markdown files in this package and paste **Prompt A** from `PROMPTS.md`. Ask it to commit only the scaffold and intentionally failing rehearsal. Run the scaffold yourself once and check it actually fails for the stated reason.
5. Open that same repository in Bob IDE. Paste **Prompt B**. Let Bob inspect the failed run, plan the repair, edit the migration/app, run the checks, and generate the release report. Use Bob for the central investigation and implementation; save meaningful Bob task session summaries.
6. Run the final rehearsal from a clean checkout. Record terminal output and the report. Make your demo video and any slides requested by the event submission form. Submit the repository and other required fields before the actual deadline.

## What you should see

- **Before Bob:** the rehearsal is red because an unsafe migration attempts to add a required `delivery_window` column while existing orders have no value. A real SQLite operation must fail; no hardcoded “red” result.
- **After Bob:** a safe additive migration succeeds; the old and new app versions both work on migrated data; rollback to the old app still works after a new app write; existing orders are preserved. The final report is green with genuine command output and a short explanation of the original failure and repair.
- **Optional stretch:** add a second scenario in which a new status value cannot be understood by the old app during rollback. Only attempt this after the first complete demo works.

## Division of work

| You | Codex | Bob IDE |
| --- | --- | --- |
| Registration, accounts, GitHub, decisions, run/record/demo/submission, check real results | Build the intentionally broken sample app and reusable rehearsal runner; document commands | Investigate failure, plan fix, implement safe rollout, run tests, generate decision report, review result |

**Critical rule:** using Bob only to write a README or generate screenshots does not fulfill this concept. Show Bob doing the release investigation and repair in the IDE. The guide requires relevant Bob task session summary screenshots under `bob_sessions/` in the final repository. Never create fake session screenshots.

## Files in this package

- `PRD.md`: precise problem, scenario, pass/fail gates and scope.
- `ARCHITECTURE.md`: repository structure and how the rehearsal should work.
- `TASKS.md`: build order and ownership.
- `PROMPTS.md`: ready-to-paste prompts for Codex and Bob.
- `DEMO.md`: demo script, evidence, and submission checklist.

All names and data in the sample app should be fictional. Do not use client data, personal information, company confidential information, or social-media data. The guide says participants bring their own datasets and document rights to public data if used. A synthetic dataset avoids that dependency.
