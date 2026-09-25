import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from shipsafe import app_v1, app_v2
from shipsafe.db import connect
import shipsafe.rehearse as runner
from shipsafe.seed import ORDERS, seed

ROOT = Path(__file__).resolve().parents[1]
UNSAFE = ROOT / "examples/unsafe.sql"


@pytest.fixture
def v2_database(tmp_path):
    # Test-only schema, not a migration or proposed repair for Bob.
    path = tmp_path / "app-contract.sqlite"
    with connect(path) as db:
        db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_label TEXT NOT NULL, "
                   "address TEXT, status TEXT NOT NULL, delivery_window TEXT)")
        db.executemany("INSERT INTO orders (id, customer_label, address, status) VALUES (?, ?, ?, ?)", ORDERS)
    return path


def test_unsafe_is_real_sqlite_failure_and_dependencies_skip():
    report = runner.rehearse(UNSAFE)
    assert report["verdict"] == "BLOCK"
    assert [g["result"] for g in report["gates"]] == ["FAIL", "SKIP", "SKIP", "SKIP", "SKIP"]
    evidence = report["gates"][0]["evidence"]
    assert evidence["error_type"] == "OperationalError"
    assert "Cannot add a NOT NULL column with default value NULL" in evidence["error"]
    assert evidence["sqlite_errorname"] == "SQLITE_ERROR"
    assert report["seed_count"] == 5
    assert report["elapsed_seconds"] > 0
    assert all(g["elapsed_seconds"] is None for g in report["gates"][1:])


def test_repeatability_fixture_unchanged_and_temp_cleanup(monkeypatch):
    original = (ROOT / "shipsafe/seed.py").read_bytes(), UNSAFE.read_bytes()
    paths = []
    def observed_seed(path):
        paths.append(path)
        assert not path.exists()
        seed(path)
    monkeypatch.setattr(runner, "seed", observed_seed)
    first, second = runner.rehearse(UNSAFE), runner.rehearse(UNSAFE)
    assert paths[0] != paths[1]
    assert all(not p.parent.exists() for p in paths)
    assert first["verdict"] == second["verdict"] == "BLOCK"
    assert [(g["result"], g["evidence"]) for g in first["gates"]] == [
        (g["result"], g["evidence"]) for g in second["gates"]]
    assert original == ((ROOT / "shipsafe/seed.py").read_bytes(), UNSAFE.read_bytes())


def test_real_downstream_app_gates_on_same_database(v2_database):
    baseline = app_v1.list_orders(v2_database)
    runner.preservation(v2_database, baseline)
    runner.old_version(v2_database, baseline)
    new = runner.new_version(v2_database, baseline)
    runner.rollback(v2_database, new)
    assert len(app_v1.list_orders(v2_database)) == len(ORDERS) + 4
    assert app_v2.get_order(v2_database, new["created_order"]["id"])["delivery_window"] == "9–12"


def test_orchestration_go_with_test_only_schema(v2_database, tmp_path, monkeypatch):
    # Exercise every runner gate with real SQLite, starting from a test schema.
    # No safe migration is provided; the release candidate stays untouched.
    def test_seed(path):
        with connect(v2_database) as source, connect(path) as target:
            source.backup(target)
    monkeypatch.setattr(runner, "seed", test_seed)
    sql = tmp_path / "probe.sql"
    sql.write_text("SELECT count(*) FROM orders;", encoding="utf-8")
    report = runner.rehearse(sql)
    assert report["verdict"] == "GO"
    assert [g["result"] for g in report["gates"]] == ["PASS"] * 5
    assert report["gates"][4]["evidence"]["v2_order_read_by_v1"]["id"] == report["gates"][3]["evidence"]["created_order"]["id"]


@pytest.mark.parametrize("sql,failed", [
    ("UPDATE orders SET address = 'lost' WHERE id = 2;", "preservation"),
    ("DELETE FROM orders WHERE id = 3;", "preservation"),
    ("CREATE TRIGGER deny_insert BEFORE INSERT ON orders BEGIN SELECT RAISE(ABORT, 'write denied'); END;", "old-version"),
    ("SELECT 1;", "new-version"),
])
def test_real_gate_failures_propagate(tmp_path, sql, failed):
    migration = tmp_path / "broken.sql"
    migration.write_text(sql, encoding="utf-8")
    report = runner.rehearse(migration)
    index = list(runner.GATES).index(failed)
    assert report["verdict"] == "BLOCK"
    assert all(g["result"] == "PASS" for g in report["gates"][:index])
    assert report["gates"][index]["result"] == "FAIL"
    assert all(g["result"] == "SKIP" for g in report["gates"][index + 1:])


def test_rollback_detects_real_write_failure(v2_database):
    baseline = app_v1.list_orders(v2_database)
    new = runner.new_version(v2_database, baseline)
    with connect(v2_database) as db:
        db.execute("CREATE TRIGGER deny_insert BEFORE INSERT ON orders BEGIN SELECT RAISE(ABORT, 'rollback denied'); END;")
    with pytest.raises(sqlite3.IntegrityError, match="rollback denied"):
        runner.rollback(v2_database, new)


@pytest.mark.parametrize("result", ["FAIL", "SKIP"])
@pytest.mark.parametrize("index", range(5))
def test_every_nonpassing_gate_blocks(result, index):
    gates = [dict(id=name, result="PASS") for name in runner.GATES]
    assert runner.decision(gates) == "GO"
    gates[index]["result"] = result
    assert runner.decision(gates) == "BLOCK"
    assert runner.decision([]) == "BLOCK"


def test_parameterized_sql_validation_and_optional_window(v2_database):
    label = "Demo '); DROP TABLE orders; --"
    order_id = app_v1.create_order(v2_database, label, None, "pending")
    assert app_v1.get_order(v2_database, order_id)["customer_label"] == label
    assert app_v2.get_order(v2_database, order_id)["delivery_window"] is None
    assert app_v1.get_order(v2_database, -1) is None
    assert app_v2.get_order(v2_database, -1) is None
    with pytest.raises(ValueError):
        app_v1.create_order(v2_database, "", None, "pending")
    with pytest.raises(ValueError):
        app_v2.create_order(v2_database, "Demo", None, "unknown")
    with pytest.raises(ValueError):
        app_v2.create_order(v2_database, "Demo", None, "pending", "")


def test_reports_and_cli(tmp_path):
    json_path, md_path = tmp_path / "report.json", tmp_path / "decision.md"
    run = subprocess.run([sys.executable, "-m", "shipsafe", "rehearse", "--migration", str(UNSAFE),
                          "--json", str(json_path), "--markdown", str(md_path)],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 1
    assert "BLOCK" in run.stdout and "Cannot add a NOT NULL column" in run.stdout
    report = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = md_path.read_text(encoding="utf-8")
    assert report["verdict"] == "BLOCK"
    for gate in report["gates"]:
        assert f"{gate['id']}: {gate['result']}" in markdown
    assert report["gates"][0]["evidence"]["error"] in markdown


def test_cli_missing_input_and_path_collision(tmp_path):
    from shipsafe.__main__ import main
    assert main(["rehearse", "--migration", str(tmp_path / "missing.sql")]) == 2
    with pytest.raises(SystemExit) as error:
        main(["rehearse", "--migration", str(UNSAFE), "--json", str(UNSAFE)])
    assert error.value.code == 2
