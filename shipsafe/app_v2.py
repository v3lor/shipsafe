"""Candidate app supports an optional delivery window on the migrated schema."""
from .db import connect, validate


def create_order(db_path, customer_label, address, status, delivery_window=None):
    validate(customer_label, address, status)
    if delivery_window is not None and (
        not isinstance(delivery_window, str) or not delivery_window.strip()
    ):
        raise ValueError("delivery_window must be nonempty text or None")
    with connect(db_path) as db:
        return db.execute(
            "INSERT INTO orders (customer_label, address, status, delivery_window) "
            "VALUES (?, ?, ?, ?)",
            (customer_label, address, status, delivery_window),
        ).lastrowid


def get_order(db_path, order_id):
    with connect(db_path) as db:
        row = db.execute(
            "SELECT id, customer_label, address, status, delivery_window "
            "FROM orders WHERE id = ?", (order_id,),
        ).fetchone()
        return dict(row) if row else None


def list_orders(db_path):
    with connect(db_path) as db:
        return [dict(row) for row in db.execute(
            "SELECT id, customer_label, address, status, delivery_window "
            "FROM orders ORDER BY id"
        )]
