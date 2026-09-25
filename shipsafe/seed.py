"""Deterministic fictional fixture. Never stores a checked-in database."""
from .db import connect

ORDERS = (
    (1, "Demo Cedar", "1 Imaginary Lane", "pending"),
    (2, "Demo Orbit", None, "pending"),
    (3, "Demo O'Clock", "", "shipped"),
    (4, "Demo Café", "Unit Ω, Fictional Station", "delivered"),
    (5, "Demo Parcel", "Line one\nLine two — invented", "pending"),
)


def seed(db_path):
    with connect(db_path) as db:
        db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, "
                   "customer_label TEXT NOT NULL, address TEXT, status TEXT NOT NULL)")
        db.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", ORDERS)
