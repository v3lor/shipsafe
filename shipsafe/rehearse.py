"""Ordered gates operating on one disposable database per rehearsal."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
import hashlib

from . import app_v1, app_v2
from .db import connect
from .seed import seed

GATES = ("migration", "preservation", "old-version", "new-version", "rollback")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def decision(gates):
    return "GO" if (
        [gate["id"] for gate in gates] == list(GATES)
        and all(gate["result"] == "PASS" for gate in gates)
    ) else "BLOCK"


def migrate(db_path, sql):
    with connect(db_path) as db:
        db.executescript(sql)
    return {"summary": "SQLite executed the candidate SQL"}


def preservation(db_path, baseline):
    after = app_v1.list_orders(db_path)
    require(after == baseline, "Seeded IDs, fields, or order count changed")
    return {"count_before": len(baseline), "count_after": len(after),
            "preserved_orders": after}


def old_version(db_path, baseline):
    require(app_v1.get_order(db_path, baseline[0]["id"]) == baseline[0],
            "v1 could not read the original order")
    order_id = app_v1.create_order(db_path, "Demo Rollout", None, "pending")
    expected = dict(id=order_id, customer_label="Demo Rollout", address=None, status="pending")
    require(app_v1.get_order(db_path, order_id) == expected, "v1 write did not round-trip")
    return {"read_seed_id": baseline[0]["id"], "created_order": expected}


def new_version(db_path, baseline):
    legacy = app_v2.get_order(db_path, baseline[0]["id"])
    require(legacy == dict(baseline[0], delivery_window=None),
            "v2 must read the legacy order with no delivery window")
    order_id = app_v2.create_order(db_path, "Demo New App", "Imaginary depot", "pending", "9–12")
    expected = dict(id=order_id, customer_label="Demo New App", address="Imaginary depot",
                    status="pending", delivery_window="9–12")
    require(app_v2.get_order(db_path, order_id) == expected, "v2 window did not round-trip")
    require(expected in app_v2.list_orders(db_path), "v2 list omitted its new order")
    optional_id = app_v2.create_order(db_path, "Demo Optional", None, "pending")
    require(app_v2.get_order(db_path, optional_id) == dict(
        id=optional_id, customer_label="Demo Optional", address=None, status="pending",
        delivery_window=None), "v2 optional window did not round-trip")
    return {"legacy_order": legacy, "created_order": expected, "optional_order_id": optional_id}


def rollback(db_path, new_evidence):
    expected = {key: value for key, value in new_evidence["created_order"].items()
                if key != "delivery_window"}
    require(app_v1.get_order(db_path, expected["id"]) == expected,
            "v1 cannot read the v2-written order after application rollback")
    require(expected in app_v1.list_orders(db_path), "v1 list omitted the v2-written order")
    order_id = app_v1.create_order(db_path, "Demo Rollback", "Fictional locker", "pending")
    created = dict(id=order_id, customer_label="Demo Rollback", address="Fictional locker", status="pending")
    require(app_v1.get_order(db_path, order_id) == created, "Rollback write did not round-trip")
    return {"v2_order_read_by_v1": expected, "created_order": created,
            "schema_unchanged": True}


def rehearse(migration):
    started = perf_counter()
    migration = Path(migration)
    sql = migration.read_text(encoding="utf-8")
    gates = []
    with TemporaryDirectory(prefix="shipsafe-") as directory:
        db_path = Path(directory) / "orders.sqlite"
        seed(db_path)
        baseline = app_v1.list_orders(db_path)
        actions = (
            lambda: migrate(db_path, sql),
            lambda: preservation(db_path, baseline),
            lambda: old_version(db_path, baseline),
            lambda: new_version(db_path, baseline),
            lambda: rollback(db_path, gates[3]["evidence"]),
        )
        failed = None
        for gate_id, action in zip(GATES, actions):
            if failed:
                gates.append(dict(id=gate_id, result="SKIP", elapsed_seconds=None,
                                  evidence={"reason": f"Prerequisite {failed} failed"}))
                continue
            gate_started = perf_counter()
            try:
                evidence = action()
                result = "PASS"
            except Exception as error:
                result = "FAIL"
                failed = gate_id
                evidence = {"error_type": type(error).__name__, "error": str(error)}
                for attribute in ("sqlite_errorcode", "sqlite_errorname"):
                    if hasattr(error, attribute):
                        evidence[attribute] = getattr(error, attribute)
            gates.append(dict(id=gate_id, result=result, evidence=evidence,
                              elapsed_seconds=perf_counter() - gate_started))
    verdict = decision(gates)
    return {"schema_version": 1, "verdict": verdict,
            "summary": ("GO for this simulated scenario" if verdict == "GO" else
                        "Release blocked: required gates failed or were skipped"),
            "migration": migration.as_posix(),
            "migration_sha256": hashlib.sha256(sql.encode("utf-8")).hexdigest(),
            "seed_count": len(baseline), "gates": gates,
            "elapsed_seconds": perf_counter() - started,
            "scope": "Local synthetic SQLite simulation; not a production safety guarantee."}
