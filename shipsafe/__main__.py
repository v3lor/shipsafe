import argparse
from pathlib import Path
import sys

from .rehearse import rehearse
from .report import terminal, write_reports


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rehearse a local synthetic SQLite release")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("rehearse")
    run.add_argument("--migration", type=Path, default=Path("migrations/candidate.sql"))
    run.add_argument("--json", type=Path, default=Path("out/report.json"))
    run.add_argument("--markdown", type=Path, default=Path("out/release-decision.md"))
    args = parser.parse_args(argv)
    paths = [args.migration.resolve(), args.json.resolve(), args.markdown.resolve()]
    if len(set(paths)) != 3:
        parser.error("Migration, JSON, and Markdown paths must be distinct")
    try:
        report = rehearse(args.migration)
        write_reports(report, args.json, args.markdown)
    except (OSError, UnicodeError) as error:
        print(f"ShipSafe input/output error: {error}", file=sys.stderr)
        return 2
    print(terminal(report))
    return 0 if report["verdict"] == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
