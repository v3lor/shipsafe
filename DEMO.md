# Demo, evidence, and submission

## Suggested 2–3 minute video script

| Time | Show | Say |
| --- | --- | --- |
| 0:00–0:20 | Old and new app versions, one migration | “Releases can fail even when the new app works. Old instances and rollback still need to work.” |
| 0:20–0:45 | Run unsafe migration through ShipSafe; real BLOCK and SQLite error | “This candidate tries to add a required field to orders that already exist. The rehearsal catches the failure before release.” |
| 0:45–1:25 | Bob IDE task: inspection, plan, file changes, real checks | “Bob investigates the failed gate, repairs the migration for a compatible rollout, and verifies old, new, and rollback paths.” |
| 1:25–2:10 | Rerun clean rehearsal; all gates PASS; report | “Here is the actual evidence: preserved records, v1 during rollout, v2 with new data, and v1 after switching back.” |
| 2:10–2:30 | Final report and limitations | “The decision is GO for this simulated release. Real deployment still needs environment-specific checks.” |

Record a screen capture of actual Bob actions, not only slides. If Bob cannot finish a fix, show honest BLOCK and explain what remains; do not edit the report to green.

## Evidence to retain

- `evidence/red-report.json` and `evidence/green-report.json` copied from real CLI runs, plus a short README with exact commands. Capture red evidence **before** Bob's fix.
- Test output and CLI exit statuses in the video or written README; count only gates that genuinely ran.
- `bob_sessions/` PNG screenshots for all relevant Bob IDE tasks per the official guide. In Bob IDE: Tasks → relevant task → task header → session consumption summary → screenshot. Use filenames such as `shipsafe_task01_investigation_summary.png`.
- A demo video, slides, repo link, and any deployment/demo URL the event form actually requires. Check the live form for exact fields and deadline.

## Useful numbers to report honestly

- `5/5 required gates pass` only if the actual gate report says so.
- Number of preexisting orders whose fields match after migration.
- Number of old/new/rollback operations actually executed.
- Measured elapsed seconds for each rehearsal, labeled as this local environment only.
- Do **not** claim “X hours saved” without a timed manual comparison.

## Final 10-minute check

- [ ] Repository is public and the correct commit is pushed.
- [ ] A fresh setup runs from README instructions.
- [ ] Red and green evidence matches the recorded commands and code versions.
- [ ] No real personal/customer data, secrets, or confidential data.
- [ ] Bob session screenshots are present and legible.
- [ ] Submission form fields, video access, and actual cutoff are checked.

Official guide: https://lablab-ibm-bob-2-hackathon-guide.s3.us.cloud-object-storage.appdomain.cloud/index.html
