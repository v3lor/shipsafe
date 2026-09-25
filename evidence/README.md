# Captured initial rehearsal

Captured on 2026-09-25 with Python 3.12.14 and SQLite 3.53.1 on Windows.
From the repository root, using the installed local virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 22 passed in 0.59s; exit 0
.\.venv\Scripts\python.exe -m shipsafe rehearse --migration migrations/candidate.sql --json out/report.json
# BLOCK; exit 1; measured local elapsed time rounded to 0.017s
Copy-Item out/report.json evidence/red-report.json
Copy-Item out/release-decision.md evidence/red-release-decision.md
```

SQLite raised `OperationalError: Cannot add a NOT NULL column with default value NULL`
(`SQLITE_ERROR`, code 1). Migration failed and all four dependent gates were
skipped. The JSON contains the actual measured timing and migration SQL hash;
the Markdown was generated from that same result. The candidate and unsafe
exhibit were byte-identical when this evidence was captured.

There is no green release evidence yet. Passing downstream tests use a test-only
schema and do not establish that the release candidate works. Bob's handoff is
Prompt B in `PROMPTS.md`: investigate this observed failure, repair the candidate,
rerun the tests and rehearsal, and retain actual green evidence and session screenshots.
