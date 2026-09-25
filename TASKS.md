# Tasks and handoff gates

## Phase 0 — Leen, about 30–60 minutes

- [ ] Verify registration, IBMid, hackathon Bob account, current Bob IDE and actual submission deadline.
- [ ] Create public `shipsafe` repo and put these Markdown files inside it.
- [ ] Check the event submission form for required URLs, video format, slides, and team membership.

## Phase 1 — Codex, target first working block

- [x] Initialize package, CLI, tests, Git ignore rules and simple install/run instructions.
- [x] Write v1 and v2 sample app functions, synthetic seed data, unsafe SQL candidate and rehearsal runner.
- [x] Gate runner uses a fresh temporary DB for every call and returns a genuine BLOCK caused by the migration.
- [x] Tests verify the unsafe candidate fails for the expected reason, fixture remains untouched, and report verdict follows the gate results.
- [x] Stop and show Leen the actual failing CLI output and repo status. Do **not** repair `candidate.sql` yet.

## Phase 2 — Leen + Bob IDE, core hackathon work

- [ ] Leen opens repo in Bob IDE and gives Bob Prompt B from `PROMPTS.md`.
- [ ] Bob explains the root cause from observed evidence, plans an additive migration, edits code/SQL as needed, runs the rehearsal and tests, and produces the final release decision.
- [ ] Leen checks that v1 and v2 operations truly ran against the same migrated DB; the test suite and clean CLI run pass.
- [ ] Save Bob task-session consumption summary screenshots in `bob_sessions/` with clear names. The guide requires **all relevant** sessions, from each participant who used Bob.

## Phase 3 — Presentation and submission

- [ ] Capture red and green terminal evidence from actual runs, including commands and exit status.
- [ ] Record a short video following `DEMO.md` and prepare the slides or links actually requested by the event.
- [ ] Check repository works from clean checkout using documented install commands.
- [ ] Push final repo; verify screenshots, video link, any app/demo link required by the form, and submit before deadline.

## Priority when time is tight

1. Real failing rehearsal.
2. Bob-led investigation and safe repair.
3. Real passing rehearsal and clear report.
4. Required submission artifacts.
5. Only then, UI or a second scenario.
