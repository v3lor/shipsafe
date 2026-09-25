"""Short-lived, committed SQLite connections shared by the sample apps."""
from contextlib import contextmanager
import sqlite3


@contextmanager
def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()


def validate(customer_label, address, status):
    if not isinstance(customer_label, str) or not customer_label.strip():
        raise ValueError("customer_label must be nonempty text")
    if address is not None and not isinstance(address, str):
        raise ValueError("address must be text or None")
    if status not in {"pending", "shipped", "delivered"}:
        raise ValueError("status must be pending, shipped, or delivered")
