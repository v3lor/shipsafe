"""Original order interface; explicit columns tolerate additive schema changes."""
from .db import connect, validate


def create_order(db_path, customer_label, address, status):
    validate(customer_label, address, status)
    with connect(db_path) as db:
        return db.execute(
            "INSERT INTO orders (customer_label, address, status) VALUES (?, ?, ?)",
            (customer_label, address, status),
        ).lastrowid


def get_order(db_path, order_id):
    with connect(db_path) as db:
        row = db.execute(
            "SELECT id, customer_label, address, status FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
        return dict(row) if row else None


def list_orders(db_path):
    with connect(db_path) as db:
        return [dict(row) for row in db.execute(
            "SELECT id, customer_label, address, status FROM orders ORDER BY id"
        )]
