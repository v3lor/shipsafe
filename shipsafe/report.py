"""All output formats derive from the same observed result object."""
import json
from pathlib import Path


def terminal(report):
    lines = [report["verdict"] + ": " + report["summary"],
             f"{'Gate':<16} {'Result':<8} Evidence"]
    for gate in report["gates"]:
        lines.append(f"{gate['id']:<16} {gate['result']:<8} " +
                     json.dumps(gate["evidence"], ensure_ascii=False))
    lines.append(f"Elapsed: {report['elapsed_seconds']:.3f}s (measured locally)")
    return "\n".join(lines)


def markdown(report):
    lines = [f"# Release decision: {report['verdict']}", "", report["summary"], "",
             report["scope"], "", f"Migration: `{report['migration']}`",
             f"SQL SHA-256: `{report['migration_sha256']}`", "",
             f"Seeded orders: {report['seed_count']}",
             f"Measured elapsed seconds: {report['elapsed_seconds']:.6f}", ""]
    for gate in report["gates"]:
        lines.extend([f"## {gate['id']}: {gate['result']}", "",
                      f"Measured seconds: {gate['elapsed_seconds']}", "", "```json",
                      json.dumps(gate["evidence"], ensure_ascii=False, indent=2), "```", ""])
    lines.extend(["## Investigation and remediation", "",
                  "Gate evidence above is observed. IBM Bob IDE should investigate the failure, "
                  "implement and verify the repair, then document the root cause and exact "
                  "remediation. This generated report does not claim that work has occurred.", ""])
    return "\n".join(lines)


def write_reports(report, json_path, markdown_path):
    for path, content in ((json_path, json.dumps(report, ensure_ascii=False, indent=2) + "\n"),
                          (markdown_path, markdown(report))):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
